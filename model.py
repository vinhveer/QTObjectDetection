from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2
from ultralytics import YOLO

class YOLOModel:
    def __init__(self):
        self.model = None
        
    def load_model(self, model_path):
        try:
            self.model = YOLO(model_path)
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
            
    def detect(self, image):
        if self.model is None:
            return None
            
        try:
            # Thực hiện inference
            results = self.model(image, verbose=False)
            
            # Lấy kết quả detection
            detections = []
            for result in results[0].boxes.data:
                x1, y1, x2, y2, conf, cls = result
                detections.append({
                    'bbox': (int(x1), int(y1), int(x2), int(y2)),
                    'confidence': float(conf),
                    'class': int(cls)
                })
                
            return detections
        except Exception as e:
            print(f"Error during detection: {e}")
            return None

# Singleton instance
model_instance = YOLOModel()