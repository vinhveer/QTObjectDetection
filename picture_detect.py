from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2
import numpy as np
from model import model_instance

class PictureDetector(QObject):
    detection_finished = pyqtSignal()
    
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.current_image = None
        self.processed_image = None
        self.detection_thread = None
        self.setup_ui()
        self.setup_ui_connections()
        
    def setup_ui(self):
        """Thiết lập UI ban đầu"""
        # Thêm QTextEdit để hiển thị thông tin chi tiết
        self.text_edit_info = QTextEdit(self.ui.tabPicture)
        self.text_edit_info.setGeometry(QRect(500, 60, 231, 251))
        self.text_edit_info.setReadOnly(True)
        
        # Tùy chỉnh frame hiển thị ảnh
        self.ui.framePicture.setStyleSheet("border: 2px solid black;")
        self.ui.framePicture.setAlignment(Qt.AlignCenter)
        
        # Thêm progress bar
        self.progress_bar = QProgressBar(self.ui.tabPicture)
        self.progress_bar.setGeometry(QRect(110, 30, 441, 23))
        self.progress_bar.hide()
        
        # Thiết lập trạng thái ban đầu
        self.ui.buttonDownloadPicture.setEnabled(False)
        
    def setup_ui_connections(self):
        """Thiết lập các kết nối signals/slots"""
        self.ui.buttonChoosePicture.clicked.connect(self.select_picture)
        self.ui.buttonDownloadPicture.clicked.connect(self.save_detected_picture)
        self.detection_finished.connect(self.on_detection_complete)
        
    def select_picture(self):
        """Xử lý chọn ảnh từ file"""
        self.progress_bar.hide()
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Chọn hình ảnh",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                # Hiển thị progress bar
                self.progress_bar.setRange(0, 0)  # Chế độ không xác định
                self.progress_bar.show()
                
                image = cv2.imread(file_path)
                if image is None:
                    raise ValueError("Không thể đọc file ảnh")
                    
                self.current_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                self.process_image()
                
            except Exception as e:
                QMessageBox.warning(None, "Lỗi", f"Không thể tải hình ảnh: {str(e)}")
                self.reset_ui()
                
    def process_image(self):
        """Xử lý ảnh và thực hiện detection"""
        if self.current_image is None:
            return
            
        if model_instance.model is None:
            QMessageBox.warning(None, "Lỗi", "Chưa tải Model. Vui lòng tải Model trước!")
            self.reset_ui()
            return
            
        # Disable các nút trong quá trình xử lý
        self.ui.buttonChoosePicture.setEnabled(False)
        self.ui.buttonDownloadPicture.setEnabled(False)
        
        # Tạo và start detection thread
        self.detection_thread = DetectionThread(self.current_image)
        self.detection_thread.finished.connect(self.handle_detection_result)
        self.detection_thread.start()
        
    def handle_detection_result(self):
        """Xử lý kết quả detection từ thread"""
        if self.detection_thread.error:
            QMessageBox.warning(None, "Lỗi", f"Lỗi khi nhận diện: {self.detection_thread.error}")
            self.reset_ui()
            return
            
        self.processed_image = self.detection_thread.processed_image
        detections = self.detection_thread.detections
        
        if detections:
            self.draw_detections(detections)
            self.update_detections_info(detections)
            
        self.update_display(self.processed_image)
        self.ui.buttonDownloadPicture.setEnabled(True)
        self.detection_finished.emit()
        
        # Ẩn progress bar
        self.progress_bar.hide()
        
    def draw_detections(self, detections):
        """Vẽ kết quả detection lên ảnh"""
        if self.processed_image is None:
            return
            
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            class_id = det['class']
            
            # Màu cho mỗi class (đảm bảo màu không đổi cho cùng class)
            color = self.get_color_for_class(class_id)
            
            # Vẽ bounding box với độ dày 2px
            cv2.rectangle(self.processed_image, 
                        (x1, y1), (x2, y2), 
                        color, 2)
            
            # Tính toán vị trí và kích thước text
            label = f"Class {class_id}"
            conf_text = f"{confidence:.2f}"
            
            # Vẽ background cho label
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            font_thickness = 2
            
            # Tính kích thước của cả label và confidence
            (label_width, label_height), _ = cv2.getTextSize(
                label, font, font_scale, font_thickness)
            (conf_width, conf_height), _ = cv2.getTextSize(
                conf_text, font, font_scale, font_thickness)
            
            # Lấy kích thước lớn nhất
            max_width = max(label_width, conf_width)
            total_height = label_height + conf_height + 5  # 5px spacing
            
            # Vẽ background đen mờ
            alpha = 0.6
            overlay = self.processed_image.copy()
            cv2.rectangle(
                overlay,
                (x1, y1 - total_height - 10),  # 10px padding
                (x1 + max_width + 10, y1),      # 10px padding
                (0, 0, 0),
                -1
            )
            # Áp dụng độ mờ
            cv2.addWeighted(overlay, alpha, self.processed_image, 1 - alpha, 0, 
                        self.processed_image)
            
            # Vẽ label
            cv2.putText(
                self.processed_image,
                label,
                (x1 + 5, y1 - total_height + label_height),  # 5px padding
                font,
                font_scale,
                color,
                font_thickness
            )
            
            # Vẽ confidence
            cv2.putText(
                self.processed_image,
                conf_text,
                (x1 + 5, y1 - 5),  # 5px padding from bottom
                font,
                font_scale,
                color,
                font_thickness
            )
            
    def draw_label(self, image, label, position, color):
        """Vẽ label với background"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 2
        
        # Tính kích thước text
        (text_width, text_height), baseline = cv2.getTextSize(
            label, font, font_scale, thickness
        )
        
        # Vẽ background
        x, y = position
        cv2.rectangle(
            image,
            (x, y - text_height - baseline),
            (x + text_width, y),
            color,
            -1
        )
        
        # Vẽ text
        cv2.putText(
            image, 
            label,
            (x, y - baseline),
            font,
            font_scale,
            (255, 255, 255),
            thickness
        )
    
    @staticmethod
    def get_color_for_class(class_id):
        """Tạo màu ngẫu nhiên nhưng ổn định cho mỗi class"""
        np.random.seed(class_id)
        return tuple(map(int, np.random.randint(0, 255, 3)))
        
    def update_display(self, image):
        """Cập nhật hiển thị ảnh lên frame"""
        if image is None:
            return
            
        # Lấy kích thước của frame
        frame_width = self.ui.framePicture.width()
        frame_height = self.ui.framePicture.height()
        
        # Tính toán tỷ lệ scale để ảnh vừa với frame và giữ tỷ lệ
        img_height, img_width = image.shape[:2]
        scale = min(frame_width/img_width, frame_height/img_height)
        
        # Kích thước mới
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Chuyển sang QImage và scale
        bytes_per_line = 3 * image.shape[1]
        q_image = QImage(image.data, image.shape[1], image.shape[0], 
                        bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        # Scale ảnh với chất lượng cao
        scaled_pixmap = pixmap.scaled(
            new_width,
            new_height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        
        # Hiển thị lên frame
        self.ui.framePicture.setPixmap(scaled_pixmap)
        
    def update_detections_info(self, detections):
        """Cập nhật thông tin detection"""
        self.text_edit_info.clear()
        
        # Thêm thông tin tổng quan
        total_objects = len(detections)
        class_counts = {}
        
        for det in detections:
            class_id = det['class']
            class_counts[class_id] = class_counts.get(class_id, 0) + 1
        
        # Hiển thị tổng quan
        self.text_edit_info.append("=== TỔNG QUAN ===")
        self.text_edit_info.append(f"Tổng số đối tượng: {total_objects}")
        self.text_edit_info.append("\nPhân bố các lớp:")
        for class_id, count in class_counts.items():
            self.text_edit_info.append(f"- Class {class_id}: {count} đối tượng")
        
        # Hiển thị chi tiết từng đối tượng
        self.text_edit_info.append("\n=== CHI TIẾT ===")
        for i, det in enumerate(detections, 1):
            info = (f"\nĐối tượng {i}:"
                   f"\n- Lớp: {det['class']}"
                   f"\n- Độ tin cậy: {det['confidence']:.2f}"
                   f"\n- Vị trí: {det['bbox']}")
            self.text_edit_info.append(info)
            
    def save_detected_picture(self):
        """Lưu ảnh đã detect"""
        if self.processed_image is None:
            QMessageBox.warning(None, "Lỗi", "Không có ảnh để lưu!")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Lưu ảnh đã detect",
            "",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            try:
                # Chuyển từ RGB sang BGR để lưu với OpenCV
                save_image = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2BGR)
                
                # Lưu ảnh với chất lượng cao nhất
                if file_path.lower().endswith('.jpg') or file_path.lower().endswith('.jpeg'):
                    cv2.imwrite(file_path, save_image, [cv2.IMWRITE_JPEG_QUALITY, 100])
                else:  # PNG
                    cv2.imwrite(file_path, save_image, [cv2.IMWRITE_PNG_COMPRESSION, 0])
                    
                QMessageBox.information(None, "Thành công", 
                                    f"Đã lưu ảnh tại:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(None, "Lỗi", f"Không thể lưu ảnh: {str(e)}")
                
    def reset_ui(self):
        """Reset UI về trạng thái ban đầu"""
        self.ui.buttonChoosePicture.setEnabled(True)
        self.ui.buttonDownloadPicture.setEnabled(False)
        self.progress_bar.hide()
        self.text_edit_info.clear()
        self.ui.framePicture.clear()
        
    def on_detection_complete(self):
        """Xử lý sau khi detection hoàn thành"""
        self.ui.buttonChoosePicture.setEnabled(True)
        
class DetectionThread(QThread):
    """Thread riêng cho việc detection"""
    def __init__(self, image):
        super().__init__()
        self.image = image
        self.processed_image = None
        self.detections = None
        self.error = None
        
    def run(self):
        try:
            self.processed_image = self.image.copy()
            # Thực hiện detection
            self.detections = model_instance.detect(self.image)
            
            # In thông tin chi tiết về các detection
            if self.detections:
                print("\n=== DETECTION RESULTS ===")
                print(f"Total objects detected: {len(self.detections)}")
                
                # Thống kê theo class
                class_counts = {}
                for det in self.detections:
                    class_id = det['class']
                    class_counts[class_id] = class_counts.get(class_id, 0) + 1
                
                print("\nObjects per class:")
                for class_id, count in class_counts.items():
                    print(f"Class {class_id}: {count} objects")
                
                # In chi tiết từng detection
                print("\nDetailed coordinates:")
                for i, det in enumerate(self.detections, 1):
                    x1, y1, x2, y2 = det['bbox']
                    print(f"\nObject {i}:")
                    print(f"- Class: {det['class']}")
                    print(f"- Confidence: {det['confidence']:.4f}")
                    print(f"- Coordinates:")
                    print(f"  + Top-left     (x1, y1): ({x1}, {y1})")
                    print(f"  + Bottom-right (x2, y2): ({x2}, {y2})")
                    print(f"  + Width : {x2 - x1}")
                    print(f"  + Height: {y2 - y1}")
                    
                print("\n" + "="*30 + "\n")
            else:
                print("No objects detected in the image")
                
        except Exception as e:
            self.error = str(e)
            print(f"Error during detection: {self.error}")