import json
import os
from datetime import datetime
from PySide6.QtWidgets import QFileDialog, QMessageBox

class Settings:
    # Định nghĩa các hằng số cho loại lưu
    SAVE_TO_CONFIGURED_PATH = 0  # Lưu vào đường dẫn đã cài đặt sẵn
    SAVE_WITH_PROMPT = 1         # Hỏi người dùng chọn đường dẫn trước khi lưu

    def __init__(self, ui):
        self.ui = ui
        self.config_path = "configuration/.config"
        self.config_data = {}

        self.last_export_path = None
        
        # Define instance attributes
        self.save_path = ""
        self.save_prompt_type = self.SAVE_TO_CONFIGURED_PATH  # Default save prompt type
        
        # Define default configuration structure
        self.default_config = {
            "save_path": "",
            "save_prompt_type": self.SAVE_TO_CONFIGURED_PATH,
        }
        
        self.load_config()
        self.init_ui()
        self.connect_signals()
        
    def validate_config(self):
        """Kiểm tra và thêm các thuộc tính thiếu trong config"""
        config_changed = False
        
        # Kiểm tra từng thuộc tính trong default_config
        for key, default_value in self.default_config.items():
            if key not in self.config_data:
                self.config_data[key] = default_value
                config_changed = True
                print(f"Đã thêm thuộc tính thiếu '{key}' với giá trị mặc định: {default_value}")
        
        # Lưu lại nếu có thay đổi
        if config_changed:
            self.save_config()
        
    def load_config(self):
        """Đọc tệp cấu hình"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as file:
                    self.config_data = json.load(file)
                
                # Kiểm tra và thêm các thuộc tính thiếu
                self.validate_config()
                
                # Load vào instance attributes
                self.save_path = self.config_data.get("save_path", "")
                self.save_prompt_type = self.config_data.get("save_prompt_type", self.SAVE_TO_CONFIGURED_PATH)
                
                # Update UI
                self.ui.pathSaveShot.setText(self.save_path)
                self.ui.comboBoxChooseTypeSaveData.setCurrentIndex(self.save_prompt_type)
            else:
                # Tạo cấu hình mặc định nếu tệp không tồn tại
                self.save_path = ""
                self.save_prompt_type = self.SAVE_TO_CONFIGURED_PATH
                self.config_data = self.default_config.copy()
                self.save_config()
        except Exception as e:
            print(f"Lỗi khi đọc tệp cấu hình: {e}")
            self.save_path = ""
            self.save_prompt_type = self.SAVE_TO_CONFIGURED_PATH
            self.config_data = self.default_config.copy()
    
    def save_config(self):
        """Lưu cấu hình vào tệp"""
        try:
            # Đảm bảo thư mục tồn tại
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Update config_data với các giá trị hiện tại
            self.config_data["save_path"] = self.save_path
            self.config_data["save_prompt_type"] = self.save_prompt_type
            
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(self.config_data, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Lỗi khi lưu tệp cấu hình: {e}")
            QMessageBox.critical(None, "Lỗi", f"Không thể lưu cấu hình: {e}")
    
    def init_ui(self):
        """Khởi tạo UI với dữ liệu từ cấu hình"""
        # Thiết lập đường dẫn lưu
        self.ui.pathSaveShot.setText(self.save_path)
        
        # Thiết lập loại lưu
        self.ui.comboBoxChooseTypeSaveData.setCurrentIndex(self.save_prompt_type)
    
    def connect_signals(self):
        """Kết nối các tín hiệu UI với các hàm xử lý"""
        self.ui.buttonSaveShot.clicked.connect(self.select_save_path)
        self.ui.buttonSaveSettings.clicked.connect(self.save_settings)
        self.ui.comboBoxChooseTypeSaveData.currentIndexChanged.connect(self.save_prompt_type_changed)
    
    def select_save_path(self):
        """Mở hộp thoại chọn thư mục để lưu ảnh"""
        path = QFileDialog.getExistingDirectory(None, "Chọn thư mục lưu ảnh")
        if path:
            self.save_path = path
            self.ui.pathSaveShot.setText(path)
    
    def save_settings(self):
        """Lưu các thiết lập từ UI vào cấu hình"""
        # Lấy đường dẫn lưu từ UI
        self.save_path = self.ui.pathSaveShot.text()
        self.save_prompt_type = self.ui.comboBoxChooseTypeSaveData.currentIndex()
        
        # Lưu cấu hình vào tệp
        self.save_config()
        QMessageBox.information(None, "Thông báo", "Đã lưu cấu hình thành công!")
    
    def save_prompt_type_changed(self, index):
        """Xử lý khi người dùng thay đổi loại lưu"""
        self.save_prompt_type = index
    
    def get_save_path(self):
        """Trả về đường dẫn lưu hiện tại"""
        return self.save_path
    
    def get_save_prompt_type(self):
        """Trả về loại prompt lưu hiện tại"""
        return self.save_prompt_type
        
    def should_prompt_for_save_location(self):
        """Kiểm tra xem có cần hỏi người dùng chọn vị trí lưu không"""
        return self.save_prompt_type == self.SAVE_WITH_PROMPT