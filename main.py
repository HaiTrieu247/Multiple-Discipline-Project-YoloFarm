# -*- coding: utf-8 -*-
"""
main.py - Yolobit MicroPython RTOS
Chạy các task theo event manager
"""
import time
from event_manager import *
import config
import task1
import task2
import task_gpio
import task_i2c
import task_lcd
import task_pump
import task_webserver_client
# Khởi tạo event manager
event_manager.reset()

# Gọi task_init()
task1.task_init()
task2.task_init()
task_gpio.task_init()
task_i2c.task_init()
task_lcd.task_init()
task_pump.task_init()
task_webserver_client.task_init()

# Đăng ký task_run() vào event_manager (timer event)
event_manager.add_timer_event(config.INTERVAL_TASK1_MS, task1.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK2_MS, task2.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK_GPIO_MS, task_gpio.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK_I2C_MS, task_i2c.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK_LCD_MS, task_lcd.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK_PUMP_MS, task_pump.task_run)
event_manager.add_timer_event(config.INTERVAL_TASK_WEBSERVER_CLIENT_MS, task_webserver_client.task_run)

# ===== Cấu hình máy bơm =====
task_pump.set_mode("auto")
task_pump.set_humidity_threshold(55.0)

# In ra serial
print("=== Yolobit MicroPython with Pump Control ===")
print("Mode: AUTO (humidity < 55%)")
print("=" * 60)
print()

while True:
    event_manager.run()
    time.sleep_ms(10)
