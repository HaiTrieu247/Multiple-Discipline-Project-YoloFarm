# -*- coding: utf-8 -*-
"""
Lab 1 - RGB indicator blinky.
Dùng AIOT RGB LED (nếu có) để đổi màu chỉ thị.
"""

try:
    from yolobit import *
    from lib.aiot.aiot_rgbled import RGBLed
    _rgb_ok = True
except Exception:
    _rgb_ok = False

status = 0
rgb = None


def task_init():
    """Khởi tạo RGB LED nếu phần cứng sẵn sàng."""
    global status, rgb
    status = 0
    if _rgb_ok:
        try:
            rgb = RGBLed(pin14.pin, 4)
        except Exception:
            rgb = None


def task_run():
    """Đổi màu RGB theo chu kỳ hoặc log nếu không có phần cứng."""
    global status
    status = 1 - status
    if rgb:
        if status == 0:
            rgb.show(0, (255, 0, 0))
        else:
            rgb.show(0, (0, 0, 255))
    else:
        if status == 0:
            print("[LAB1] RGB indicator: RED")
        else:
            print("[LAB1] RGB indicator: BLUE")
