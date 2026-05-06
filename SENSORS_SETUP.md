# Hướng dẫn Cảm Biến Độ Ẩm Đất (SM) & Ánh Sáng (LUX)

## 📝 Tổng Quan

Dự án đã được cập nhật để hỗ trợ **2 cảm biến analog**:
- **Pin 1**: Cảm biến độ ẩm đất (Soil Moisture - SM)
- **Pin 2**: Cảm biến ánh sáng (Light Level - LUX)

Dữ liệu được:
- ✅ Hiển thị trên **LCD 16x2**
- ✅ Gửi lên **Webserver** để xem trên Dashboard
- ✅ Có thể publish lên **MQTT broker** (nếu cấu hình)

---

## 🔧 Các File Được Thêm/Cập Nhật

### 1. **task_sensors.py** (FILE MỚI)
**Chức năng:** Đọc dữ liệu SM từ Pin1 và LUX từ Pin2, xử lý logic.

```python
# Khởi tạo
import task_sensors
task_sensors.task_init()

# Lấy dữ liệu
soil_moisture = task_sensors.get_soil_moisture()  # 0-100%
light_level = task_sensors.get_light_level()      # 0-4096
```

### 2. **config.py** (CẬP NHẬT)
Thêm chu kỳ chạy task_sensors:
```python
INTERVAL_TASK_SENSORS_MS = 2000  # Đọc cảm biến mỗi 2 giây
```

### 3. **main.py** (CẬP NHẬT)
- Import `task_sensors`
- Gọi `task_sensors.task_init()`
- Đăng ký `task_sensors.task_run()` với event manager

### 4. **task_lcd.py** (CẬP NHẬT)
- Hiển thị xoay chiều: 
  - **Chế độ 1** (2s): T, H từ DHT20
  - **Chế độ 2** (2s): SM, LUX từ cảm biến

### 5. **task_webserver_client.py** (CẬP NHẬT)
- Thu thập dữ liệu SM, LUX
- Gửi lên webserver qua HTTP POST

### 6. **task_i2c.py** (CẬP NHẬT)
- Cập nhật task_sensors với dữ liệu T, H từ DHT20

### 7. **webserver.py** (CẬP NHẬT)
- Thêm card hiển thị SM & LUX trên dashboard
- Cập nhật device_data để lưu SM, LUX

---

## 📊 Chế độ Hiển thị LCD

LCD 16x2 sẽ xoay chiều giữa 2 chế độ mỗi 2 giây:

**Chế độ 1:**
```
RT:25.3*C RH:65%
LUX:2500 SM:45%
```

**Chế độ 2:**
```
SM:45% LUX:2500
[Soil & Light]
```

---

## 🌐 Dashboard Web

Khi chạy webserver.py trên laptop, bạn sẽ thấy card mới:

```
🌱 Cảm Biến Đất & Ánh Sáng
┌─────────────────┬─────────────────┐
│  Độ ẩm đất      │   Ánh sáng      │
│      45%        │      2500       │
└─────────────────┴─────────────────┘
📍 Pin1: Cảm biến độ ẩm | Pin2: Cảm biến ánh sáng
```

---

## 🚀 Sử Dụng

### 1. **Cơ bản** - Chạy trên Yolobit

```bash
# Kết nối USB và chạy main.py
# Xem serial output:
[SENSORS] Task initialized - SM on pin1, LUX on pin2
[LAB2][LCD] ready via aiot_lcd1602
```

### 2. **Xem trên Web Dashboard**

```bash
# Trên laptop
pip install flask
python webserver.py

# Mở browser: http://localhost:5000
```

### 3. **Lấy dữ liệu từ task_sensors**

```python
# Trong task khác hoặc chương trình
import task_sensors

# Đọc SM (0-100%)
sm = task_sensors.get_soil_moisture()
print(f"Độ ẩm đất: {sm}%")

# Đọc LUX (0-4096)
lux = task_sensors.get_light_level()
print(f"Ánh sáng: {lux}")

# Lấy tất cả
all_data = task_sensors.get_all_sensor_data()
# Returns: {
#     'soil_moisture': 45,
#     'light_level': 2500,
#     'temperature': 25.3,
#     'humidity': 65
# }
```

---

## 📡 MQTT Integration (Tùy chọn)

Nếu cấu hình MQTT, task_sensors sẽ tự động publish:

```
Topic: SM    | Value: 45  (độ ẩm đất %)
Topic: LUX   | Value: 2500  (mức ánh sáng)
```

---

## 🔌 Kết nối Phần Cứng

| Cảm biến | Pin | Loại | Ghi chú |
|---------|-----|------|---------|
| Độ ẩm đất | 1 | Analog | 0V = khô, 3.3V = ướt |
| Ánh sáng | 2 | Analog | 0V = tối, 3.3V = sáng |
| DHT20 | I2C | Digital | Đã có sẵn trên Yolobit |
| LCD1602 | I2C | Digital | Đã có sẵn trên Yolobit |

---

## 🐛 Khắc Phục Sự Cố

### ❌ LCD không hiển thị SM/LUX

1. Kiểm tra Pin 1, Pin 2 có kết nối đúng không
2. Xem serial output có lỗi không:
   ```
   [SENSORS] Read error: ...
   ```
3. Kiểm tra `_read_interval_ms` trong `task_sensors.py` (mặc định: 2000ms)

### ❌ Webserver không nhận SM/LUX

1. Kiểm tra WiFi kết nối chưa
2. Xem `task_webserver_client.py` có import `task_sensors` không
3. Kiểm tra IP webserver trong `config.py`

---

## 📝 Ghi Chú

- Giá trị SM được chuyển đổi từ ADC (0-4096) sang % (0-100)
- Công thức: `SM = (adc_value * 100) / 4096`
- LUX là giá trị thô từ cảm biến (không chuyển đổi)
- Tất cả dữ liệu được gửi mỗi 2 giây (INTERVAL_TASK_SENSORS_MS)
- LCD cập nhật mỗi 2 giây (xoay chiều giữa 2 chế độ)

---

## 📚 Tài Liệu Liên Quan

- [TASK_PUMP_GUIDE.md](TASK_PUMP_GUIDE.md) - Hướng dẫn máy bơm
- [WEBSERVER_README.md](WEBSERVER_README.md) - Hướng dẫn webserver
- [WORK_SUMMARY.md](WORK_SUMMARY.md) - Tóm tắt dự án
