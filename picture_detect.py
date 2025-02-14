from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2

class PictureDetector:
    def __init__(self, ui):
        self.ui = ui
        self.model = None
        self.current_image = None
        self.setup_ui_connections()
        
    def setup_ui_connections(self):
        # Kết nối trực tiếp với các button trong tab Picture
        self.ui.buttonChoosePicture.clicked.connect(self.select_picture)
        self.ui.buttonDownloadPicture.clicked.connect(self.save_detected_picture)
        
    def set_model(self, model_path):
        # Khởi tạo YOLO model
        pass
        
    def select_picture(self):
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Select Image",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        if file_path:
            image = cv2.imread(file_path)
            if image is not None:
                self.current_image = image
                self.process_image()
                
    def process_image(self):
        if self.current_image is not None:
            # Thực hiện detection
            # detected_objects = self.model.detect(self.current_image)
            self.update_display(self.current_image)
            # self.update_detections(detected_objects)
            
    def update_display(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.ui.framePicture.setPixmap(pixmap.scaled(
            self.ui.framePicture.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        ))
        
    def update_detections(self, detections):
        # Update bảng kết quả detection
        pass
        
    def save_detected_picture(self):
        if self.current_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(
                None,
                "Save Detected Image",
                "",
                "Image Files (*.png *.jpg *.jpeg)"
            )
            if file_path:
                cv2.imwrite(file_path, self.current_image)
