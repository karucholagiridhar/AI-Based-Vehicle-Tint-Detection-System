"""
View only TEST RESULTS table
"""
from app import create_app, db
from app.models import User, TestResult
import sys

app = create_app()

with app.app_context():
    print("\n" + "=" * 100)
    print("  🧪 TEST RESULTS TABLE")
    print("=" * 100)
    
    # Filter by username if provided
    username = sys.argv[1] if len(sys.argv) > 1 else None
    
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            tests = TestResult.query.filter_by(user_id=user.id).order_by(TestResult.created_at.desc()).all()
            print(f"\nShowing results for user: {username}")
        else:
            print(f"\n❌ User '{username}' not found")
            tests = []
    else:
        tests = TestResult.query.order_by(TestResult.created_at.desc()).all()
        print(f"\nShowing all test results")
    
    print(f"Total: {len(tests)}\n")
    
    if tests:
        # Summary
        image_count = len([t for t in tests if t.test_type == 'image'])
        video_count = len([t for t in tests if t.test_type == 'video'])
        webcam_count = len([t for t in tests if t.test_type == 'webcam'])
        
        print("📊 Summary:")
        print(f"  Image Tests:  {image_count}")
        print(f"  Video Tests:  {video_count}")
        print(f"  Webcam Tests: {webcam_count}")
        print()
        
        # Table header
        print(f"{'ID':<5} {'User':<12} {'Type':<8} {'Windows':<8} {'Tinted':<8} {'Clear':<7} {'Conf':<8} {'Time':<7} {'Date':<17}")
        print("-" * 100)
        
        for test in tests[:50]:  # Limit to 50 most recent
            user = test.user.username if test.user else 'Unknown'
            date = test.created_at.strftime('%Y-%m-%d %H:%M')
            
            print(f"{test.id:<5} {user:<12} {test.test_type:<8} {test.windows_detected:<8} "
                  f"{test.tinted_windows:<8} {test.clear_windows:<7} "
                  f"{test.average_confidence*100:>6.1f}% {test.processing_time:>6.1f}s {date:<17}")
        
        if len(tests) > 50:
            print(f"\n... and {len(tests) - 50} more results (showing 50 most recent)")
    else:
        print("No test results found.")
    
    print("\n💡 TIP: Run 'python view_test_results.py <username>' to filter by user")
    print("=" * 100)
    print()
