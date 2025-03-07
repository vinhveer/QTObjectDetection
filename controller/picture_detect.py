from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtGui import QPixmap, QImage, QResizeEvent

import cv2
import numpy as np

from module.model import model_instance
from module.detection_thread import DetectionThread
from module.image_utils import ImageUtils
from module.data_exporter import DataExporter
from module.process_dialog import ProcessDialog


class PictureDetector(QObject):
    """
    Class handling image detection functionality for the application.
    """
    detection_finished = Signal()

    def __init__(self, ui, settings):
        """
        Initialize the PictureDetector with UI and settings.

        Args:
            ui: The UI object containing widgets
            settings: Application settings
        """
        super().__init__()
        self.ui = ui
        self.settings = settings

        # Image data
        self.current_image = None
        self.processed_image_binding_box = None
        self.processed_image_warm_up = None
        self.detections = None

        # Helper components
        self.detection_thread = None
        self.data_exporter = DataExporter(settings=self.settings)
        self.process_dialog = ProcessDialog()

        # Setup UI and connections
        self._setup_ui()
        self._setup_ui_connections()

    def _setup_ui(self):
        """Configure initial UI state"""
        self.ui.buttonDownloadPictureBindingBox.setEnabled(False)
        self.ui.buttonDownloadPictureWarmUp.setEnabled(False)
        self.ui.buttonChoosePicture.setEnabled(True)
        self.ui.buttonSaveDataDetectImg.setEnabled(False)

        # Set up frame resize events to maintain proper image sizing
        self.ui.framePictureBindingBox.resizeEvent = lambda event: self._handle_frame_resize(
            event, 'binding_box', self.ui.framePictureBindingBox
        )
        self.ui.framePictureWarmUp.resizeEvent = lambda event: self._handle_frame_resize(
            event, 'warm_up', self.ui.framePictureWarmUp
        )

    def _handle_frame_resize(self, event, frame_type, frame_widget):
        """
        Handle frame resize events to properly scale images

        Args:
            event: Resize event
            frame_type: Type of frame ('binding_box' or 'warm_up')
            frame_widget: The frame widget being resized
        """
        # Call original resize event handler
        QResizeEvent.accept(event)

        # Re-display image with proper sizing if available
        if frame_type == 'binding_box' and self.processed_image_binding_box is not None:
            self._display_image_with_scaling(self.processed_image_binding_box, frame_widget)
        elif frame_type == 'warm_up' and self.processed_image_warm_up is not None:
            self._display_image_with_scaling(self.processed_image_warm_up, frame_widget)

    def _display_image_with_scaling(self, image, frame_widget):
        """
        Display image in frame with proper scaling

        Args:
            image: Image to display (numpy array)
            frame_widget: Widget to display image in
        """
        if image is None:
            return

        # Convert numpy array to QImage
        height, width, channel = image.shape
        if channel == 3:
            q_image = QImage(image.data, width, height, width * 3, QImage.Format_RGB888)
        else:
            q_image = QImage(image.data, width, height, width * 4, QImage.Format_RGBA8888)

        # Create pixmap and scale it to fit the frame while preserving aspect ratio
        pixmap = QPixmap.fromImage(q_image)
        scaled_pixmap = pixmap.scaled(
            frame_widget.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )

        # Set the pixmap on the frame
        frame_widget.setPixmap(scaled_pixmap)

    def _setup_ui_connections(self):
        """Setup signal/slot connections"""
        self.ui.buttonChoosePicture.clicked.connect(self.select_picture)
        self.ui.buttonDownloadPictureBindingBox.clicked.connect(
            lambda: self.save_detected_picture("binding_box"))
        self.ui.buttonDownloadPictureWarmUp.clicked.connect(
            lambda: self.save_detected_picture("warm_up"))
        self.ui.buttonSaveDataDetectImg.clicked.connect(self.save_data_detected_picture)
        self.detection_finished.connect(self._on_detection_complete)

        # Fix for image resizing when switching tabs
        if hasattr(self.ui, 'tabWidget'):
            self.ui.tabWidget.currentChanged.connect(self._update_current_tab_images)

    def _update_current_tab_images(self, tab_index):
        """
        Update images when changing tabs to maintain proper sizing

        Args:
            tab_index: Index of the selected tab
        """
        # Force redisplay of images with proper scaling
        if self.processed_image_binding_box is not None:
            self._display_image_with_scaling(
                self.processed_image_binding_box,
                self.ui.framePictureBindingBox
            )

        if self.processed_image_warm_up is not None:
            self._display_image_with_scaling(
                self.processed_image_warm_up,
                self.ui.framePictureWarmUp
            )

    def select_picture(self):
        """Handle picture selection from files"""
        if not self._check_model_loaded():
            return

        file_path = self._get_image_file_path()
        if not file_path:
            return

        try:
            self.process_dialog.show()
            self._load_and_process_image(file_path)
        except Exception as e:
            self._handle_error(f"Không thể tải hình ảnh: {str(e)}")

    def _check_model_loaded(self):
        """
        Check if the model is loaded

        Returns:
            bool: True if model is loaded, False otherwise
        """
        if model_instance.model is None:
            QMessageBox.warning(None, "Lỗi", "Chưa tải Model. Vui lòng tải Model trước!")
            self.reset_ui()
            return False
        return True

    def _get_image_file_path(self):
        """
        Display file dialog to get image path

        Returns:
            str: Selected file path or empty string
        """
        file_path, _ = QFileDialog.getOpenFileName(
            None,
            "Chọn hình ảnh",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        return file_path

    def _load_and_process_image(self, file_path):
        """
        Load image from file and start processing

        Args:
            file_path: Path to the image file
        """
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Không thể đọc file ảnh")

        self.current_image = ImageUtils.convert_bgr_to_rgb(image)
        self._display_image_with_scaling(self.current_image, self.ui.framePictureBindingBox)

        # Start detection process
        self._detect_static_image(file_path)

    def _detect_static_image(self, image_path):
        """
        Process static image with DetectionThread

        Args:
            image_path: Path to the image file
        """
        # Configure DetectionThread
        self.detection_thread = DetectionThread(0)  # camera_index not important for static images
        self._connect_detection_thread_signals()

        # Start detection
        self.detection_thread.detect_static_image(image_path)

    def _connect_detection_thread_signals(self):
        """Connect signals from detection thread to handler methods"""
        self.detection_thread.frame_signal.connect(self._handle_frame_update)
        self.detection_thread.detection_signal.connect(self._handle_detection_update)
        self.detection_thread.static_detection_complete_signal.connect(self._handle_static_detection_complete)
        self.detection_thread.error_signal.connect(self._handle_detection_error)

    def _handle_frame_update(self, frames):
        """
        Handle frame updates from DetectionThread

        Args:
            frames: Dictionary containing processed frames
        """
        if 'binding_box' in frames:
            self.processed_image_binding_box = frames['binding_box']
            self._display_image_with_scaling(frames['binding_box'], self.ui.framePictureBindingBox)

        if 'warm_up' in frames:
            self.processed_image_warm_up = frames['warm_up']
            self._display_image_with_scaling(frames['warm_up'], self.ui.framePictureWarmUp)

    def _handle_detection_update(self, detections):
        """
        Handle detection updates from DetectionThread

        Args:
            detections: List of detected objects
        """
        self.detections = detections
        self._update_detections_info(detections)

    def _handle_detection_error(self, error_message):
        """
        Handle errors from DetectionThread

        Args:
            error_message: Error message to display
        """
        self._handle_error(error_message)

    def _handle_error(self, error_message):
        """
        Display error message and reset UI

        Args:
            error_message: Error message to display
        """
        QMessageBox.warning(None, "Lỗi", error_message)
        self.reset_ui()
        self.process_dialog.hide()

    def _handle_static_detection_complete(self, results):
        """
        Handle completed static image detection

        Args:
            results: Dictionary containing detection results
        """
        if results:
            self.processed_image_binding_box = results['binding_box_frame']
            self.processed_image_warm_up = results['warmup_frame']
            self.detections = results['detections']

            # Update UI with results
            self._display_image_with_scaling(self.processed_image_binding_box, self.ui.framePictureBindingBox)
            self._display_image_with_scaling(self.processed_image_warm_up, self.ui.framePictureWarmUp)
            self._update_detections_info(self.detections)

            # Enable buttons
            self._enable_result_buttons()

        # Hide progress dialog
        self.process_dialog.hide()
        self.detection_finished.emit()

    def _enable_result_buttons(self):
        """Enable buttons for interacting with results"""
        self.ui.buttonDownloadPictureBindingBox.setEnabled(True)
        self.ui.buttonDownloadPictureWarmUp.setEnabled(True)
        self.ui.buttonSaveDataDetectImg.setEnabled(True)

    def _update_detections_info(self, detections):
        """
        Update detection information display

        Args:
            detections: List of detected objects
        """
        if not detections:
            return

        text_edit = self.ui.textEditStatusPicture
        text_edit.clear()

        # Calculate statistics
        total_objects = len(detections)
        class_counts = {}

        for det in detections:
            class_id = det['class']
            class_counts[class_id] = class_counts.get(class_id, 0) + 1

        # Display summary
        text_edit.append("=== TỔNG QUAN ===")
        text_edit.append(f"Tổng số đối tượng: {total_objects}")
        text_edit.append("\nPhân bố các lớp:")

        for class_id, count in class_counts.items():
            text_edit.append(f"- Class {class_id}: {count} đối tượng")

        # Display details
        text_edit.append("\n=== CHI TIẾT ===")

        for i, det in enumerate(detections, 1):
            info = (f"\nĐối tượng {i}:"
                    f"\n- Lớp: {det['class']}"
                    f"\n- Độ tin cậy: {det['confidence']:.2f}"
                    f"\n- Vị trí: {det['bbox']}")
            text_edit.append(info)

    def save_detected_picture(self, image_type="binding_box"):
        """
        Save detected picture

        Args:
            image_type: Type of image to save ("binding_box" or "warm_up")
        """
        frames = {
            'binding_box': self.processed_image_binding_box,
            'warm_up': self.processed_image_warm_up
        }

        if image_type not in frames or frames[image_type] is None:
            QMessageBox.warning(None, "Lỗi", "Không có ảnh để lưu!")
            return

        file_path = self._get_save_file_path(f"detected_{image_type}")
        if not file_path:
            return

        try:
            self._save_image(file_path, frames[image_type])
            QMessageBox.information(None, "Thành công", f"Đã lưu ảnh tại:\n{file_path}")
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể lưu ảnh: {str(e)}")

    def _get_save_file_path(self, default_name):
        """
        Get file path for saving

        Args:
            default_name: Default filename

        Returns:
            str: Selected file path or empty string
        """
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "Lưu ảnh đã detect",
            default_name,
            "Image Files (*.png *.jpg *.jpeg)"
        )
        return file_path

    def _save_image(self, file_path, image):
        """
        Save image to file

        Args:
            file_path: Path to save the image
            image: Image to save
        """
        save_image = ImageUtils.convert_rgb_to_bgr(image)
        cv2.imwrite(file_path, save_image)

    def save_data_detected_picture(self):
        """Save detection data using DataExporter"""
        if not self._check_data_available():
            return

        # Prepare data for export
        frames = {
            'original': self.current_image,
            'binding_box': self.processed_image_binding_box,
            'warm_up': self.processed_image_warm_up
        }

        # Export data
        export_result = self.data_exporter.export_single_frame(frames, self.detections)
        if not export_result:
            QMessageBox.warning(None, "Lỗi", "Không thể lưu dữ liệu!")

    def _check_data_available(self):
        """
        Check if data is available for saving

        Returns:
            bool: True if data is available, False otherwise
        """
        if self.current_image is None:
            QMessageBox.warning(None, "Lỗi", "Không có ảnh để lưu!")
            return False

        if not self.detections:
            QMessageBox.warning(None, "Lỗi", "Không có dữ liệu nhận diện để lưu!")
            return False

        return True

    def reset_ui(self):
        """Reset UI to initial state"""
        self.ui.buttonChoosePicture.setEnabled(True)
        self.ui.buttonDownloadPictureBindingBox.setEnabled(False)
        self.ui.buttonDownloadPictureWarmUp.setEnabled(False)
        self.ui.buttonSaveDataDetectImg.setEnabled(False)
        self.ui.textEditStatusPicture.clear()

        # Clear frames
        if hasattr(self.ui.framePictureBindingBox, 'clear'):
            self.ui.framePictureBindingBox.clear()
        else:
            self.ui.framePictureBindingBox.setPixmap(QPixmap())

        if hasattr(self.ui.framePictureWarmUp, 'clear'):
            self.ui.framePictureWarmUp.clear()
        else:
            self.ui.framePictureWarmUp.setPixmap(QPixmap())

    def _on_detection_complete(self):
        """Handle detection completion"""
        self.ui.buttonChoosePicture.setEnabled(True)