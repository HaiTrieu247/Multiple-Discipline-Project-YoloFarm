# 🌐 Yolobit IoT Webserver - Tóm Tắt

## 🎯 Mục Đích

Tạo **hệ thống IoT** để điều khiển mạch Yolobit từ xa qua **webserver trên laptop**:

- 📊 **Mạch gửi**: nhiệt độ, độ ẩm, trạng thái máy bơm
- 🎮 **Laptop nhận**: hiển thị dashboard, cho phép điều khiển
- 📡 **Giao tiếp**: HTTP REST API qua WiFi

## 📁 Các File Cần Thiết

### Trên Yolobit:
1. **task_webserver_client.py** - Task gửi/nhận dữ liệu (đã tạo)
2. **task_pump.py** - Task máy bơm (từ trước)
3. **task_i2c.py** - Task DHT20 (từ trước)
4. **config.py** - Cấu hình WiFi + IP webserver
5. **main.py** - Khởi tạo tất cả task

### Trên Laptop:
1. **webserver.py** - Flask webserver + dashboard (đã tạo)
2. **api_test_examples.bat** (Windows) hoặc **.sh** (macOS/Linux) - Test API

## ⚡ Quick Start (5 phút)

### 1. Chỉnh config.py trên Yolobit:

```python
WIFI_SSID = "WiFi_nhà_bạn"              # ← Thay tên WiFi
WIFI_PASSWORD = "Mật_khẩu_WiFi"        # ← Thay mật khẩu
WEBSERVER_IP = "192.168.1.100"         # ← Thay IP laptop

INTERVAL_TASK_I2C_MS = 2000
INTERVAL_TASK_PUMP_MS = 500
INTERVAL_TASK_WEBSERVER_CLIENT_MS = 1000  # ← Thêm dòng này
```

### 2. Chỉnh main.py trên Yolobit:

```python
import task_webserver_client            # ← Thêm

task_webserver_client.task_init()       # ← Thêm
event_manager.add_timer_event(config.INTERVAL_TASK_WEBSERVER_CLIENT_MS, 
                              task_webserver_client.task_run)  # ← Thêm

task_pump.set_mode("auto")
task_pump.set_humidity_threshold(55.0)
```

### 3. Nạp code vào Yolobit bằng PyMakr

### 4. Trên Laptop, chạy webserver:

```bash
# Cài Flask (lần đầu)
pip install flask

# Chạy webserver
python webserver.py
```

### 5. Mở Dashboard:

```
Browser: http://localhost:5000
```

✅ **Xong!** Bạn đã có webserver IoT hoàn chỉnh.

## 🌐 API Endpoints

| Method | Endpoint | Chức năng |
|--------|----------|----------|
| GET | `/` | Hiển thị Dashboard HTML |
| POST | `/api/data` | Yolobit gửi dữ liệu |
| GET | `/api/command` | Yolobit lấy lệnh |
| POST | `/api/command` | Frontend gửi lệnh |
| GET | `/api/status` | Lấy trạng thái hiện tại |

## 📡 Luồng Dữ Liệu

```
Yolobit                              Laptop
   │                                   │
   ├─ Read DHT20 (task_i2c)           │
   ├─ Read Pump (task_pump)           │
   │                                   │
   ├─ POST /api/data ──────────────> │ Webserver Flask
   │  {temp, humidity, pump_state}    │ Lưu vào memory
   │                                   │
   │ <──── GET /api/command ──────── │
   │  {command, params}               │
   │                                   │
   ├─ Execute command                │
   │  (set_mode, set_threshold)       │
   │                                   │ <─ Browser
   │                                   │  Hiển thị Dashboard
   │                                   │  User bấm nút
   │                                   │  Frontend POST /api/command
```

## 🎮 Cách Dùng Dashboard

### Mode Manual (Thủ công):
- Bấm "Bật" hoặc "Tắt" để điều khiển ngay

### Mode Auto (Theo độ ẩm):
- Điều chỉnh slider độ ẩm
- Máy bơm tự động bật khi độ ẩm thấp

### Mode Scheduled (Hẹn giờ):
- Nhập giờ bắt đầu, kết thúc, thời gian chạy
- Máy bơm chạy tự động theo lịch

## 🔧 Cấu Hình IP Laptop

### Tìm IP Laptop:

**Windows (Command Prompt):**
```
ipconfig
→ Tìm IPv4 Address: 192.168.1.100
```

**macOS/Linux (Terminal):**
```bash
ifconfig
→ Tìm inet: 192.168.1.100
```

### Nhập vào config.py:
```python
WEBSERVER_IP = "192.168.1.100"
```

## 📊 Dữ Liệu Được Gửi

Mỗi lần gửi, Yolobit gửi:

```json
{
  "timestamp": 1704067200,
  "temperature": 28.5,
  "humidity": 65.3,
  "pump_state": 1,
  "pump_mode": "auto",
  "humidity_threshold": 55.0
}
```

## 🆘 Gỡ Lỗi

| Vấn đề | Nguyên nhân | Giải pháp |
|--------|-----------|----------|
| Không kết nối WiFi | Config sai | Kiểm tra WIFI_SSID, WIFI_PASSWORD |
| Không tìm thấy webserver | IP sai | Kiểm tra WEBSERVER_IP, bật webserver |
| Dashboard không cập nhật | Task không gửi dữ liệu | Kiểm tra task_webserver_client chạy |
| Port 5000 bị dùng | Ứng dụng khác dùng port | Đổi port trong webserver.py |

## 📚 Tài Liệu Chi Tiết

- **WEBSERVER_SETUP_GUIDE.md** - Hướng dẫn cài đặt chi tiết
- **task_webserver_client.py** - Mã nguồn Yolobit client
- **webserver.py** - Mã nguồn Flask webserver

## 🎓 Học Thêm

### API Testing:

**Windows:**
```
python api_test_examples.bat
```

**macOS/Linux:**
```bash
bash api_test_examples.sh
```

### cURL Manual:

```bash
# Lấy trạng thái
curl http://localhost:5000/api/status

# Bật máy bơm
curl -X POST http://localhost:5000/api/command \
  -H "Content-Type: application/json" \
  -d '{"command":"set_pump_state","params":{"state":1}}'
```

## 🎉 Tính Năng

✅ Real-time dashboard  
✅ Điều khiển từ xa qua web  
✅ 3 chế độ hoạt động (manual, auto, scheduled)  
✅ Đọc cảm biến DHT20  
✅ Lưu trạng thái device  
✅ HTTP REST API  
✅ Giao diện web responsive  

## 🚀 Tiếp Theo

1. **Thêm Database**: Lưu lịch sử dữ liệu (SQLite, MySQL)
2. **Thêm Biểu Đồ**: Vẽ đồ thị nhiệt độ, độ ẩm theo thời gian
3. **Thêm Thông Báo**: Gửi email, SMS khi có cảnh báo
4. **Mobile App**: Tạo ứng dụng mobile để điều khiển
5. **Cloud Sync**: Đồng bộ lên cloud (AWS IoT, Google Cloud, etc.)

---

**Xong!** Bây giờ bạn có một hệ thống IoT hoàn chỉnh. 🎊
