from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtWidgets import QMessageBox, QFileDialog, QPushButton, QListWidgetItem, QApplication
from PySide6.QtGui import QPixmap, QImage, QResizeEvent
import os
import cv2
import tempfile
import shutil
from datetime import datetime

from module.model import model_instance
from module.detection_thread import DetectionThread
from module.image_utils import ImageUtils
from module.data_exporter import DataExporter


class MultiplePictureDetector(QObject):
    detection_finished = Signal(str)  # Signal when detection of a single image is complete
    all_detections_finished = Signal()  # Signal when all images are processed
    progress_updated = Signal(int)  # Signal for progress updates

    def __init__(self, ui, settings):
        super().__init__()
        self.ui = ui
        self.settings = settings
        self.data_exporter = DataExporter(settings=self.settings)

        # Store detection results for each image
        self.detection_results = {}  # {image_path: {'binding_box': img, 'warm_up': img, 'detections': []}}
        self.current_folder = None
        self.image_files = []  # List of image paths
        self.detection_thread = None
        self.processing_cancelled = False
        self.current_displayed_image = None

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup initial UI configuration"""
        # Configure initial button states
        self.ui.buttonSaveAllData.setEnabled(False)
        self.ui.buttonSaveImageChoose.setEnabled(False)

        # Configure frames for consistent image display
        for frame in [self.ui.frameFolderBindingBox, self.ui.frameFolderWarmUp]:
            frame.setScaledContents(False)
            frame.setAlignment(Qt.AlignCenter)

            # Set up resize event handling for frames
            original_resize_event = frame.resizeEvent

            def create_resize_handler(frame_widget, original_handler):
                def resize_handler(event):
                    # Call original handler if it exists
                    if original_handler:
                        original_handler(event)
                    # Refresh image display if needed
                    if self.current_displayed_image:
                        self.refresh_current_image_display()
                    QResizeEvent.accept(event)

                return resize_handler

            frame.resizeEvent = create_resize_handler(frame, original_resize_event)

        # Configure tab names
        self.ui.tabWidgetResultFolder.setTabText(0, "Binding Box")
        self.ui.tabWidgetResultFolder.setTabText(1, "Warm Up")
        self.ui.tabWidgetResultFolder.setTabText(2, "Trạng thái")

        # Add and configure cancel button
        self.ui.buttonCancelProcessing = QPushButton("Hủy xử lý")
        self.ui.buttonCancelProcessing.setVisible(False)
        self.ui.folderControls.addWidget(self.ui.buttonCancelProcessing)

    def setup_connections(self):
        """Setup signals/slots connections"""
        # UI Button connections
        self.ui.buttonChooseFolder.clicked.connect(self.select_folder)
        self.ui.buttonSaveAllData.clicked.connect(self.save_all_detection_data)
        self.ui.buttonSaveImageChoose.clicked.connect(self.save_selected_image)
        self.ui.buttonCancelProcessing.clicked.connect(self.cancel_processing)

        # List widget connections
        self.ui.listImage.itemClicked.connect(self.display_selected_image)
        self.ui.listImage.currentItemChanged.connect(self.on_item_selection_changed)

        # Custom signal connections
        self.detection_finished.connect(self.on_single_detection_complete)
        self.all_detections_finished.connect(self.on_all_detections_complete)
        self.progress_updated.connect(self.update_progress_bar)

        # Connect tab change events to handle image resizing
        self.ui.tabWidgetResultFolder.currentChanged.connect(self.handle_tab_change)

    def handle_tab_change(self, tab_index):
        """
        Handle tab change to ensure proper image display

        Args:
            tab_index: Index of the selected tab
        """
        if self.current_displayed_image and tab_index < 2:  # Only for image tabs (0 and 1)
            self.refresh_current_image_display()

    def refresh_current_image_display(self):
        """Refresh the display of the current image with proper scaling"""
        if not self.current_displayed_image or self.current_displayed_image not in self.detection_results:
            return

        results = self.detection_results[self.current_displayed_image]
        current_tab = self.ui.tabWidgetResultFolder.currentIndex()

        # Display images based on current tab
        if current_tab == 0:  # Binding Box tab
            self._display_image_with_scaling(results['binding_box'], self.ui.frameFolderBindingBox)
        elif current_tab == 1:  # Warm Up tab
            self._display_image_with_scaling(results['warm_up'], self.ui.frameFolderWarmUp)
        else:  # For status tab or any other tab, update both
            self._display_image_with_scaling(results['binding_box'], self.ui.frameFolderBindingBox)
            self._display_image_with_scaling(results['warm_up'], self.ui.frameFolderWarmUp)

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
        frame_widget.setAlignment(Qt.AlignCenter)

    def select_folder(self):
        """Select folder containing images and start processing"""
        # Check if model is loaded
        if model_instance.model is None:
            QMessageBox.warning(None, "Lỗi", "Chưa tải Model. Vui lòng tải Model trước!")
            return

        # Make sure any ongoing detection is cancelled
        self.cleanup_detection_thread()

        # Show warning if there's existing data
        if self.detection_results:
            confirm = QMessageBox.warning(
                None,
                "Cảnh báo",
                "Việc này có thể làm mất dữ liệu hiện tại. Bạn có chắc chắn tiếp tục?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if confirm == QMessageBox.No:
                return

        folder_path = QFileDialog.getExistingDirectory(
            None,
            "Chọn thư mục chứa ảnh",
            "",
            QFileDialog.ShowDirsOnly
        )

        if not folder_path:
            return  # User cancelled selection

        try:
            # Reset previous data
            self.reset_detection_state()
            self.current_folder = folder_path
            QApplication.processEvents()  # Process UI events

            # Get list of image files with supported extensions
            self.image_files = self.get_image_files_from_folder(folder_path)

            if not self.image_files:
                QMessageBox.warning(None, "Lỗi", "Không tìm thấy ảnh trong thư mục!")
                return

            # Setup UI for processing
            self.setup_ui_for_processing(len(self.image_files), folder_path)
            QApplication.processEvents()  # Process UI events

            # Start processing the first image
            self.process_next_image()

        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Lỗi khi đọc thư mục: {str(e)}")
            self.reset_ui_after_processing()

    def cleanup_detection_thread(self):
        """Clean up detection thread if it exists"""
        if self.detection_thread:
            if self.detection_thread.isRunning():
                self.detection_thread.terminate()
                self.detection_thread.wait()
            # Disconnect all signals
            try:
                self.detection_thread.frame_signal.disconnect()
                self.detection_thread.detection_signal.disconnect()
                self.detection_thread.static_detection_complete_signal.disconnect()
                self.detection_thread.error_signal.disconnect()
            except:
                # Ignore disconnection errors
                pass
            self.detection_thread = None

    def reset_detection_state(self):
        """Reset detection state for a new folder"""
        self.detection_results.clear()
        self.ui.listImage.clear()
        self.ui.textEditFolderStatus.clear()
        self.processing_cancelled = False  # Reset the cancellation flag
        self.current_displayed_image = None

        # Reset frames
        if hasattr(self.ui.frameFolderBindingBox, 'clear'):
            self.ui.frameFolderBindingBox.clear()
        else:
            self.ui.frameFolderBindingBox.setPixmap(QPixmap())

        if hasattr(self.ui.frameFolderWarmUp, 'clear'):
            self.ui.frameFolderWarmUp.clear()
        else:
            self.ui.frameFolderWarmUp.setPixmap(QPixmap())

    def get_image_files_from_folder(self, folder_path):
        """Get all image files from a folder with supported extensions"""
        image_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')
        image_files = [
            os.path.join(folder_path, f) for f in os.listdir(folder_path)
            if f.lower().endswith(image_extensions)
        ]
        return sorted(image_files)  # Sort for consistent processing order

    def setup_ui_for_processing(self, file_count, folder_path):
        """Setup UI elements for batch processing"""
        # Configure progress bar
        self.ui.multiProcessBar.setVisible(True)
        self.ui.multiProcessBar.setMaximum(file_count)
        self.ui.multiProcessBar.setValue(0)

        # Configure buttons
        self.ui.buttonCancelProcessing.setVisible(True)
        self.ui.buttonChooseFolder.setEnabled(False)

        # Hide save buttons during processing
        self.ui.buttonSaveAllData.setVisible(False)
        self.ui.buttonSaveImageChoose.setVisible(False)

        # Display initial messages
        self.ui.textEditFolderStatus.append(f"Bắt đầu xử lý {file_count} ảnh từ thư mục:")
        self.ui.textEditFolderStatus.append(f"{folder_path}\n")

        # Set initial frame messages
        if hasattr(self.ui.frameFolderBindingBox, 'setText'):
            self.ui.frameFolderBindingBox.setText("Đang trong quá trình nhận dạng ...")
            self.ui.frameFolderWarmUp.setText("Đang trong quá trình nhận dạng ...")

    def process_next_image(self):
        """Process next image in the list"""
        # Check if processing should stop
        if self.processing_cancelled or not self.image_files:
            if self.processing_cancelled:
                self.ui.textEditFolderStatus.append("\nĐã hủy xử lý!")

            self.all_detections_finished.emit()
            return

        # Get next image path
        image_path = self.image_files.pop(0)
        base_name = os.path.basename(image_path)

        try:
            # Update status
            self.ui.textEditFolderStatus.append(f"Đang xử lý: {base_name}")
            QApplication.processEvents()  # Ensure UI updates

            # Initialize and configure detection thread
            self.initialize_detection_thread(image_path)

        except Exception as e:
            self.ui.textEditFolderStatus.append(f"Lỗi xử lý {base_name}: {str(e)}")
            QApplication.processEvents()

            # Continue with next image
            self.progress_updated.emit(self.ui.multiProcessBar.value() + 1)
            self.process_next_image()

    def initialize_detection_thread(self, image_path):
        """Initialize and start detection thread for an image"""
        # Clean up any existing detection thread
        self.cleanup_detection_thread()

        # Create new detection thread
        self.detection_thread = DetectionThread(0)

        # Connect signals
        self.detection_thread.frame_signal.connect(self.handle_frame_update)
        self.detection_thread.detection_signal.connect(self.handle_detection_update)
        self.detection_thread.static_detection_complete_signal.connect(
            lambda results: self.handle_static_detection_complete(results, image_path)
        )
        self.detection_thread.error_signal.connect(self.handle_detection_error)

        # Start detection for current image
        self.detection_thread.detect_static_image(image_path)

    def handle_frame_update(self, frames):
        """Handle frame updates from DetectionThread"""
        if not frames:
            return

        # Display binding box frame if available
        if 'binding_box' in frames:
            self._display_image_with_scaling(frames['binding_box'], self.ui.frameFolderBindingBox)

        # Display warm up frame if available
        if 'warm_up' in frames:
            self._display_image_with_scaling(frames['warm_up'], self.ui.frameFolderWarmUp)

    def handle_detection_update(self, detections):
        """Handle detection updates from DetectionThread"""
        if detections:
            self.update_detection_info(detections)

    def handle_static_detection_complete(self, results, image_path):
        """Handle completed detection results for an image"""
        if self.processing_cancelled:
            self.process_next_image()
            return

        if results:
            # Store results with timestamp
            self.store_detection_results(results, image_path)

            # Add to list widget
            self.add_image_to_list(image_path)

            # Update status with detection count
            detection_count = len(results['detections'])
            self.ui.textEditFolderStatus.append(
                f"✓ Hoàn thành: {os.path.basename(image_path)} - {detection_count} đối tượng"
            )
            QApplication.processEvents()

        # Update progress and continue
        self.progress_updated.emit(self.ui.multiProcessBar.value() + 1)
        self.detection_finished.emit(image_path)
        self.process_next_image()

    def store_detection_results(self, results, image_path):
        """Store detection results with timestamp"""
        self.detection_results[image_path] = {
            'binding_box': results['binding_box_frame'],
            'warm_up': results['warmup_frame'],
            'detections': results['detections'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def add_image_to_list(self, image_path):
        """Add image to list widget"""
        item = QListWidgetItem(os.path.basename(image_path))
        item.setData(Qt.UserRole, image_path)
        self.ui.listImage.addItem(item)

    def handle_detection_error(self, error_message):
        """Handle errors from DetectionThread"""
        self.ui.textEditFolderStatus.append(f"Lỗi: {error_message}")
        QApplication.processEvents()

        # Continue with next image
        self.progress_updated.emit(self.ui.multiProcessBar.value() + 1)
        self.process_next_image()

    def display_selected_image(self, item):
        """Display selected image from the list"""
        if not item:
            return

        image_path = item.data(Qt.UserRole)
        if image_path not in self.detection_results:
            return

        # Store current displayed image reference
        self.current_displayed_image = image_path

        # Use the refresh method to display the image with proper scaling
        self.refresh_current_image_display()

        # Update detection info
        results = self.detection_results[image_path]
        self.update_detection_info(results['detections'], image_path)

    def on_item_selection_changed(self, current, previous):
        """Handle item selection change in the list"""
        if current:
            self.display_selected_image(current)

    def update_detection_info(self, detections, image_path=None):
        """Update detection information in the status text box"""
        self.ui.textEditFolderStatus.clear()

        # Display file and timestamp info if available
        if image_path:
            self.ui.textEditFolderStatus.append(f"File: {os.path.basename(image_path)}")
            if image_path in self.detection_results:
                self.ui.textEditFolderStatus.append(f"Thời gian: {self.detection_results[image_path]['timestamp']}\n")

        # Calculate statistics
        total_objects = len(detections)
        class_counts = {}

        for det in detections:
            class_id = det['class']
            class_counts[class_id] = class_counts.get(class_id, 0) + 1

        # Display overview
        self.ui.textEditFolderStatus.append("=== TỔNG QUAN ===")
        self.ui.textEditFolderStatus.append(f"Tổng số đối tượng: {total_objects}")

        # Display class distribution
        if total_objects > 0:
            self.ui.textEditFolderStatus.append("\nPhân bố các lớp:")
            for class_id, count in sorted(class_counts.items()):
                class_percentage = (count / total_objects) * 100
                self.ui.textEditFolderStatus.append(f"- Class {class_id}: {count} đối tượng ({class_percentage:.1f}%)")

        # Display details section
        self.ui.textEditFolderStatus.append("\n=== CHI TIẾT ===")

        # Sort detections by confidence for better readability
        sorted_detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
        for i, det in enumerate(sorted_detections, 1):
            info = (f"\nĐối tượng {i}:"
                    f"\n- Lớp: {det['class']}"
                    f"\n- Độ tin cậy: {det['confidence']:.2f}"
                    f"\n- Vị trí: {det['bbox']}")
            self.ui.textEditFolderStatus.append(info)

    def save_all_detection_data(self):
        """Save all detection data using DataExporter"""
        if not self.detection_results:
            QMessageBox.warning(None, "Lỗi", "Không có dữ liệu để lưu!")
            return

        try:
            # Create a temporary directory for image processing
            temp_dir = tempfile.mkdtemp()
            frame_data = self.prepare_frame_data_for_export(temp_dir)

            if not frame_data['images']:
                shutil.rmtree(temp_dir)  # Clean up
                raise Exception("Không có ảnh nào được xử lý thành công!")

            # Export the prepared data
            result = self.data_exporter.export_all_frames(frame_data)
            shutil.rmtree(temp_dir)  # Clean up temporary directory

            if result and isinstance(result, dict):
                QMessageBox.information(
                    None,
                    "Thành công",
                    f"Đã lưu {len(frame_data['images'])} ảnh thành công!\n"
                    f"Vị trí lưu: {result['root_dir']}"
                )

        except Exception as e:
            # Ensure temporary directory is cleaned up on error
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir)
            QMessageBox.warning(None, "Lỗi", f"Không thể lưu dữ liệu: {str(e)}")

    def prepare_frame_data_for_export(self, temp_dir):
        """Prepare frame data for export"""
        frame_data = {
            'images': [],
            'detections': []
        }

        for image_path, results in self.detection_results.items():
            try:
                # Normalize the image path
                image_path = os.path.normpath(image_path).replace('\\', '/')

                # Save frames to temporary files
                binding_box_path = os.path.join(temp_dir, f"{os.path.basename(image_path)}_binding_box.jpg")
                warm_up_path = os.path.join(temp_dir, f"{os.path.basename(image_path)}_warm_up.jpg")

                # Convert RGB to BGR for OpenCV and write to files
                cv2.imwrite(binding_box_path, cv2.cvtColor(results['binding_box'], cv2.COLOR_RGB2BGR))
                cv2.imwrite(warm_up_path, cv2.cvtColor(results['warm_up'], cv2.COLOR_RGB2BGR))

                # Create frame_info with file paths
                frame_info = {
                    'timestamp': os.path.splitext(os.path.basename(image_path))[0],
                    'detections': results['detections'],
                    'original_path': image_path,
                    'binding_box_path': binding_box_path,
                    'warmup_path': warm_up_path
                }
                frame_data['images'].append(frame_info)

                # Add detections with metadata
                for detection in results['detections']:
                    detection_with_meta = detection.copy()
                    detection_with_meta.update({
                        'timestamp': frame_info['timestamp'],
                        'image_path': image_path
                    })
                    frame_data['detections'].append(detection_with_meta)

            except Exception as img_error:
                self.ui.textEditFolderStatus.append(
                    f"Lỗi xử lý ảnh {os.path.basename(image_path)}: {str(img_error)}"
                )
                continue

        return frame_data

    def save_selected_image(self):
        """Save currently selected image"""
        current_item = self.ui.listImage.currentItem()
        if not current_item:
            QMessageBox.warning(None, "Lỗi", "Vui lòng chọn một ảnh để lưu!")
            return

        image_path = current_item.data(Qt.UserRole)
        if image_path not in self.detection_results:
            return

        try:
            # Get the results for the selected image
            results = self.detection_results[image_path]

            # Read original image and convert to RGB
            original_img = cv2.imread(image_path)
            if original_img is None:
                raise Exception(f"Không thể đọc ảnh gốc: {image_path}")

            original_rgb = cv2.cvtColor(original_img, cv2.COLOR_BGR2RGB)

            # Use existing frames directly
            frames = {
                'original': original_rgb,
                'binding_box': results['binding_box'],
                'warm_up': results['warm_up']
            }

            # Use DataExporter to save single frame
            self.data_exporter.export_single_frame(
                frames=frames,
                detections=results['detections']
            )

            QMessageBox.information(None, "Thành công", "Đã lưu ảnh thành công!")

        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể lưu dữ liệu: {str(e)}")

    def cancel_processing(self):
        """Cancel ongoing processing"""
        self.processing_cancelled = True

        # Terminate detection thread if running
        self.cleanup_detection_thread()

        self.ui.textEditFolderStatus.append("\nĐã hủy xử lý!")
        QApplication.processEvents()

        # Reset UI immediately instead of waiting for process_next_image
        self.reset_ui_after_processing()

        # Show cancellation dialog
        QMessageBox.information(
            None,
            "Đã hủy",
            f"Quá trình xử lý đã bị hủy bỏ.\nĐã xử lý {self.ui.listImage.count()} ảnh."
        )

        # Enable and show appropriate buttons based on processed images
        has_images = self.ui.listImage.count() > 0
        self.ui.buttonSaveImageChoose.setEnabled(has_images)
        self.ui.buttonSaveAllData.setEnabled(has_images)
        self.ui.buttonSaveImageChoose.setVisible(True)
        self.ui.buttonSaveAllData.setVisible(True)

        # Select first item if available
        if has_images:
            self.ui.listImage.setCurrentRow(0)

    def update_progress_bar(self, value):
        """Update progress bar value"""
        self.ui.multiProcessBar.setValue(value)

    def on_single_detection_complete(self, image_path):
        """Handle completion of single image detection"""
        self.ui.buttonSaveAllData.setEnabled(self.ui.listImage.count() > 0)

    def on_all_detections_complete(self):
        """Handle completion of all image detections"""
        self.reset_ui_after_processing()

        # Enable appropriate buttons based on results
        has_images = self.ui.listImage.count() > 0
        self.ui.buttonSaveImageChoose.setEnabled(has_images)
        self.ui.buttonSaveAllData.setEnabled(has_images)

        # Select first item if available
        if has_images:
            self.ui.listImage.setCurrentRow(0)
            QMessageBox.information(
                None,
                "Hoàn thành",
                f"Đã xử lý xong {self.ui.listImage.count()} ảnh!"
            )

    def reset_ui_after_processing(self):
        """Reset UI elements after processing is complete"""
        self.ui.multiProcessBar.setVisible(False)
        self.ui.buttonCancelProcessing.setVisible(False)
        self.ui.buttonChooseFolder.setEnabled(True)

        # Show save buttons again (they'll be enabled/disabled based on results)
        self.ui.buttonSaveAllData.setVisible(True)
        self.ui.buttonSaveImageChoose.setVisible(True)