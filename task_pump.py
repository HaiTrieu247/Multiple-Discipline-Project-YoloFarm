# -*- coding: utf-8 -*-
"""
Task điều khiển máy bơm trên pin 10/13 (GPIO I/O).

Cách sử dụng:
  import task_pump
  task_pump.task_init()
  
  # Chế độ Manual
  task_pump.set_mode("manual")
  task_pump.set_pump_manual(1)  # Bật
  task_pump.set_pump_manual(0)  # Tắt
  
  # Chế độ Auto
  task_pump.set_mode("auto")
  task_pump.set_humidity_threshold(60.0)
  
  # Chế độ Scheduled
  task_pump.set_mode("scheduled")
  task_pump.set_schedule(6, 0, 22, 0, 15)  # 6h-22h, chạy 15s
"""

from yolobit import *
import time

# ========== Cấu hình Pin ==========
# Chọn PIN_NUMBER = 10 hoặc 13
PIN_NUMBER = 10
PUMP_PIN = None  # Sẽ được khởi tạo trong task_init()

# ========== Biến trạng thái toàn cục ==========
pump_state = 0  # 0 = OFF, 1 = ON
mode = "manual"  # "manual", "auto", "scheduled"
humidity_threshold = 50.0

# Thời gian hẹn giờ
schedule_start_hour = 6
schedule_start_min = 0
schedule_end_hour = 22
schedule_end_min = 0
schedule_duration_sec = 10
schedule_interval_sec = 3600  # Chu kỳ lặp lại (giây), mặc định 1 tiếng

# Trạng thái scheduler
_schedule_pump_running_at = None
_schedule_last_off_at = None  # Thời điểm bơm tắt lần cuối (để tính interval)
_last_button_a = 0


def task_init():
    """Khởi tạo pin, biến trạng thái"""
    global pump_state, mode, PUMP_PIN, _last_button_a, _schedule_pump_running_at, _schedule_last_off_at
    
    pump_state = 0
    mode = "manual"
    _last_button_a = 0
    _schedule_pump_running_at = None
    _schedule_last_off_at = None
    
    # Khởi tạo PUMP_PIN từ yolobit module
    try:
        if PIN_NUMBER == 10:
            PUMP_PIN = pin10
        elif PIN_NUMBER == 13:
            PUMP_PIN = pin13
        else:
            print(f"[PUMP] ERROR: PIN_NUMBER {PIN_NUMBER} not valid (use 10 or 13)")
            return
    except Exception as e:
        print(f"[PUMP] ERROR initializing pin: {e}")
        return
    
    if PUMP_PIN is None:
        print(f"[PUMP] ERROR: Pin {PIN_NUMBER} not available")
        return
    
    # Tắt máy bơm khi khởi động
    PUMP_PIN.write_digital(0)
    print(f"[PUMP] Initialized at Pin {PIN_NUMBER}")


def set_mode(new_mode):
    """
    Thay đổi chế độ hoạt động.
    new_mode: "manual", "auto", "scheduled"
    """
    global mode, pump_state
    mode = new_mode
    print(f"[PUMP] Mode changed to: {mode}")
    if mode == "manual":
        pump_state = 0
        _set_pump(0)


def set_pump_manual(state):
    """
    Bật/tắt máy bơm thủ công (khi mode = "manual")
    state: 0 = OFF, 1 = ON
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


def set_schedule(start_hour, start_min, end_hour, end_min, duration_sec, interval_sec=3600):
    """
    Tùy chỉnh thời gian hẹn giờ.
    interval_sec: khoảng cách giữa các lần bơm (giây). Mặc định 3600 = 1 tiếng.
    """
    global schedule_start_hour, schedule_start_min
    global schedule_end_hour, schedule_end_min, schedule_duration_sec, schedule_interval_sec
    global _schedule_pump_running_at, _schedule_last_off_at
    
    schedule_start_hour = start_hour
    schedule_start_min = start_min
    schedule_end_hour = end_hour
    schedule_end_min = end_min
    schedule_duration_sec = duration_sec
    schedule_interval_sec = interval_sec
    # Reset trạng thái để bơm chạy ngay lần đầu
    _schedule_pump_running_at = None
    _schedule_last_off_at = None
    print(f"[PUMP] Schedule set: {start_hour:02d}:{start_min:02d} - {end_hour:02d}:{end_min:02d}, duration {duration_sec}s, interval {interval_sec}s")


def _set_pump(state):
    """
    Thiết lập trạng thái thực tế của pin máy bơm.
    state: 0 = OFF, 1 = ON
    """
    global pump_state, PUMP_PIN
    
    if PUMP_PIN is None:
        return
    
    # Ghi trạng thái GPIO sử dụng write_digital (như mã mẫu OhStem)
    PUMP_PIN.write_digital(state)
    pump_state = state
    
    status_str = "ON" if state else "OFF"
    print(f"[PUMP] Pump {status_str}")


def _button_a_pressed():
    """
    Kiểm tra nút Button A có được nhấn hay không.
    """
    try:
        current = 1 if button_a.is_pressed() else 0
        return current == 1
    except:
        return False


def _get_current_humidity():
    """
    Lấy độ ẩm từ DHT20 (được đọc bởi task_i2c.py).
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
    """
    try:
        # Sử dụng time.localtime() - ổn định hơn time.time()
        # Trả về tuple: (year, month, day, hour, minute, second, weekday, yearday)
        t = time.localtime()
        current_hour = t[3]  # hour
        current_min = t[4]   # minute
        
        current_total_min = current_hour * 60 + current_min
        start_total_min = schedule_start_hour * 60 + schedule_start_min
        end_total_min = schedule_end_hour * 60 + schedule_end_min
        
        in_window = start_total_min <= current_total_min < end_total_min
        return in_window
    except Exception as e:
        print(f"[PUMP] Error in schedule check: {e}")
        return False


def task_run():
    """
    Chạy máy bơm theo chế độ.
    """
    global pump_state, mode, _last_button_a, _schedule_pump_running_at, _schedule_last_off_at
    
    # === Kiểm tra Button A ===
    if _button_a_pressed():
        if mode == "manual":
            _set_pump(1 - pump_state)
        print(f"[PUMP] Button A pressed, mode={mode}, state={pump_state}")
    
    # === Mode MANUAL ===
    if mode == "manual":
        pass
    
    # === Mode AUTO ===
    elif mode == "auto":
        humidity = _get_current_humidity()
        if humidity is not None:
            if humidity < humidity_threshold and pump_state == 0:
                _set_pump(1)
                print(f"[PUMP] Auto: humidity {humidity}% < {humidity_threshold}%, ON")
            elif humidity >= humidity_threshold and pump_state == 1:
                _set_pump(0)
                print(f"[PUMP] Auto: humidity {humidity}% >= {humidity_threshold}%, OFF")
    
    # === Mode SCHEDULED ===
    elif mode == "scheduled":
        in_window = _is_in_schedule_window()
        now_ms = time.ticks_ms()
        
        if in_window:
            if _schedule_pump_running_at is not None:
                # Đang bơm → kiểm tra hết duration chưa
                elapsed_ms = time.ticks_diff(now_ms, _schedule_pump_running_at)
                if elapsed_ms >= schedule_duration_sec * 1000:
                    _set_pump(0)
                    _schedule_pump_running_at = None
                    _schedule_last_off_at = now_ms
                    print(f"[PUMP] Scheduled: duration {schedule_duration_sec}s reached, OFF. Next in {schedule_interval_sec}s")
            else:
                # Chưa bơm → kiểm tra đã đủ interval chưa
                should_start = False
                if _schedule_last_off_at is None:
                    # Chưa từng chạy → bật ngay
                    should_start = True
                else:
                    # Đã chạy trước đó → chờ đủ interval
                    wait_ms = time.ticks_diff(now_ms, _schedule_last_off_at)
                    if wait_ms >= schedule_interval_sec * 1000:
                        should_start = True
                
                if should_start:
                    _schedule_pump_running_at = now_ms
                    _set_pump(1)
                    print(f"[PUMP] Scheduled: ON (duration {schedule_duration_sec}s)")
        else:
            if pump_state == 1:
                _set_pump(0)
            _schedule_pump_running_at = None
            _schedule_last_off_at = None
            # Khi ra khỏi window, reset để lần vào window sau chạy ngay
