from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import cv2, time, sys, os, tempfile, json, shutil, datetime
import numpy as np
import pandas as pd
from model import model_instance
from datetime import datetime

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
        # Tùy chỉnh frame hiển thị ảnh
        self.ui.frameCamera.setScaledContents(False)
        self.ui.frameCamera.setAlignment(Qt.AlignCenter)
        
        # Thiết lập trạng thái ban đầu
        self.ui.buttonStopDetect.setEnabled(False)
        self.ui.buttonStartDetect.setEnabled(False)
        self.ui.buttonCapture.setEnabled(False)
        self.ui.buttonSaveAllDetectCam.setEnabled(False)
   
    def setup_ui_connections(self):
        """Thiết lập các kết nối signals/slots"""
        self.ui.buttonStartRecord.clicked.connect(self.toggle_camera)
        self.ui.buttonStartDetect.clicked.connect(self.start_detection)
        self.ui.buttonStopDetect.clicked.connect(self.stop_detection)
        self.ui.buttonCapture.clicked.connect(self.capture_frame)
        self.ui.buttonSaveAllDetectCam.clicked.connect(self.save_all_data_detect_cam)
        
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
            self.ui.buttonSaveAllDetectCam.setEnabled(False)
            self.ui.buttonCapture.setEnabled(True)
            self.ui.text_edit_camera_info.clear()  # Xóa thông tin detection cũ
        else:
            QMessageBox.warning(None, "Lỗi", "Vui lòng tải Model trước!")
            
    def stop_detection(self):
        """Dừng nhận diện đối tượng"""
        if self.thread:
            self.thread.stop_detection()
            self.ui.buttonStartDetect.setEnabled(True)
            self.ui.buttonStopDetect.setEnabled(False)
            self.ui.buttonCapture.setEnabled(False)
            self.ui.buttonSaveAllDetectCam.setEnabled(True)
            
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
        self.ui.text_edit_camera_info.clear()
        
        # Thêm thông tin tổng quan
        total_objects = len(detections)
        class_counts = {}
        
        for det in detections:
            class_id = det['class']
            class_counts[class_id] = class_counts.get(class_id, 0) + 1
        
        # Hiển thị tổng quan
        self.ui.text_edit_camera_info.append("=== TỔNG QUAN ===")
        self.ui.text_edit_camera_info.append(f"Tổng số đối tượng: {total_objects}")
        self.ui.text_edit_camera_info.append("\nPhân bố các lớp:")
        for class_id, count in class_counts.items():
            self.ui.text_edit_camera_info.append(f"- Class {class_id}: {count} đối tượng")
        
        # Hiển thị chi tiết từng đối tượng
        self.ui.text_edit_camera_info.append("\n=== CHI TIẾT ===")
        for i, det in enumerate(detections, 1):
            info = (f"\nĐối tượng {i}:"
                   f"\n- Lớp: {det['class']}"
                   f"\n- Độ tin cậy: {det['confidence']:.2f}"
                   f"\n- Vị trí: {det['bbox']}")
            self.ui.text_edit_camera_info.append(info)

    def save_all_data_detect_cam(self):
        # Kiểm tra dữ liệu
        temp_data = self.thread.get_temp_data()
        if not temp_data['detections']:
            QMessageBox.warning(None, "Lỗi", "Không có dữ liệu detection để lưu!")
            return

        # Cho người dùng chọn thư mục gốc để lưu
        root_dir = QFileDialog.getExistingDirectory(
            None,
            "Chọn thư mục để lưu dữ liệu",
            "",
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not root_dir:  # Người dùng đã hủy
            return

        try:
            # Tạo progress dialog
            progress = QProgressDialog("Đang lưu dữ liệu...", "Hủy", 0, len(temp_data['images']), None)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle("Tiến trình lưu")
            progress.setMinimumDuration(0)
            
            # Tạo các thư mục con
            subdirs = [
                'images/original',
                'images/detected',
                'data_excel',
                'data_json'
            ]
            for subdir in subdirs:
                full_path = os.path.join(root_dir, subdir)
                os.makedirs(full_path, exist_ok=True)

            # Xử lý từng frame
            for i, frame_info in enumerate(temp_data['images']):
                if progress.wasCanceled():
                    break
                    
                progress.setValue(i)
                progress.setLabelText(f"Đang lưu frame {i+1}/{len(temp_data['images'])}...")
                
                # ... existing save operations ...
                timestamp = frame_info['timestamp']
                original_path = frame_info['original_path']
                detected_path = frame_info['detected_path']
                detections = frame_info['detections']
                
                base_filename = f"detection_{timestamp}"
                
                # Copy files and save data
                original_dest = os.path.join(root_dir, 'images/original', f"{base_filename}.jpg")
                shutil.copy2(original_path, original_dest)
                
                detected_dest = os.path.join(root_dir, 'images/detected', f"{base_filename}.jpg")
                shutil.copy2(detected_path, detected_dest)
                
                # Save JSON
                json_path = os.path.join(root_dir, 'data_json', f"{base_filename}.json")
                json_data = {
                    'timestamp': timestamp,
                    'original_image': f"images/original/{base_filename}.jpg",
                    'detected_image': f"images/detected/{base_filename}.jpg",
                    'detections': detections
                }
                with open(json_path, 'w') as f:
                    json.dump(json_data, f, indent=4)
                
                # Save Excel
                excel_path = os.path.join(root_dir, 'data_excel', f"{base_filename}.xlsx")
                
                # Create DataFrames
                df_class = pd.DataFrame(columns=['Class', 'Count'])
                df_detail = pd.DataFrame(columns=[
                    'Class', 
                    'Confidence', 
                    'Top', 
                    'Left', 
                    'Bottom', 
                    'Right', 
                    'Width', 
                    'Height'
                ])
                
                # Process detection data
                class_counts = {}
                for det in detections:
                    class_name = det['class']
                    confidence = det['confidence']
                    bbox = det['bbox']
                    
                    top, left = bbox[1], bbox[0]
                    bottom, right = bbox[3], bbox[2]
                    width = right - left
                    height = bottom - top
                    
                    df_detail.loc[len(df_detail)] = [
                        class_name, 
                        confidence, 
                        top, 
                        left, 
                        bottom, 
                        right, 
                        width, 
                        height
                    ]
                    
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
                
                for class_name, count in class_counts.items():
                    df_class.loc[len(df_class)] = [class_name, count]
                
                with pd.ExcelWriter(excel_path) as writer:
                    df_class.to_excel(writer, sheet_name='Class Summary', index=False)
                    df_detail.to_excel(writer, sheet_name='Detection Details', index=False)

            progress.setValue(len(temp_data['images']))
            
            if not progress.wasCanceled():
                QMessageBox.information(None, "Thành công", 
                    f"Đã lưu tất cả dữ liệu vào thư mục:\n{root_dir}")
                self.thread.clear_temp_data()
                
        except Exception as e:
            QMessageBox.critical(None, "Lỗi", f"Lỗi khi lưu dữ liệu: {str(e)}")
        
        return
            
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
        # Thêm các thuộc tính mới để lưu trữ tạm thời
        self.temp_images = []  # Lưu các ảnh
        self.temp_detections = []  # Lưu kết quả detection
        self.temp_dir = tempfile.mkdtemp()  # Tạo thư mục tạm
        
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
                frame_to_display = frame.copy()
                
                if self.detecting and model_instance.model is not None:
                    try:
                        # Thực hiện detection
                        detections = model_instance.detect(frame)
                        if detections:
                            # Draw detections on the display frame
                            frame_to_display = self.draw_detections(frame_to_display, detections)
                            self.detection_signal.emit(detections)
                            # Lưu frame gốc và detection vào bộ nhớ tạm
                            self.save_temp_frame(frame, detections)
                    except Exception as e:
                        print(f"Detection error: {str(e)}")
                
                # Gửi frame đã vẽ detection đến UI
                self.frame_signal.emit(frame_to_display)
            else:
                self.error_signal.emit("Lỗi khi đọc frame từ camera")
                break
                
            time.sleep(1/30)  # Giới hạn fps

        cap.release()

    def save_temp_frame(self, frame, detections):
        """Lưu frame và detection vào bộ nhớ tạm"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Lưu frame gốc vào thư mục tạm
        temp_original_path = os.path.join(self.temp_dir, f"frame_original_{timestamp}.jpg")
        cv2.imwrite(temp_original_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        
        # Tạo và lưu frame đã detect
        frame_with_detection = self.draw_detections(frame.copy(), detections)
        temp_detected_path = os.path.join(self.temp_dir, f"frame_detected_{timestamp}.jpg")
        cv2.imwrite(temp_detected_path, cv2.cvtColor(frame_with_detection, cv2.COLOR_RGB2BGR))
        
        # Lưu thông tin
        frame_info = {
            'timestamp': timestamp,
            'original_path': temp_original_path,
            'detected_path': temp_detected_path,
            'detections': detections
        }
        
        self.temp_images.append(frame_info)
        self.temp_detections.append(detections)

    def get_temp_data(self):
        """Trả về dữ liệu tạm thời"""
        return {
            'images': self.temp_images,
            'detections': self.temp_detections
        }

    def clear_temp_data(self):
        """Xóa tất cả dữ liệu tạm thời"""
        # Xóa các file ảnh
        for frame_info in self.temp_images:
            try:
                os.remove(frame_info['image_path'])
            except:
                pass
        
        # Xóa thư mục tạm
        try:
            shutil.rmtree(self.temp_dir)
        except:
            pass
        
        # Reset danh sách
        self.temp_images = []
        self.temp_detections = []
        
    def __del__(self):
        """Destructor để đảm bảo xóa dữ liệu tạm khi object bị hủy"""
        self.clear_temp_data()
        
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
            bbox = det['bbox']
            x1, y1, x2, y2 = map(int, bbox)  # Convert coordinates to integers
            confidence = det['confidence']
            class_id = det['class']
            
            # Lấy màu cho class
            color = self.get_color_for_class(class_id)
            
            # Vẽ bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Chuẩn bị text
            label = f"Class {class_id} ({confidence:.2f})"
            
            # Vẽ background cho text
            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
            cv2.rectangle(frame, 
                        (x1, y1 - text_height - 10), 
                        (x1 + text_width + 10, y1),
                        color, -1)
            
            # Vẽ text
            cv2.putText(frame, label,
                      (x1 + 5, y1 - 5),
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                      (255, 255, 255), 2)
            
        return frame
        
    @staticmethod
    def get_color_for_class(class_id):
        """Tạo màu ngẫu nhiên nhưng ổn định cho mỗi class"""
        np.random.seed(class_id)
        return tuple(map(int, np.random.randint(0, 255, 3)))