from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2, time, sys, os, tempfile
import numpy as np
from model import model_instance

if sys.platform.startswith("win"):
    from pygrabber.dshow_graph import FilterGraph

class CameraDetector(QObject):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.thread = None
        self.current_frame = None
        self.setup_ui()
        self.setup_ui_connections()
        self.setup_camera_list()
        
    def setup_ui(self):
        """Thiết lập UI ban đầu"""
        # Thêm QTextEdit để hiển thị thông tin chi tiết
        self.text_edit_camera_info = QTextEdit(self.ui.tabCamera)
        self.text_edit_camera_info.setGeometry(QRect(500, 60, 231, 251))
        self.text_edit_camera_info.setReadOnly(True)
        
        # Tùy chỉnh frame hiển thị ảnh
        self.ui.frameCamera.setScaledContents(False)
        self.ui.frameCamera.setAlignment(Qt.AlignCenter)
        
        # Thiết lập trạng thái ban đầu
        self.ui.buttonStopDetect.setEnabled(False)
        self.ui.buttonStartDetect.setEnabled(False)
        
    def setup_ui_connections(self):
        """Thiết lập các kết nối signals/slots"""
        self.ui.buttonStartRecord.clicked.connect(self.toggle_camera)
        self.ui.buttonStartDetect.clicked.connect(self.start_detection)
        self.ui.buttonStopDetect.clicked.connect(self.stop_detection)
        self.ui.buttonCapture.clicked.connect(self.capture_frame)
        
    def setup_camera_list(self):
        """Quét và hiển thị danh sách camera có sẵn"""
        self.ui.comboBoxChooseCamera.clear()
        camera_found = False  # Cờ kiểm tra có camera hay không

        if sys.platform.startswith("win"):
            # Windows: Lấy danh sách camera bằng pygrabber
            graph = FilterGraph()
            devices = graph.get_input_devices()

            for i, device_name in enumerate(devices):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self.ui.comboBoxChooseCamera.addItem(device_name)  # Hiển thị tên thiết bị
                    cap.release()
                    camera_found = True

        else:
            # MacOS: OpenCV không hỗ trợ lấy tên, chỉ kiểm tra camera hoạt động
            for i in range(10):  # Quét tối đa 10 camera
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self.ui.comboBoxChooseCamera.addItem("Camera")  # Không có tên cụ thể
                    cap.release()
                    camera_found = True

        # Nếu không tìm thấy camera nào
        if not camera_found:
            self.ui.comboBoxChooseCamera.addItem("Không tìm thấy camera")
            self.ui.buttonStartRecord.setEnabled(False)
        else:
            self.ui.buttonStartRecord.setEnabled(True)  # Kích hoạt nút nếu có camera
            
    def toggle_camera(self):
        """Bắt đầu/dừng camera"""
        if not self.thread or not self.thread.running:
            camera_index = self.ui.comboBoxChooseCamera.currentIndex()
            if camera_index < 0:
                QMessageBox.warning(None, "Lỗi", "Không có camera nào được chọn!")
                return
                
            self.thread = CameraThread(camera_index)
            self.thread.frame_signal.connect(self.update_camera_feed)
            self.thread.error_signal.connect(self.handle_camera_error)
            self.thread.detection_signal.connect(self.update_detections_info)
            self.thread.start()
            
            self.ui.buttonStartRecord.setText("Dừng nhận hình ảnh")
            self.ui.buttonStartDetect.setEnabled(True)
            self.ui.comboBoxChooseCamera.setEnabled(False)
        else:
            self.stop_detection()
            self.thread.stop_capture()
            self.thread = None
            self.ui.frameCamera.clear()
            self.ui.buttonStartRecord.setText("Bắt đầu nhận hình ảnh")
            self.ui.buttonStartDetect.setEnabled(False)
            self.ui.comboBoxChooseCamera.setEnabled(True)
            
    def start_detection(self):
        """Bắt đầu nhận diện đối tượng"""
        if self.thread and model_instance.model is not None:
            self.thread.start_detection()
            self.ui.buttonStartDetect.setEnabled(False)
            self.ui.buttonStopDetect.setEnabled(True)
            self.text_edit_camera_info.clear()  # Xóa thông tin detection cũ
        else:
            QMessageBox.warning(None, "Lỗi", "Vui lòng tải Model trước!")
            
    def stop_detection(self):
        """Dừng nhận diện đối tượng"""
        if self.thread:
            self.thread.stop_detection()
            self.ui.buttonStartDetect.setEnabled(True)
            self.ui.buttonStopDetect.setEnabled(False)
            
    def update_camera_feed(self, frame):
        """Cập nhật frame camera"""
        self.current_frame = frame  # Lưu frame hiện tại
        
        # Lấy kích thước của QLabel
        label_width = self.ui.frameCamera.width()
        label_height = self.ui.frameCamera.height()
        
        # Chuyển frame sang QImage
        height, width, channel = frame.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # Tạo pixmap và scale với tỷ lệ giữ nguyên
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            label_width,
            label_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Hiển thị ảnh đã scale
        self.ui.frameCamera.setPixmap(scaled_pixmap)
    
    def handle_camera_error(self, error_msg):
        """Xử lý lỗi camera"""
        QMessageBox.warning(None, "Lỗi Camera", error_msg)
        self.toggle_camera()  # Dừng camera khi có lỗi
        
    def update_detections_info(self, detections):
        """Cập nhật thông tin detection"""
        self.text_edit_camera_info.clear()
        
        # Thêm thông tin tổng quan
        total_objects = len(detections)
        class_counts = {}
        
        for det in detections:
            class_id = det['class']
            class_counts[class_id] = class_counts.get(class_id, 0) + 1
        
        # Hiển thị tổng quan
        self.text_edit_camera_info.append("=== TỔNG QUAN ===")
        self.text_edit_camera_info.append(f"Tổng số đối tượng: {total_objects}")
        self.text_edit_camera_info.append("\nPhân bố các lớp:")
        for class_id, count in class_counts.items():
            self.text_edit_camera_info.append(f"- Class {class_id}: {count} đối tượng")
        
        # Hiển thị chi tiết từng đối tượng
        self.text_edit_camera_info.append("\n=== CHI TIẾT ===")
        for i, det in enumerate(detections, 1):
            info = (f"\nĐối tượng {i}:"
                   f"\n- Lớp: {det['class']}"
                   f"\n- Độ tin cậy: {det['confidence']:.2f}"
                   f"\n- Vị trí: {det['bbox']}")
            self.text_edit_camera_info.append(info)
            
    def capture_frame(self):
        """Chụp ảnh, lưu tạm rồi yêu cầu lưu vào vị trí người dùng chọn"""
        if self.current_frame is None:
            return

        # Lưu ảnh tạm vào thư mục hệ thống
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, "temp_capture.png")
        cv2.imwrite(temp_path, cv2.cvtColor(self.current_frame, cv2.COLOR_RGB2BGR))

        # Hiển thị hộp thoại lưu file
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Lưu ảnh",
            "",
            "Images (*.png *.jpg)"
        )

        if file_path:  # Nếu chọn lưu, di chuyển file tạm sang vị trí đã chọn
            os.replace(temp_path, file_path)
            QMessageBox.information(None, "Thành công", "Đã lưu ảnh thành công!")
        else:  # Nếu hủy, xóa ảnh tạm
            os.remove(temp_path)

    @staticmethod
    def get_color_for_class(class_id):
        """Tạo màu ngẫu nhiên nhưng ổn định cho mỗi class"""
        np.random.seed(class_id)
        return tuple(map(int, np.random.randint(0, 255, 3)))
        
class CameraThread(QThread):
    frame_signal = pyqtSignal(object)
    error_signal = pyqtSignal(str)
    detection_signal = pyqtSignal(list)
    
    def __init__(self, camera_index):
        super().__init__()
        self.camera_index = camera_index
        self.running = False
        self.detecting = False
        
    def run(self):
        self.running = True
        cap = cv2.VideoCapture(self.camera_index)
        
        if not cap.isOpened():
            self.error_signal.emit(f"Không thể mở camera {self.camera_index}")
            self.running = False
            return

        while self.running:
            ret, frame = cap.read()
            if ret:
                # Chuyển từ BGR sang RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                if self.detecting and model_instance.model is not None:
                    try:
                        # Thực hiện detection
                        detections = model_instance.detect(frame)
                        if detections:
                            frame = self.draw_detections(frame.copy(), detections)
                            self.detection_signal.emit(detections)
                    except Exception as e:
                        print(f"Detection error: {str(e)}")
                
                # Gửi frame đến UI
                self.frame_signal.emit(frame)
            else:
                self.error_signal.emit("Lỗi khi đọc frame từ camera")
                break
                
            time.sleep(1/30)  # Giới hạn fps

        cap.release()
       
    def stop_capture(self):
        self.running = False
        self.detecting = False
        self.wait()
        
    def start_detection(self):
        self.detecting = True
        
    def stop_detection(self):
        self.detecting = False
        
    def draw_detections(self, frame, detections):
        """Vẽ kết quả detection lên frame"""
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            class_id = det['class']
            
            # Màu cho mỗi class
            color = self.get_color_for_class(class_id)
            
            # Vẽ bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Tính toán vị trí và kích thước text
            label = f"Class {class_id}"
            conf_text = f"{confidence:.2f}"
            
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 2
            
            # Tính kích thước của label và confidence
            (label_width, label_height), _ = cv2.getTextSize(
                label, font, font_scale, font_thickness)
            (conf_width, conf_height), _ = cv2.getTextSize(
                conf_text, font, font_scale, font_thickness)
            
            # Lấy kích thước lớn nhất
            max_width = max(label_width, conf_width)
            total_height = label_height + conf_height + 5  # 5px spacing
            
            # Vẽ background đen mờ
            alpha = 0.6
            overlay = frame.copy()
            cv2.rectangle(
                overlay,
                (x1, y1 - total_height - 10),  # 10px padding
                (x1 + max_width + 10, y1),      # 10px padding
                (0, 0, 0),
                -1
            )
            # Áp dụng độ mờ
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            
            # Vẽ label
            cv2.putText(
                frame,
                label,
                (x1 + 5, y1 - total_height + label_height),  # 5px padding
                font,
                font_scale,
                color,
                font_thickness
            )
            
            # Vẽ confidence
            cv2.putText(
                frame,
                conf_text,
                (x1 + 5, y1 - 5),  # 5px padding from bottom
                font,
                font_scale,
                color,
                font_thickness
            )
            
        return frame
        
    @staticmethod
    def get_color_for_class(class_id):
        """Tạo màu ngẫu nhiên nhưng ổn định cho mỗi class"""
        np.random.seed(class_id)
        return tuple(map(int, np.random.randint(0, 255, 3)))