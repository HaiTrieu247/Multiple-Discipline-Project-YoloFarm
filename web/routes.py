"""
Flask API routes for YoLo Farm dashboard.
"""

from flask import Blueprint, jsonify, request
from model.device_state import DeviceState
from communication.mqtt_client import publish_command

api = Blueprint("api", __name__)


@api.route("/api/state")
def get_state():
    """Return current sensor + actuator state as JSON."""
    return jsonify(DeviceState.to_dict())


@api.route("/api/history")
def get_history():
    """Return historical lux & soil data for charts."""
    return jsonify(DeviceState.get_history())


# 💧 Bật tắt bơm (V10)
@api.route("/api/pump", methods=["POST"])
def set_pump():
    state = request.json.get("state", 0)
    publish_command("pump", state)
    DeviceState.pump_on = bool(int(state))
    return jsonify({"status": "ok", "pump": DeviceState.pump_on})


# 💡 Bật tắt đèn / máy bơm 2 (V11)
@api.route("/api/light", methods=["POST"])
def set_light():
    state = request.json.get("state", 0)
    publish_command("light", state)
    DeviceState.light_on = bool(int(state))
    return jsonify({"status": "ok", "light": DeviceState.light_on})