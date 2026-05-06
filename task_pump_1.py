# -*- coding: utf-8 -*-
from machine import Pin
import time

# ========== Biến trạng thái toàn cục ==========
pump_state = 0  # 0 = OFF, 1 = ON
mode = "manual"  # "manual" hoặc "auto" hoặc "scheduled"
pump_pin = None

# Ngưỡng độ ẩm (bật máy bơm nếu độ ẩm < ngưỡng)
humidity_threshold = 50.0

# Thời gian hẹn giờ (scheduler)
schedule_start_hour = 6    # bắt đầu từ 6h sáng
schedule_start_min = 0
schedule_end_hour = 22     # kết thúc lúc 22h tối
schedule_end_min = 0
schedule_duration_sec = 10  # chạy máy bơm trong 10 giây

# Trạng thái scheduler
_schedule_pump_running_at = None  # Thời điểm bắt đầu chạy máy bơm theo schedule (milli giây)
_last_button_a = 0


def task_init():
    """Khởi tạo pin, biến trạng thái"""
    global pump_state, mode, pump_pin, _last_button_a
    global _schedule_pump_running_at
    
    pump_state = 0
    mode = "manual"  # Mặc định manual
    _last_button_a = 0
    _schedule_pump_running_at = None
    
    # Khởi tạo pin 10 (hoặc pin 13 nếu dùng chung cắm)
    # Pin 10 = GPIO 10, Pin 13 = GPIO 13
    pump_pin = Pin(10, Pin.OUT)
    pump_pin.value(0)
    print("[PUMP] Initialized at Pin 10")


def set_mode(new_mode):
    """
    Thay đổi chế độ hoạt động.
    new_mode: "manual", "auto", "scheduled"
    """
    global mode, pump_state
    mode = new_mode
    print(f"[PUMP] Mode changed to: {mode}")
    if mode == "manual":
        # Khi chuyển sang manual, tắt máy bơm
        pump_state = 0
        _set_pump(0)


def set_pump_manual(state):
    """
    Bật/tắt máy bơm thủ công (khi mode = "manual")
    """
    global pump_state, mode
    if mode != "manual":
        print("[PUMP] Cannot set manual state in non-manual mode")
        return False
    pump_state = state
    _set_pump(state)
    return True


def set_humidity_threshold(threshold):
    """Tùy chỉnh ngưỡng độ ẩm (% RH)"""
    global humidity_threshold
    humidity_threshold = float(threshold)
    print(f"[PUMP] Humidity threshold set to {humidity_threshold}%")


def set_schedule(start_hour, start_min, end_hour, end_min, duration_sec):
    """
    Tùy chỉnh thời gian hẹn giờ.
    - start_hour, start_min: giờ bắt đầu (24h)
    - end_hour, end_min: giờ kết thúc
    - duration_sec: máy bơm chạy bao lâu trong khoảng thời gian (giây)
    """
    global schedule_start_hour, schedule_start_min
    global schedule_end_hour, schedule_end_min, schedule_duration_sec
    
    schedule_start_hour = start_hour
    schedule_start_min = start_min
    schedule_end_hour = end_hour
    schedule_end_min = end_min
    schedule_duration_sec = duration_sec
    print(f"[PUMP] Schedule set: {start_hour:02d}:{start_min:02d} - {end_hour:02d}:{end_min:02d}, duration {duration_sec}s")


def _set_pump(state):
    """
    Thiết lập trạng thái thực tế của pin máy bơm
    state: 0 = OFF, 1 = ON
    """
    global pump_state
    if pump_pin:
        pump_pin.value(state)
        pump_state = state
        status_str = "ON" if state else "OFF"
        print(f"[PUMP] Pump {status_str}")


def _button_a_pressed():
    """
    Kiểm tra nút Button A có được nhấn hay không.
    Trả về True khi có cạnh lên (nhấn xuống).
    Giả sử bạn có yolobit module với button_a
    """
    try:
        from yolobit import button_a
        current = 1 if button_a.is_pressed() else 0
        return current == 1
    except:
        return False


def _get_current_humidity():
    """
    Lấy độ ẩm từ DHT20 (được đọc bởi task_i2c.py).
    Nếu task_i2c chưa khởi tạo hoặc lỗi, trả về None.
    """
    try:
        import task_i2c
        if task_i2c.sensor_ok and task_i2c.latest_hum is not None:
            return task_i2c.latest_hum
    except:
        pass
    return None


def _is_in_schedule_window():
    """
    Kiểm tra thời gian hiện tại có nằm trong khung thời gian hẹn giờ hay không.
    Trả về True nếu đang trong khung giờ.
    """
    try:
        import config
        # Giả sử có hàm ntp để lấy thời gian
        # Nếu không có NTP, bạn có thể dùng đơn giản như sau:
        # Cách 1: Dùng time.time() nếu có NTP (từ task_ntp)
        # Cách 2: Dùng RTC của Yolobit (nếu có)
        # Cách 3: Sử dụng một biến counter thay vì thời gian thực
        
        # Tạm thời, dùng cách đơn giản: lấy giây từ time.time()
        # và tính giờ từ giây (chỉ hoạt động trong 1 ngày, từ 0:00 UTC)
        elapsed_sec = int(time.time())
        seconds_in_day = elapsed_sec % 86400  # Giây trong ngày (86400 = 24*60*60)
        
        current_hour = seconds_in_day // 3600
        current_min = (seconds_in_day % 3600) // 60
        
        # So sánh thời gian
        current_total_min = current_hour * 60 + current_min
        start_total_min = schedule_start_hour * 60 + schedule_start_min
        end_total_min = schedule_end_hour * 60 + schedule_end_min
        
        in_window = start_total_min <= current_total_min < end_total_min
        return in_window
    except:
        return False


def task_run():
    """
    Chạy máy bơm theo chế độ.
    Gọi lặp lại theo chu kỳ từ event_manager.
    """
    global pump_state, mode, _last_button_a, _schedule_pump_running_at
    
    # === Kiểm tra Button A để chuyển mode ===
    if _button_a_pressed():
        if mode == "manual":
            # Nhấn nút A trong mode manual: bật/tắt máy bơm
            _set_pump(1 - pump_state)
        print(f"[PUMP] Button A pressed, mode={mode}, state={pump_state}")
    
    # === Mode MANUAL: chỉ bật/tắt khi gọi set_pump_manual() ===
    if mode == "manual":
        pass  # Không làm gì thêm
    
    # === Mode AUTO: dựa vào độ ẩm ===
    elif mode == "auto":
        humidity = _get_current_humidity()
        if humidity is not None:
            if humidity < humidity_threshold and pump_state == 0:
                _set_pump(1)
                print(f"[PUMP] Auto mode: humidity {humidity}% < threshold {humidity_threshold}%, turning ON")
            elif humidity >= humidity_threshold and pump_state == 1:
                _set_pump(0)
                print(f"[PUMP] Auto mode: humidity {humidity}% >= threshold {humidity_threshold}%, turning OFF")
    
    # === Mode SCHEDULED: hẹn giờ bật ===
    elif mode == "scheduled":
        in_window = _is_in_schedule_window()
        
        if in_window:
            # Đang trong khung giờ
            if _schedule_pump_running_at is None:
                # Bắt đầu chạy máy bơm
                _schedule_pump_running_at = time.ticks_ms()
                _set_pump(1)
                print(f"[PUMP] Scheduled mode: entering time window, pump ON")
            else:
                # Kiểm tra thời gian chạy đã đủ hay chưa
                elapsed_ms = time.ticks_diff(time.ticks_ms(), _schedule_pump_running_at)
                if elapsed_ms >= schedule_duration_sec * 1000:
                    # Đã chạy đủ thời gian, tắt
                    _set_pump(0)
                    _schedule_pump_running_at = None
                    print(f"[PUMP] Scheduled mode: pump duration {schedule_duration_sec}s reached, turning OFF")
        else:
            # Ngoài khung giờ
            if pump_state == 1:
                _set_pump(0)
                _schedule_pump_running_at = None
                print(f"[PUMP] Scheduled mode: outside time window, turning OFF")
