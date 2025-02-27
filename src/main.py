from PySide6.QtWidgets import *

from views.ui import Ui_mainWindow
from controller.camera_detect import CameraDetector
from controller.picture_detect import PictureDetector
from module.model import model_instance

import sys
import logging

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
            logger.info("Initializing detectors ...")

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
                "Chọn Model",
                "",
                "Model Files (*.pt *.pth *.weights)"
            )
            
            if file_path:
                logger.info(f"Loading model from: {file_path}")
                self.ui.labelPictureDirect.setText("Đang khởi tạo model ...")

                if model_instance.load_model(file_path):
                    self.ui.labelPictureDirect.setText(file_path)

                    self.ui.buttonChoosePicture.setEnabled(True)
                    logger.info("Model loaded successfully")
                else:
                    logger.error("Failed to load model")
                    QMessageBox.warning(self, "Lỗi", "Không thể khởi tạo Model. Vui lòng chọn file khác.")
                    
        except Exception as e:
            logger.error(f"Error in model selection: {str(e)}")
            QMessageBox.warning(self, "Lỗi", f"Không thể chọn Model: {str(e)}")

def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()
        
    except Exception as e:
        logger.critical(f"Critical error in main: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())