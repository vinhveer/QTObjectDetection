from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        
        # Set minimum window size for better responsiveness
        mainWindow.setMinimumSize(800, 400)
        
        # Set default font
        self.default_font = QFont("Segoe UI", 8)
        mainWindow.setFont(self.default_font)
        
        # Main layout setup
        self.centralwidget = QWidget(mainWindow)
        self.main_layout = QVBoxLayout(self.centralwidget)
        self.main_layout.setSpacing(10)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        # Model selection section
        self.model_group = QGroupBox("Chọn Model")
        self.model_group.setFont(self.default_font)
        self.model_layout = QHBoxLayout(self.model_group)
        
        self.buttonChooseModel = QPushButton("Chọn tập tin")
        self.buttonChooseModel.setMinimumWidth(120)
        self.labelPictureDirect = QLabel("Chưa chọn tập tin Model")
        self.labelPictureDirect.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.model_layout.addWidget(self.buttonChooseModel)
        self.model_layout.addWidget(self.labelPictureDirect)
        self.main_layout.addWidget(self.model_group)

        # Tab widget
        self.tabWidget = QTabWidget()
        self.tabWidget.setFont(self.default_font)
        self.main_layout.addWidget(self.tabWidget)

        # Camera Tab
        self.tabCamera = QWidget()
        self.camera_layout = QVBoxLayout(self.tabCamera)
        self.camera_layout.setSpacing(15)
        
        # Camera controls - all in one row
        self.camera_controls = QHBoxLayout()
        self.camera_controls.setSpacing(10)
        
        # Camera selection with label
        self.camera_selection = QHBoxLayout()
        self.labelChooseCamera = QLabel("Chọn Camera")
        self.labelChooseCamera.setFont(self.default_font)
        self.comboBoxChooseCamera = QComboBox()
        self.comboBoxChooseCamera.setMinimumWidth(150)
        
        self.camera_selection.addWidget(self.labelChooseCamera)
        self.camera_selection.addWidget(self.comboBoxChooseCamera)
        
        # Add all controls to the same row
        self.camera_controls.addLayout(self.camera_selection)
        self.camera_controls.addSpacing(20)  # Space between camera selection and buttons
        
        self.buttonStartRecord = QPushButton("Bắt đầu nhận hình ảnh")
        self.buttonStartRecord.setMinimumWidth(130)
        self.buttonCapture = QPushButton("Chụp lại khung hình")
        self.buttonCapture.setMinimumWidth(120)
        
        self.camera_controls.addWidget(self.buttonStartRecord)
        self.camera_controls.addWidget(self.buttonCapture)
        self.camera_controls.addStretch()
        self.buttonDetect = QPushButton("Bắt đầu nhận diện")
        self.buttonDetect.setMinimumWidth(120)
        self.camera_controls.addWidget(self.buttonDetect)
        
        # Camera content
        self.camera_content = QHBoxLayout()
        self.camera_content.setSpacing(15)
        
        self.frameCamera = QLabel()
        self.frameCamera.setStyleSheet("border: 1px solid gray;")
        self.frameCamera.setAlignment(Qt.AlignCenter)
        self.frameCamera.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frameCamera.setMinimumSize(480, 100)
        
        self.camera_info = QVBoxLayout()
        self.camera_info.setSpacing(10)
        self.text_edit_camera_info = QTextEdit()
        self.text_edit_camera_info.setReadOnly(True)
        self.text_edit_camera_info.setMinimumWidth(250)
        self.buttonSaveAllDetectCam = QPushButton("Lưu toàn bộ hình ảnh và dữ liệu nhận diện")
        self.buttonSaveAllDetectCam.setMinimumWidth(230)
        
        self.camera_info.addWidget(self.text_edit_camera_info)
        self.camera_info.addWidget(self.buttonSaveAllDetectCam)
        
        self.camera_content.addWidget(self.frameCamera, 2)
        self.camera_content.addLayout(self.camera_info, 1)
        
        self.camera_layout.addLayout(self.camera_controls)
        self.camera_layout.addLayout(self.camera_content)
        
        # Picture Tab
        self.tabPicture = QWidget()
        self.picture_layout = QVBoxLayout(self.tabPicture)
        self.picture_layout.setSpacing(15)
        
        # Picture controls - all in one row
        self.picture_controls = QHBoxLayout()
        self.picture_controls.setSpacing(10)
        
        # Picture selection with label
        self.picture_selection = QHBoxLayout()
        self.buttonChoosePicture = QPushButton("Chọn tập tin hình ảnh")
        self.buttonChoosePicture.setMinimumWidth(120)
        
        self.picture_selection.addWidget(self.buttonChoosePicture)
        
        self.picture_controls.addLayout(self.picture_selection)
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        self.picture_controls.addWidget(self.progress_bar)
        self.picture_controls.addStretch()
        
        self.buttonSaveDataDetectImg = QPushButton("Lưu dữ liệu nhận diện")
        self.buttonSaveDataDetectImg.setMinimumWidth(130)
        self.buttonDownloadPicture = QPushButton("Tải về hình ảnh đã nhận diện")
        self.buttonDownloadPicture.setMinimumWidth(170)
        
        self.picture_controls.addWidget(self.buttonSaveDataDetectImg)
        self.picture_controls.addWidget(self.buttonDownloadPicture)
        
        # Picture content
        self.picture_content = QHBoxLayout()
        self.picture_content.setSpacing(15)
        
        self.framePicture = QLabel()
        self.framePicture.setStyleSheet("border: 1px solid gray;")
        self.framePicture.setAlignment(Qt.AlignCenter)
        self.framePicture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.framePicture.setMinimumSize(480, 100)
        
        self.text_edit_info = QTextEdit()
        self.text_edit_info.setReadOnly(True)
        self.text_edit_info.setMinimumWidth(250)
        
        self.picture_content.addWidget(self.framePicture, 2)
        self.picture_content.addWidget(self.text_edit_info, 1)
        
        self.picture_layout.addLayout(self.picture_controls)
        self.picture_layout.addLayout(self.picture_content)

        ## Multi-Image Tab
        self.tabMultiImage = QWidget()
        self.multi_image_layout = QVBoxLayout(self.tabMultiImage)
        self.multi_image_layout.setSpacing(15)
        
        # Controls section
        self.folder_controls = QHBoxLayout()
        self.folder_controls.setSpacing(10)
        
        # Choose folder section
        self.folder_selection = QHBoxLayout()
        self.buttonChooseFolder = QPushButton("Chọn thư mục ...")
        self.buttonChooseFolder.setMinimumWidth(120)
        
        self.folder_selection.addWidget(self.buttonChooseFolder)
        
        # Progress bar
        self.multi_progress_bar = QProgressBar()
        self.multi_progress_bar.hide()
        
        # Action buttons
        self.buttonSaveDataDetectMulti = QPushButton("Lưu dữ liệu nhận diện")
        self.buttonSaveDataDetectMulti.setMinimumWidth(130)
        self.buttonDownloadMultiPicture = QPushButton("Tải về hình ảnh đã nhận diện")
        self.buttonDownloadMultiPicture.setMinimumWidth(170)
        
        # Add all controls
        self.folder_controls.addLayout(self.folder_selection)
        self.folder_controls.addWidget(self.multi_progress_bar)
        self.folder_controls.addStretch()
        self.folder_controls.addWidget(self.buttonSaveDataDetectMulti)
        self.folder_controls.addWidget(self.buttonDownloadMultiPicture)
        
        # Content section
        self.multi_image_content = QHBoxLayout()
        self.multi_image_content.setSpacing(15)
        
        # File list
        self.image_list_container = QVBoxLayout()
        self.image_list = QListWidget()
        self.image_list.setMinimumWidth(150)
        
        self.image_list_container.addWidget(self.image_list)
        
        # Preview frame
        self.frameMultiPreview = QLabel()
        self.frameMultiPreview.setStyleSheet("border: 1px solid gray;")
        self.frameMultiPreview.setAlignment(Qt.AlignCenter)
        self.frameMultiPreview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.frameMultiPreview.setMinimumSize(480, 100)
        
        # Detection info
        self.text_edit_multi_info = QTextEdit()
        self.text_edit_multi_info.setReadOnly(True)
        self.text_edit_multi_info.setMinimumWidth(150)
        
        # Add all content with ratio 1:3:1
        self.multi_image_content.addLayout(self.image_list_container, 1)  # 1/5
        self.multi_image_content.addWidget(self.frameMultiPreview, 3)     # 3/5
        self.multi_image_content.addWidget(self.text_edit_multi_info, 1)  # 1/5
        
        # Add to main layout
        self.multi_image_layout.addLayout(self.folder_controls)
        self.multi_image_layout.addLayout(self.multi_image_content)
        
        # Add tabs
        self.tabWidget.addTab(self.tabCamera, "Nhận diện qua Camera")
        self.tabWidget.addTab(self.tabPicture, "Nhận diện hình ảnh")
        self.tabWidget.addTab(self.tabMultiImage, "Nhận diện nhiều hình ảnh")
        
        # Set central widget
        mainWindow.setCentralWidget(self.centralwidget)
        
        # Menu and status bar
        self.menubar = QMenuBar(mainWindow)
        self.menubar.setGeometry(QRect(0, 0, 800, 21))
        mainWindow.setMenuBar(self.menubar)
        
        self.statusbar = QStatusBar(mainWindow)
        mainWindow.setStatusBar(self.statusbar)
        
        # Set window title
        mainWindow.setWindowTitle("Object Detection with YOLO")
        
        # Set default tab
        self.tabWidget.setCurrentIndex(0)
        QMetaObject.connectSlotsByName(mainWindow)