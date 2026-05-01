"""
Telemetry handler – receives MQTT data from board and updates DeviceState.

Automation (auto-water, light scheduling, GDD) runs on the YoloBit board.
PC only displays data and allows manual override via the web dashboard.
"""

import logging

from model.device_state import DeviceState
from controller.event_handler import EventBus

log = logging.getLogger(__name__)

# ──────────────────────────────────────────────
#  Telemetry handler (runs on every MQTT message)
# ──────────────────────────────────────────────

def handle_telemetry(data):
    """Process incoming sensor / command data from MQTT."""
    feed, value = data

    try:
        if feed == "V1":
            DeviceState.temperature = float(value)
        elif feed == "V2":
            DeviceState.humidity = float(value)
        elif feed == "V3":
            DeviceState.soil_moisture = float(value)
            DeviceState.update_status()
        elif feed == "V4":
            DeviceState.lux = float(value)
        elif feed == "V5":
            DeviceState.gdd = int(float(value))
        elif feed == "V6":
            DeviceState.status = str(value)
        elif feed == "V10":
            DeviceState.pump_on = value == "1"
        elif feed == "V11":
            DeviceState.light_on = value == "1"
    except (ValueError, TypeError) as exc:
        log.warning("Bad telemetry %s=%s: %s", feed, value, exc)

    # Push history snapshot on sensor data
    if feed in ("V3", "V4"):
        DeviceState.push_history()


def start():
    """No-op – automation runs on the board, not on PC."""
    log.info("Telemetry handler ready (automation disabled – board handles it)")


# ── Register EventBus listener ──
EventBus.on("mqtt_data", handle_telemetry)