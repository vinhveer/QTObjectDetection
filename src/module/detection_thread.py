from PySide6.QtCore import QThread, Signal
import cv2
import time
import os
import tempfile
import shutil
from datetime import datetime
import numpy as np

from module.model import model_instance

class DetectionThread(QThread):
    frame_signal = Signal(dict) 
    error_signal = Signal(str)
    detection_signal = Signal(list)
    static_detection_complete_signal = Signal(dict) 
    
    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.detecting = False
        self.processing_static_image = False
        
        # Temporary storage
        self.temp_dir = tempfile.mkdtemp()
        self.temp_images = []
        self.temp_detections = []
        
        # Frame storage
        self.current_frame = None
        self.current_detected_frame = None
        self.current_warmup_frame = None
        self.current_detections = None
        
        # Processing settings
        self.frame_count = 0
        self.frame_skip = 1
        
        # Static image processing
        self.static_image_path = None
        self.static_image_results = None
        
        # Performance optimization
        self.color_cache = {}

    def run(self):
        self.running = True
        
        # Handle static image processing
        if self.processing_static_image and self.static_image_path:
            self.process_static_image()
            self.processing_static_image = False
            return
            
        # Regular camera processing
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            self.error_signal.emit(f"Cannot open camera {self.camera_index}")
            self.running = False
            return

        while self.running:
            ret, frame = cap.read()
            if not ret:
                self.error_signal.emit("Error reading frame from camera")
                break
                
            # Increase frame counter
            self.frame_count += 1
            
            # Convert from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.current_frame = frame.copy()
            
            # Create copies for different processing
            binding_box_frame = frame.copy()
            warmup_frame = frame.copy()
            
            # Process detection on selected frames
            if self.frame_count % self.frame_skip == 0 and self.detecting and model_instance.model is not None:
                try:
                    # Perform detection
                    detections = model_instance.detect(frame)
                    if detections:
                        # Draw binding box
                        binding_box_frame, self.current_detections = self.draw_detections(
                            binding_box_frame, 
                            detections
                        )
                        # Process warm up visualization
                        warmup_frame = self.process_warmup(
                            warmup_frame, 
                            detections
                        )
                        
                        self.current_detected_frame = binding_box_frame.copy()
                        self.current_warmup_frame = warmup_frame.copy()
                        self.detection_signal.emit(detections)
                        
                        # Save frame and detection to temp storage
                        self.save_temp_frame(frame, detections, binding_box_frame, warmup_frame)
                        
                except Exception as e:
                    print(f"Detection error: {str(e)}")
            
            # Send frames to UI
            self.frame_signal.emit({
                'binding_box': binding_box_frame,
                'warm_up': warmup_frame
            })
                
            time.sleep(1/30)  # Limit to 30fps

        cap.release()

    def detect_static_image(self, image_path):
        """Process a static image for detection"""
        if not os.path.exists(image_path):
            self.error_signal.emit(f"Image file not found: {image_path}")
            return False
            
        self.static_image_path = image_path
        self.processing_static_image = True
        self.start()
        return True
        
    def process_static_image(self):
        """Process the static image specified by static_image_path"""
        try:
            # Read image
            frame = cv2.imread(self.static_image_path)
            if frame is None:
                self.error_signal.emit(f"Could not read image: {self.static_image_path}")
                return
                
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create copies for processing
            binding_box_frame = frame.copy()
            warmup_frame = frame.copy()
            
            # Perform detection if model is loaded
            if model_instance.model is not None:
                detections = model_instance.detect(frame)
                
                if detections:
                    # Draw binding boxes
                    binding_box_frame, detections_data = self.draw_detections(
                        binding_box_frame,
                        detections
                    )
                    
                    # Process warm up visualization
                    warmup_frame = self.process_warmup(
                        warmup_frame,
                        detections
                    )
                    
                    # Save results to temp storage
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    
                    # Save the processed images to temp directory
                    temp_original_path = os.path.join(self.temp_dir, f"static_original_{timestamp}.jpg")
                    temp_binding_box_path = os.path.join(self.temp_dir, f"static_binding_box_{timestamp}.jpg")
                    temp_warmup_path = os.path.join(self.temp_dir, f"static_warmup_{timestamp}.jpg")
                    
                    cv2.imwrite(temp_original_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
                    cv2.imwrite(temp_binding_box_path, cv2.cvtColor(binding_box_frame, cv2.COLOR_RGB2BGR))
                    cv2.imwrite(temp_warmup_path, cv2.cvtColor(warmup_frame, cv2.COLOR_RGB2BGR))
                    
                    # Store results
                    self.static_image_results = {
                        'timestamp': timestamp,
                        'original_path': temp_original_path,
                        'binding_box_path': temp_binding_box_path,
                        'warmup_path': temp_warmup_path,
                        'detections': detections,
                        'original_frame': frame,
                        'binding_box_frame': binding_box_frame,
                        'warmup_frame': warmup_frame
                    }
                    
                    # Emit the results
                    self.static_detection_complete_signal.emit(self.static_image_results)
                else:
                    self.error_signal.emit("No objects detected in the image")
            else:
                self.error_signal.emit("Model not loaded. Please load a model first.")
                
        except Exception as e:
            self.error_signal.emit(f"Error processing static image: {str(e)}")

    def save_temp_frame(self, original_frame, detections, binding_box_frame, warmup_frame):
        """Save frame and detection to temporary memory"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Save frames to temp directory
        temp_original_path = os.path.join(self.temp_dir, f"frame_original_{timestamp}.jpg")
        temp_binding_box_path = os.path.join(self.temp_dir, f"frame_binding_box_{timestamp}.jpg")
        temp_warmup_path = os.path.join(self.temp_dir, f"frame_warmup_{timestamp}.jpg")
        
        # Save frames
        cv2.imwrite(temp_original_path, cv2.cvtColor(original_frame, cv2.COLOR_RGB2BGR))
        cv2.imwrite(temp_binding_box_path, cv2.cvtColor(binding_box_frame, cv2.COLOR_RGB2BGR))
        cv2.imwrite(temp_warmup_path, cv2.cvtColor(warmup_frame, cv2.COLOR_RGB2BGR))
        
        # Save information
        frame_info = {
            'timestamp': timestamp,
            'original_path': temp_original_path,
            'binding_box_path': temp_binding_box_path,
            'warmup_path': temp_warmup_path,
            'detections': detections
        }
        
        self.temp_images.append(frame_info)
        self.temp_detections.append(detections)

    def get_color_for_class(self, class_id):
        """Create random but consistent color for each class"""
        # Use cache to optimize performance
        if class_id in self.color_cache:
            return self.color_cache[class_id]
        
        # Create a unique numeric value from string for seed
        hash_value = 0
        for char in str(class_id):
            hash_value = hash_value * 31 + ord(char)
        
        # Use hash as seed to create stable color
        np.random.seed(hash_value % (2**32 - 1))
        color = tuple(map(int, np.random.randint(0, 255, 3)))
        
        # Save to cache
        self.color_cache[class_id] = color
        return color
        
    def draw_detections(self, frame, detections):
        """Draw detection results on frame"""
        # Try to use model's built-in plot method
        try:
            if model_instance.last_results is not None:
                result_frame = model_instance.plot_detection(
                    frame,
                    conf=0.5,
                    line_width=2,
                    font_size=0.5,
                    labels=True
                )
                return result_frame, detections
        except Exception as e:
            print(f"Error using YOLO's built-in plot: {e}")
        
        # Fallback: Use manual drawing method
        frame_copy = frame.copy()
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            confidence = det['confidence']
            class_id = det.get('class', 'Unknown')
            
            # Get color for class
            color = self.get_color_for_class(str(class_id))
            
            # Draw bounding box
            cv2.rectangle(frame_copy, (x1, y1), (x2, y2), color, 2)
            
            # Prepare text
            label = f"{class_id} ({confidence:.2f})"
            
            # Draw background for text
            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame_copy, 
                        (x1, y1 - text_height - 10), 
                        (x1 + text_width + 10, y1),
                        color, -1)
            
            # Draw text
            cv2.putText(frame_copy, label,
                    (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (255, 255, 255), 2)
                
        return frame_copy, detections

    def process_warmup(self, frame, detections):
        """Process warm up frame for visualization"""
        if frame is None or not detections:
            return frame
        
        # Try to use built-in visualization if available
        try:
            if model_instance.model is not None and hasattr(model_instance, 'last_results'):
                results = model_instance.last_results[0]
                
                if hasattr(results, 'plot_heat'):
                    return results.plot_heat()
                elif hasattr(results, 'plot_thermal'):
                    return results.plot_thermal()
        except Exception as e:
            print(f"Error using thermal visualization: {str(e)}")
        
        # Fallback to manual thermal processing
        processed_frame = frame.copy()
        
        # Convert image to grayscale for processing
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply blur filter to reduce noise
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Create thermal background image (cool tone)
        heat_map = cv2.applyColorMap(gray, cv2.COLORMAP_OCEAN)
        
        # Create mask for detection area
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        
        # Process each detection area
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            
            # Add detection area to mask
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            
            # Create "hot" effect for detection area
            if y2 > y1 and x2 > x1:
                roi = gray[y1:y2, x1:x2]
                if roi.size > 0:
                    # Apply heat colormap to detection area
                    roi_heat = cv2.applyColorMap(roi, cv2.COLORMAP_JET)
                    
                    # Enhance brightness and contrast
                    roi_enhanced = cv2.convertScaleAbs(roi_heat, alpha=1.3, beta=30)
                    
                    # Apply to original frame
                    processed_frame[y1:y2, x1:x2] = roi_enhanced
        
        # Expand mask to create soft transition effect
        kernel = np.ones((5, 5), np.uint8)
        mask_dilated = cv2.dilate(mask, kernel, iterations=3)
        mask_blur = cv2.GaussianBlur(mask_dilated, (21, 21), 0)
        
        # Create gradient mask and ensure correct data type
        gradient_mask = mask_blur.astype(np.float32) / 255.0
        
        # Expand to 3 channels
        gradient_mask_3d = np.stack([gradient_mask] * 3, axis=2)
        
        # Combine images
        blended = (processed_frame.astype(np.float32) * gradient_mask_3d + 
                heat_map.astype(np.float32) * (1.0 - gradient_mask_3d))
        
        # Convert to uint8
        result = np.clip(blended, 0, 255).astype(np.uint8)
        
        # Add borders for detection areas
        for det in detections:
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)
            confidence = det.get('confidence', 0)
            class_name = det.get('class', 'Unknown')
            
            # Border color based on object class
            color = self.get_color_for_class(str(class_name))
            
            # Draw outer border with glow effect
            cv2.rectangle(result, (x1-1, y1-1), (x2+1, y2+1), (255, 255, 255), 3)
            cv2.rectangle(result, (x1, y1), (x2, y2), color, 2)
            
            # Add class and confidence information
            label = f"{class_name}: {confidence:.2f}" if confidence else class_name
            t_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)[0]
            c2 = x1 + t_size[0] + 3, y1 + t_size[1] + 4
            
            # Background for text
            cv2.rectangle(result, (x1, y1), c2, color, -1)
            # Text
            cv2.putText(result, label, (x1, y1 + t_size[1] + 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        return result

    # Public API methods
    def get_current_frames(self):
        """Return current frames"""
        return {
            'original': self.current_frame,
            'binding_box': self.current_detected_frame,
            'warm_up': self.current_warmup_frame,
            'detections': self.current_detections
        }
    
    def get_status(self):
        """Return current thread status"""
        return {
            'running': self.running,
            'detecting': self.detecting,
            'processing_static_image': self.processing_static_image,
            'frame_count': self.frame_count,
            'frame_skip': self.frame_skip,
            'has_current_frame': self.current_frame is not None,
            'has_detections': self.current_detections is not None,
            'has_static_image_results': self.static_image_results is not None
        }
    
    def get_temp_data(self):
        """Return temporary data"""
        return {
            'images': self.temp_images,
            'detections': self.temp_detections,
            'static_image_results': self.static_image_results
        }

    def clear_temp_data(self):
        """Clear all temporary data"""
        # Delete image files
        for frame_info in self.temp_images:
            try:
                os.remove(frame_info['original_path'])
                os.remove(frame_info['binding_box_path'])
                os.remove(frame_info['warmup_path'])
            except Exception as e:
                print(f"Error removing temp files: {str(e)}")
        
        # Clear static image results if exist
        if self.static_image_results:
            try:
                os.remove(self.static_image_results['original_path'])
                os.remove(self.static_image_results['binding_box_path'])
                os.remove(self.static_image_results['warmup_path'])
            except Exception as e:
                print(f"Error removing static image temp files: {str(e)}")
            
            self.static_image_results = None
        
        # Delete temp directory
        try:
            shutil.rmtree(self.temp_dir)
            # Create a new temp directory
            self.temp_dir = tempfile.mkdtemp()
        except Exception as e:
            print(f"Error removing temp directory: {str(e)}")
        
        # Reset lists
        self.temp_images = []
        self.temp_detections = []
        
    def __del__(self):
        """Clean up resources when object is destroyed"""
        self.clear_temp_data()
        
    def stop_capture(self):
        """Stop camera capture"""
        self.running = False
        self.detecting = False
        self.wait()
        
    def start_detection(self):
        """Start object detection"""
        self.detecting = True
        
    def stop_detection(self):
        """Stop object detection"""
        self.detecting = False