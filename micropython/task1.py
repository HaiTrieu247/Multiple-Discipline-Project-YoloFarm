# -*- coding: utf-8 -*-
"""
Lab 1 - LED blinky.
Nháy icon HEART/HEART_SMALL như nhịp tim để mô phỏng trạng thái LED.
"""

from yolobit import *

status = 0


def task_init():
    """Khởi tạo task 1 (chạy một lần khi bắt đầu chương trình)."""
    global status
    status = 0


def task_run():
    """Nháy đèn bằng cách đổi icon hiển thị."""
    global status
    status = 1 - status
    if status == 0:
        display.show(Image.HEART)
    else:
        display.show(Image.HEART_SMALL)
