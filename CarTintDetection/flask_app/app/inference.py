import cv2
import os
import time
import tempfile
from inference_sdk import InferenceHTTPClient
import numpy as np


class InferenceManager:
    """Handles inference operations with Roboflow API"""
    
    def __init__(self, api_url, api_key, model_id):
        # Initialize client without specifying api_url to use default hosted API
        self.client = InferenceHTTPClient(
            api_url="https://detect.roboflow.com",
            api_key=api_key
        )
        self.model_id = model_id
        self.colors = {
            'tinted': (255, 0, 255),      # Magenta/Pink
            'clear': (180, 0, 255)        # Purple
        }
    
    def resize_for_api(self, path, max_w=1920):
        """Resize image to avoid 413 error - optimized for speed and quality balance"""
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Cannot read image: {path}")
        
        h, w, _ = img.shape
        scale = 1.0
        
        # Ensure minimum resolution for good window detection
        min_width = 1280
        if w < min_width:
            scale = min_width / w
            new_w = min_width
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        elif w > max_w:
            scale = max_w / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        temp_path = os.path.join(tempfile.gettempdir(), "temp_upload.jpg")
        # Use 90% quality for faster processing while maintaining detection accuracy
        cv2.imwrite(temp_path, img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        
        return temp_path, scale
    
    def run_inference(self, image_path):
        """Run inference with smart strategies to balance speed and accuracy"""
        start_time = time.time()
        
        try:
            # Validate image file exists
            if not os.path.exists(image_path):
                raise ValueError(f"Image file not found: {image_path}")
            
            all_predictions = []
            
            # Strategy 1: Try original image first (fastest)
            print(f"\n=== Running smart detection ===")
            result = self._attempt_inference(image_path)
            predictions = result.get('predictions', [])
            
            if predictions:
                print(f"✓ Original image: Found {len(predictions)} predictions")
                for pred in predictions:
                    pred['strategy'] = 'original'
                all_predictions.extend(predictions)
            else:
                print(f"✗ Original image: No predictions")
            
            # Check if we have good quality predictions (confidence > 25%)
            high_conf_preds = [p for p in predictions if p.get('confidence', 0) > 0.25]
            
            # Only try additional strategies if we didn't find good predictions
            if len(high_conf_preds) < 2:
                print(f"⚡ Trying enhanced strategies for better detection...")
                
                # Strategy 2: Enhanced contrast (best for tinted windows)
                enhanced_strategies = [
                    ('contrast_enhanced', self.adjust_contrast(image_path, 1.3)),
                    ('sharpened', self.sharpen_image(image_path)),
                ]
                
                for strategy_name, processed_path in enhanced_strategies:
                    if processed_path is None:
                        continue
                        
                    result = self._attempt_inference(processed_path)
                    predictions = result.get('predictions', [])
                    
                    if predictions:
                        print(f"✓ Strategy '{strategy_name}': Found {len(predictions)} predictions")
                        for pred in predictions:
                            pred['strategy'] = strategy_name
                        all_predictions.extend(predictions)
                    else:
                        print(f"✗ Strategy '{strategy_name}': No predictions")
                    
                    # Clean up temp files
                    if os.path.exists(processed_path):
                        try:
                            os.remove(processed_path)
                        except:
                            pass
                    
                    # Early exit if we found good predictions
                    if len([p for p in all_predictions if p.get('confidence', 0) > 0.20]) >= 2:
                        print(f"✓ Found sufficient predictions, skipping remaining strategies")
                        break
            else:
                print(f"✓ Found {len(high_conf_preds)} high-confidence predictions, skipping enhancement")
            
            # Deduplicate predictions (keep highest confidence for each region)
            final_predictions = self.deduplicate_predictions(all_predictions)
            
            processing_time = time.time() - start_time
            print(f"=== Total: {len(final_predictions)} unique predictions in {processing_time:.2f}s ===")
            
            return {
                'success': True,
                'predictions': final_predictions,
                'processing_time': processing_time
            }
        
        except Exception as e:
            processing_time = time.time() - start_time
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'processing_time': processing_time,
                'predictions': []
            }
    
    def adjust_brightness(self, image_path, factor):
        """Adjust image brightness"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            v = np.clip(v * factor, 0, 255).astype(np.uint8)
            enhanced = cv2.merge([h, s, v])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_HSV2BGR)
            
            temp_path = os.path.join(tempfile.gettempdir(), f"bright_{factor}_{os.path.basename(image_path)}")
            cv2.imwrite(temp_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 95])
            return temp_path
        except Exception as e:
            print(f"Brightness adjustment failed: {e}")
            return None
    
    def adjust_contrast(self, image_path, factor):
        """Adjust image contrast using CLAHE for better window edge detection"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Apply CLAHE to improve local contrast
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            clahe = cv2.createCLAHE(clipLimit=factor, tileGridSize=(8,8))
            l = clahe.apply(l)
            enhanced = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            
            temp_path = os.path.join(tempfile.gettempdir(), f"contrast_{os.path.basename(image_path)}")
            cv2.imwrite(temp_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 92])
            return temp_path
        except Exception as e:
            print(f"Contrast adjustment failed: {e}")
            return None
    
    def gamma_correction(self, image_path, gamma):
        """Apply gamma correction"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            inv_gamma = 1.0 / gamma
            table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype(np.uint8)
            enhanced = cv2.LUT(img, table)
            
            temp_path = os.path.join(tempfile.gettempdir(), f"gamma_{gamma}_{os.path.basename(image_path)}")
            cv2.imwrite(temp_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 95])
            return temp_path
        except Exception as e:
            print(f"Gamma correction failed: {e}")
            return None
    
    def sharpen_image(self, image_path):
        """Apply sharpening filter to enhance edges (helps detect window frames)"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Apply unsharp mask for better edge enhancement
            gaussian = cv2.GaussianBlur(img, (0, 0), 2.0)
            enhanced = cv2.addWeighted(img, 1.5, gaussian, -0.5, 0)
            
            temp_path = os.path.join(tempfile.gettempdir(), f"sharp_{os.path.basename(image_path)}")
            cv2.imwrite(temp_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, 92])
            return temp_path
        except Exception as e:
            print(f"Sharpening failed: {e}")
            return None
    
    def deduplicate_predictions(self, predictions):
        """Remove duplicate predictions, keeping highest confidence - optimized for speed"""
        if not predictions:
            return []
        
        # Skip deduplication if we have very few predictions (saves processing time)
        if len(predictions) <= 3:
            return predictions
        
        # Group by proximity (IoU-based)
        unique_preds = []
        for pred in sorted(predictions, key=lambda p: p.get('confidence', 0), reverse=True):
            is_duplicate = False
            for existing in unique_preds:
                # Calculate IoU (Intersection over Union)
                iou = self.calculate_iou(pred, existing)
                if iou > 0.5:  # 50% overlap = duplicate
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_preds.append(pred)
        
        return unique_preds
    
    def calculate_iou(self, box1, box2):
        """Calculate Intersection over Union"""
        x1_min = box1.get('x', 0) - box1.get('width', 0) / 2
        y1_min = box1.get('y', 0) - box1.get('height', 0) / 2
        x1_max = box1.get('x', 0) + box1.get('width', 0) / 2
        y1_max = box1.get('y', 0) + box1.get('height', 0) / 2
        
        x2_min = box2.get('x', 0) - box2.get('width', 0) / 2
        y2_min = box2.get('y', 0) - box2.get('height', 0) / 2
        x2_max = box2.get('x', 0) + box2.get('width', 0) / 2
        y2_max = box2.get('y', 0) + box2.get('height', 0) / 2
        
        # Calculate intersection
        inter_xmin = max(x1_min, x2_min)
        inter_ymin = max(y1_min, y2_min)
        inter_xmax = min(x1_max, x2_max)
        inter_ymax = min(y1_max, y2_max)
        
        if inter_xmax < inter_xmin or inter_ymax < inter_ymin:
            return 0.0
        
        inter_area = (inter_xmax - inter_xmin) * (inter_ymax - inter_ymin)
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
    
    def _attempt_inference(self, image_path):
        """Attempt inference with automatic retry and scaling"""
        try:
            # Resize for API
            resized_path, scale = self.resize_for_api(image_path)
            
            # Run inference
            result = self.client.infer(
                resized_path,
                model_id=self.model_id
            )
            
            # Extract predictions from result
            predictions = result.get('predictions', [])
            
            # Scale predictions back to original image size
            for pred in predictions:
                if scale < 1.0:  # If image was resized
                    pred['x'] = pred.get('x', 0) / scale
                    pred['y'] = pred.get('y', 0) / scale
                    pred['width'] = pred.get('width', 0) / scale
                    pred['height'] = pred.get('height', 0) / scale
            
            # Clean up temp file
            if os.path.exists(resized_path):
                try:
                    os.remove(resized_path)
                except:
                    pass
            
            return {
                'success': True,
                'predictions': predictions,
                'raw_result': result
            }
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'predictions': []
            }
    
    def draw_predictions(self, image_path, predictions, output_path):
        """Draw predictions on image and save"""
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Cannot read image: {image_path}")
        
        # Sort predictions by x coordinate
        predictions = sorted(predictions, key=lambda x: x.get("x", 0))
        
        tinted_count = 0
        clear_count = 0
        
        for pred in predictions:
            x, y = int(pred.get("x", 0)), int(pred.get("y", 0))
            w, h = int(pred.get("width", 0)), int(pred.get("height", 0))
            cls = pred.get("class", "unknown").lower()  # Convert to lowercase for consistency
            conf = pred.get("confidence", 0)
            
            # Calculate bounding box
            x1 = int(x - w / 2)
            y1 = int(y - h / 2)
            x2 = int(x + w / 2)
            y2 = int(y + h / 2)
            
            # Color based on class
            color = self.colors.get(cls, (0, 255, 0))
            
            # Count windows - only count valid tinted/clear classifications
            if cls == "tinted":
                tinted_count += 1
            elif cls == "clear":
                clear_count += 1
            # If it's neither tinted nor clear, don't count it
            
            # Draw bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
            
            # Prepare label
            label = f"{cls} {int(conf * 100)}%"
            
            # Get text size for background
            (tw, th), _ = cv2.getTextSize(
                label,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7, 2
            )
            
            # Draw label background
            cv2.rectangle(
                img,
                (x1, y1 - th - 10),
                (x1 + tw + 8, y1),
                color, -1
            )
            
            # Draw label text
            cv2.putText(
                img,
                label,
                (x1 + 4, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2
            )
        
        # Save output
        cv2.imwrite(output_path, img)
        
        # Return accurate counts
        return {
            'output_path': output_path,
            'tinted_count': tinted_count,
            'clear_count': clear_count,
            'total_count': tinted_count + clear_count  # Only count tinted + clear, not other objects
        }
    
    def extract_video_frames(self, video_path, output_dir, frame_skip=10):
        """Extract frames from video for processing"""
        cap = cv2.VideoCapture(video_path)
        frame_count = 0
        extracted_frames = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_skip == 0:
                frame_path = os.path.join(output_dir, f"frame_{frame_count:06d}.jpg")
                cv2.imwrite(frame_path, frame)
                extracted_frames.append({
                    'frame_number': frame_count,
                    'path': frame_path
                })
            
            frame_count += 1
        
        cap.release()
        return extracted_frames
    
    def calculate_statistics(self, predictions_list):
        """Calculate statistics from predictions"""
        if not predictions_list:
            return {
                'avg_confidence': 0,
                'total_detections': 0,
                'tinted_count': 0,
                'clear_count': 0
            }
        
        all_predictions = []
        tinted_count = 0
        clear_count = 0
        
        for predictions in predictions_list:
            for pred in predictions:
                all_predictions.append(pred)
                cls = pred.get('class', '').lower()  # Case-insensitive comparison
                if cls == 'tinted':
                    tinted_count += 1
                elif cls == 'clear':
                    clear_count += 1
                # If it's neither tinted nor clear, don't count it
        
        avg_confidence = np.mean([p.get('confidence', 0) for p in all_predictions]) if all_predictions else 0
        
        return {
            'avg_confidence': float(avg_confidence),
            'total_detections': tinted_count + clear_count,  # Only count valid windows
            'tinted_count': tinted_count,
            'clear_count': clear_count
        }
