# -*- coding: utf-8 -*-
"""
Task đọc cảm biến SM (độ ẩm đất) và LUX (ánh sáng).

Cách sử dụng:
  import task_sensors
  task_sensors.task_init()
  
  # Gọi lặp lại trong vòng lặp chính:
  event_manager.add_timer_event(config.INTERVAL_TASK_SENSORS_MS, task_sensors.task_run)
  
  # Lấy dữ liệu:
  soil_moisture = task_sensors.get_soil_moisture()
  light_level = task_sensors.get_light_level()
"""

from yolobit import pin1, pin2
from time import ticks_ms
import time

# ========== Cấu hình ==========
SOIL_MOISTURE_PIN = pin1    # Pin 1 - Cảm biến độ ẩm đất
LIGHT_LEVEL_PIN = pin2      # Pin 2 - Cảm biến ánh sáng

# Hằng số chuyển đổi
SM_MIN_ADC = 0
SM_MAX_ADC = 4096
SM_MIN_PERCENT = 0
SM_MAX_PERCENT = 100

LUX_MIN_ADC = 0
LUX_MAX_ADC = 4096

# ========== Biến trạng thái ==========
soil_moisture = 0       # 0-100%
light_level = 0         # 0-4096
temp = 0               # Nhiệt độ từ DHT20
humidity = 0           # Độ ẩm từ DHT20

# Thống kê & trạng thái
sensor_ok = False
_last_read_time = 0
_read_interval_ms = 2000  # Đọc cảm biến mỗi 2 giây

# MQTT (nếu được cấu hình)
mqtt = None
mqtt_ok = False


def task_init():
    """Khởi tạo: cố gắng kết nối MQTT"""
    global mqtt, mqtt_ok, sensor_ok, _last_read_time
    
    try:
        # Cố gắng import MQTT
        try:
            from lib.mqtt import mqtt as mqtt_instance
            mqtt = mqtt_instance
            mqtt_ok = True
            print("[SENSORS] MQTT initialized")
        except:
            print("[SENSORS] MQTT not available, will use webserver only")
        
        sensor_ok = True
        _last_read_time = ticks_ms()
        print("[SENSORS] Task initialized - SM on pin1, LUX on pin2")
        
    except Exception as e:
        print(f"[SENSORS] Init error: {e}")
        sensor_ok = False


def _translate(value, in_min, in_max, out_min, out_max):
    """Chuyển đổi giá trị từ khoảng này sang khoảng khác."""
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)


def _read_sensors():
    """Đọc giá trị thô từ cảm biến."""
    global soil_moisture, light_level
    
    try:
        # Đọc SM từ pin1 (analog)
        sm_adc = SOIL_MOISTURE_PIN.read_analog()
        soil_moisture = _translate(sm_adc, SM_MIN_ADC, SM_MAX_ADC, SM_MIN_PERCENT, SM_MAX_PERCENT)
        
        # Đọc LUX từ pin2 (analog)
        light_level = LIGHT_LEVEL_PIN.read_analog()
        
        return True
        
    except Exception as e:
        print(f"[SENSORS] Read error: {e}")
        return False


def _publish_mqtt():
    """Gửi dữ liệu lên MQTT broker."""
    global mqtt, mqtt_ok, soil_moisture, light_level, temp, humidity
    
    if not mqtt_ok or mqtt is None:
        return
    
    try:
        # Publish SM, LUX
        mqtt.publish('SM', soil_moisture)
        mqtt.publish('LUX', light_level)
        
    except Exception as e:
        print(f"[SENSORS] MQTT publish error: {e}")


def task_run():
    """Chạy lặp lại mỗi khoảng thời gian."""
    global _last_read_time, _read_interval_ms
    
    if not sensor_ok:
        return
    
    now = ticks_ms()
    if now - _last_read_time < _read_interval_ms:
        return
    
    _last_read_time = now
    
    # Đọc cảm biến
    if _read_sensors():
        # Gửi lên MQTT nếu có
        _publish_mqtt()


# ========== Public API ==========

def get_soil_moisture():
    """Lấy độ ẩm đất (0-100%)."""
    return soil_moisture


def get_light_level():
    """Lấy mức ánh sáng (0-4096)."""
    return light_level


def set_temp_humidity(t, h):
    """Cập nhật nhiệt độ & độ ẩm từ DHT20 (để hiển thị LCD)."""
    global temp, humidity
    temp = t
    humidity = h


def get_all_sensor_data():
    """Lấy tất cả dữ liệu cảm biến dưới dạng dict."""
    return {
        "soil_moisture": soil_moisture,
        "light_level": light_level,
        "temperature": temp,
        "humidity": humidity,
    }
