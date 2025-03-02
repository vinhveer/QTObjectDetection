from PySide6.QtWidgets import QDialog, QVBoxLayout, QProgressBar
from PySide6.QtCore import Qt

class ProcessDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Thiết lập cửa sổ dialog
        self.setWindowTitle("Đang nhận diện")
        self.setModal(True)  # Modal dialog - không thể tương tác với cửa sổ chính
        self.setWindowFlags(
            Qt.Dialog | 
            Qt.CustomizeWindowHint | 
            Qt.WindowTitleHint  # Chỉ hiện tiêu đề, không có nút đóng
        )
        
        # Tạo layout
        layout = QVBoxLayout(self)
        
        # Tạo progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Chế độ không xác định
        self.progress_bar.setTextVisible(False)  # Ẩn phần trăm
        
        # Thêm vào layout
        layout.addWidget(self.progress_bar)
        
        # Thiết lập kích thước
        self.setFixedSize(300, 50)  # Kích thước cố định
        
    def closeEvent(self, event):
        # Ngăn không cho đóng dialog
        event.ignore()