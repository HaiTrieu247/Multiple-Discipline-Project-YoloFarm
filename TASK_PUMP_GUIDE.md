# Hướng dẫn sử dụng Task Máy Bơm (task_pump.py)

## 1. Cấu trúc Task Máy Bơm

File `task_pump.py` cung cấp 3 chế độ hoạt động:
- **Manual**: Bật/tắt thủ công bằng nút Button A hoặc hàm
- **Auto**: Tự động bật khi độ ẩm thấp hơn ngưỡng
- **Scheduled**: Hẹn giờ bật trong khoảng thời gian cụ thể

## 2. Tích hợp vào Dự án

### Bước 1: Cập nhật `config.py`

Thêm chu kỳ chạy task máy bơm:

```python
# ... các config khác ...

# Task Máy bơm
INTERVAL_TASK_PUMP_MS = 500  # Chạy mỗi 500ms để kiểm tra nút bấm, độ ẩm
```

### Bước 2: Cập nhật `main.py`

Thêm import và khởi tạo task:

```python
import task_pump  # Thêm dòng này

# ... trong phần task_init() ...
task_pump.task_init()

# ... trong phần add_timer_event ...
event_manager.add_timer_event(config.INTERVAL_TASK_PUMP_MS, task_pump.task_run)
```

## 3. Các Tính Năng & Hàm API

### 3.1 Chế độ Manual (Bật/tắt thủ công)

```python
import task_pump

# Chuyển sang chế độ manual
task_pump.set_mode("manual")

# Bật máy bơm
task_pump.set_pump_manual(1)

# Tắt máy bơm
task_pump.set_pump_manual(0)

# Hoặc nhấn Button A để bật/tắt
```

### 3.2 Chế độ Auto (Dựa vào độ ẩm)

```python
# Chuyển sang chế độ auto
task_pump.set_mode("auto")

# Tùy chỉnh ngưỡng độ ẩm (mặc định 50%)
task_pump.set_humidity_threshold(60.0)  # Bật khi độ ẩm < 60%
```

**Cách hoạt động:**
- Khi độ ẩm < ngưỡng: máy bơm bật tự động
- Khi độ ẩm >= ngưỡng: máy bơm tắt
- Đọc dữ liệu từ DHT20 (task_i2c.py phải chạy)

### 3.3 Chế độ Scheduled (Hẹn giờ)

```python
# Chuyển sang chế độ scheduled
task_pump.set_mode("scheduled")

# Hẹn giờ: bắt đầu 6:00, kết thúc 22:00, chạy 10 giây mỗi lần
task_pump.set_schedule(
    start_hour=6, 
    start_min=0, 
    end_hour=22, 
    end_min=0, 
    duration_sec=10
)

# Hoặc: bất cứ lúc nào trong ngày, chạy 5 giây
task_pump.set_schedule(0, 0, 23, 59, 5)
```

**Cách hoạt động:**
- Trong khung giờ: máy bơm bật lên chạy `duration_sec` giây, rồi tắt
- Ngoài khung giờ: máy bơm luôn tắt
- Lặp lại vòng này trong suốt ngày

## 4. Ví dụ Thực Tế

### Ví dụ 1: Bơm nước tự động theo độ ẩm

```python
# Trong main.py sau khi khởi tạo
task_pump.set_mode("auto")
task_pump.set_humidity_threshold(55.0)  # Bơm khi độ ẩm < 55%

# Máy bơm sẽ tự động bắt đầu khi DHT20 đo được độ ẩm < 55%
```

### Ví dụ 2: Bơm nước vào lúc 6h-22h, mỗi 2 phút

```python
task_pump.set_mode("scheduled")
task_pump.set_schedule(
    start_hour=6,
    start_min=0,
    end_hour=22,
    end_min=0,
    duration_sec=15  # Chạy 15 giây
)

# Máy bơm sẽ bật lên 15 giây rồi tắt, lặp lại trong khung 6h-22h
```

### Ví dụ 3: Kết hợp - Bơm tự động VÀ thủ công

```python
# Mặc định auto mode
task_pump.set_mode("auto")
task_pump.set_humidity_threshold(60.0)

# Nếu muốn bật thủ công: chuyển sang manual, bật, rồi quay lại auto
task_pump.set_mode("manual")
task_pump.set_pump_manual(1)  # Bật thủ công
# ... sau vài giây ...
task_pump.set_mode("auto")  # Quay lại auto
```

## 5. Ghi Chú & Yêu Cầu

### Yêu cầu Phần Cứng
- **Pin 10 (hoặc 13)** cắm relay hoặc module bơm
- **DHT20** trên I2C (nếu dùng mode auto)
- **Button A** trên Yolobit (để bật/tắt manual)

### Yêu cầu Phần Mềm
- `task_i2c.py` phải chạy và khởi tạo DHT20 (để dùng mode auto)
- Yolobit firmware hỗ trợ I2C và GPIO
- Bộ điều khiển `event_manager` chạy ở background

### Lưu Ý
- **Độ ẩm**: DHT20 trả về giá trị % RH (Relative Humidity), từ 0-100%
- **Ngưỡng mặc định**: 50% - bạn có thể điều chỉnh theo nhu cầu
- **Thời gian NTP**: Mode scheduled dùng `time.time()` từ NTP (nếu có) hoặc tính từ lúc khởi động
- **Pin GPIO**: Hiện tại dùng pin 10; nếu muốn dùng pin 13, chỉnh trong `task_pump.task_init()`

## 6. Cách Chỉnh Sửa Pin

Nếu muốn dùng pin 13 thay vì pin 10:

```python
# Trong task_pump.py, sửa task_init():
pump_pin = Pin(13, Pin.OUT)  # Thay pin 10 thành pin 13
```

## 7. Gỡ Lỗi (Debugging)

Mở Serial Monitor (115200 baud) để xem log:

```
[PUMP] Initialized at Pin 10
[PUMP] Mode changed to: auto
[PUMP] Humidity threshold set to 60.0%
[PUMP] Auto mode: humidity 45.2% < threshold 60.0%, turning ON
[PUMP] Auto mode: humidity 65.0% >= threshold 60.0%, turning OFF
```

Nếu không thấy log:
1. Kiểm tra baud rate Serial Monitor là 115200
2. Kiểm tra task_pump được add vào main.py hay chưa
3. Kiểm tra config.py có INTERVAL_TASK_PUMP_MS hay chưa
