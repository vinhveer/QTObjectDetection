from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2

class CameraDetector:
    def __init__(self, ui):
        self.ui = ui
        self.thread = None
        self.setup_ui_connections()
        self.setup_camera_list()

    def setup_ui_connections(self):
        # Kết nối trực tiếp với các button trong tab Camera
        self.ui.buttonStartRecord.clicked.connect(self.toggle_camera)
        self.ui.buttonStartDetect.clicked.connect(self.start_detection)
        self.ui.buttonStopDetect.clicked.connect(self.stop_detection)
        
    def setup_camera_list(self):
        # Quét và thêm camera vào combobox
        for i in range(5):
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                self.ui.comboBoxChooseCamera.addItem(f"Camera {i}")
                cap.release()
    
    def set_model(self, model_path):
        # Khởi tạo YOLO model
        pass
        
    def toggle_camera(self):
        if not self.thread or not self.thread.running:
            # Start camera
            camera_index = self.ui.comboBoxChooseCamera.currentIndex()
            self.thread = CameraThread(camera_index)
            self.thread.frame_signal.connect(self.update_camera_feed)
            self.thread.detection_signal.connect(self.update_detections)
            self.thread.start()
            self.ui.buttonStartRecord.setText("Dừng nhận hình ảnh")
        else:
            # Stop camera
            self.thread.stop_capture()
            self.thread = None
            self.ui.buttonStartRecord.setText("Bắt đầu nhận hình ảnh")
            
    def start_detection(self):
        if self.thread:
            self.thread.start_detection()
            self.ui.buttonStartDetect.setEnabled(False)
            self.ui.buttonStopDetect.setEnabled(True)
            
    def stop_detection(self):
        if self.thread:
            self.thread.stop_detection()
            self.ui.buttonStartDetect.setEnabled(True)
            self.ui.buttonStopDetect.setEnabled(False)
            
    def update_camera_feed(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.ui.frameCamera.setPixmap(pixmap.scaled(
            self.ui.frameCamera.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        ))
        
    def update_detections(self, detections):
        # Update bảng kết quả detection
        pass

class CameraThread(QThread):
    frame_signal = pyqtSignal(object)
    detection_signal = pyqtSignal(list)
    
    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.detecting = False
        
    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        
        while self.running:
            ret, frame = cap.read()
            if ret:
                if self.detecting:
                    # Thực hiện detection
                    # detected_objects = model.detect(frame)
                    # self.detection_signal.emit(detected_objects)
                    pass
                self.frame_signal.emit(frame)
                
        cap.release()
        
    def stop_capture(self):
        self.running = False
        self.wait()
        
    def start_detection(self):
        self.detecting = True
        
    def stop_detection(self):
        self.detecting = False