# Object Detection

## Tổng quan
Đây là một ứng dụng desktop để phát hiện đối tượng thời gian thực sử dụng mô hình YOLO, được xây dựng với PySide6 và OpenCV. Ứng dụng hỗ trợ cả phát hiện từ nguồn cấp dữ liệu camera và phát hiện từ tệp hình ảnh.

## Tính năng
- Phát hiện đối tượng thời gian thực qua nguồn cấp dữ liệu camera
- Hỗ trợ phát hiện từ tệp hình ảnh, hoặc một thư mục chứa nhiều hình ảnh
- Lưu dữ liệu nhận diện với nhiều định dạng
- Giao diện người dùng thân thiện

## Yêu cầu
- Python 3.12 trở lên
- Xem `requirements.txt` để biết chi tiết các gói phụ thuộc

## Cài đặt

1. Sao chép kho lưu trữ:
```bash
git clone [repository-url]
cd [repository-name]
```

2. Cài đặt các gói yêu cầu:
```bash
pip install -r requirements.txt
```

## Cách chạy

Chạy ứng dụng chính:
```bash
python main.py
```

Hoặc

## Cài đặt các bản đã build sẵn

Bạn có thể tải xuống các bản build sẵn cho Windows x64 và macOS arm từ phần **Releases** trên GitHub:

[Link đến trang Releases của GitHub](https://github.com/vinhveer/QTObjectDetection/releases)

Chỉ cần tải xuống và chạy file cài đặt tương ứng với hệ điều hành của bạn.

## Giấy phép
Dự án này được cấp phép theo Giấy phép MIT - xem tệp LICENSE để biết chi tiết.
