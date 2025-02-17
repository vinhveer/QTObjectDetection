from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui import Ui_mainWindow
from camera_detect import CameraDetector
from picture_detect import PictureDetector
from model import model_instance

import sys
import os
import platform
import logging
import ctypes

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.ui = Ui_mainWindow()
            self.ui.setupUi(self)
            
            # Initialize detectors
            logger.info("Initializing detectors...")
            self.camera_detector = CameraDetector(self.ui)
            self.picture_detector = PictureDetector(self.ui)
            
            # Connect model selection button
            self.ui.buttonChooseModel.clicked.connect(self.select_model)
            logger.info("MainWindow initialization complete")
            
        except Exception as e:
            logger.error(f"Error initializing MainWindow: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to initialize application: {str(e)}")
        
    def select_model(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select YOLO Model",
                "",
                "Model Files (*.pt *.pth *.weights)"
            )
            if file_path:
                logger.info(f"Loading model from: {file_path}")
                self.ui.labelPictureDirect.setText("Đang khởi tạo model ...")

                if model_instance.load_model(file_path):
                    self.ui.labelPictureDirect.setText(file_path)
                    self.ui.buttonStartDetect.setEnabled(True)
                    logger.info("Model loaded successfully")
                else:
                    logger.error("Failed to load model")
                    QMessageBox.warning(self, "Error", "Failed to load model")
                    
        except Exception as e:
            logger.error(f"Error in model selection: {str(e)}")
            QMessageBox.warning(self, "Error", f"Error selecting model: {str(e)}")

def main():
    try:
        # Enable high DPI scaling on Windows
        if platform.system() == 'Windows':
            os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

            current_dpi = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100.0
            if (current_dpi == 1):
                os.environ["QT_SCALE_FACTOR"] = "1.75"
            elif (current_dpi == 1.25):
                os.environ["QT_SCALE_FACTOR"] = "1.75"
                os.environ["QT_FONT_DPI"] = "96"

        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec_()
        
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())