# 📡 Webserver IoT - Hướng dẫn Cài Đặt

## Tổng Quan Hệ Thống

```
Yolobit (Mạch)                     Laptop
┌─────────────────┐               ┌──────────────────┐
│  task_i2c.py    │ ──WiFi──>  │  webserver.py    │
│  task_pump.py   │ <──────────  │  (Flask)         │
│  task_...       │             │  Dashboard HTML  │
└─────────────────┘             └──────────────────┘
     Gửi dữ liệu                  Nhận lệnh & Hiển thị
  HTTP POST /api/data          HTTP GET /api/status
```

## 🔧 Bước 1: Cấu Hình Wifi trên Mạch

Chỉnh sửa **config.py** trên Yolobit:

```python
# Cấu hình WiFi
WIFI_SSID = "Tên_WiFi_Nhà_Bạn"        # <-- Thay tên WiFi
WIFI_PASSWORD = "Mật_Khẩu_WiFi"       # <-- Thay mật khẩu

# Địa chỉ IP Laptop (nơi chạy webserver)
WEBSERVER_IP = "192.168.1.100"        # <-- Thay IP laptop

# Các config khác (giữ nguyên)
INTERVAL_TASK_I2C_MS = 2000
INTERVAL_TASK_PUMP_MS = 500
INTERVAL_TASK_WEBSERVER_CLIENT_MS = 1000  # <-- Thêm dòng này
```

### Cách tìm IP của Laptop:

**Trên Windows:**
```
1. Mở Command Prompt (Win + R, gõ "cmd")
2. Gõ: ipconfig
3. Tìm dòng "IPv4 Address" trong "Wireless LAN adapter" hoặc "Ethernet adapter"
   Ví dụ: 192.168.1.100
```

**Trên macOS/Linux:**
```bash
ifconfig | grep "inet "
# Tìm IP của WiFi hoặc Ethernet
```

## 🔧 Bước 2: Tích Hợp task_webserver_client vào main.py

Chỉnh sửa **main.py** trên Yolobit:

```python
import time
from event_manager import *
import config
import task_i2c
import task_pump
import task_webserver_client  # <-- Thêm import

# Khởi tạo event manager
event_manager.reset()

# Gọi task_init()
task_i2c.task_init()
task_pump.task_init()
task_webserver_client.task_init()  # <-- Thêm

# Đăng ký task_run()
event_manager.add_timer_event(config.INTERVAL_TASK_I2C_MS, task_i2c.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK_PUMP_MS, task_pump.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK_WEBSERVER_CLIENT_MS, task_webserver_client.task_run)  # <-- Thêm

# Cấu hình máy bơm mặc định
task_pump.set_mode("auto")
task_pump.set_humidity_threshold(55.0)

print("=== Yolobit IoT - Webserver Client ===")
print(f"WiFi: {config.WIFI_SSID}")
print(f"Server: http://{config.WEBSERVER_IP}:5000")

while True:
    event_manager.run()
    time.sleep_ms(10)
```

## 💻 Bước 3: Cài Đặt & Chạy Webserver trên Laptop

### 3.1 Cài Flask

```bash
# Windows (Command Prompt)
pip install flask

# macOS/Linux (Terminal)
pip3 install flask
```

### 3.2 Chạy Webserver

```bash
# Windows
python webserver.py

# macOS/Linux
python3 webserver.py
```

**Kết quả:**
```
============================================================
🚀 Yolobit Webserver Dashboard
============================================================
📱 Mở browser: http://localhost:5000
📊 API endpoints:
   - POST /api/data      : Nhận dữ liệu từ Yolobit
   - GET  /api/command   : Trả lệnh cho Yolobit
   - POST /api/command   : Gửi lệnh (từ web)
   - GET  /api/status    : Lấy trạng thái hiện tại
============================================================
```

## 🌐 Bước 4: Mở Dashboard trong Browser

1. Mở browser trên **cùng laptop** hoặc **máy tính khác trong WiFi**
2. Nhập: `http://localhost:5000` (hoặc `http://192.168.1.100:5000` nếu từ máy khác)
3. Bạn sẽ thấy dashboard với:
   - 📊 Nhiệt độ & Độ ẩm
   - 💧 Trạng thái máy bơm
   - ⚙️ Lựa chọn chế độ (Manual, Auto, Scheduled)

## 📡 Quá Trình Hoạt Động

### Lần Đầu Kết Nối:

1. **Yolobit khởi động**
   - Kết nối WiFi
   - Khởi tạo task_webserver_client
   - Log: `[WEBSERVER] WiFi connected, server: http://192.168.1.100:5000`

2. **Yolobit gửi dữ liệu**
   - Mỗi ~1 giây, task_webserver_client gửi:
     ```
     POST http://192.168.1.100:5000/api/data
     {
       "temperature": 28.5,
       "humidity": 65.3,
       "pump_state": 1,
       "pump_mode": "auto",
       "humidity_threshold": 55.0
     }
     ```

3. **Webserver cập nhật dashboard**
   - Browser tự động làm mới mỗi 1 giây
   - Hiển thị: nhiệt độ, độ ẩm, trạng thái

4. **User bấm nút trên dashboard**
   - Ví dụ: Chọn "Auto" mode
   - Dashboard gửi:
     ```
     POST http://192.168.1.100:5000/api/command
     {
       "command": "set_pump_mode",
       "params": {"mode": "auto"}
     }
     ```

5. **Yolobit nhận lệnh**
   - task_webserver_client gọi `/api/command` mỗi chu kỳ
   - Nhận lệnh và thực hiện
   - Log: `[WEBSERVER] Executed: set_pump_mode(auto)`

## 🎮 Cách Sử Dụng Dashboard

### Mode Manual (Thủ công)

```
1. Chọn "Manual (Thủ công)" từ dropdown
2. Bấm "Bật ✓" hoặc "Tắt ✗"
3. Máy bơm sẽ bật/tắt ngay
```

### Mode Auto (Theo độ ẩm)

```
1. Chọn "Auto (Theo độ ẩm)"
2. Điều chỉnh "Ngưỡng độ ẩm (%)" với slider
3. Bấm "Áp dụng"
4. Máy bơm sẽ tự động bơm khi độ ẩm < ngưỡng
```

### Mode Scheduled (Hẹn giờ)

```
1. Chọn "Scheduled (Hẹn giờ)"
2. Nhập:
   - Giờ bắt đầu: 6:00
   - Giờ kết thúc: 22:00
   - Thời gian chạy: 15 (giây)
3. Bấm "Áp dụng Lịch"
4. Máy bơm sẽ chạy 15 giây, tắt, lặp lại trong khung 6h-22h
```

## 🆘 Gỡ Lỗi

### 1. Yolobit không kết nối WiFi

**Lỗi:** `[WEBSERVER] No WiFi config in config.py`

**Giải pháp:**
- Kiểm tra `config.py` có `WIFI_SSID` và `WIFI_PASSWORD` không
- Kiểm tra tên WiFi và mật khẩu có đúng không
- Đảm bảo Yolobit nằm trong phạm vi WiFi

### 2. Yolobit không tìm thấy webserver

**Lỗi:** `[WEBSERVER] send error: ...`

**Giải pháp:**
- Kiểm tra IP laptop trong `config.py` có đúng không
- Ping từ Yolobit: kiểm tra kết nối mạng
- Kiểm tra webserver đang chạy trên laptop
- Tắt Firewall hoặc cho phép port 5000

### 3. Dashboard không hiển thị dữ liệu

**Lỗi:** Browser mở nhưng thấy `--°C` và `--%`

**Giải pháp:**
- Kiểm tra task_i2c và task_pump có khởi tạo không
- Kiểm tra DHT20 có kết nối đúng không
- Xem Serial Monitor Yolobit để debug

### 4. Dashboard không cập nhật

**Giải pháp:**
- Nhấn F5 để tải lại trang
- Kiểm tra brow browser console (F12) để xem lỗi JavaScript
- Kiểm tra webserver có chạy không (xem terminal)

## 📊 Log Mẫu trên Serial Monitor

```
[WEBSERVER] WiFi connected, server: http://192.168.1.100:5000
[WEBSERVER] Initialized at Pin 10
[LAB2][I2C] DHT20 ready
[WEBSERVER] Data received: T=28.5°C, H=65.3%
[WEBSERVER] Data received: T=28.6°C, H=64.8%
[WEBSERVER] Command sent to device: set_pump_mode
[WEBSERVER] Executed: set_pump_mode(auto)
[WEBSERVER] Data received: T=28.7°C, H=63.5%
```

## 🌍 Truy Cập Dashboard từ Máy Khác

### Trong WiFi nhà:

```
1. Trên máy khác (điện thoại, tablet, PC khác):
2. Mở browser
3. Nhập: http://192.168.1.100:5000  (thay IP của laptop)
```

### Từ ngoài (qua Internet):

Cần cấu hình port forwarding trên router (nâng cao) hoặc dùng ngrok:

```bash
pip install ngrok
ngrok http 5000
# Sẽ cho URL public: https://xxxx-xx-xxx-xxx-xx.ngrok.io
```

## 📝 Ví Dụ cURL (Kiểm Thử API)

### Gửi lệnh từ terminal:

```bash
# Bật máy bơm
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_pump_state", "params": {"state": 1}}'

# Chuyển sang chế độ auto
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command": "set_pump_mode", "params": {"mode": "auto"}}'

# Lấy trạng thái hiện tại
curl http://localhost:5000/api/status
```

## 🎉 Xong!

Bây giờ bạn có:
✅ Mạch Yolobit tự động gửi dữ liệu
✅ Webserver trên laptop nhận và lưu dữ liệu
✅ Dashboard web để xem & điều khiển
✅ Thời gian thực (real-time)

Chúc mừng! 🚀
