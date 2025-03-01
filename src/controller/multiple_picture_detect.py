from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
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
    detection_finished = Signal(str)  # Signal to emit when detection of a single image is complete
    all_detections_finished = Signal()  # Signal to emit when all images are processed
    progress_updated = Signal(int)  # Signal to emit progress updates
    
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
        
        self.setup_ui()
        self.setup_ui_connections()
        
    def setup_ui(self):
        """Setup initial UI"""
        # Configure initial button states
        self.ui.buttonSaveAllData.setEnabled(False)
        self.ui.buttonSaveImageChoose.setEnabled(False)
        
        # Configure frames
        for frame in [self.ui.frameFolderBindingBox, self.ui.frameFolderWarmUp]:
            frame.setScaledContents(False)
            frame.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Configure tab names
        self.ui.tabWidgetResultFolder.setTabText(0, "Binding Box")
        self.ui.tabWidgetResultFolder.setTabText(1, "Warm Up")
        self.ui.tabWidgetResultFolder.setTabText(2, "Trạng thái")
        
        # Add cancel button
        self.ui.buttonCancelProcessing = QPushButton("Hủy xử lý")
        self.ui.buttonCancelProcessing.setVisible(False)
        self.ui.folderControls.addWidget(self.ui.buttonCancelProcessing)
        
    def setup_ui_connections(self):
        """Setup signals/slots connections"""
        self.ui.buttonChooseFolder.clicked.connect(self.select_folder)
        self.ui.buttonSaveAllData.clicked.connect(self.save_all_detection_data)
        self.ui.buttonSaveImageChoose.clicked.connect(self.save_selected_image)
        self.ui.listImage.itemClicked.connect(self.display_selected_image)
        self.ui.listImage.currentItemChanged.connect(self.on_item_selection_changed)
        self.ui.buttonCancelProcessing.clicked.connect(self.cancel_processing)
        
        self.detection_finished.connect(self.on_single_detection_complete)
        self.all_detections_finished.connect(self.on_all_detections_complete)
        self.progress_updated.connect(self.update_progress_bar)
        
    def select_folder(self):
        """Select folder containing images and start processing"""
        if model_instance.model is None:
            QMessageBox.warning(None, "Lỗi", "Chưa tải Model. Vui lòng tải Model trước!")
            return
            
        folder_path = QFileDialog.getExistingDirectory(
            None,
            "Chọn thư mục chứa ảnh",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if folder_path:
            try:
                # Reset previous data
                self.current_folder = folder_path
                self.detection_results.clear()
                self.ui.listImage.clear()
                self.ui.textEditFolderStatus.clear()
                self.processing_cancelled = False
                
                # Get list of image files
                self.image_files = [
                    os.path.join(folder_path, f) for f in os.listdir(folder_path)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp'))
                ]
                
                if not self.image_files:
                    QMessageBox.warning(None, "Lỗi", "Không tìm thấy ảnh trong thư mục!")
                    return
                
                # Sort files by name for consistent processing order
                self.image_files.sort()
                    
                # Setup progress bar and controls
                self.ui.multiProcessBar.setVisible(True)
                self.ui.multiProcessBar.setMaximum(len(self.image_files))
                self.ui.multiProcessBar.setValue(0)
                self.ui.buttonCancelProcessing.setVisible(True)
                self.ui.buttonChooseFolder.setEnabled(False)
                
                # Display status message
                self.ui.textEditFolderStatus.append(f"Bắt đầu xử lý {len(self.image_files)} ảnh từ thư mục:")
                self.ui.textEditFolderStatus.append(f"{folder_path}\n")

                self.ui.frameFolderBindingBox.setText("Đang trong quá trình nhận dạng ...")
                self.ui.frameFolderWarmUp.setText("Đang trong quá trình nhận dạng ...")
                
                # Start processing images
                self.process_next_image()
                
            except Exception as e:
                QMessageBox.warning(None, "Lỗi", f"Lỗi khi đọc thư mục: {str(e)}")
                self.ui.multiProcessBar.setVisible(False)
                self.ui.buttonCancelProcessing.setVisible(False)
                self.ui.buttonChooseFolder.setEnabled(True)
                
    def process_next_image(self):
        """Process next image in the list"""
        if self.processing_cancelled or not self.image_files:
            if self.processing_cancelled:
                self.ui.textEditFolderStatus.append("\nĐã hủy xử lý!")
            
            self.all_detections_finished.emit()
            return
            
        image_path = self.image_files.pop(0)
        
        try:
            # Update status
            base_name = os.path.basename(image_path)
            self.ui.textEditFolderStatus.append(f"Đang xử lý: {base_name}")
            QApplication.processEvents()  # Ensure UI updates
            
            # Initialize detection thread
            self.detection_thread = DetectionThread(0)
            self.detection_thread.frame_signal.connect(self.handle_frame_update)
            self.detection_thread.detection_signal.connect(self.handle_detection_update)
            self.detection_thread.static_detection_complete_signal.connect(
                lambda results: self.handle_static_detection_complete(results, image_path)
            )
            self.detection_thread.error_signal.connect(self.handle_detection_error)
            
            # Start detection for current image
            self.detection_thread.detect_static_image(image_path)
            
        except Exception as e:
            self.ui.textEditFolderStatus.append(f"Lỗi xử lý {base_name}: {str(e)}")
            QApplication.processEvents()
            
            # Continue with next image
            current_value = self.ui.multiProcessBar.value()
            self.progress_updated.emit(current_value + 1)
            self.process_next_image()
            
    def handle_frame_update(self, frames):
        """Handle frame updates from DetectionThread"""
        if not frames:
            return
            
        if 'binding_box' in frames:
            ImageUtils.display_image_in_widget(frames['binding_box'], self.ui.frameFolderBindingBox)
        if 'warm_up' in frames:
            ImageUtils.display_image_in_widget(frames['warm_up'], self.ui.frameFolderWarmUp)
            
    def handle_detection_update(self, detections):
        """Handle detection updates from DetectionThread"""
        if not detections:
            return
            
        self.update_detection_info(detections)
            
    def handle_static_detection_complete(self, results, image_path):
        """Handle completed detection results for an image"""
        if self.processing_cancelled:
            self.process_next_image()
            return
            
        if results:
            # Store results
            self.detection_results[image_path] = {
                'binding_box': results['binding_box_frame'],
                'warm_up': results['warmup_frame'],
                'detections': results['detections'],
                'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Add to list widget
            item = QListWidgetItem(os.path.basename(image_path))
            item.setData(Qt.UserRole, image_path)
            self.ui.listImage.addItem(item)
            
            # Update status with detection count
            detection_count = len(results['detections'])
            self.ui.textEditFolderStatus.append(
                f"✓ Hoàn thành: {os.path.basename(image_path)} - {detection_count} đối tượng"
            )
            QApplication.processEvents()
            
            # Update progress
            current_value = self.ui.multiProcessBar.value()
            self.progress_updated.emit(current_value + 1)
            
        # Process next image
        self.detection_finished.emit(image_path)
        self.process_next_image()
        
    def handle_detection_error(self, error_message):
        """Handle errors from DetectionThread"""
        self.ui.textEditFolderStatus.append(f"Lỗi: {error_message}")
        QApplication.processEvents()
        
        # Continue with next image
        current_value = self.ui.multiProcessBar.value()
        self.progress_updated.emit(current_value + 1)
        self.process_next_image()
        
    def display_selected_image(self, item):
        """Display selected image from the list"""
        if not item:
            return
            
        image_path = item.data(Qt.UserRole)
        if image_path not in self.detection_results:
            return
            
        results = self.detection_results[image_path]
        
        # Display images
        ImageUtils.display_image_in_widget(results['binding_box'], self.ui.frameFolderBindingBox)
        ImageUtils.display_image_in_widget(results['warm_up'], self.ui.frameFolderWarmUp)
        
        # Update detection info
        self.update_detection_info(results['detections'], image_path)
        
    def on_item_selection_changed(self, current, previous):
        """Handle item selection change in the list"""
        if current:
            self.display_selected_image(current)
        
    def update_detection_info(self, detections, image_path=None):
        """Update detection information in the status text box"""
        self.ui.textEditFolderStatus.clear()
        
        if image_path:
            self.ui.textEditFolderStatus.append(f"File: {os.path.basename(image_path)}")
            if image_path in self.detection_results:
                self.ui.textEditFolderStatus.append(f"Thời gian: {self.detection_results[image_path]['timestamp']}\n")
        
        total_objects = len(detections)
        class_counts = {}
        
        for det in detections:
            class_id = det['class']
            class_counts[class_id] = class_counts.get(class_id, 0) + 1
            
        self.ui.textEditFolderStatus.append("=== TỔNG QUAN ===")
        self.ui.textEditFolderStatus.append(f"Tổng số đối tượng: {total_objects}")
        self.ui.textEditFolderStatus.append("\nPhân bố các lớp:")
        for class_id, count in sorted(class_counts.items()):
            class_percentage = (count / total_objects) * 100 if total_objects > 0 else 0
            self.ui.textEditFolderStatus.append(f"- Class {class_id}: {count} đối tượng ({class_percentage:.1f}%)")
            
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
        """Save all detection data using DataExporter's export_all_frames method"""
        if not self.detection_results:
            QMessageBox.warning(None, "Lỗi", "Không có dữ liệu để lưu!")
            return

        try:
            # Create a temporary directory to store image files
            temp_dir = tempfile.mkdtemp()

            # Prepare data for export
            frame_data = {
                'images': [],
                'detections': []
            }

            for image_path, results in self.detection_results.items():
                try:
                    # Normalize the image path
                    image_path = os.path.normpath(image_path).replace('\\', '/')

                    # Use the original image path directly (assuming it’s a file path)
                    original_path = image_path

                    # Save binding_box and warm_up arrays as temporary files
                    binding_box_path = os.path.join(temp_dir, f"{os.path.basename(image_path)}_binding_box.jpg")
                    warm_up_path = os.path.join(temp_dir, f"{os.path.basename(image_path)}_warm_up.jpg")

                    # Write image arrays to temporary files (convert RGB to BGR for OpenCV)
                    cv2.imwrite(binding_box_path, cv2.cvtColor(results['binding_box'], cv2.COLOR_RGB2BGR))
                    cv2.imwrite(warm_up_path, cv2.cvtColor(results['warm_up'], cv2.COLOR_RGB2BGR))

                    # Create frame_info with file paths
                    frame_info = {
                        'timestamp': os.path.splitext(os.path.basename(image_path))[0],  # Unique identifier
                        'detections': results['detections'],
                        'original_path': original_path,
                        'binding_box_path': binding_box_path,
                        'warmup_path': warm_up_path  # Match key expected by copy_image_files
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

            if not frame_data['images']:
                shutil.rmtree(temp_dir)  # Clean up temporary directory
                raise Exception("Không có ảnh nào được xử lý thành công!")

            # Export the prepared data using DataExporter
            result = self.data_exporter.export_all_frames(frame_data)

            # Clean up temporary directory after export
            shutil.rmtree(temp_dir)

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

    def save_selected_image(self):
        """Save currently selected image using DataExporter's export_single_frame method"""
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
            
            # Read original image
            original_img = cv2.imread(image_path)
            if original_img is None:
                raise Exception(f"Không thể đọc ảnh gốc: {image_path}")
                
            # Normalize image path
            image_path = os.path.normpath(image_path).replace('\\', '/')
                
            # Use existing frames directly - they should already be in correct format
            frames = {
                'original': original_img,
                'binding_box': results['binding_box'],
                'warm_up': results['warm_up']
            }
            
            # Use DataExporter to save single frame
            self.data_exporter.export_single_frame(
                frames=frames,
                detections=results['detections']
            )
             
        except Exception as e:
            QMessageBox.warning(None, "Lỗi", f"Không thể lưu dữ liệu: {str(e)}")

    def cancel_processing(self):
        """Cancel ongoing processing"""
        self.processing_cancelled = True
        if self.detection_thread and self.detection_thread.isRunning():
            self.detection_thread.terminate()
            self.detection_thread.wait()
            
        self.ui.textEditFolderStatus.append("\nĐang hủy xử lý...")
        QApplication.processEvents()
            
    def update_progress_bar(self, value):
        """Update progress bar value"""
        self.ui.multiProcessBar.setValue(value)
            
    def on_single_detection_complete(self, image_path):
        """Handle completion of single image detection"""
        self.ui.buttonSaveAllData.setEnabled(self.ui.listImage.count() > 0)
        
    def on_all_detections_complete(self):
        """Handle completion of all image detections"""
        self.ui.multiProcessBar.setVisible(False)
        self.ui.buttonCancelProcessing.setVisible(False)
        self.ui.buttonChooseFolder.setEnabled(True)
        self.ui.buttonSaveImageChoose.setEnabled(self.ui.listImage.count() > 0)
        
        # Select first item if available
        if self.ui.listImage.count() > 0:
            self.ui.listImage.setCurrentRow(0)
        
        if self.ui.listImage.count() > 0:
            QMessageBox.information(None, "Hoàn thành", f"Đã xử lý xong {self.ui.listImage.count()} ảnh!")