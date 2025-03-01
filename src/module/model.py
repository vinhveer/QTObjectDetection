from PySide6.QtCore import QObject
from PySide6.QtWidgets import QMessageBox
from ultralytics import YOLO

class YOLOModel(QObject):
    def __init__(self):
        super().__init__()
        self.model = None
        self.last_results = None  # Thêm biến để lưu kết quả nguyên bản
        self.class_names = {}  # Thêm biến để lưu tên các lớp
        
    def load_model(self, model_path):
        try:
            self.model = YOLO(model_path)
            # Lưu tên các lớp nếu có
            if hasattr(self.model, 'names'):
                self.class_names = self.model.names
            return True
        except Exception as e:
            QMessageBox.critical(
                None,
                "Lỗi tải Model",
                f"Không thể tải model: {str(e)}\nVui lòng kiểm tra đường dẫn và thử lại."
            )
            return False
        
    def detect(self, image):
        if self.model is None:
            return None
            
        try:
            # Thực hiện inference
            results = self.model(image, verbose=False)
            
            # Lưu kết quả nguyên bản để sử dụng trong các phương thức vẽ
            self.last_results = results
            
            # Lấy kết quả detection
            detections = []
            
            # Check if we have any results
            if results and len(results) > 0:
                for result in results[0].boxes.data:
                    # Convert tensor to list if needed
                    result_data = result.cpu().numpy() if hasattr(result, 'cpu') else result
                    
                    # Extract detection data
                    x1, y1, x2, y2, conf, cls = result_data
                    class_id = int(cls)
                    
                    # Lấy tên lớp nếu có
                    class_name = self.class_names.get(class_id, str(class_id)) if self.class_names else str(class_id)
                    
                    detections.append({
                        'bbox': (int(x1), int(y1), int(x2), int(y2)),
                        'confidence': float(conf),
                        'class': class_name,
                        'class_id': class_id
                    })
                
            return detections
        except Exception as e:
            QMessageBox.critical(
                None,
                "Lỗi nhận diện",
                f"Đã xảy ra lỗi trong quá trình nhận diện: {str(e)}\nVui lòng thử lại."
            )
            return None
    
    def get_original_results(self):
        """Trả về kết quả nguyên bản từ model"""
        return self.last_results
    
    def plot_detection(self, image, conf=0.5, line_width=2, font_size=0.5, labels=True):
        """Sử dụng phương thức plot có sẵn của Ultralytics để vẽ"""
        if self.last_results is None or len(self.last_results) == 0:
            return image.copy()
        
        try:
            # Sử dụng phương thức plot có sẵn
            result_image = self.last_results[0].plot(
                conf=conf,
                line_width=line_width,
                font_size=font_size,
                labels=labels
            )
            return result_image
        except Exception as e:
            QMessageBox.critical(
                None,
                "Lỗi hiển thị",
                f"Đã xảy ra lỗi khi vẽ kết quả nhận diện: {str(e)}\nVui lòng thử lại."
            )
            return image.copy()

# Singleton instance
model_instance = YOLOModel()