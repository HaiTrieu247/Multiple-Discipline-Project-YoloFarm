# -*- coding: utf-8 -*-
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
_init_retry = 0
latest_temp = None
latest_hum = None
sensor_ok = False
_read_err_count = 0


def task_init():
    global dht, i2c, _scan_once, _init_retry, latest_temp, latest_hum, sensor_ok, _read_err_count
    _scan_once = False
    _init_retry = 0
    _read_err_count = 0
    latest_temp = None
    latest_hum = None
    sensor_ok = False
    i2c = SoftI2C(scl=Pin(pin19.pin), sda=Pin(pin20.pin), freq=100000)
    _try_init_dht(log_error=True)


def _try_init_dht(log_error=False):
    global dht, sensor_ok
    try:
        dht = DHT20()
        # Chi danh dau OK sau khi doc du lieu thanh cong.
        sensor_ok = False
        print("[LAB2][I2C] DHT20 ready")
        return True
    except Exception as err:
        dht = None
        sensor_ok = False
        if log_error:
            print("[LAB2][I2C] DHT20 error:", err)
        return False


def task_run():
    global dht, _scan_once, _init_retry, latest_temp, latest_hum, sensor_ok, _read_err_count

    if i2c and not _scan_once:
        _scan_once = True
        devices = i2c.scan()
        print("[LAB2][I2C] devices =", devices)

    if dht:
        try:
            temp = dht.dht20_temperature()
            hum = dht.dht20_humidity()
            latest_temp = temp
            latest_hum = hum
            sensor_ok = True
            _read_err_count = 0
            
            # Cập nhật task_sensors với dữ liệu nhiệt độ & độ ẩm
            try:
                import task_sensors
                task_sensors.set_temp_humidity(temp, hum)
            except:
                pass
            
            print("[LAB2][I2C] Temp={:.1f}C Hum={:.1f}%".format(temp, hum))
        except Exception as err:
            dht = None
            sensor_ok = False
            _read_err_count += 1
            if _read_err_count % 5 == 1:
                print("[LAB2][I2C] Read error:", err)
    else:
        # Retry khoi tao DHT20 theo chu ky de tranh loi ENODEV luc moi cap nguon.
        _init_retry += 1
        if _init_retry % 3 == 0:
            _try_init_dht(log_error=False)
