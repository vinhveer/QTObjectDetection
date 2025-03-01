# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainbhFLRx.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QProgressBar, QPushButton, QSizePolicy,
    QSpacerItem, QStatusBar, QTabWidget, QTextEdit,
    QVBoxLayout, QWidget)

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        mainWindow.resize(974, 543)
        mainWindow.setMinimumSize(QSize(800, 400))
        font = QFont()
        font.setPointSize(9)
        mainWindow.setFont(font)
        self.centralwidget = QWidget(mainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setSpacing(10)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.modelGroup = QWidget(self.centralwidget)
        self.modelGroup.setObjectName(u"modelGroup")
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(9)
        self.modelGroup.setFont(font1)
        self.model_layout = QHBoxLayout(self.modelGroup)
        self.model_layout.setObjectName(u"model_layout")
        self.model_layout.setContentsMargins(0, 0, 0, 0)
        self.buttonChooseModel = QPushButton(self.modelGroup)
        self.buttonChooseModel.setObjectName(u"buttonChooseModel")
        self.buttonChooseModel.setMinimumSize(QSize(150, 0))

        self.model_layout.addWidget(self.buttonChooseModel)

        self.labelPictureDirect = QLabel(self.modelGroup)
        self.labelPictureDirect.setObjectName(u"labelPictureDirect")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelPictureDirect.sizePolicy().hasHeightForWidth())
        self.labelPictureDirect.setSizePolicy(sizePolicy)

        self.model_layout.addWidget(self.labelPictureDirect)


        self.main_layout.addWidget(self.modelGroup)

        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setFont(font1)
        self.tabCamera = QWidget()
        self.tabCamera.setObjectName(u"tabCamera")
        self.gridLayout_7 = QGridLayout(self.tabCamera)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.CameraControls = QHBoxLayout()
        self.CameraControls.setSpacing(10)
        self.CameraControls.setObjectName(u"CameraControls")
        self.CameraSelection = QHBoxLayout()
        self.CameraSelection.setObjectName(u"CameraSelection")
        self.labelChooseCamera = QLabel(self.tabCamera)
        self.labelChooseCamera.setObjectName(u"labelChooseCamera")
        self.labelChooseCamera.setFont(font1)

        self.CameraSelection.addWidget(self.labelChooseCamera)

        self.comboBoxChooseCamera = QComboBox(self.tabCamera)
        self.comboBoxChooseCamera.setObjectName(u"comboBoxChooseCamera")
        self.comboBoxChooseCamera.setMinimumSize(QSize(180, 0))

        self.CameraSelection.addWidget(self.comboBoxChooseCamera)


        self.CameraControls.addLayout(self.CameraSelection)

        self.horizontalSpacer = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)

        self.CameraControls.addItem(self.horizontalSpacer)

        self.buttonStartRecord = QPushButton(self.tabCamera)
        self.buttonStartRecord.setObjectName(u"buttonStartRecord")
        self.buttonStartRecord.setMinimumSize(QSize(150, 0))

        self.CameraControls.addWidget(self.buttonStartRecord)

        self.buttonCapture = QPushButton(self.tabCamera)
        self.buttonCapture.setObjectName(u"buttonCapture")
        self.buttonCapture.setMinimumSize(QSize(150, 0))

        self.CameraControls.addWidget(self.buttonCapture)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.CameraControls.addItem(self.horizontalSpacer_2)

        self.buttonDetect = QPushButton(self.tabCamera)
        self.buttonDetect.setObjectName(u"buttonDetect")
        self.buttonDetect.setMinimumSize(QSize(140, 0))

        self.CameraControls.addWidget(self.buttonDetect)

        self.buttonSaveAllDetectCam = QPushButton(self.tabCamera)
        self.buttonSaveAllDetectCam.setObjectName(u"buttonSaveAllDetectCam")
        self.buttonSaveAllDetectCam.setMinimumSize(QSize(150, 0))

        self.CameraControls.addWidget(self.buttonSaveAllDetectCam)


        self.gridLayout_7.addLayout(self.CameraControls, 0, 0, 1, 1)

        self.tabWidgetCamera = QTabWidget(self.tabCamera)
        self.tabWidgetCamera.setObjectName(u"tabWidgetCamera")
        self.tabBindingBoxCamera = QWidget()
        self.tabBindingBoxCamera.setObjectName(u"tabBindingBoxCamera")
        self.gridLayout_5 = QGridLayout(self.tabBindingBoxCamera)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.frameCameraBindingBox = QLabel(self.tabBindingBoxCamera)
        self.frameCameraBindingBox.setObjectName(u"frameCameraBindingBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(2)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.frameCameraBindingBox.sizePolicy().hasHeightForWidth())
        self.frameCameraBindingBox.setSizePolicy(sizePolicy1)
        self.frameCameraBindingBox.setMinimumSize(QSize(480, 100))
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(9)
        font2.setBold(True)
        self.frameCameraBindingBox.setFont(font2)
        self.frameCameraBindingBox.setStyleSheet(u"")
        self.frameCameraBindingBox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_5.addWidget(self.frameCameraBindingBox, 0, 0, 1, 1)

        self.tabWidgetCamera.addTab(self.tabBindingBoxCamera, "")
        self.tabWarmUpCamera = QWidget()
        self.tabWarmUpCamera.setObjectName(u"tabWarmUpCamera")
        self.gridLayout_8 = QGridLayout(self.tabWarmUpCamera)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.frameCameraWarmUp = QLabel(self.tabWarmUpCamera)
        self.frameCameraWarmUp.setObjectName(u"frameCameraWarmUp")
        sizePolicy1.setHeightForWidth(self.frameCameraWarmUp.sizePolicy().hasHeightForWidth())
        self.frameCameraWarmUp.setSizePolicy(sizePolicy1)
        self.frameCameraWarmUp.setMinimumSize(QSize(480, 100))
        self.frameCameraWarmUp.setFont(font2)
        self.frameCameraWarmUp.setStyleSheet(u"")
        self.frameCameraWarmUp.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_8.addWidget(self.frameCameraWarmUp, 0, 0, 1, 1)

        self.tabWidgetCamera.addTab(self.tabWarmUpCamera, "")
        self.tabStatusCamera = QWidget()
        self.tabStatusCamera.setObjectName(u"tabStatusCamera")
        self.gridLayout_6 = QGridLayout(self.tabStatusCamera)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.textEditCameraInfo = QTextEdit(self.tabStatusCamera)
        self.textEditCameraInfo.setObjectName(u"textEditCameraInfo")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(1)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.textEditCameraInfo.sizePolicy().hasHeightForWidth())
        self.textEditCameraInfo.setSizePolicy(sizePolicy2)
        self.textEditCameraInfo.setMinimumSize(QSize(250, 0))
        self.textEditCameraInfo.setReadOnly(True)

        self.gridLayout_6.addWidget(self.textEditCameraInfo, 0, 0, 1, 1)

        self.tabWidgetCamera.addTab(self.tabStatusCamera, "")

        self.gridLayout_7.addWidget(self.tabWidgetCamera, 1, 0, 1, 1)

        self.tabWidget.addTab(self.tabCamera, "")
        self.tabPicture = QWidget()
        self.tabPicture.setObjectName(u"tabPicture")
        self.gridLayout_4 = QGridLayout(self.tabPicture)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.pictureControls = QHBoxLayout()
        self.pictureControls.setSpacing(10)
        self.pictureControls.setObjectName(u"pictureControls")
        self.pictureSelection = QHBoxLayout()
        self.pictureSelection.setObjectName(u"pictureSelection")
        self.buttonChoosePicture = QPushButton(self.tabPicture)
        self.buttonChoosePicture.setObjectName(u"buttonChoosePicture")
        self.buttonChoosePicture.setMinimumSize(QSize(180, 0))

        self.pictureSelection.addWidget(self.buttonChoosePicture)


        self.pictureControls.addLayout(self.pictureSelection)

        self.processBarPicture = QProgressBar(self.tabPicture)
        self.processBarPicture.setObjectName(u"processBarPicture")
        self.processBarPicture.setVisible(False)

        self.pictureControls.addWidget(self.processBarPicture)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.pictureControls.addItem(self.horizontalSpacer_3)

        self.buttonSaveDataDetectImg = QPushButton(self.tabPicture)
        self.buttonSaveDataDetectImg.setObjectName(u"buttonSaveDataDetectImg")
        self.buttonSaveDataDetectImg.setMinimumSize(QSize(180, 0))

        self.pictureControls.addWidget(self.buttonSaveDataDetectImg)

        self.buttonDownloadPictureBindingBox = QPushButton(self.tabPicture)
        self.buttonDownloadPictureBindingBox.setObjectName(u"buttonDownloadPictureBindingBox")
        self.buttonDownloadPictureBindingBox.setMinimumSize(QSize(180, 0))

        self.pictureControls.addWidget(self.buttonDownloadPictureBindingBox)

        self.buttonDownloadPictureWarmUp = QPushButton(self.tabPicture)
        self.buttonDownloadPictureWarmUp.setObjectName(u"buttonDownloadPictureWarmUp")
        self.buttonDownloadPictureWarmUp.setMinimumSize(QSize(180, 0))

        self.pictureControls.addWidget(self.buttonDownloadPictureWarmUp)


        self.gridLayout_4.addLayout(self.pictureControls, 0, 0, 1, 1)

        self.tabWidgetPicture = QTabWidget(self.tabPicture)
        self.tabWidgetPicture.setObjectName(u"tabWidgetPicture")
        self.tabImageBindingBox = QWidget()
        self.tabImageBindingBox.setObjectName(u"tabImageBindingBox")
        self.gridLayout_2 = QGridLayout(self.tabImageBindingBox)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.framePictureBindingBox = QLabel(self.tabImageBindingBox)
        self.framePictureBindingBox.setObjectName(u"framePictureBindingBox")
        self.framePictureBindingBox.setFont(font2)
        self.framePictureBindingBox.setStyleSheet(u"")
        self.framePictureBindingBox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_2.addWidget(self.framePictureBindingBox, 0, 0, 1, 1)

        self.tabWidgetPicture.addTab(self.tabImageBindingBox, "")
        self.tabPictureWarmUp = QWidget()
        self.tabPictureWarmUp.setObjectName(u"tabPictureWarmUp")
        self.gridLayout = QGridLayout(self.tabPictureWarmUp)
        self.gridLayout.setObjectName(u"gridLayout")
        self.framePictureWarmUp = QLabel(self.tabPictureWarmUp)
        self.framePictureWarmUp.setObjectName(u"framePictureWarmUp")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(1)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.framePictureWarmUp.sizePolicy().hasHeightForWidth())
        self.framePictureWarmUp.setSizePolicy(sizePolicy3)
        self.framePictureWarmUp.setMinimumSize(QSize(0, 0))
        self.framePictureWarmUp.setFont(font2)
        self.framePictureWarmUp.setStyleSheet(u"")
        self.framePictureWarmUp.setScaledContents(False)
        self.framePictureWarmUp.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout.addWidget(self.framePictureWarmUp, 0, 0, 1, 1)

        self.tabWidgetPicture.addTab(self.tabPictureWarmUp, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.gridLayout_3 = QGridLayout(self.tab)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.textEditStatusPicture = QTextEdit(self.tab)
        self.textEditStatusPicture.setObjectName(u"textEditStatusPicture")
        sizePolicy2.setHeightForWidth(self.textEditStatusPicture.sizePolicy().hasHeightForWidth())
        self.textEditStatusPicture.setSizePolicy(sizePolicy2)
        self.textEditStatusPicture.setMinimumSize(QSize(250, 0))
        self.textEditStatusPicture.setReadOnly(True)

        self.gridLayout_3.addWidget(self.textEditStatusPicture, 0, 0, 1, 1)

        self.tabWidgetPicture.addTab(self.tab, "")

        self.gridLayout_4.addWidget(self.tabWidgetPicture, 1, 0, 1, 1)

        self.tabWidget.addTab(self.tabPicture, "")
        self.tabMultiImage = QWidget()
        self.tabMultiImage.setObjectName(u"tabMultiImage")
        self.gridLayout_12 = QGridLayout(self.tabMultiImage)
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.folderControls = QHBoxLayout()
        self.folderControls.setSpacing(10)
        self.folderControls.setObjectName(u"folderControls")
        self.folderSelection = QHBoxLayout()
        self.folderSelection.setObjectName(u"folderSelection")
        self.buttonChooseFolder = QPushButton(self.tabMultiImage)
        self.buttonChooseFolder.setObjectName(u"buttonChooseFolder")
        self.buttonChooseFolder.setMinimumSize(QSize(120, 0))

        self.folderSelection.addWidget(self.buttonChooseFolder)


        self.folderControls.addLayout(self.folderSelection)

        self.multiProcessBar = QProgressBar(self.tabMultiImage)
        self.multiProcessBar.setObjectName(u"multiProcessBar")
        self.multiProcessBar.setVisible(False)

        self.folderControls.addWidget(self.multiProcessBar)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.folderControls.addItem(self.horizontalSpacer_4)

        self.buttonSaveDataDetectMulti = QPushButton(self.tabMultiImage)
        self.buttonSaveDataDetectMulti.setObjectName(u"buttonSaveDataDetectMulti")
        self.buttonSaveDataDetectMulti.setMinimumSize(QSize(230, 0))

        self.folderControls.addWidget(self.buttonSaveDataDetectMulti)

        self.buttonDownloadMultiPicture = QPushButton(self.tabMultiImage)
        self.buttonDownloadMultiPicture.setObjectName(u"buttonDownloadMultiPicture")
        self.buttonDownloadMultiPicture.setMinimumSize(QSize(250, 0))

        self.folderControls.addWidget(self.buttonDownloadMultiPicture)


        self.gridLayout_12.addLayout(self.folderControls, 0, 0, 1, 2)

        self.listImage = QListWidget(self.tabMultiImage)
        self.listImage.setObjectName(u"listImage")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.listImage.sizePolicy().hasHeightForWidth())
        self.listImage.setSizePolicy(sizePolicy4)
        self.listImage.setMinimumSize(QSize(150, 0))

        self.gridLayout_12.addWidget(self.listImage, 1, 0, 1, 1)

        self.tabWidgetResultFolder = QTabWidget(self.tabMultiImage)
        self.tabWidgetResultFolder.setObjectName(u"tabWidgetResultFolder")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.tabWidgetResultFolder.sizePolicy().hasHeightForWidth())
        self.tabWidgetResultFolder.setSizePolicy(sizePolicy5)
        self.tabResultBindingBox = QWidget()
        self.tabResultBindingBox.setObjectName(u"tabResultBindingBox")
        self.gridLayout_10 = QGridLayout(self.tabResultBindingBox)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.frameFolderBindingBox = QLabel(self.tabResultBindingBox)
        self.frameFolderBindingBox.setObjectName(u"frameFolderBindingBox")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy6.setHorizontalStretch(3)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.frameFolderBindingBox.sizePolicy().hasHeightForWidth())
        self.frameFolderBindingBox.setSizePolicy(sizePolicy6)
        self.frameFolderBindingBox.setMinimumSize(QSize(480, 100))
        self.frameFolderBindingBox.setFont(font2)
        self.frameFolderBindingBox.setStyleSheet(u"")
        self.frameFolderBindingBox.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_10.addWidget(self.frameFolderBindingBox, 0, 0, 1, 1)

        self.tabWidgetResultFolder.addTab(self.tabResultBindingBox, "")
        self.tabResultWarmUp = QWidget()
        self.tabResultWarmUp.setObjectName(u"tabResultWarmUp")
        self.gridLayout_13 = QGridLayout(self.tabResultWarmUp)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.frameFolderWarmUp = QLabel(self.tabResultWarmUp)
        self.frameFolderWarmUp.setObjectName(u"frameFolderWarmUp")
        self.frameFolderWarmUp.setFont(font2)
        self.frameFolderWarmUp.setStyleSheet(u"")
        self.frameFolderWarmUp.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_13.addWidget(self.frameFolderWarmUp, 0, 0, 1, 1)

        self.tabWidgetResultFolder.addTab(self.tabResultWarmUp, "")
        self.tabResultStatus = QWidget()
        self.tabResultStatus.setObjectName(u"tabResultStatus")
        self.gridLayout_11 = QGridLayout(self.tabResultStatus)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.textEditFolderStatus = QTextEdit(self.tabResultStatus)
        self.textEditFolderStatus.setObjectName(u"textEditFolderStatus")
        sizePolicy2.setHeightForWidth(self.textEditFolderStatus.sizePolicy().hasHeightForWidth())
        self.textEditFolderStatus.setSizePolicy(sizePolicy2)
        self.textEditFolderStatus.setMinimumSize(QSize(150, 0))
        self.textEditFolderStatus.setReadOnly(True)

        self.gridLayout_11.addWidget(self.textEditFolderStatus, 0, 0, 1, 1)

        self.tabWidgetResultFolder.addTab(self.tabResultStatus, "")

        self.gridLayout_12.addWidget(self.tabWidgetResultFolder, 1, 1, 1, 1)

        self.tabWidget.addTab(self.tabMultiImage, "")
        self.tabSettings = QWidget()
        self.tabSettings.setObjectName(u"tabSettings")
        self.gridLayout_9 = QGridLayout(self.tabSettings)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.label_2 = QLabel(self.tabSettings)
        self.label_2.setObjectName(u"label_2")
        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setPointSize(14)
        self.label_2.setFont(font3)

        self.gridLayout_9.addWidget(self.label_2, 0, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_9.addItem(self.verticalSpacer, 2, 0, 1, 1)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_9.addItem(self.verticalSpacer_2, 7, 0, 1, 1)

        self.label = QLabel(self.tabSettings)
        self.label.setObjectName(u"label")

        self.gridLayout_9.addWidget(self.label, 5, 0, 1, 1)

        self.comboBoxChooseTypeSaveData = QComboBox(self.tabSettings)
        self.comboBoxChooseTypeSaveData.addItem("")
        self.comboBoxChooseTypeSaveData.addItem("")
        self.comboBoxChooseTypeSaveData.setObjectName(u"comboBoxChooseTypeSaveData")

        self.gridLayout_9.addWidget(self.comboBoxChooseTypeSaveData, 6, 0, 1, 1)

        self.label_3 = QLabel(self.tabSettings)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_9.addWidget(self.label_3, 3, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.buttonSaveShot = QPushButton(self.tabSettings)
        self.buttonSaveShot.setObjectName(u"buttonSaveShot")
        self.buttonSaveShot.setMinimumSize(QSize(151, 0))

        self.horizontalLayout_2.addWidget(self.buttonSaveShot)

        self.pathSaveShot = QLineEdit(self.tabSettings)
        self.pathSaveShot.setObjectName(u"pathSaveShot")

        self.horizontalLayout_2.addWidget(self.pathSaveShot)


        self.gridLayout_9.addLayout(self.horizontalLayout_2, 4, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_5)

        self.buttonSaveSettings = QPushButton(self.tabSettings)
        self.buttonSaveSettings.setObjectName(u"buttonSaveSettings")
        self.buttonSaveSettings.setMinimumSize(QSize(150, 0))

        self.horizontalLayout.addWidget(self.buttonSaveSettings)


        self.gridLayout_9.addLayout(self.horizontalLayout, 8, 0, 1, 1)

        self.label_4 = QLabel(self.tabSettings)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_9.addWidget(self.label_4, 1, 0, 1, 1)

        self.tabWidget.addTab(self.tabSettings, "")

        self.main_layout.addWidget(self.tabWidget)

        mainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(mainWindow)
        self.statusbar.setObjectName(u"statusbar")
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)

        self.tabWidget.setCurrentIndex(0)
        self.tabWidgetCamera.setCurrentIndex(0)
        self.tabWidgetPicture.setCurrentIndex(0)
        self.tabWidgetResultFolder.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(mainWindow)
    # setupUi

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"Object Detection with YOLO", None))
        self.buttonChooseModel.setText(QCoreApplication.translate("mainWindow", u"Ch\u1ecdn t\u1eadp tin Model", None))
        self.labelPictureDirect.setText(QCoreApplication.translate("mainWindow", u"Ch\u01b0a ch\u1ecdn t\u1eadp tin Model", None))
        self.labelChooseCamera.setText(QCoreApplication.translate("mainWindow", u"Ch\u1ecdn Camera", None))
        self.buttonStartRecord.setText(QCoreApplication.translate("mainWindow", u"B\u1eaft \u0111\u1ea7u nh\u1eadn h\u00ecnh \u1ea3nh", None))
        self.buttonCapture.setText(QCoreApplication.translate("mainWindow", u"Ch\u1ee5p l\u1ea1i frame hi\u1ec7n t\u1ea1i", None))
        self.buttonDetect.setText(QCoreApplication.translate("mainWindow", u"B\u1eaft \u0111\u1ea7u nh\u1eadn di\u1ec7n", None))
        self.buttonSaveAllDetectCam.setText(QCoreApplication.translate("mainWindow", u"L\u01b0u to\u00e0n b\u1ed9 d\u1eef li\u1ec7u", None))
        self.frameCameraBindingBox.setText(QCoreApplication.translate("mainWindow", u"Nh\u1ea5n \"B\u1eaft \u0111\u1ea7u ch\u1ecdn h\u00ecnh \u1ea3nh\" \u0111\u1ec3 hi\u1ec7n khung h\u00ecnh xem tr\u01b0\u1edbc", None))
        self.tabWidgetCamera.setTabText(self.tabWidgetCamera.indexOf(self.tabBindingBoxCamera), QCoreApplication.translate("mainWindow", u"H\u00ecnh \u1ea3nh (Binding Box)", None))
        self.frameCameraWarmUp.setText(QCoreApplication.translate("mainWindow", u"Nh\u1ea5n \"B\u1eaft \u0111\u1ea7u ch\u1ecdn h\u00ecnh \u1ea3nh\" \u0111\u1ec3 hi\u1ec7n khung h\u00ecnh xem tr\u01b0\u1edbc", None))
        self.tabWidgetCamera.setTabText(self.tabWidgetCamera.indexOf(self.tabWarmUpCamera), QCoreApplication.translate("mainWindow", u"H\u00ecnh \u1ea3nh (Warm Up)", None))
        self.tabWidgetCamera.setTabText(self.tabWidgetCamera.indexOf(self.tabStatusCamera), QCoreApplication.translate("mainWindow", u"Tr\u1ea1ng th\u00e1i", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabCamera), QCoreApplication.translate("mainWindow", u"Nh\u1eadn di\u1ec7n qua Camera", None))
        self.buttonChoosePicture.setText(QCoreApplication.translate("mainWindow", u"Ch\u1ecdn t\u1eadp tin h\u00ecnh \u1ea3nh", None))
        self.buttonSaveDataDetectImg.setText(QCoreApplication.translate("mainWindow", u"L\u01b0u d\u1eef li\u1ec7u nh\u1eadn di\u1ec7n (.xlsx)", None))
        self.buttonDownloadPictureBindingBox.setText(QCoreApplication.translate("mainWindow", u"L\u01b0u h\u00ecnh \u1ea3nh (Binding Box)", None))
        self.buttonDownloadPictureWarmUp.setText(QCoreApplication.translate("mainWindow", u"L\u01b0u h\u00ecnh \u1ea3nh (Warm Up)", None))
        self.framePictureBindingBox.setText(QCoreApplication.translate("mainWindow", u"Nh\u1ea5n \"Ch\u1ecdn t\u1eadp tin h\u00ecnh \u1ea3nh\" \u0111\u1ec3 b\u1eaft \u0111\u1ea7u", None))
        self.tabWidgetPicture.setTabText(self.tabWidgetPicture.indexOf(self.tabImageBindingBox), QCoreApplication.translate("mainWindow", u"K\u1ebft qu\u1ea3 (Binding Box)", None))
        self.framePictureWarmUp.setText(QCoreApplication.translate("mainWindow", u"Nh\u1ea5n \"Ch\u1ecdn t\u1eadp tin h\u00ecnh \u1ea3nh\" \u0111\u1ec3 b\u1eaft \u0111\u1ea7u", None))
        self.tabWidgetPicture.setTabText(self.tabWidgetPicture.indexOf(self.tabPictureWarmUp), QCoreApplication.translate("mainWindow", u"K\u1ebft qu\u1ea3 (Warm Up)", None))
        self.tabWidgetPicture.setTabText(self.tabWidgetPicture.indexOf(self.tab), QCoreApplication.translate("mainWindow", u"Tr\u1ea1ng th\u00e1i", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabPicture), QCoreApplication.translate("mainWindow", u"Nh\u1eadn di\u1ec7n h\u00ecnh \u1ea3nh", None))
        self.buttonChooseFolder.setText(QCoreApplication.translate("mainWindow", u"Ch\u1ecdn th\u01b0 m\u1ee5c ...", None))
        self.buttonSaveDataDetectMulti.setText(QCoreApplication.translate("mainWindow", u"L\u01b0u d\u1eef li\u1ec7u nh\u1eadn di\u1ec7n (\u1ea2nh hi\u1ec7n t\u1ea1i)", None))
        self.buttonDownloadMultiPicture.setText(QCoreApplication.translate("mainWindow", u"L\u01b0u d\u1eef li\u1ec7u nh\u1eadn di\u1ec7n (To\u00e0n b\u1ed9 h\u00ecnh \u1ea3nh)", None))
        self.frameFolderBindingBox.setText(QCoreApplication.translate("mainWindow", u"Nh\u1ea5n \"Ch\u1ecdn th\u01b0 m\u1ee5c\" \u0111\u1ec3 b\u1eaft \u0111\u1ea7u", None))
        self.tabWidgetResultFolder.setTabText(self.tabWidgetResultFolder.indexOf(self.tabResultBindingBox), QCoreApplication.translate("mainWindow", u"H\u00ecnh \u1ea3nh (Binding Box)", None))
        self.frameFolderWarmUp.setText(QCoreApplication.translate("mainWindow", u"Nh\u1ea5n \"Ch\u1ecdn th\u01b0 m\u1ee5c\" \u0111\u1ec3 b\u1eaft \u0111\u1ea7u", None))
        self.tabWidgetResultFolder.setTabText(self.tabWidgetResultFolder.indexOf(self.tabResultWarmUp), QCoreApplication.translate("mainWindow", u"H\u00ecnh \u1ea3nh (Warm Up)", None))
        self.tabWidgetResultFolder.setTabText(self.tabWidgetResultFolder.indexOf(self.tabResultStatus), QCoreApplication.translate("mainWindow", u"Tr\u1ea1ng th\u00e1i", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabMultiImage), QCoreApplication.translate("mainWindow", u"Nh\u1eadn di\u1ec7n nhi\u1ec1u h\u00ecnh \u1ea3nh", None))
        self.label_2.setText(QCoreApplication.translate("mainWindow", u"C\u00e0i \u0111\u1eb7t ch\u01b0\u01a1ng tr\u00ecnh", None))
        self.label.setText(QCoreApplication.translate("mainWindow", u"Ph\u01b0\u01a1ng th\u1ee9c l\u01b0u t\u1eadp tin", None))
        self.comboBoxChooseTypeSaveData.setItemText(0, QCoreApplication.translate("mainWindow", u"L\u01b0u v\u00e0o \u0111\u01b0\u1eddng d\u1eabn \u0111\u00e3 c\u00e0i \u0111\u1eb7t s\u1eb5n", None))
        self.comboBoxChooseTypeSaveData.setItemText(1, QCoreApplication.translate("mainWindow", u"H\u1ecfi ng\u01b0\u1eddi d\u00f9ng ch\u1ecdn \u0111\u01b0\u1eddng d\u1eabn tr\u01b0\u1edbc khi l\u01b0u", None))

        self.label_3.setText(QCoreApplication.translate("mainWindow", u"\u0110\u01b0\u1eddng d\u1eabn l\u01b0u h\u00ecnh ch\u1ee5p k\u1ebft qu\u1ea3", None))
        self.buttonSaveShot.setText(QCoreApplication.translate("mainWindow", u"Ch\u1ecdn \u0111\u01b0\u1eddng d\u1eabn", None))
        self.buttonSaveSettings.setText(QCoreApplication.translate("mainWindow", u"L\u01b0u c\u00e0i \u0111\u1eb7t", None))
        self.label_4.setText(QCoreApplication.translate("mainWindow", u"\u0110\u1ec3 c\u00e1c thay \u0111\u1ed5i c\u00f3 hi\u1ec7u l\u1ef1c, vui l\u00f2ng ch\u1ecdn v\u00e0o \"L\u01b0u c\u00e0i \u0111\u1eb7t\" sau khi \u0111\u00e3 thi\u1ebft \u0111\u1eb7t xong.", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabSettings), QCoreApplication.translate("mainWindow", u"C\u00e0i \u0111\u1eb7t", None))
    # retranslateUi

