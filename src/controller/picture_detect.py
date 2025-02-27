from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import cv2

from module.model import model_instance
from module.detection_thread import DetectionThread
from module.image_utils import ImageUtils
from module.data_exporter import DataExporter

class PictureDetector(QObject):
    detection_finished = Signal()
    
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.current_image = None
        self.processed_image_binding_box = None
        self.processed_image_warm_up = None
        self.detection_thread = None
        self.detections = None
        self.data_exporter = DataExporter()
        self.setup_ui()
        self.setup_ui_connections()
        
    def setup_ui(self):
        """Thiết lập UI ban đầu"""
        self.ui.buttonDownloadPictureBindingBox.setEnabled(False)
        self.ui.buttonDownloadPictureWarmUp.setEnabled(False)
        self.ui.buttonChoosePicture.setEnabled(True)
        self.ui.buttonSaveDataDetectImg.setEnabled(False)
        
    def setup_ui_connections(self):
        """Thiết lập các kết nối signals/slots"""
        self.ui.buttonChoosePicture.clicked.connect(self.select_picture)
        self.ui.buttonDownloadPictureBindingBox.clicked.connect(
            lambda: self.save_detected_picture("binding_box"))
        self.ui.buttonDownloadPictureWarmUp.clicked.connect(
            lambda: self.save_detected_picture("warm_up"))
        self.ui.buttonSaveDataDetectImg.clicked.connect(self.save_data_detected_picture)
        self.detection_finished.connect(self.on_detection_complete)
        
    def select_picture(self):
        """Xử lý chọn ảnh từ file"""
        self.ui.processBarPicture.hide()
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Chọn hình ảnh",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                # Hiển thị progress bar
                self.ui.processBarPicture.setRange(0, 0)
                self.ui.processBarPicture.show()
                
                # Sử dụng ImageUtils để đọc và chuyển đổi ảnh
                image = cv2.imread(file_path)
                if image is None:
                    raise ValueError("Không thể đọc file ảnh")
                
                self.current_image = ImageUtils.convert_bgr_to_rgb(image)
                
                # Thay đổi dòng này:
                # self.update_display(self.current_image)
                # Thành:
                ImageUtils.display_image_in_widget(self.current_image, self.ui.framePictureBindingBox)
                
                # Start processing in thread
                self.detect_static_image(file_path)
                
            except Exception as e:
                QMessageBox.warning(None, "Lỗi", f"Không thể tải hình ảnh: {str(e)}")
                self.reset_ui()

    def detect_static_image(self, image_path):
        """Xử lý ảnh tĩnh với DetectionThread module"""
        if model_instance.model is None:
            QMessageBox.warning(None, "Lỗi", "Chưa tải Model. Vui lòng tải Model trước!")
            self.reset_ui()
            return
            
        # Tạo và cấu hình DetectionThread
        self.detection_thread = DetectionThread(0)  # camera_index không quan trọng cho ảnh tĩnh
        self.detection_thread.frame_signal.connect(self.handle_frame_update)
        self.detection_thread.detection_signal.connect(self.handle_detection_update)
        self.detection_thread.static_detection_complete_signal.connect(self.handle_static_detection_complete)
        self.detection_thread.error_signal.connect(self.handle_detection_error)
        
        # Detect ảnh tĩnh
        self.detection_thread.detect_static_image(image_path)

    def handle_frame_update(self, frames):
        """Xử lý cập nhật frame từ DetectionThread"""
        if 'binding_box' in frames:
            self.processed_image_binding_box = frames['binding_box']
            ImageUtils.display_image_in_widget(frames['binding_box'], self.ui.framePictureBindingBox)
        if 'warm_up' in frames:
            self.processed_image_warm_up = frames['warm_up']
            ImageUtils.display_image_in_widget(frames['warm_up'], self.ui.framePictureWarmUp)

    def handle_detection_update(self, detections):
        """Xử lý cập nhật detections từ DetectionThread"""
        self.detections = detections
        self.update_detections_info(detections)

    def handle_detection_error(self, error_message):
        """Xử lý lỗi từ DetectionThread"""
        QMessageBox.warning(None, "Lỗi", error_message)
        self.reset_ui()

    def handle_static_detection_complete(self, results):
        """Xử lý kết quả detection ảnh tĩnh hoàn thành"""
        if results:
            self.processed_image_binding_box = results['binding_box_frame']
            self.processed_image_warm_up = results['warmup_frame']
            self.detections = results['detections']
            
            # Cập nhật hiển thị
            ImageUtils.display_image_in_widget(self.processed_image_binding_box, self.ui.framePictureBindingBox)
            ImageUtils.display_image_in_widget(self.processed_image_warm_up, self.ui.framePictureWarmUp)
            self.update_detections_info(self.detections)
            
            # Enable các nút
            self.ui.buttonDownloadPictureBindingBox.setEnabled(True)
            self.ui.buttonDownloadPictureWarmUp.setEnabled(True)
            self.ui.buttonSaveDataDetectImg.setEnabled(True)
        
        self.ui.processBarPicture.hide()
        self.detection_finished.emit()

    def update_detections_info(self, detections):
        """Cập nhật thông tin detection"""
        if not detections:
            return
            
        self.ui.textEditStatusPicture.clear()
        
        total_objects = len(detections)
        class_counts = {}
        
        for det in detections:
            class_id = det['class']
            class_counts[class_id] = class_counts.get(class_id, 0) + 1
        
        self.ui.textEditStatusPicture.append("=== TỔNG QUAN ===")
        self.ui.textEditStatusPicture.append(f"Tổng số đối tượng: {total_objects}")
        self.ui.textEditStatusPicture.append("\nPhân bố các lớp:")
        for class_id, count in class_counts.items():
            self.ui.textEditStatusPicture.append(f"- Class {class_id}: {count} đối tượng")
        
        self.ui.textEditStatusPicture.append("\n=== CHI TIẾT ===")
        for i, det in enumerate(detections, 1):
            info = (f"\nĐối tượng {i}:"
                   f"\n- Lớp: {det['class']}"
                   f"\n- Độ tin cậy: {det['confidence']:.2f}"
                   f"\n- Vị trí: {det['bbox']}")
            self.ui.textEditStatusPicture.append(info)

    def save_detected_picture(self, image_type="binding_box"):
        """Lưu ảnh đã detect"""
        frames = {
            'binding_box': self.processed_image_binding_box,
            'warm_up': self.processed_image_warm_up
        }
        
        if image_type not in frames or frames[image_type] is None:
            QMessageBox.warning(None, "Lỗi", "Không có ảnh để lưu!")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Lưu ảnh đã detect",
            f"detected_{image_type}",
            "Image Files (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            try:
                # Sử dụng ImageUtils để chuyển đổi và lưu ảnh
                save_image = ImageUtils.convert_rgb_to_bgr(frames[image_type])
                cv2.imwrite(file_path, save_image)
                QMessageBox.information(None, "Thành công", f"Đã lưu ảnh tại:\n{file_path}")
            except Exception as e:
                QMessageBox.warning(None, "Lỗi", f"Không thể lưu ảnh: {str(e)}")

    def save_data_detected_picture(self):
        """Lưu dữ liệu detection với DataExporter"""
        if self.current_image is None:
            QMessageBox.warning(None, "Lỗi", "Không có ảnh để lưu!")
            return
            
        if not self.detections:
            QMessageBox.warning(None, "Lỗi", "Không có dữ liệu nhận diện để lưu!")
            return
            
        # Tạo dữ liệu để export
        frames = {
            'original': self.current_image,
            'binding_box': self.processed_image_binding_box,
            'warm_up': self.processed_image_warm_up
        }
        
        # Sử dụng DataExporter để export
        export_result = self.data_exporter.export_single_frame(frames, self.detections)
        if not export_result:
            QMessageBox.warning(None, "Lỗi", "Không thể lưu dữ liệu!")
            return

    def reset_ui(self):
        """Reset UI về trạng thái ban đầu"""
        self.ui.buttonChoosePicture.setEnabled(True)
        self.ui.buttonDownloadPictureBindingBox.setEnabled(False)
        self.ui.buttonDownloadPictureWarmUp.setEnabled(False)
        self.ui.buttonSaveDataDetectImg.setEnabled(False)
        self.ui.textEditStatusPicture.clear()
        self.ui.framePictureBindingBox.clear()
        self.ui.framePictureWarmUp.clear()
        
    def on_detection_complete(self):
        """Xử lý sau khi detection hoàn thành"""
        self.ui.buttonChoosePicture.setEnabled(True)