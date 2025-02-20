from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
            
        mainWindow.resize(758, 439)
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(10, 60, 741, 351))
        font = QFont()
        font.setFamily(u"Segoe UI")
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.tabWidget.setFont(font)
        self.tabCamera = QWidget()

        ## Start Setup Tab Camera
        self.tabCamera.setObjectName(u"tabCamera")

        # Choose Camera
        self.comboBoxChooseCamera = QComboBox(self.tabCamera)
        self.comboBoxChooseCamera.setObjectName(u"comboBoxChooseCamera")
        self.comboBoxChooseCamera.setGeometry(QRect(10, 30, 150, 22))
        self.labelChooseCamera = QLabel(self.tabCamera)
        self.labelChooseCamera.setObjectName(u"labelChooseCamera")
        self.labelChooseCamera.setGeometry(QRect(10, 10, 81, 16))
        self.labelChooseCamera.setFont(font)

        # Record Image
        self.buttonStartRecord = QPushButton(self.tabCamera)
        self.buttonStartRecord.setObjectName(u"buttonStartRecord")
        self.buttonStartRecord.setGeometry(QRect(170, 30, 131, 23))
        self.buttonStartRecord.setFont(font)

        # Capture Frame
        self.buttonCapture = QPushButton(self.tabCamera)
        self.buttonCapture.setObjectName(u"buttonCapture")
        self.buttonCapture.setGeometry(QRect(310, 30, 120, 23))
        self.buttonCapture.setFont(font)

        self.frameCamera = QLabel(self.tabCamera)
        self.frameCamera.setObjectName(u"frameCamera")
        self.frameCamera.setGeometry(QRect(10, 60, 481, 251))
        self.frameCamera.setStyleSheet("border: 1px solid gray;")  # Thêm viền đen
        self.frameCamera.setAlignment(Qt.AlignCenter)

        # Display Detect Information
        self.text_edit_camera_info = QTextEdit(self.tabCamera)
        self.text_edit_camera_info.setGeometry(QRect(500, 60, 231, 221))
        self.text_edit_camera_info.setReadOnly(True)

        # Start Detect
        self.buttonDetect = QPushButton(self.tabCamera)
        self.buttonDetect.setObjectName(u"buttonDetect")
        self.buttonDetect.setGeometry(QRect(620, 30, 111, 23))
        self.buttonDetect.setFont(font)

        # Save All Data
        self.buttonSaveAllDetectCam = QPushButton(self.tabCamera)
        self.buttonSaveAllDetectCam.setObjectName(u"buttonSaveAllDetectCam")
        self.buttonSaveAllDetectCam.setGeometry(QRect(500, 290, 231, 23))

        self.tabWidget.addTab(self.tabCamera, "")
        ## End Setup Tab Camera

        ## Start Setup Tab Picture
        self.tabPicture = QWidget()
        self.tabPicture.setObjectName(u"tabPicture")

        # Choose Picture
        self.labelChoosePicture = QLabel(self.tabPicture)
        self.labelChoosePicture.setObjectName(u"labelChoosePicture")
        self.labelChoosePicture.setGeometry(QRect(10, 10, 81, 16))
        self.labelChoosePicture.setFont(font)
        self.buttonChoosePicture = QPushButton(self.tabPicture)
        self.buttonChoosePicture.setObjectName(u"buttonChoosePicture")
        self.buttonChoosePicture.setGeometry(QRect(10, 30, 91, 23))
        self.buttonChoosePicture.setFont(font)

        # Progress Bar when Detecting
        self.progress_bar = QProgressBar(self.tabPicture)
        self.progress_bar.setGeometry(QRect(110, 30, 200, 23))
        self.progress_bar.hide()

        # Display Picture (Input and Output)
        self.framePicture = QLabel(self.tabPicture)
        self.framePicture.setObjectName(u"framePicture")
        self.framePicture.setGeometry(QRect(10, 60, 481, 251))
        self.framePicture.setScaledContents(True)
        self.framePicture.setScaledContents(False)
        self.framePicture.setAlignment(Qt.AlignCenter)
        self.framePicture.setStyleSheet("border: 1px solid gray;")
        self.framePicture.setAlignment(Qt.AlignCenter)

        # Display Output Information
        self.text_edit_info = QTextEdit(self.tabPicture)
        self.text_edit_info.setGeometry(QRect(500, 60, 231, 251))
        self.text_edit_info.setReadOnly(True)

        # Download Data Result
        self.buttonSaveDataDetectImg = QPushButton(self.tabPicture)
        self.buttonSaveDataDetectImg.setObjectName(u"buttonSaveDataDetectImg")
        self.buttonSaveDataDetectImg.setGeometry(QRect(410, 30, 141, 23))

        # Download Image Result
        self.buttonDownloadPicture = QPushButton(self.tabPicture)
        self.buttonDownloadPicture.setObjectName(u"buttonDownloadPicture")
        self.buttonDownloadPicture.setGeometry(QRect(560, 30, 171, 23))
        self.buttonDownloadPicture.setFont(font)
        self.tabWidget.addTab(self.tabPicture, "")
        ## End Setup Tab Picture

        ## Choose Model
        self.labelChooseModel = QLabel(self.centralwidget)
        self.labelChooseModel.setObjectName(u"labelChooseModel")
        self.labelChooseModel.setGeometry(QRect(10, 10, 81, 16))
        self.labelChooseModel.setFont(font)
        self.buttonChooseModel = QPushButton(self.centralwidget)
        self.buttonChooseModel.setObjectName(u"buttonChooseModel")
        self.buttonChooseModel.setGeometry(QRect(10, 30, 91, 23))
        self.buttonChooseModel.setFont(font)
        self.labelPictureDirect = QLabel(self.centralwidget)
        self.labelPictureDirect.setObjectName(u"labelPictureDirect")
        self.labelPictureDirect.setGeometry(QRect(110, 30, 421, 21))
        self.labelPictureDirect.setFont(font)

        ## Tab Control
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(mainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 758, 21))
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName(u"statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)

        self.tabWidget.setCurrentIndex(1)
        QMetaObject.connectSlotsByName(mainWindow)

    # Set Text and Title
    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"Object Detection with YOLO", None))
        self.labelChooseCamera.setText(QCoreApplication.translate("mainWindow", u"Chọn Camera", None))
        self.buttonStartRecord.setText(QCoreApplication.translate("mainWindow", u"Bắt đầu nhận hình ảnh", None))
        self.buttonCapture.setText(QCoreApplication.translate("mainWindow", u"Chụp lại khung hình", None))
        self.buttonDetect.setText(QCoreApplication.translate("mainWindow", u"Bắt đầu nhận diện", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCamera), QCoreApplication.translate("mainWindow", u"Nhận diện qua Camera", None))
        self.labelChoosePicture.setText(QCoreApplication.translate("mainWindow", u"Chọn hình ảnh", None))
        self.buttonChoosePicture.setText(QCoreApplication.translate("mainWindow", u"Chọn tập tin ...", None))
        self.buttonDownloadPicture.setText(QCoreApplication.translate("mainWindow", u"Tải về hình ảnh đã nhận diện", None))
        self.buttonSaveDataDetectImg.setText(QCoreApplication.translate("mainWindow", u"Lưu dữ liệu nhận diện", None))
        self.buttonSaveAllDetectCam.setText(QCoreApplication.translate("mainWindow", u"Lưu toàn bộ hình ảnh và dữ liệu nhận diện", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPicture), QCoreApplication.translate("mainWindow", u"Nhận diện hình ảnh", None))
        self.labelChooseModel.setText(QCoreApplication.translate("mainWindow", u"Chọn Model", None))
        self.buttonChooseModel.setText(QCoreApplication.translate("mainWindow", u"Chọn tập tin ...", None))
        self.labelPictureDirect.setText(QCoreApplication.translate("mainWindow", u"Chưa chọn tập tin Model", None))