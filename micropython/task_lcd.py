# -*- coding: utf-8 -*-
"""
Lab 2 - LCD1602 over I2C.
Tu dong thu 2 kieu thu vien pho bien tren firmware OhStem:
- from aiot_lcd1602 import LCD1602
- from lcd_1602 import LCD1602
"""

from time import ticks_ms
from machine import SoftI2C, Pin
from yolobit import pin19, pin20
import task_i2c
import task_sensors

lcd = None
_lcd_mode = ""
_last_update = 0
_display_mode = 0  # 0 = T/H, 1 = SM/LUX


def _init_lcd():
    global lcd, _lcd_mode

    # Kieu 1: API AIOT block style (khong can tham so cong)
    try:
        from aiot_lcd1602 import LCD1602  # type: ignore

        lcd = LCD1602()
        _lcd_mode = "aiot_lcd1602"
        return True
    except Exception:
        pass

    # Kieu 2: API port-based tren mot so firmware OhStem
    try:
        from lcd_1602 import LCD1602  # type: ignore

        lcd = LCD1602(0)
        _lcd_mode = "lcd_1602"
        return True
    except Exception:
        pass

    # Kieu 3: fallback driver noi bo trong repo
    try:
        from lib.aiot.lcd1602_i2c import LCD1602I2C

        i2c = SoftI2C(scl=Pin(pin19.pin), sda=Pin(pin20.pin), freq=100000)
        found = i2c.scan()
        # LCD I2C thuong gap: 0x27/0x3F; module OhStem trong anh: 0x21/0x24.
        candidate_addrs = [0x21, 0x24, 0x27, 0x3F]
        for addr in candidate_addrs:
            if addr in found:
                lcd = LCD1602I2C(addr=addr)
                _lcd_mode = "lib.aiot.lcd1602_i2c@{}".format(hex(addr))
                return True
    except Exception:
        pass

    lcd = None
    _lcd_mode = ""
    return False


def task_init():
    global _last_update, _display_mode
    _last_update = 0
    _display_mode = 0

    if not _init_lcd():
        print("[LAB2][LCD] Khong khoi tao duoc LCD1602")
        return

    try:
        if hasattr(lcd, "backlight_on"):
            lcd.backlight_on()
        lcd.clear()
        lcd.move_to(0, 0)
        lcd.putstr("YoloFarm Ready")
        lcd.move_to(0, 1)
        lcd.putstr(_lcd_mode[:16])
        print("[LAB2][LCD] ready via", _lcd_mode)
    except Exception as err:
        print("[LAB2][LCD] init error:", err)


def task_run():
    global _last_update, _display_mode
    if not lcd:
        return

    now = ticks_ms()
    if now - _last_update < 2000:
        return
    _last_update = now

    try:
        # Xoay chiều giữa 2 chế độ hiển thị
        _display_mode = 1 - _display_mode
        
        if _display_mode == 0:
            # Hiển thị Nhiệt độ & Độ ẩm
            lcd.move_to(0, 0)
            if task_i2c.latest_temp is not None and task_i2c.latest_hum is not None:
                line1 = "T:{:.1f}C H:{:.0f}%".format(task_i2c.latest_temp, task_i2c.latest_hum)
                lcd.putstr((line1 + " " * 16)[:16])
            else:
                lcd.putstr("DHT20 waiting... ")
            lcd.move_to(0, 1)
            lcd.putstr("[Sensors]       ")
        else:
            # Hiển thị Độ ẩm đất & Ánh sáng
            lcd.move_to(0, 0)
            sm = task_sensors.get_soil_moisture()
            lux = task_sensors.get_light_level()
            line1 = "SM:{:.0f}% LUX:{}".format(sm, lux)
            lcd.putstr((line1 + " " * 16)[:16])
            lcd.move_to(0, 1)
            lcd.putstr("[Soil & Light]  ")
            
    except Exception as err:
        print("[LAB2][LCD] run error:", err)
