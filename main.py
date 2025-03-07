import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QSplashScreen
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt, QTimer

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

        app.setWindowIcon(QIcon("resources/icon.ico"))
        # Hiển thị Splash Screen
        splash_pix = QPixmap("resources/startscreen.png")
        # Scale ảnh về kích thước mong muốn (ví dụ 600x400), giữ tỉ lệ và dùng SmoothTransformation để ảnh sắc nét hơn
        scaled_pix = splash_pix.scaled(600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        splash = QSplashScreen(scaled_pix, Qt.WindowStaysOnTopHint)
        splash.show()

        # Khởi tạo cửa sổ chính sau 2 giây
        def start_main_window():
            window = MainWindow()
            window.show()
            splash.finish(window)  # Đóng splash screen khi cửa sổ chính sẵn sàng
            # Giữ tham chiếu đến cửa sổ chính để tránh bị thu gom rác
            app.main_window = window

        QTimer.singleShot(2000, start_main_window)  # Đợi 2 giây trước khi mở cửa sổ chính

        return app.exec()

    except Exception as e:
        print("Lỗi:", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
