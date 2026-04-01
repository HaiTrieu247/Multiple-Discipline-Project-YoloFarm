"""
Lab 2 - GPIO peripherals.
- Nut A: bat/tat LED onboard.
- Nut B: bat/tat relay output (gia lap qua GPIO2).
"""

from yolobit import *
from machine import Pin

led_state = 0
relay_state = 0
_last_a = 0
_last_b = 0
relay_pin = None


def task_init():
    global led_state, relay_state, _last_a, _last_b, relay_pin
    led_state = 0
    relay_state = 0
    _last_a = 0
    _last_b = 0
    relay_pin = Pin(2, Pin.OUT)
    relay_pin.value(0)
    display.clear()


def _pressed_now(button, last):
    current = 1 if button.is_pressed() else 0
    pressed_edge = current == 1 and last == 0
    return current, pressed_edge


def task_run():
    global led_state, relay_state, _last_a, _last_b

    _last_a, a_pressed = _pressed_now(button_a, _last_a)
    _last_b, b_pressed = _pressed_now(button_b, _last_b)

    if a_pressed:
        led_state = 1 - led_state
        if led_state:
            display.show(Image.HAPPY)
        else:
            display.clear()
        print("[LAB2][GPIO] LED =", led_state)

    if b_pressed:
        relay_state = 1 - relay_state
        relay_pin.value(relay_state)
        print("[LAB2][GPIO] RELAY(GPIO2) =", relay_state)
