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
    
    def resize_for_api(self, path, max_w=1280):
        """Resize image to avoid 413 error"""
        img = cv2.imread(path)
        if img is None:
            raise ValueError(f"Cannot read image: {path}")
        
        h, w, _ = img.shape
        scale = 1.0
        
        if w > max_w:
            scale = max_w / w
            new_w = int(w * scale)
            new_h = int(h * scale)
            img = cv2.resize(img, (new_w, new_h))
        
        temp_path = os.path.join(tempfile.gettempdir(), "temp_upload.jpg")
        cv2.imwrite(temp_path, img)
        
        return temp_path, scale
    
    def run_inference(self, image_path):
        """Run inference on image and return predictions"""
        start_time = time.time()
        
        try:
            # Validate image file exists
            if not os.path.exists(image_path):
                raise ValueError(f"Image file not found: {image_path}")
            
            # Resize for API
            resized_path, scale = self.resize_for_api(image_path)
            
            # Run inference
            result = self.client.infer(
                resized_path,
                model_id=self.model_id
            )
            
            processing_time = time.time() - start_time
            
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
                os.remove(resized_path)
            
            return {
                'success': True,
                'predictions': predictions,
                'processing_time': processing_time,
                'raw_result': result
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
            cls = pred.get("class", "unknown")
            conf = pred.get("confidence", 0)
            
            # Calculate bounding box
            x1 = int(x - w / 2)
            y1 = int(y - h / 2)
            x2 = int(x + w / 2)
            y2 = int(y + h / 2)
            
            # Color based on class
            color = self.colors.get(cls, (0, 255, 0))
            
            # Count windows
            if cls == "tinted":
                tinted_count += 1
            else:
                clear_count += 1
            
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
        
        return {
            'output_path': output_path,
            'tinted_count': tinted_count,
            'clear_count': clear_count,
            'total_count': len(predictions)
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
                if pred.get('class') == 'tinted':
                    tinted_count += 1
                else:
                    clear_count += 1
        
        avg_confidence = np.mean([p.get('confidence', 0) for p in all_predictions]) if all_predictions else 0
        
        return {
            'avg_confidence': float(avg_confidence),
            'total_detections': len(all_predictions),
            'tinted_count': tinted_count,
            'clear_count': clear_count
        }
