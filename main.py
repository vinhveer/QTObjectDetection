import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from ui import Ui_mainWindow

def main():
    # Khởi tạo ứng dụng
    app = QApplication(sys.argv)
    
    # Tạo cửa sổ chính
    mainWindow = QMainWindow()
    
    # Cài đặt giao diện người dùng
    ui = Ui_mainWindow()
    ui.setupUi(mainWindow)
    
    # Hiển thị cửa sổ
    mainWindow.show()
    
    # Chạy ứng dụng
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()