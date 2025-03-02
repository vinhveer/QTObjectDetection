import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox

from views.ui import Ui_mainWindow
from controller.camera_detect import CameraDetector
from controller.picture_detect import PictureDetector
from controller.multiple_picture_detect import MultiplePictureDetector
from controller.settings import Settings
from module.model import model_instance


class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.ui = Ui_mainWindow()
            self.ui.setupUi(self)

            self.settings = Settings(self.ui)

            self.camera_detector = CameraDetector(self.ui, settings=self.settings)
            self.picture_detector = PictureDetector(self.ui, settings=self.settings)
            self.multiple_picture_detector = MultiplePictureDetector(self.ui, settings=self.settings)

            print(self.settings.save_prompt_type)
            
            # Connect model selection button
            self.ui.buttonChooseModel.clicked.connect(self.select_model)
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể khởi tạo ứng dụng: {str(e)}")
        
    def select_model(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Chọn Model",
                "",
                "Tập tin Model (*.pt *.pth *.weights)"
            )
            
            if file_path:
                self.ui.statusbar.showMessage(f"Đang tải Model từ: {file_path}")
                self.ui.labelPictureDirect.setText("Đang khởi tạo model ...")

                if model_instance.load_model(file_path):
                    self.ui.labelPictureDirect.setText(file_path)

                    self.ui.buttonChoosePicture.setEnabled(True)
                    self.ui.statusbar.showMessage("Model đã được khởi tạo")
                else:
                    self.ui.statusbar.showMessage("Model không được khởi tạo thành công. Vui lòng chọn file khác.")
                    QMessageBox.warning(self, "Lỗi", "Không thể khởi tạo Model. Vui lòng chọn file khác.")
                    
        except Exception as e:
            QMessageBox.warning(self, "Lỗi", f"Không thể chọn Model: {str(e)}")

def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        return app.exec()
        
    except Exception as e:
        return 1

if __name__ == "__main__":
    sys.exit(main())