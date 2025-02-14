from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui import Ui_mainWindow
from camera_detect import CameraDetector
from picture_detect import PictureDetector

import sys, os, platform

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Khởi tạo các detector và truyền UI vào
        self.camera_detector = CameraDetector(self.ui)
        self.picture_detector = PictureDetector(self.ui)
        
        # Chỉ xử lý sự kiện chọn model ở main
        self.ui.buttonChooseModel.clicked.connect(self.select_model)
        
    def select_model(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select YOLO Model",
            "",
            "Model Files (*.pt *.pth *.weights)"
        )
        if file_path:
            # Gửi model cho cả hai detector
            self.camera_detector.set_model(file_path)
            self.picture_detector.set_model(file_path)
            self.ui.labelPictureDirect.setText(file_path)

if __name__ == "__main__":
    # Xử lý High DPI scaling cho Windows
    if platform.system() == 'Windows':
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())