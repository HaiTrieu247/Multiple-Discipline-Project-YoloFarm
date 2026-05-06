# 🔧 Fix: Máy Bơm Không Chạy (Pin 10/13)

## ✅ Vấn Đề Đã Được Sửa

**Nguyên nhân:** task_pump.py sử dụng `from machine import Pin` + `Pin.value()` nhưng không import `from yolobit import *`, dẫn đến pin không được khởi tạo đúng theo chuẩn OhStem.

**Giải pháp:** Sửa task_pump.py để:
1. ✅ Import `from yolobit import *` (lấy pin10, pin13 từ yolobit module)
2. ✅ Sử dụng `PUMP_PIN.write_digital(state)` thay vì `Pin.value(state)`
3. ✅ Tạo PIN_MAP để dễ chọn pin 10 hoặc 13

## 📝 Thay Đổi Chính

### Trước (Sai)
```python
from machine import Pin  # ← Không import yolobit
import time

pump_pin = Pin(10, Pin.OUT)
pump_pin.value(0)  # Không hoạt động trên OhStem

def _set_pump(state):
    pump_pin.value(state)  # ← Sai
```

### Sau (Đúng)
```python
from yolobit import *  # ← Thêm dòng này
import time

PIN_NUMBER = 10
PIN_MAP = {
    10: pin10,  # pin10 từ yolobit
    13: pin13,  # pin13 từ yolobit
}
PUMP_PIN = PIN_MAP.get(PIN_NUMBER)
PUMP_PIN.write_digital(0)  # ✅ Đúng cách OhStem

def _set_pump(state):
    PUMP_PIN.write_digital(state)  # ✅ Sử dụng write_digital
```

## 🧪 Cách Test Máy Bơm

### 1. Test nhanh (file có sẵn)
```
1. Mở file: test_pump_simple.py
2. Upload qua PyMakr
3. Serial Monitor sẽ hiển thị:
   ✓ Máy bơm BẬT (cycle 0)
   ✗ Máy bơm TẮT
   ✓ Máy bơm BẬT (cycle 1)
   ...
4. Kiểm tra máy bơm có chạy (hoặc LED relay sáng)
5. Nhấn Ctrl+C để dừng
```

### 2. Test thủ công qua REPL
```python
# Trong REPL của PyMakr:
import task_pump
task_pump.task_init()
task_pump.set_mode("manual")

# Bật máy bơm
task_pump.set_pump_manual(1)
# → Xem Serial Monitor: [PUMP] Pump ON

# Tắt máy bơm
task_pump.set_pump_manual(0)
# → Xem Serial Monitor: [PUMP] Pump OFF
```

### 3. Test trong main.py
```python
# Trong main.py:
import task_pump

task_pump.task_init()
task_pump.set_mode("manual")
task_pump.set_pump_manual(1)  # Bật ngay khi khởi động

# Hoặc tự động theo độ ẩm:
task_pump.set_mode("auto")
task_pump.set_humidity_threshold(55.0)
```

## 🔍 Kiểm Tra Phần Cứng

Nếu máy bơm vẫn không chạy:

### 1. Kiểm tra Relay/Module Bơm
```
Yolobit Pin 10 → Relay Signal IN
Relay VCC → 3.3V hoặc 5V
Relay GND → GND (chung Yolobit)
Relay OUT+ → Motor +
Relay OUT- → Motor -
```

### 2. Kiểm tra LED Relay
- Pin 10 ghi HIGH (1) → LED relay phải sáng
- Pin 10 ghi LOW (0) → LED relay phải tắt

### 3. Kiểm tra Motor/Bơm
- Relay kích hoạt → Motor có âm thanh không?
- Kiểm tra nguồn 5V/12V của motor
- Kiểm tra dây kết nối

### 4. Test GPIO trực tiếp
```python
# Trong REPL, test pin 10 độc lập:
from yolobit import pin10

# Bật
pin10.write_digital(1)
# Xem relay có sáng không

# Tắt
pin10.write_digital(0)
# Xem relay tắt không
```

## 📊 Log Mẫu (Serial Monitor)

```
==================================================
🔧 Test Máy Bơm - Pin 10/13
==================================================
Máy bơm sẽ bật 2 giây, tắt 2 giây, lặp lại...
Kiểm tra LED trên relay hoặc âm thanh máy bơm
==================================================

Chương trình chạy. Nhấn Ctrl+C để dừng.

[PUMP] Initialized at Pin 10
[PUMP] Mode changed to: manual
✓ Máy bơm BẬT (cycle 0)
[PUMP] Pump ON
✗ Máy bơm TẮT
[PUMP] Pump OFF
✓ Máy bơm BẬT (cycle 1)
[PUMP] Pump ON
✗ Máy bơm TẮT
[PUMP] Pump OFF
...
```

## ⚙️ Cấu Hình Pin

Nếu muốn dùng Pin 13 thay vì Pin 10:

**Trong task_pump.py:**
```python
# Đổi dòng này:
PIN_NUMBER = 10  # ← Thay thành 13

# Thành:
PIN_NUMBER = 13  # ← Sử dụng pin13
```

Hoặc trong code:
```python
task_pump.PUMP_PIN = pin13  # Chuyển sang pin13
```

## 🎯 Chế Độ Hoạt Động

### Manual (Thủ công)
```python
task_pump.set_mode("manual")
task_pump.set_pump_manual(1)  # Bật
task_pump.set_pump_manual(0)  # Tắt
```

### Auto (Theo độ ẩm)
```python
task_pump.set_mode("auto")
task_pump.set_humidity_threshold(60.0)  # Bơm khi độ ẩm < 60%
# Cần task_i2c chạy để đọc DHT20
```

### Scheduled (Hẹn giờ)
```python
task_pump.set_mode("scheduled")
task_pump.set_schedule(6, 0, 22, 0, 15)  # 6h-22h, chạy 15s
```

## 📚 Tài Liệu Liên Quan

- **task_pump.py** - Code máy bơm (đã sửa)
- **test_pump_simple.py** - File test (mới tạo)
- **TASK_PUMP_GUIDE.md** - Hướng dẫn chi tiết
- **PUMP_QUICK_START.md** - Quick start

## ✅ Checklist Fix

- ✅ Import `from yolobit import *`
- ✅ Sử dụng `pin10`/`pin13` từ yolobit
- ✅ Dùng `write_digital()` để ghi GPIO
- ✅ Tạo test file đơn giản
- ✅ Hướng dẫn kiểm tra phần cứng

## 🎉 Tiếp Theo

1. **Test máy bơm:**
   - Upload `test_pump_simple.py`
   - Xem serial monitor
   - Kiểm tra máy bơm chạy

2. **Tích hợp vào main.py:**
   - Import task_pump
   - Khởi tạo + đăng ký event
   - Chọn chế độ (manual/auto/scheduled)

3. **Kết hợp webserver:**
   - Thêm task_webserver_client
   - Điều khiển từ dashboard

---

**Ngày sửa:** 2026-05-06  
**Trạng thái:** ✅ Đã Fix
