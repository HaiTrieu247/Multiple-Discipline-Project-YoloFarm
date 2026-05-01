"""
MQTT Topic mapping for OhStem broker.
OhStem format: {username}/feeds/{feed_id}
"""

USERNAME = "YoloFarm_2907"

TELEMETRY_TOPICS = {
    "temp": "V1",
    "humidity": "V2",
    "soil": "V3",
    "lux": "V4",
    "gdd": "V5",
    "status": "V6",
}

COMMAND_TOPICS = {
    "pump": "V10",
    "light": "V11",
}

# Reverse lookup: full_topic → short key
_TOPIC_REVERSE = {}


def to_full_topic(feed_id: str) -> str:
    """Convert short feed id (e.g. 'V1') to full OhStem topic."""
    return f"{USERNAME}/feeds/{feed_id}"


def feed_from_topic(full_topic: str) -> str | None:
    """Extract feed id from a full topic string, e.g. 'YoloFarm_2907/feeds/V1' → 'V1'."""
    parts = full_topic.split("/")
    if len(parts) >= 3 and parts[1] == "feeds":
        return parts[2]
    return None


def build_reverse_map():
    """Build reverse lookup map once at startup."""
    for key, feed in {**TELEMETRY_TOPICS, **COMMAND_TOPICS}.items():
        _TOPIC_REVERSE[to_full_topic(feed)] = (key, feed)


build_reverse_map()