# -*- coding: utf-8 -*-

USE_BUILTIN_LED = False
LED_GPIO = 2
PIN_LED = "pin0"

INTERVAL_TASK1_MS = 1000
INTERVAL_TASK2_MS = 500
INTERVAL_TASK_GPIO_MS = 100
INTERVAL_TASK_I2C_MS = 2000
INTERVAL_TASK_LCD_MS = 200

# Task kiểm thử thư viện lib (MQTT, NTP, AIOT, Event)
INTERVAL_TASK_MQTT_MS = 5000
INTERVAL_TASK_NTP_MS = 5000
INTERVAL_TASK_AIOT_MS = 3000
INTERVAL_TASK_EVENT_MS = 2000

# Task AI
INTERVAL_TASK_AI_MS = 3000
# Task thu thập data (bật khi cần thu thập, tắt khi chạy AI)
INTERVAL_TASK_COLLECT_MS = 2000

# Tùy chọn: WiFi và MQTT cho task_mqtt / NTP (để trống nếu không dùng)
# WIFI_SSID = "TenWiFi"
# WIFI_PASSWORD = "MatKhau"
# MQTT_SERVER = "mqtt.ohstem.vn"
# MQTT_PORT = 1883
# MQTT_USER = ""
# MQTT_PASSWORD = ""
