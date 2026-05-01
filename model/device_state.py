"""
Singleton device state – all class-level variables shared across the app.
Includes sensor history for chart rendering.
"""

import time
from collections import deque

MAX_HISTORY = 50


class DeviceState:
    # ── Sensor values ──────────────────────────
    temperature: float = 0.0
    humidity: float = 0.0
    soil_moisture: float = 0.0
    lux: float = 0.0
    gdd: int = 0
    status: str = "---"  # V6: "KHÔ" / "TỐT" / "ƯỚT"

    # ── Actuator states ────────────────────────
    pump_on: bool = False
    light_on: bool = False

    # ── History for charts ─────────────────────
    lux_history: deque = deque(maxlen=MAX_HISTORY)
    soil_history: deque = deque(maxlen=MAX_HISTORY)

    @classmethod
    def update_status(cls):
        """Derive V6 status from soil moisture."""
        if cls.soil_moisture < 50:
            cls.status = "KHÔ"
        elif cls.soil_moisture > 80:
            cls.status = "ƯỚT"
        else:
            cls.status = "TỐT"

    @classmethod
    def push_history(cls):
        """Append current lux & soil readings to history."""
        ts = time.strftime("%H:%M:%S")
        cls.lux_history.append({"time": ts, "value": cls.lux})
        cls.soil_history.append({"time": ts, "value": cls.soil_moisture})

    @classmethod
    def get_history(cls):
        return {
            "lux": list(cls.lux_history),
            "soil": list(cls.soil_history),
        }

    @classmethod
    def to_dict(cls):
        return {
            "temp": cls.temperature,
            "humidity": cls.humidity,
            "soil": cls.soil_moisture,
            "lux": cls.lux,
            "gdd": cls.gdd,
            "status": cls.status,
            "pump": cls.pump_on,
            "light": cls.light_on,
        }