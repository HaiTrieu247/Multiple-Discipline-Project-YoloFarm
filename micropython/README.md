# Yolobit MicroPython Code

Thư mục này chứa chỉ code cần thiết cho board Yolobit/MicroPython.

## Cách upload lên mạch

1. Mở thư mục `micropython/` trong VS Code
2. Cài đặt Pymakr extension nếu chưa có
3. Kết nối mạch qua USB
4. Nhấn nút upload trong Pymakr

## Cấu trúc

- `boot.py` - khởi động
- `main.py` - chương trình chính
- `config.py` - cấu hình
- `task_*.py` - các task riêng biệt
- `lib/` - thư viện
- `ai/` - code AI/inference
- `webserver.py` - web server trên board

## Lưu ý

- Chỉ upload từ thư mục này để tránh lỗi bộ nhớ đầy
- Backend và frontend riêng biệt trong thư mục cha