# Object Detection Application

## Overview
A desktop application for real-time object detection using YOLO model, built with PyQt5 and OpenCV. The application supports both camera feed detection and image file detection.

## Features
- Real-time object detection through camera feed
- Image file detection support
- Multiple camera device support
- Screenshot capture functionality
- Detailed detection information display
- User-friendly GUI interface

## Requirements
- Python 3.8 or higher
- See `requirements.txt` for detailed package dependencies

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the main application:
```bash
python main.py
```

### Camera Detection
1. Select a camera from the dropdown menu
2. Click "Bắt đầu nhận hình ảnh" to start camera feed
3. Click "Bắt đầu nhận diện" to start object detection
4. Use "Chụp ảnh" to capture current frame

### Image Detection
1. Click "Chọn ảnh" to select an image file
2. Click "Bắt đầu nhận diện" to perform detection on the image

## Dependencies
- PyQt5>=5.15.0
- opencv-python>=4.5.0
- numpy>=1.19.0
- ultralytics>=8.0.0
- pygrabber (Windows only)

## License
This project is licensed under the MIT License - see the LICENSE file for details.