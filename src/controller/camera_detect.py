from datetime import datetime
import cv2
import numpy as np
import sys
from PySide6.QtCore import Qt, QObject
from PySide6.QtWidgets import QMessageBox

from module.detection_thread import DetectionThread
from module.model import model_instance
from module.image_utils import ImageUtils
from module.data_exporter import DataExporter

if sys.platform.startswith("win"):
    from pygrabber.dshow_graph import FilterGraph

class CameraDetector(QObject):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.thread = None
        self.current_frame = None
        self.image_utils = ImageUtils()
        self.data_exporter = DataExporter()
        self.setup_ui()
        self.setup_ui_connections()
        self.setup_camera_list()
        
    def setup_ui(self):
        """Configure initial UI components and states"""
        # Configure image display frames
        for frame in [self.ui.frameCameraBindingBox, self.ui.frameCameraWarmUp]:
            frame.setScaledContents(False)
            frame.setAlignment(Qt.AlignCenter)
        
        # Set initial button states
        self.ui.buttonDetect.setEnabled(False)
        self.ui.buttonDetect.setText("Start Detection")
        self.ui.buttonCapture.setEnabled(False)
        self.ui.buttonSaveAllDetectCam.setEnabled(False)
   
    def setup_ui_connections(self):
        """Set up signal/slot connections for UI components"""
        self.ui.buttonStartRecord.clicked.connect(self.toggle_camera)
        self.ui.buttonDetect.clicked.connect(self.toggle_detection)
        self.ui.buttonCapture.clicked.connect(self.capture_frame)
        self.ui.buttonSaveAllDetectCam.clicked.connect(self.save_all_data_detect_cam)
        
    def setup_camera_list(self):
        """Scan for available cameras and populate the dropdown list"""
        self.ui.comboBoxChooseCamera.clear()
        camera_found = False

        if sys.platform.startswith("win"):
            # Windows: Get camera list using pygrabber
            graph = FilterGraph()
            devices = graph.get_input_devices()

            for i, device_name in enumerate(devices):
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self.ui.comboBoxChooseCamera.addItem(device_name)
                    cap.release()
                    camera_found = True
        else:
            # MacOS/Linux: OpenCV doesn't support fetching device names
            for i in range(10):  # Scan up to 10 cameras
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    self.ui.comboBoxChooseCamera.addItem(f"Camera {i}")
                    cap.release()
                    camera_found = True

        # Handle case when no cameras are found
        if not camera_found:
            self.ui.comboBoxChooseCamera.addItem("No cameras found")
            self.ui.buttonStartRecord.setEnabled(False)
        else:
            self.ui.buttonStartRecord.setEnabled(True)
            
    def toggle_camera(self):
        """Start or stop camera capture"""
        if not self.thread or not self.thread.running:
            # Start camera
            camera_index = self.ui.comboBoxChooseCamera.currentIndex()
            if camera_index < 0:
                QMessageBox.warning(None, "Error", "No camera selected!")
                return
                
            # Initialize detection thread
            self.thread = DetectionThread(camera_index)
            self.thread.frame_signal.connect(self.update_camera_feed)
            self.thread.error_signal.connect(self.handle_camera_error)
            self.thread.detection_signal.connect(self.update_detections_info)
            self.thread.start()
            
            # Update UI state
            self.ui.buttonStartRecord.setText("Stop Camera")
            self.ui.buttonDetect.setEnabled(True)
            self.ui.comboBoxChooseCamera.setEnabled(False)
        else:
            # Stop camera
            if self.thread.detecting:
                self.toggle_detection()  # Stop detection if running
            
            self.thread.stop_capture()
            self.thread = None
            
            # Clear display frames
            self.ui.frameCameraBindingBox.clear()
            self.ui.frameCameraWarmUp.clear()
            
            # Reset UI state
            self.ui.buttonStartRecord.setText("Start Camera")
            self.ui.buttonDetect.setEnabled(False)
            self.ui.buttonDetect.setText("Start Detection")
            self.ui.buttonCapture.setEnabled(False)
            self.ui.buttonSaveAllDetectCam.setEnabled(False)
            self.ui.comboBoxChooseCamera.setEnabled(True)
            
    def toggle_detection(self):
        """Start or stop object detection"""
        if not self.thread:
            return
            
        if not self.thread.detecting:
            # Start detection
            if model_instance.model is None:
                QMessageBox.warning(None, "Error", "Please load the Model first!")
                return
                
            self.thread.start_detection()
            self.ui.buttonDetect.setText("Stop Detection")
            self.ui.buttonCapture.setEnabled(True)
            self.ui.buttonSaveAllDetectCam.setEnabled(False)
            self.ui.textEditCameraInfo.clear()
        else:
            # Stop detection
            self.thread.stop_detection()
            self.ui.buttonDetect.setText("Start Detection")
            self.ui.buttonCapture.setEnabled(False)
            self.ui.buttonSaveAllDetectCam.setEnabled(True)
            
    def update_camera_feed(self, frames):
        """Update camera frames in UI"""
        if not isinstance(frames, dict):
            return
            
        # Store binding box frame for later use
        self.current_frame = frames.get('binding_box')
        
        # Update both frame displays
        if 'binding_box' in frames:
            # Using ImageUtils to display image in widget
            ImageUtils.display_image_in_widget(frames['binding_box'], self.ui.frameCameraBindingBox)
            
        if 'warm_up' in frames:
            # Using ImageUtils to display image in widget
            ImageUtils.display_image_in_widget(frames['warm_up'], self.ui.frameCameraWarmUp)
    
    def handle_camera_error(self, error_msg):
        """Handle camera errors"""
        QMessageBox.warning(None, "Camera Error", error_msg)
        self.toggle_camera()  # Stop camera on error
        
    def update_detections_info(self, detections):
        """Update detection information in the text display"""
        self.ui.textEditCameraInfo.clear()
        
        # Count objects by class
        total_objects = len(detections)
        class_counts = {}
        
        for det in detections:
            class_id = det['class']
            class_counts[class_id] = class_counts.get(class_id, 0) + 1
        
        # Display summary information
        self.ui.textEditCameraInfo.append(f"Total objects: {total_objects}")
        self.ui.textEditCameraInfo.append("\nClass distribution:")
        for class_id, count in class_counts.items():
            self.ui.textEditCameraInfo.append(f"- Class {class_id}: {count} objects")
        
        # Display frame information
        if self.current_frame is not None:
            self.ui.textEditCameraInfo.append("\nFrame information:")
            self.ui.textEditCameraInfo.append(f"- Frame count: {self.thread.frame_count}")
            self.ui.textEditCameraInfo.append(f"- Size: {self.current_frame.shape[1]}x{self.current_frame.shape[0]}")

    def capture_frame(self):
        """Capture current frame and save with detection data"""
        # Get current frames and detection data
        current_frames = self.thread.get_current_frames()
        
        # Export the current frame using DataExporter
        export_result = self.data_exporter.export_single_frame(
            frames=current_frames,
            detections=current_frames.get('detections', [])
        )
        
        # Return result from DataExporter (success message is handled there)
        return export_result

    def save_all_data_detect_cam(self):
        """Save all detection data from camera session"""
        # Get all temporary data from the thread
        temp_data = self.thread.get_temp_data()
        
        # Use DataExporter to save all frames
        export_result = self.data_exporter.export_all_frames(temp_data)
        
        # If export was successful, clear temporary data
        if export_result:
            self.thread.clear_temp_data()
            
        return export_result

    @staticmethod
    def get_color_for_class(class_id):
        """Generate stable random color for each class ID"""
        # Using ImageUtils for consistent color generation
        return ImageUtils.get_color_for_class(class_id)