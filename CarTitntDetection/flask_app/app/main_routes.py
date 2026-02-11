from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, send_file
from functools import wraps
from datetime import datetime, timedelta
import os
import json
from sqlalchemy import func
import numpy as np

from app.models import db, User, TestResult, PerformanceLog
from app.inference import InferenceManager
from app.config import Config

main_bp = Blueprint('main', __name__)

# Initialize inference manager
inference_manager = InferenceManager(
    api_url=Config.ROBOFLOW_API_URL,
    api_key=Config.ROBOFLOW_API_KEY,
    model_id=Config.MODEL_ID
)


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in first', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current logged-in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None


@main_bp.route('/')
def index():
    """Home/landing page"""
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard with system overview"""
    user = get_current_user()
    
    # Get statistics
    test_results = TestResult.query.filter_by(user_id=user.id).all()
    
    stats = {
        'total_tests': len(test_results),
        'image_tests': len([t for t in test_results if t.test_type == 'image']),
        'video_tests': len([t for t in test_results if t.test_type == 'video']),
        'webcam_tests': len([t for t in test_results if t.test_type == 'webcam']),
        'total_detections': sum(t.windows_detected for t in test_results),
        'tinted_windows': sum(t.tinted_windows for t in test_results),
        'clear_windows': sum(t.clear_windows for t in test_results),
        'avg_confidence': np.mean([t.average_confidence for t in test_results if t.average_confidence > 0]) if test_results else 0
    }
    
    # Get recent tests
    recent_tests = TestResult.query.filter_by(user_id=user.id).order_by(
        TestResult.created_at.desc()
    ).limit(5).all()
    
    # Performance data for chart (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_tests = db.session.query(
        func.date(TestResult.created_at).label('date'),
        func.count(TestResult.id).label('count')
    ).filter(
        TestResult.user_id == user.id,
        TestResult.created_at >= seven_days_ago
    ).group_by(
        func.date(TestResult.created_at)
    ).all()
    
    chart_data = {
        'dates': [str(d[0]) for d in daily_tests],
        'counts': [d[1] for d in daily_tests]
    }
    
    return render_template(
        'main/dashboard.html',
        user=user,
        stats=stats,
        recent_tests=recent_tests,
        chart_data=json.dumps(chart_data)
    )


@main_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user = get_current_user()
    test_count = TestResult.query.filter_by(user_id=user.id).count()
    
    return render_template('main/profile.html', user=user, test_count=test_count)


@main_bp.route('/test')
@login_required
def test_page():
    """Test page with options for image, video, webcam"""
    return render_template('main/test.html')


@main_bp.route('/test/image', methods=['GET', 'POST'])
@login_required
def test_image():
    """Test with image"""
    if request.method == 'POST':
        user = get_current_user()
        try:
            # Ensure upload folder exists
            if not os.path.exists(Config.UPLOAD_FOLDER):
                os.makedirs(Config.UPLOAD_FOLDER)
            
            if 'image' not in request.files:
                return jsonify({'success': False, 'error': 'No image provided'}), 400
            
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Validate file type
            allowed_extensions = {'jpg', 'jpeg', 'png', 'webp', 'bmp'}
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                return jsonify({'success': False, 'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
            
            # Save uploaded file
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{file.filename}"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            
            file.save(filepath)
            
            # Run inference
            result = inference_manager.run_inference(filepath)
            
            if not result['success']:
                test_result = TestResult(
                    user_id=user.id,
                    test_type='image',
                    file_path=filepath,
                    original_filename=file.filename,
                    status='failed',
                    error_message=result['error'],
                    processing_time=result['processing_time']
                )
                db.session.add(test_result)
                db.session.commit()
                
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
            
            predictions = result['predictions']
            
            # Draw predictions
            output_filename = f"output_{timestamp}.jpg"
            output_path = os.path.join(Config.UPLOAD_FOLDER, output_filename)
            
            draw_result = inference_manager.draw_predictions(filepath, predictions, output_path)
            
            # Calculate statistics
            stats = inference_manager.calculate_statistics([predictions])
            
            # Save to database
            test_result = TestResult(
                user_id=user.id,
                test_type='image',
                file_path=filepath,
                original_filename=file.filename,
                output_path=output_filename,
                windows_detected=draw_result['total_count'],
                tinted_windows=draw_result['tinted_count'],
                clear_windows=draw_result['clear_count'],
                average_confidence=stats['avg_confidence'],
                total_detections=stats['total_detections'],
                processing_time=result['processing_time'],
                predictions_json=json.dumps(predictions),
                status='completed'
            )
            
            db.session.add(test_result)
            db.session.commit()
            
            # Update performance log
            update_performance_log(user.id)
            
            # Prepare response message
            message = None
            if draw_result['total_count'] == 0:
                message = "No tinted windows detected in this image. The AI did not find any vehicle windows or tinted glass."
            
            return jsonify({
                'success': True,
                'result_id': test_result.id,
                'windows_detected': draw_result['total_count'],
                'tinted_windows': draw_result['tinted_count'],
                'clear_windows': draw_result['clear_count'],
                'average_confidence': round(stats['avg_confidence'], 3) if stats['avg_confidence'] > 0 else 0,
                'processing_time': round(result['processing_time'], 2),
                'output_path': url_for('main.get_image', filename=output_filename),
                'message': message
            })
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('main/test_image.html')


@main_bp.route('/test/video', methods=['GET', 'POST'])
@login_required
def test_video():
    """Test with video"""
    user = get_current_user()
    
    if request.method == 'POST':
        try:
            # Ensure upload folder exists
            if not os.path.exists(Config.UPLOAD_FOLDER):
                os.makedirs(Config.UPLOAD_FOLDER)
            
            if 'video' not in request.files:
                return jsonify({'success': False, 'error': 'No video provided'}), 400
            
            file = request.files['video']
            
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            # Validate file type
            allowed_extensions = {'mp4', 'avi', 'mov', 'mkv', 'webm'}
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                return jsonify({'success': False, 'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
            
            # Save video file
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{file.filename}"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            
            file.save(filepath)
            
            # Extract frames (every 10th frame)
            frame_dir = os.path.join(Config.UPLOAD_FOLDER, f"frames_{timestamp}")
            os.makedirs(frame_dir, exist_ok=True)
            
            frames = inference_manager.extract_video_frames(filepath, frame_dir, frame_skip=10)
            
            if not frames:
                return jsonify({'success': False, 'error': 'Could not extract frames from video'}), 400
            
            # Run inference on frames
            all_predictions = []
            processing_times = []
            
            for idx, frame_info in enumerate(frames):
                result = inference_manager.run_inference(frame_info['path'])
                if result['success']:
                    all_predictions.extend(result['predictions'])
                    processing_times.append(result['processing_time'])
            
            # Calculate statistics
            stats = inference_manager.calculate_statistics(
                [[p] for p in all_predictions]
            )
            
            # Process first frame for output image
            output_filename = f"video_output_{timestamp}.jpg"
            output_path = os.path.join(Config.UPLOAD_FOLDER, output_filename)
            
            if frames and all_predictions:
                inference_manager.draw_predictions(
                    frames[0]['path'],
                    all_predictions[:len(all_predictions)//len(frames)] if frames else all_predictions,
                    output_path
                )
            
            # Save to database
            test_result = TestResult(
                user_id=user.id,
                test_type='video',
                file_path=filepath,
                original_filename=file.filename,
                output_path=output_filename if os.path.exists(output_path) else None,
                windows_detected=stats['total_detections'],
                tinted_windows=stats['tinted_count'],
                clear_windows=stats['clear_count'],
                average_confidence=stats['avg_confidence'],
                total_detections=stats['total_detections'],
                processing_time=sum(processing_times) if processing_times else 0,
                predictions_json=json.dumps(all_predictions),
                status='completed'
            )
            
            db.session.add(test_result)
            db.session.commit()
            
            # Update performance log
            update_performance_log(user.id)
            
            # Prepare response message
            message = None
            if stats['total_detections'] == 0:
                message = "No tinted windows detected in this video. The AI did not find any vehicle windows or tinted glass in the processed frames."
            
            return jsonify({
                'success': True,
                'result_id': test_result.id,
                'windows_detected': stats['total_detections'],
                'tinted_windows': stats['tinted_count'],
                'clear_windows': stats['clear_count'],
                'average_confidence': round(stats['avg_confidence'], 3) if stats['avg_confidence'] > 0 else 0,
                'processing_time': round(sum(processing_times) if processing_times else 0, 2),
                'frames_processed': len(frames),
                'output_path': url_for('main.get_image', filename=output_filename) if os.path.exists(output_path) else None,
                'message': message
            })
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('main/test_video.html')


@main_bp.route('/test/webcam', methods=['GET', 'POST'])
@login_required
def test_webcam():
    """Test with webcam"""
    if request.method == 'POST':
        try:
            # Ensure upload folder exists
            if not os.path.exists(Config.UPLOAD_FOLDER):
                os.makedirs(Config.UPLOAD_FOLDER)
            
            # Get image data from webcam
            data = request.get_json()
            image_data = data.get('image')
            
            if not image_data:
                return jsonify({'success': False, 'error': 'No image data'}), 400
            
            user = get_current_user()
            
            # Decode base64 image
            import base64
            try:
                image_bytes = base64.b64decode(image_data.split(',')[1])
            except Exception as e:
                return jsonify({'success': False, 'error': f'Invalid image data: {str(e)}'}), 400
            
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename = f"webcam_{timestamp}.jpg"
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            # Run inference
            result = inference_manager.run_inference(filepath)
            
            if not result['success']:
                test_result = TestResult(
                    user_id=user.id,
                    test_type='webcam',
                    file_path=filepath,
                    original_filename=filename,
                    status='failed',
                    error_message=result['error'],
                    processing_time=result['processing_time']
                )
                db.session.add(test_result)
                db.session.commit()
                
                return jsonify({
                    'success': False,
                    'error': result['error']
                }), 500
            
            predictions = result['predictions']
            
            # Draw predictions
            output_filename = f"webcam_output_{timestamp}.jpg"
            output_path = os.path.join(Config.UPLOAD_FOLDER, output_filename)
            
            draw_result = inference_manager.draw_predictions(filepath, predictions, output_path)
            
            # Calculate statistics
            stats = inference_manager.calculate_statistics([predictions])
            
            # Save to database
            test_result = TestResult(
                user_id=user.id,
                test_type='webcam',
                file_path=filepath,
                original_filename=filename,
                output_path=output_filename,
                windows_detected=draw_result['total_count'],
                tinted_windows=draw_result['tinted_count'],
                clear_windows=draw_result['clear_count'],
                average_confidence=stats['avg_confidence'],
                total_detections=stats['total_detections'],
                processing_time=result['processing_time'],
                predictions_json=json.dumps(predictions),
                status='completed'
            )
            
            db.session.add(test_result)
            db.session.commit()
            
            # Update performance log
            update_performance_log(user.id)
            
            # Prepare response message
            message = None
            if draw_result['total_count'] == 0:
                message = "No tinted windows detected in this webcam capture. The AI did not find any vehicle windows or tinted glass."
            
            return jsonify({
                'success': True,
                'result_id': test_result.id,
                'windows_detected': draw_result['total_count'],
                'tinted_windows': draw_result['tinted_count'],
                'clear_windows': draw_result['clear_count'],
                'average_confidence': round(stats['avg_confidence'], 3) if stats['avg_confidence'] > 0 else 0,
                'processing_time': round(result['processing_time'], 2),
                'output_path': url_for('main.get_image', filename=output_filename),
                'message': message
            })
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'success': False, 'error': str(e)}), 500
    
    return render_template('main/test_webcam.html')


@main_bp.route('/results')
@login_required
def results():
    """View all test results"""
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    paginated_results = TestResult.query.filter_by(user_id=user.id).order_by(
        TestResult.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return render_template(
        'main/results.html',
        results=paginated_results.items,
        total=paginated_results.total,
        pages=paginated_results.pages,
        current_page=page
    )


@main_bp.route('/results/<int:result_id>')
@login_required
def result_detail(result_id):
    """View single result details"""
    user = get_current_user()
    result = TestResult.query.get_or_404(result_id)
    
    if result.user_id != user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.results'))
    
    predictions = json.loads(result.predictions_json) if result.predictions_json else []
    
    return render_template('main/result_detail.html', result=result, predictions=predictions)


@main_bp.route('/stats')
@login_required
def stats():
    """Statistics and charts page"""
    user = get_current_user()
    test_results = TestResult.query.filter_by(user_id=user.id).all()
    
    if not test_results:
        return render_template('main/stats.html', chart_data={})
    
    # Test type breakdown
    type_breakdown = {
        'image': len([t for t in test_results if t.test_type == 'image']),
        'video': len([t for t in test_results if t.test_type == 'video']),
        'webcam': len([t for t in test_results if t.test_type == 'webcam'])
    }
    
    # Window type breakdown
    window_breakdown = {
        'tinted': sum(t.tinted_windows for t in test_results),
        'clear': sum(t.clear_windows for t in test_results)
    }
    
    # Daily trend (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_data = db.session.query(
        func.date(TestResult.created_at).label('date'),
        func.count(TestResult.id).label('count'),
        func.avg(TestResult.average_confidence).label('avg_conf')
    ).filter(
        TestResult.user_id == user.id,
        TestResult.created_at >= thirty_days_ago
    ).group_by(
        func.date(TestResult.created_at)
    ).order_by('date').all()
    
    trend_data = {
        'dates': [str(d[0]) for d in daily_data],
        'counts': [d[1] for d in daily_data],
        'confidence': [round(float(d[2]), 3) if d[2] else 0 for d in daily_data]
    }
    
    chart_data = {
        'type_breakdown': type_breakdown,
        'window_breakdown': window_breakdown,
        'trend_data': trend_data
    }
    
    return render_template('main/stats.html', chart_data=json.dumps(chart_data))


@main_bp.route('/logs')
@login_required
def logs():
    """View test logs"""
    user = get_current_user()
    page = request.args.get('page', 1, type=int)
    filter_type = request.args.get('type', 'all')
    
    query = TestResult.query.filter_by(user_id=user.id)
    
    if filter_type != 'all':
        query = query.filter_by(test_type=filter_type)
    
    paginated_logs = query.order_by(TestResult.created_at.desc()).paginate(
        page=page, per_page=20
    )
    
    return render_template(
        'main/logs.html',
        logs=paginated_logs.items,
        total=paginated_logs.total,
        pages=paginated_logs.pages,
        current_page=page,
        filter_type=filter_type
    )


@main_bp.route('/image/<filename>')
@login_required
def get_image(filename):
    """Serve image files"""
    user = get_current_user()
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    
    # Verify ownership
    test_result = TestResult.query.filter(
        (TestResult.file_path.like(f'%{filename}%')) |
        (TestResult.output_path.like(f'%{filename}%'))
    ).first()
    
    if not test_result or test_result.user_id != user.id:
        flash('Unauthorized access', 'error')
        return redirect(url_for('main.dashboard'))
    
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/jpeg')
    
    flash('File not found', 'error')
    return redirect(url_for('main.results'))


def update_performance_log(user_id):
    """Update performance log for user"""
    test_results = TestResult.query.filter_by(user_id=user_id).all()
    
    perf_log = PerformanceLog.query.filter_by(user_id=user_id).first()
    
    if not perf_log:
        perf_log = PerformanceLog(user_id=user_id)
    
    # Update statistics
    perf_log.total_tests = len(test_results)
    perf_log.total_detections = sum(t.windows_detected for t in test_results)
    perf_log.image_tests = len([t for t in test_results if t.test_type == 'image'])
    perf_log.video_tests = len([t for t in test_results if t.test_type == 'video'])
    perf_log.webcam_tests = len([t for t in test_results if t.test_type == 'webcam'])
    perf_log.tinted_count = sum(t.tinted_windows for t in test_results)
    perf_log.clear_count = sum(t.clear_windows for t in test_results)
    
    if test_results:
        perf_log.average_confidence = np.mean([t.average_confidence for t in test_results if t.average_confidence > 0])
        processing_times = [t.processing_time for t in test_results if t.processing_time]
        if processing_times:
            perf_log.avg_processing_time = np.mean(processing_times)
            perf_log.max_processing_time = np.max(processing_times)
            perf_log.min_processing_time = np.min(processing_times)
    
    db.session.add(perf_log)
    db.session.commit()
