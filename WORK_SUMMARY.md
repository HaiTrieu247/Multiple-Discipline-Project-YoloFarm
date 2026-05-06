# 📚 Tóm Tắt Công Việc: Hệ Thống IoT Yolobit (Pump + Webserver)

**Ngày:** May 6, 2026  
**Dự án:** Yolobit RTOS Lab - IoT Control System  
**Mục tiêu:** Tạo hệ thống điều khiển máy bơm từ xa qua webserver

---

## 🎯 Tóm Tắt Công Việc

### Giai đoạn 1: Tạo Task Máy Bơm (task_pump.py)
- ✅ Tạo file **task_pump.py** với 3 chế độ hoạt động
  - **Manual**: Bật/tắt thủ công bằng Button A
  - **Auto**: Tự động bơm khi độ ẩm < ngưỡng (dùng DHT20)
  - **Scheduled**: Hẹn giờ bơm trong khoảng thời gian cụ thể
- ✅ Tạo hướng dẫn chi tiết: **TASK_PUMP_GUIDE.md**
- ✅ Tạo quick start: **PUMP_QUICK_START.md**
- ✅ Tạo ví dụ: **main_pump_example.py**, **config_pump_example.py**

### Giai đoạn 2: Tạo Hệ Thống Webserver IoT
- ✅ Tạo task Yolobit: **task_webserver_client.py**
  - Gửi dữ liệu (T, H, pump state) lên webserver
  - Nhận lệnh từ webserver qua HTTP
  - Hỗ trợ 4 lệnh: set_pump_state, set_pump_mode, set_humidity_threshold, set_schedule
  
- ✅ Tạo webserver Flask: **webserver.py**
  - API endpoints: /api/data, /api/command, /api/status
  - Dashboard HTML hiệu ứng đẹp
  - Real-time update mỗi 1 giây
  - Hỗ trợ 3 chế độ điều khiển

- ✅ Tạo hướng dẫn: **WEBSERVER_SETUP_GUIDE.md**, **WEBSERVER_README.md**
- ✅ Tạo ví dụ: **main_webserver_example.py**, **config_webserver_example.py**
- ✅ Tạo test API: **api_test_examples.bat** (Windows), **api_test_examples.sh** (Linux/macOS)

---

## 📁 Danh Sách File Được Tạo

### Core Files (Chạy trên Yolobit)
```
e:\coding\Yolobit-RTOS-Lab\
├── task_pump.py                      # Task máy bơm (3 chế độ)
├── task_webserver_client.py          # Task gửi/nhận dữ liệu HTTP
├── main_pump_example.py              # Ví dụ main.py với pump
├── main_webserver_example.py         # Ví dụ main.py với webserver
├── config_pump_example.py            # Ví dụ config cho pump
└── config_webserver_example.py       # Ví dụ config cho webserver
```

### Webserver Files (Chạy trên Laptop)
```
├── webserver.py                      # Flask webserver + Dashboard
├── api_test_examples.bat             # Test API (Windows)
└── api_test_examples.sh              # Test API (Linux/macOS)
```

### Documentation Files
```
├── TASK_PUMP_GUIDE.md                # Hướng dẫn chi tiết pump
├── PUMP_QUICK_START.md               # Quick start pump
├── WEBSERVER_SETUP_GUIDE.md          # Hướng dẫn chi tiết webserver
├── WEBSERVER_README.md               # Tóm tắt webserver
└── WORK_SUMMARY.md                   # File này
```

---

## 🏗️ Kiến Trúc Hệ Thống

```
┌────────────────────────────────────┐
│  YOLOBIT (Mạch Microcontroller)   │
├────────────────────────────────────┤
│                                    │
│ ┌──────────────┐                 │
│ │  task_i2c    │ → Đọc DHT20    │
│ │ (Cảm biến)   │ (T°C, H%)      │
│ └──────────────┘                 │
│        ↓                          │
│ ┌──────────────┐                 │
│ │ task_pump    │ → Điều khiển   │
│ │ (Máy bơm)    │ Pin 10/13      │
│ └──────────────┘                 │
│        ↓                          │
│ ┌──────────────────────────────┐ │
│ │ task_webserver_client        │ │
│ │ • Gửi POST /api/data (T,H)   │ │
│ │ • Nhận GET /api/command      │ │
│ └──────────────────────────────┘ │
│                                    │
└────────────────┬───────────────────┘
                 │
                 │ WiFi (HTTP REST)
                 │
┌────────────────▼───────────────────┐
│  LAPTOP (Webserver Flask)          │
├────────────────────────────────────┤
│                                    │
│ ┌──────────────────────────────┐ │
│ │   webserver.py (Flask)       │ │
│ │ • API: /api/data             │ │
│ │ • API: /api/command          │ │
│ │ • API: /api/status           │ │
│ └──────────────────────────────┘ │
│                                    │
│ ┌──────────────────────────────┐ │
│ │   Dashboard HTML             │ │
│ │ • Hiển thị T°C, H%           │ │
│ │ • Nút bật/tắt bơm           │ │
│ │ • Chọn chế độ (3 chế độ)    │ │
│ │ • Real-time update           │ │
│ └──────────────────────────────┘ │
│                                    │
└────────────────────────────────────┘
```

---

## ⚙️ Chế Độ Hoạt Động (Task Pump)

### 1. **Manual Mode** (Thủ công)
```
Điều khiển: Button A hoặc API
Hàm: task_pump.set_pump_manual(0|1)
Ví dụ: Nhấn nút để bật/tắt
```

### 2. **Auto Mode** (Theo độ ẩm)
```
Điều khiển: DHT20 cảm biến
Hàm: task_pump.set_mode("auto")
      task_pump.set_humidity_threshold(60.0)
Ví dụ: 
  - Độ ẩm < 60% → Máy bơm ON
  - Độ ẩm ≥ 60% → Máy bơm OFF
```

### 3. **Scheduled Mode** (Hẹn giờ)
```
Điều khiển: Thời gian hệ thống
Hàm: task_pump.set_schedule(start_h, start_m, end_h, end_m, duration_s)
Ví dụ: 6:00 - 22:00, chạy 15 giây
  - 6h00 - 22h00: Bơm ON 15s, OFF, lặp lại
  - 22h01 - 5h59: Bơm OFF
```

---

## 📡 API Endpoints (Webserver)

### 1. Nhận Dữ Liệu từ Yolobit
```
POST /api/data
Content-Type: application/json

Body:
{
  "timestamp": 1704067200,
  "temperature": 28.5,
  "humidity": 65.3,
  "pump_state": 1,
  "pump_mode": "auto",
  "humidity_threshold": 55.0
}

Response: {"status": "ok"}
```

### 2. Lấy Lệnh (Yolobit poll)
```
GET /api/command

Response (nếu có lệnh):
{
  "command": "set_pump_mode",
  "params": {"mode": "auto"}
}

Response (nếu không có):
{}
```

### 3. Gửi Lệnh (từ Frontend)
```
POST /api/command
Content-Type: application/json

Body (ví dụ):
{
  "command": "set_pump_state",
  "params": {"state": 1}
}

Response: {"status": "queued"}
```

### 4. Lấy Trạng Thái
```
GET /api/status

Response:
{
  "timestamp": "2026-05-06T10:30:45.123456",
  "temperature": 28.5,
  "humidity": 65.3,
  "pump_state": 1,
  "pump_mode": "auto",
  "humidity_threshold": 55.0
}
```

### Các Lệnh Hỗ Trợ
```
1. set_pump_state
   {"command": "set_pump_state", "params": {"state": 0|1}}

2. set_pump_mode
   {"command": "set_pump_mode", "params": {"mode": "manual|auto|scheduled"}}

3. set_humidity_threshold
   {"command": "set_humidity_threshold", "params": {"threshold": 50.0}}

4. set_schedule
   {"command": "set_schedule", "params": {
     "start_hour": 6, "start_min": 0,
     "end_hour": 22, "end_min": 0,
     "duration_sec": 15
   }}
```

---

## 🚀 Cách Triển Khai (Step-by-Step)

### Bước 1: Chuẩn Bị Phần Cứng
```
Yolobit
├── DHT20 (I2C)
│   ├── SCL → pin19
│   ├── SDA → pin20
│   └── GND, VCC
├── Relay/Module Bơm
│   ├── Signal → Pin 10 (GPIO)
│   └── VCC, GND
└── Button A (sẵn có)

Laptop
├── WiFi (kết nối cùng mạng với Yolobit)
└── Port 5000 trống (hoặc đổi config)
```

### Bước 2: Cấu Hình Yolobit (config.py)
```python
# WiFi & Webserver
WIFI_SSID = "Tên_WiFi_Nhà"           # ← Thay
WIFI_PASSWORD = "Mật_Khẩu_WiFi"     # ← Thay
WEBSERVER_IP = "192.168.1.100"      # ← Thay IP laptop

# Task Intervals
INTERVAL_TASK_I2C_MS = 2000
INTERVAL_TASK_PUMP_MS = 500
INTERVAL_TASK_WEBSERVER_CLIENT_MS = 1000  # ← Thêm

# Hoặc dùng file: config_webserver_example.py
```

**Cách tìm IP Laptop:**
```
Windows: ipconfig → IPv4 Address
macOS:   ifconfig → inet
Linux:   ip addr → inet
```

### Bước 3: Cập Nhật main.py (Yolobit)
```python
import time
from event_manager import *
import config
import task_i2c
import task_pump
import task_webserver_client      # ← Thêm import

event_manager.reset()

# Init
task_i2c.task_init()
task_pump.task_init()
task_webserver_client.task_init()  # ← Thêm

# Register events
event_manager.add_timer_event(config.INTERVAL_TASK_I2C_MS, task_i2c.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK_PUMP_MS, task_pump.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK_WEBSERVER_CLIENT_MS, 
                              task_webserver_client.task_run)  # ← Thêm

# Configure pump
task_pump.set_mode("auto")
task_pump.set_humidity_threshold(55.0)

print("=== Yolobit IoT ===")

while True:
    event_manager.run()
    time.sleep_ms(10)
```

### Bước 4: Nạp Code vào Yolobit
```
1. Cắm USB Yolobit vào laptop
2. Mở PyMakr extension trong VSCode
3. Chọn device (COM port)
4. Upload project
5. Xem Serial Monitor (115200 baud)
```

### Bước 5: Cài Flask & Chạy Webserver
```bash
# Terminal / Command Prompt
pip install flask

# Chạy webserver
python webserver.py

# Kết quả:
# 🚀 Yolobit Webserver Dashboard
# 📱 Mở browser: http://localhost:5000
```

### Bước 6: Mở Dashboard
```
Browser: http://localhost:5000
Hoặc:   http://192.168.1.100:5000 (từ máy khác)
```

---

## 🎮 Cách Sử Dụng Dashboard

### Dashboard Features
```
┌─────────────────────────────────────────┐
│ 🚰 Yolobit Dashboard                   │
├─────────────────────────────────────────┤
│ WiFi: Kết nối | Cập nhật: 10:30:45    │
├─────────────────────────────────────────┤
│                                         │
│ 📊 Cảm Biến (DHT20)                   │
│   Nhiệt độ: 28.5 °C                   │
│   Độ ẩm:    65.3 %                    │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│ 💧 Máy Bơm                            │
│   Trạng thái: BẬT (🟢)                │
│   [Bật ✓] [Tắt ✗]                    │
│   Mode: AUTO                           │
│                                         │
├─────────────────────────────────────────┤
│                                         │
│ ⚙️ Chế độ                              │
│                                         │
│ Chọn chế độ: [Manual ▼]               │
│                                         │
│ Ngưỡng độ ẩm (%):                     │
│ [====●================] 55 %           │
│ [Áp dụng]                             │
│                                         │
└─────────────────────────────────────────┘
```

### Mode Manual
1. Chọn "Manual (Thủ công)"
2. Bấm "Bật ✓" hoặc "Tắt ✗"
3. Máy bơm bật/tắt ngay

### Mode Auto
1. Chọn "Auto (Theo độ ẩm)"
2. Kéo slider độ ẩm (0-100%)
3. Bấm "Áp dụng"
4. Máy bơm tự động bơm khi độ ẩm < ngưỡng

### Mode Scheduled
1. Chọn "Scheduled (Hẹn giờ)"
2. Nhập:
   - Giờ bắt đầu: 6:00
   - Giờ kết thúc: 22:00
   - Thời gian chạy: 15 giây
3. Bấm "Áp dụng Lịch"
4. Máy bơm chạy tự động theo lịch

---

## 🧪 Test API

### Windows
```bash
python api_test_examples.bat
```

### Linux/macOS
```bash
bash api_test_examples.sh
```

### Manual cURL
```bash
# Lấy trạng thái
curl http://localhost:5000/api/status

# Bật máy bơm
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command":"set_pump_state","params":{"state":1}}'

# Chế độ Auto
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command":"set_pump_mode","params":{"mode":"auto"}}'
```

---

## 📊 Log Mẫu (Serial Monitor)

```
============================================================
🚀 Yolobit IoT - Webserver Client
============================================================
📱 WiFi: Tên_WiFi_Nhà
🌐 Webserver: http://192.168.1.100:5000
📊 Dashboard: http://192.168.1.100:5000
============================================================

[WEBSERVER] WiFi connected, server: http://192.168.1.100:5000
[WEBSERVER] Initialized at Pin 10
[LAB2][I2C] DHT20 ready
[PUMP] Mode changed to: auto
[PUMP] Humidity threshold set to 55.0%

[WEBSERVER] Data received: T=28.5°C, H=65.3%
[PUMP] Auto mode: humidity 45.2% < threshold 55.0%, turning ON
[PUMP] Pump ON
[WEBSERVER] Data received: T=28.6°C, H=64.8%

[WEBSERVER] Command sent to device: set_pump_mode
[WEBSERVER] Executed: set_pump_mode(auto)

[WEBSERVER] Data received: T=28.7°C, H=63.5%
[PUMP] Auto mode: humidity 65.0% >= threshold 55.0%, turning OFF
[PUMP] Pump OFF
```

---

## 🆘 Gỡ Lỗi

### Yolobit không kết nối WiFi
```
Lỗi: [WEBSERVER] No WiFi config in config.py
Giải pháp:
  1. Kiểm tra WIFI_SSID và WIFI_PASSWORD trong config.py
  2. Không có khoảng trắng thừa, không dấu tiếng Việt
  3. Kiểm tra mạng WiFi có hoạt động
```

### Yolobit không tìm thấy webserver
```
Lỗi: [WEBSERVER] send error: ...
Giải pháp:
  1. Kiểm tra IP laptop trong config.py (WEBSERVER_IP)
  2. Ping từ máy khác: ping 192.168.1.100
  3. Webserver có chạy trên laptop không
  4. Tắt Firewall hoặc allow port 5000
```

### Dashboard không cập nhật
```
Giải pháp:
  1. Nhấn F5 để reload trang
  2. Xem browser console (F12)
  3. Kiểm tra serial monitor Yolobit
  4. Kiểm tra task_i2c và task_pump có khởi tạo
```

### Port 5000 bị dùng
```
Windows:
  netstat -ano | findstr :5000
  Đổi port trong webserver.py: app.run(port=5001)

Linux/macOS:
  lsof -i :5000
  Đổi port trong webserver.py: app.run(port=5001)
```

---

## 📚 Tài Liệu Liên Quan

| File | Mô Tả |
|------|-------|
| **TASK_PUMP_GUIDE.md** | Hướng dẫn chi tiết task_pump |
| **PUMP_QUICK_START.md** | Quick start máy bơm (3 chế độ) |
| **WEBSERVER_SETUP_GUIDE.md** | Hướng dẫn chi tiết webserver |
| **WEBSERVER_README.md** | Tóm tắt hệ thống webserver |
| **task_pump.py** | Code task máy bơm |
| **task_webserver_client.py** | Code client webserver |
| **webserver.py** | Code Flask webserver |

---

## ✅ Checklist Triển Khai

```
Chuẩn bị:
☐ Kết nối Yolobit, DHT20, relay bơm
☐ Tìm IP laptop (WEBSERVER_IP)
☐ Tìm tên WiFi và mật khẩu

Yolobit:
☐ Copy task_pump.py
☐ Copy task_webserver_client.py
☐ Chỉnh config.py (WiFi, IP)
☐ Chỉnh main.py (import, init, register)
☐ Nạp code qua PyMakr
☐ Xem Serial Monitor 115200 baud

Laptop:
☐ Cài Flask: pip install flask
☐ Chạy webserver: python webserver.py
☐ Mở browser: http://localhost:5000

Test:
☐ Dashboard hiển thị T°C, H%
☐ BBtn bật/tắt máy bơm
☐ Chọn 3 chế độ: Manual, Auto, Scheduled
☐ API test (bash/bat)
☐ Log serial monitor OK
```

---

## 🎓 Mở Rộng (Tiếp Theo)

1. **Database**: Lưu lịch sử dữ liệu (SQLite, MySQL)
2. **Biểu Đồ**: Vẽ đồ thị nhiệt độ, độ ẩm (Chart.js)
3. **Thông Báo**: Email/SMS cảnh báo (smtplib)
4. **Mobile App**: Ứng dụng di động (React Native, Flutter)
5. **Cloud**: Đồng bộ lên AWS IoT, Google Cloud, Azure
6. **Nhiều Cảm Biến**: Thêm nhiều DHT20, đèn LED, relay

---

## 📝 Ghi Chú Quan Trọng

### Về Bộ Nhớ & Hiệu Suất
- DHT20 có độ trễ đọc ~200ms, nên INTERVAL_TASK_I2C_MS ≥ 2000ms
- Webserver client gửi mỗi 3 giây (có debounce), không gửi mỗi chu kỳ
- Yolobit RAM hạn chế, JSON payload tối thiểu

### Về WiFi & Networking
- Yolobit và Laptop phải cùng WiFi
- Không qua proxy/VPN
- WiFi 2.4GHz (5GHz có vấn đề với Yolobit)
- Tốc độ baud UART: 115200

### Về Thời Gian
- Mode Scheduled dùng NTP nếu có task_ntp.py chạy
- Nếu không có NTP, dùng time.time() từ lúc khởi động (chỉ trong ngày)
- DHT20 trả về độ ẩm tương đối (% RH)

### Về Phần Cứng
- Pin 10 (GPIO 10) có sẵn trên Yolobit, hoặc dùng pin 13
- Relay cần cấp nguồn riêng (5V hoặc 12V tùy relay)
- Cần diode flyback nếu điều khiển motor/pump trực tiếp
- Button A là nút đã sẵn trên Yolobit

---

## 📞 Support & Contacts

- **Firmware**: OhStem Yolobit MicroPython
- **Công cụ nạp**: PyMakr extension (VSCode)
- **Thư viện**: lib/mqtt.py (WiFi), lib/aiot/aiot_dht20.py (DHT20)
- **API Framework**: Flask (Python)

---

## 🎉 Kết Luận

Bạn đã có một **hệ thống IoT hoàn chỉnh**:

✅ **Máy bơm** có 3 chế độ: thủ công, tự động, hẹn giờ  
✅ **Webserver** với dashboard đẹp, real-time  
✅ **API REST** để tích hợp hệ thống khác  
✅ **Hướng dẫn chi tiết** cho mọi bước  
✅ **Test API** để debug dễ dàng  

**Tiếp theo:** Triển khai theo checklist, nạp code, test dashboard, enjoy! 🚀

---

**Ngày tạo:** 2026-05-06  
**Phiên bản:** 1.0  
**Trạng thái:** Hoàn thành ✅
