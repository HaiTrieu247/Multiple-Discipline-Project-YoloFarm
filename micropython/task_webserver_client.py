# -*- coding: utf-8 -*-
import urequests
import json
import time

# Cấu hình webserver
SERVER_IP = None  # Sẽ được gán từ config.py
SERVER_PORT = 5000
SERVER_URL = None

# Trạng thái
client_ok = False
wifi_connected = False
_last_send_time = 0
_send_interval_ms = 3000  # Gửi mỗi 3 giây


def task_init():
    """Khởi tạo: lấy cấu hình từ config.py"""
    global SERVER_IP, SERVER_URL, client_ok, wifi_connected
    
    try:
        import config
        SERVER_IP = getattr(config, 'WEBSERVER_IP', '192.168.1.100')
        SERVER_URL = "http://{}:{}".format(SERVER_IP, SERVER_PORT)
        
        # Cố gắng kết nối WiFi nếu có cấu hình
        from lib.mqtt import mqtt
        if getattr(config, 'WIFI_SSID', None) and getattr(config, 'WIFI_PASSWORD', None):
            try:
                mqtt.connect_wifi(config.WIFI_SSID, config.WIFI_PASSWORD)
                if mqtt.wifi_connected():
                    wifi_connected = True
                    client_ok = True
                    print("[WEBSERVER] WiFi connected, server: {}".format(SERVER_URL))
                else:
                    print("[WEBSERVER] WiFi connection failed")
            except Exception as e:
                print("[WEBSERVER] WiFi error: {}".format(e))
        else:
            print("[WEBSERVER] No WiFi config in config.py")
    except Exception as e:
        print("[WEBSERVER] init error: {}".format(e))


def _collect_sensor_data():
    """
    Thu thập dữ liệu từ các task.
    Trả về dictionary với thông tin hiện tại.
    """
    data = {
        "timestamp": time.time(),
        "temperature": None,
        "humidity": None,
        "soil_moisture": None,
        "light_level": None,
        "pump_state": 0,
        "pump_mode": "manual",
    }
    
    try:
        # Lấy dữ liệu từ task_i2c
        import task_i2c
        if task_i2c.sensor_ok:
            data["temperature"] = task_i2c.latest_temp
            data["humidity"] = task_i2c.latest_hum
    except:
        pass
    
    try:
        # Lấy dữ liệu từ task_sensors (SM, LUX)
        import task_sensors
        data["soil_moisture"] = task_sensors.get_soil_moisture()
        data["light_level"] = task_sensors.get_light_level()
    except:
        pass
    
    try:
        # Lấy dữ liệu từ task_pump
        import task_pump
        data["pump_state"] = task_pump.pump_state
        data["pump_mode"] = task_pump.mode
        data["humidity_threshold"] = task_pump.humidity_threshold
    except:
        pass
    
    return data


def _send_data_to_server(data):
    """
    Gửi dữ liệu lên webserver qua HTTP POST.
    
    Request:
      POST http://SERVER_IP:5000/api/data
      Content-Type: application/json
      Body: {temperature, humidity, pump_state, ...}
    """
    if not client_ok or not wifi_connected or not SERVER_URL:
        return False
    
    try:
        from lib.mqtt import mqtt
        if not mqtt.wifi_connected():
            return False
        
        # Chuẩn bị dữ liệu JSON
        json_data = json.dumps(data)
        
        # Gửi POST
        response = urequests.post(
            "{}/api/data".format(SERVER_URL),
            data=json_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            response.close()
            return True
        else:
            print("[WEBSERVER] POST failed: {}".format(response.status_code))
            response.close()
            return False
    except Exception as e:
        print("[WEBSERVER] send error: {}".format(e))
        return False


def _fetch_command_from_server():
    """
    Lấy lệnh từ webserver qua HTTP GET.
    
    Response:
      {
        "command": "set_mode",
        "params": {"mode": "auto"}
      }
    """
    if not client_ok or not wifi_connected or not SERVER_URL:
        return None
    
    try:
        from lib.mqtt import mqtt
        if not mqtt.wifi_connected():
            return None
        
        # Lấy lệnh từ server
        response = urequests.get(
            "{}/api/command".format(SERVER_URL),
            timeout=5
        )
        
        if response.status_code == 200:
            try:
                command = json.loads(response.text)
                response.close()
                return command
            except:
                response.close()
                return None
        else:
            response.close()
            return None
    except Exception as e:
        print("[WEBSERVER] fetch error: {}".format(e))
        return None


def _execute_command(command):
    """
    Thực hiện lệnh từ webserver.
    
    Các lệnh hỗ trợ:
      - "set_pump_mode": {"mode": "manual|auto|scheduled"}
      - "set_pump_state": {"state": 0|1}
      - "set_humidity_threshold": {"threshold": 50.0}
      - "set_schedule": {"start_hour": 6, "start_min": 0, "end_hour": 22, "end_min": 0, "duration_sec": 15}
    """
    if not command:
        return False
    
    try:
        cmd = command.get("command")
        params = command.get("params", {})
        
        if cmd == "set_pump_mode":
            import task_pump
            mode = params.get("mode", "manual")
            task_pump.set_mode(mode)
            print("[WEBSERVER] Executed: set_pump_mode({})".format(mode))
            return True
        
        elif cmd == "set_pump_state":
            import task_pump
            state = int(params.get("state", 0))
            task_pump.set_pump_manual(state)
            print("[WEBSERVER] Executed: set_pump_state({})".format(state))
            return True
        
        elif cmd == "set_humidity_threshold":
            import task_pump
            threshold = float(params.get("threshold", 50.0))
            task_pump.set_humidity_threshold(threshold)
            print("[WEBSERVER] Executed: set_humidity_threshold({})".format(threshold))
            return True
        
        elif cmd == "set_schedule":
            import task_pump
            task_pump.set_schedule(
                start_hour=int(params.get("start_hour", 6)),
                start_min=int(params.get("start_min", 0)),
                end_hour=int(params.get("end_hour", 22)),
                end_min=int(params.get("end_min", 0)),
                duration_sec=int(params.get("duration_sec", 10))
            )
            print("[WEBSERVER] Executed: set_schedule")
            return True
        
        else:
            print("[WEBSERVER] Unknown command: {}".format(cmd))
            return False
    
    except Exception as e:
        print("[WEBSERVER] execute error: {}".format(e))
        return False


def task_run():
    """
    Mỗi chu kỳ:
      1. Thu thập dữ liệu
      2. Gửi lên webserver (mỗi 3 giây)
      3. Lấy lệnh từ webserver
      4. Thực hiện lệnh
    """
    global _last_send_time, wifi_connected
    
    # Kiểm tra WiFi
    try:
        from lib.mqtt import mqtt
        wifi_connected = mqtt.wifi_connected()
    except:
        wifi_connected = False
    
    # Thu thập dữ liệu
    data = _collect_sensor_data()
    
    # Gửi dữ liệu (mỗi 3 giây)
    now_ms = time.ticks_ms()
    if time.ticks_diff(now_ms, _last_send_time) >= _send_interval_ms:
        if _send_data_to_server(data):
            _last_send_time = now_ms
    
    # Lấy và thực hiện lệnh
    command = _fetch_command_from_server()
    if command:
        _execute_command(command)
