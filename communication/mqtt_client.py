"""
MQTT client for OhStem broker (mqtt.ohstem.vn).
Uses paho-mqtt v2 callback API.
"""

import logging
import paho.mqtt.client as mqtt
from controller.event_handler import EventBus
from communication.protocol import (
    TELEMETRY_TOPICS,
    COMMAND_TOPICS,
    to_full_topic,
    feed_from_topic,
    USERNAME,
)

log = logging.getLogger(__name__)

BROKER = "mqtt.ohstem.vn"
PORT = 1883

# paho-mqtt v2 requires CallbackAPIVersion
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)


def connect():
    """Connect to OhStem MQTT broker and start background loop."""
    client.username_pw_set(USERNAME, "")
    client.on_connect = _on_connect
    client.on_message = _on_message

    log.info("Connecting to MQTT broker %s:%d …", BROKER, PORT)
    client.connect(BROKER, PORT)
    client.loop_start()


def _on_connect(client, userdata, flags, reason_code, properties=None):
    """Subscribe to all telemetry + command topics after successful connect."""
    log.info("MQTT connected (rc=%s)", reason_code)

    # Subscribe telemetry feeds
    for feed in TELEMETRY_TOPICS.values():
        full = to_full_topic(feed)
        client.subscribe(full)
        log.info("  subscribed → %s", full)

    # Subscribe command feeds (to sync actuator state from external sources)
    for feed in COMMAND_TOPICS.values():
        full = to_full_topic(feed)
        client.subscribe(full)
        log.info("  subscribed → %s", full)


def _on_message(client, userdata, msg):
    """Route incoming message to EventBus."""
    feed = feed_from_topic(msg.topic)
    if feed is None:
        log.warning("Unknown topic: %s", msg.topic)
        return
    payload = msg.payload.decode()
    log.debug("MQTT ← %s = %s", feed, payload)
    EventBus.emit("mqtt_data", (feed, payload))


def publish_command(device: str, value):
    """Publish a command to the broker.  device = 'pump' | 'light'."""
    feed = COMMAND_TOPICS[device]
    full = to_full_topic(feed)
    client.publish(full, str(int(value)))
    log.info("MQTT → %s = %s", full, value)