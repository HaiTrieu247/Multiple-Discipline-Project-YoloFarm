# -*- coding: utf-8 -*-
"""
config.py - Cấu hình chương trình Yolobit MicroPython
"""
# ===== WiFi & Webserver (BẮT BUỘC cho webserver) =====
WIFI_SSID = "HCMUT-MEETING"
WIFI_PASSWORD = "hcmut@meeting"
WEBSERVER_IP = "10.127.5.101"
# ===== Chu kỳ task (milliseconds) =====
USE_BUILTIN_LED = False
LED_GPIO = 2
PIN_LED = "pin0"

INTERVAL_TASK1_MS = 1000
INTERVAL_TASK2_MS = 500
INTERVAL_TASK_GPIO_MS = 100
INTERVAL_TASK_I2C_MS = 2000
INTERVAL_TASK_LCD_MS = 200
INTERVAL_TASK_PUMP_MS = 500
INTERVAL_TASK_SENSORS_MS = 2000
INTERVAL_TASK_WEBSERVER_CLIENT_MS = 1000
# Task kiểm thử thư viện lib (MQTT, NTP, AIOT, Event)
INTERVAL_TASK_MQTT_MS = 5000
INTERVAL_TASK_NTP_MS = 5000
INTERVAL_TASK_AIOT_MS = 3000
INTERVAL_TASK_EVENT_MS = 2000

# Task AI
INTERVAL_TASK_AI_MS = 3000
# Task thu thập data
INTERVAL_TASK_COLLECT_MS = 2000
# Tùy chọn: MQTT (để trống nếu không dùng)
# MQTT_SERVER = "mqtt.ohstem.vn"
# MQTT_PORT = 1883
# MQTT_USER = ""
# MQTT_PASSWORD = ""
