from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from choose_model import Model

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")

        self.model = Model

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

        # Start Setup Tab Camera
        self.tabCamera.setObjectName(u"tabCamera")

        # Choose Camera
        self.comboBoxChooseCamera = QComboBox(self.tabCamera)
        self.comboBoxChooseCamera.setObjectName(u"comboBoxChooseCamera")
        self.comboBoxChooseCamera.setGeometry(QRect(10, 30, 281, 22))
        self.labelChooseCamera = QLabel(self.tabCamera)
        self.labelChooseCamera.setObjectName(u"labelChooseCamera")
        self.labelChooseCamera.setGeometry(QRect(10, 10, 81, 16))
        self.labelChooseCamera.setFont(font)

        # Record Image
        self.buttonStartRecord = QPushButton(self.tabCamera)
        self.buttonStartRecord.setObjectName(u"buttonStartRecord")
        self.buttonStartRecord.setGeometry(QRect(300, 30, 131, 23))
        self.buttonStartRecord.setFont(font)

        self.frameCamera = QFrame(self.tabCamera)
        self.frameCamera.setObjectName(u"frameCamera")
        self.frameCamera.setGeometry(QRect(10, 60, 481, 251))
        self.frameCamera.setFrameShape(QFrame.StyledPanel)
        self.frameCamera.setFrameShadow(QFrame.Raised)

        # Start Detection
        self.buttonStartDetect = QPushButton(self.tabCamera)
        self.buttonStartDetect.setObjectName(u"buttonStartDetect")
        self.buttonStartDetect.setGeometry(QRect(500, 30, 111, 23))
        self.buttonStartDetect.setFont(font)

        # Statics Output Detection
        self.tableDetectCamera = QTableView(self.tabCamera)
        self.tableDetectCamera.setObjectName(u"tableDetectCamera")
        self.tableDetectCamera.setGeometry(QRect(500, 60, 231, 251))

        # Stop Detection
        self.buttonStopDetect = QPushButton(self.tabCamera)
        self.buttonStopDetect.setObjectName(u"buttonStopDetect")
        self.buttonStopDetect.setGeometry(QRect(620, 30, 111, 23))
        self.buttonStopDetect.setFont(font)

        self.tabWidget.addTab(self.tabCamera, "")
        # End Setup Tab Camera

        # Start Setup Tab Picture
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

        # Display Picture (Input and Output)
        self.framePicture = QFrame(self.tabPicture)
        self.framePicture.setObjectName(u"framePicture")
        self.framePicture.setGeometry(QRect(10, 60, 481, 251))
        self.framePicture.setFrameShape(QFrame.StyledPanel)
        self.framePicture.setFrameShadow(QFrame.Raised)

        # Statics Result
        self.tableDetectPicture = QTableView(self.tabPicture)
        self.tableDetectPicture.setObjectName(u"tableDetectPicture")
        self.tableDetectPicture.setGeometry(QRect(500, 60, 231, 251))

        # Download Image Result
        self.buttonDownloadPicture = QPushButton(self.tabPicture)
        self.buttonDownloadPicture.setObjectName(u"buttonDownloadPicture")
        self.buttonDownloadPicture.setGeometry(QRect(560, 30, 171, 23))
        self.buttonDownloadPicture.setFont(font)
        self.tabWidget.addTab(self.tabPicture, "")
        # End Setup Tab Picture

        # Choose Model
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

        # Tab Control
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
        self.buttonStartDetect.setText(QCoreApplication.translate("mainWindow", u"Bắt đầu nhận diện", None))
        self.buttonStopDetect.setText(QCoreApplication.translate("mainWindow", u"Dừng nhận diện", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCamera), QCoreApplication.translate("mainWindow", u"Nhận diện qua Camera", None))
        self.labelChoosePicture.setText(QCoreApplication.translate("mainWindow", u"Chọn hình ảnh", None))
        self.buttonChoosePicture.setText(QCoreApplication.translate("mainWindow", u"Chọn tập tin ...", None))
        self.buttonDownloadPicture.setText(QCoreApplication.translate("mainWindow", u"Tải về hình ảnh đã nhận diện", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPicture), QCoreApplication.translate("mainWindow", u"Nhận diện hình ảnh", None))
        self.labelChooseModel.setText(QCoreApplication.translate("mainWindow", u"Chọn Model", None))
        self.buttonChooseModel.setText(QCoreApplication.translate("mainWindow", u"Chọn tập tin ...", None))
        self.labelPictureDirect.setText(QCoreApplication.translate("mainWindow", u"Chưa chọn tập tin Model", None))
