# 🚰 Quick Start: Máy Bơm Nước với Yolobit

## 📋 Những gì bạn cần

- **Máy bơm nước** (hoặc relay bơm)
- **Yolobit + firmware MicroPython**
- **DHT20** (cảm biến nhiệt độ, độ ẩm) - nếu dùng chế độ Auto
- **Button A** - để điều khiển thủ công

## ⚡ 3 Bước Tích Hợp

### Bước 1: Thêm vào `config.py`

```python
INTERVAL_TASK_PUMP_MS = 500
```

### Bước 2: Thêm vào `main.py`

```python
import task_pump

# Trong phần khởi tạo:
task_pump.task_init()

# Trong phần add_timer_event:
event_manager.add_timer_event(config.INTERVAL_TASK_PUMP_MS, task_pump.task_run)

# Tùy chọn: Cấu hình chế độ
task_pump.set_mode("auto")
task_pump.set_humidity_threshold(55.0)
```

### Bước 3: Nạp Code!

Sử dụng PyMakr để nạp vào Yolobit.

---

## 🎯 3 Chế Độ Hoạt Động

| Chế độ | Lệnh | Ví dụ |
|-------|------|------|
| **Manual** | Nhấn Button A | `task_pump.set_mode("manual")` |
| **Auto** | Tự động theo độ ẩm | `task_pump.set_mode("auto")`<br>`task_pump.set_humidity_threshold(55.0)` |
| **Scheduled** | Hẹn giờ hoạt động | `task_pump.set_mode("scheduled")`<br>`task_pump.set_schedule(6,0,22,0,15)` |

---

## 🔧 Wiring Diagram

```
Yolobit Pin 10 (GPIO 10)
    |
    +--- Relay Signal
         |
         +--- IN (Relay)
              |
              +--- OUT (Bơm 5V/12V)
```

Hoặc dùng **Pin 13** thay vì Pin 10 (chỉnh trong `task_pump.py`)

---

## 📝 Ví dụ Code

### Bơm tự động theo độ ẩm

```python
# main.py
task_pump.set_mode("auto")
task_pump.set_humidity_threshold(60.0)  # Bơm khi độ ẩm < 60%
```

**Kết quả:**
- Độ ẩm < 60% → Máy bơm ON
- Độ ẩm ≥ 60% → Máy bơm OFF

### Bơm theo lịch (6h sáng - 10h tối)

```python
task_pump.set_mode("scheduled")
task_pump.set_schedule(6, 0, 22, 0, 20)  # 6h00 - 22h00, chạy 20s
```

**Kết quả:**
- 6h00 - 22h00: Máy bơm chạy 20 giây, rồi tắt, lặp lại
- 22h01 - 5h59: Máy bơm tắt

### Bơm thủ công

```python
task_pump.set_mode("manual")
# Nhấn Button A để bật/tắt máy bơm
```

---

## 📊 Kiểm Tra

Mở **Serial Monitor** (115200 baud) để xem log:

```
[PUMP] Initialized at Pin 10
[PUMP] Mode changed to: auto
[PUMP] Humidity threshold set to 60.0%
[PUMP] Auto mode: humidity 45.2% < threshold 60.0%, turning ON
[PUMP] Pump ON
[PUMP] Auto mode: humidity 65.0% >= threshold 60.0%, turning OFF
[PUMP] Pump OFF
```

---

## 🆘 Gỡ Lỗi

| Vấn đề | Nguyên nhân | Giải pháp |
|-------|-----------|----------|
| Máy bơm không hoạt động | Pin GPIO không được khởi tạo | Kiểm tra `task_pump.task_init()` có chạy hay không |
| Mode auto không hoạt động | DHT20 không được đọc | Kiểm tra `task_i2c.py` có chạy hay không |
| Button A không hoạt động | Mode không phải manual | Chuyển sang `task_pump.set_mode("manual")` |
| Thời gian hẹn giờ sai | NTP chưa đồng bộ | Kiểm tra `task_ntp.py` hoặc dùng `task_ntp.py` |

---

## 📚 Tài Liệu Đầy Đủ

Xem file **TASK_PUMP_GUIDE.md** để biết thêm chi tiết về API, cấu hình và ví dụ nâng cao.

---

## 💡 Mẹo

1. **Kết hợp chế độ**: Chuyển từ manual → auto khi cần
2. **Điều chỉnh ngưỡng**: Thay đổi humidity threshold để bơm nhiều hơn/ít hơn
3. **Thời gian bơm**: Tăng `duration_sec` trong scheduled mode để bơm lâu hơn
4. **Nhiều pin**: Copy task_pump.py thành task_pump2.py để điều khiển pin khác

---

Chúc mừng! 🎉 Bây giờ bạn có thể điều khiển máy bơm nước một cách tự động hoặc thủ công!
