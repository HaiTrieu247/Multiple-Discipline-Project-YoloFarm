"""
Lab 2 - I2C peripherals.
Doc DHT20 qua I2C va scan dia chi thiet bi I2C.
"""

from machine import SoftI2C, Pin
from lib.aiot.aiot_dht20 import DHT20
from yolobit import pin19, pin20

dht = None
i2c = None
_scan_once = False


def task_init():
    global dht, i2c, _scan_once
    _scan_once = False
    i2c = SoftI2C(scl=Pin(pin19.pin), sda=Pin(pin20.pin), freq=100000)
    try:
        dht = DHT20()
        print("[LAB2][I2C] DHT20 ready")
    except Exception as err:
        dht = None
        print("[LAB2][I2C] DHT20 error:", err)


def task_run():
    global _scan_once

    if i2c and not _scan_once:
        _scan_once = True
        devices = i2c.scan()
        print("[LAB2][I2C] devices =", devices)

    if dht:
        try:
            temp = dht.dht20_temperature()
            hum = dht.dht20_humidity()
            print("[LAB2][I2C] Temp={:.1f}C Hum={:.1f}%".format(temp, hum))
        except Exception as err:
            print("[LAB2][I2C] Read error:", err)
