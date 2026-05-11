from typing import Any, Dict, Optional

from db.db_manager import DBManager


class MemoryDeviceRepository:
    _DEFAULTS: Dict[str, Any] = {
        "timestamp": 0,
        "temperature": None,
        "humidity": None,
        "soil_moisture": None,
        "light_level": None,
        "pump_state": 0,
        "pump_mode": "manual",
        "humidity_threshold": 50.0,
    }

    def __init__(self, db_manager: DBManager) -> None:
        self._db_manager = db_manager
        self._db_manager.initialize_database()
        self._device_data: Dict[str, Any] = dict(self._DEFAULTS)
        # Warm cache from latest DB record so status is non-null after server restart
        records, _ = self._db_manager.get_sensor_history(limit=1, offset=0)
        if records:
            self._device_data.update(records[0])
        self._pending_command: Optional[Dict[str, Any]] = None

    def save_device_data(self, data: Dict[str, Any]) -> None:
        self._db_manager.insert_sensor_history(data)
        self._device_data.update(data)

    def get_device_status(self) -> Dict[str, Any]:
        return self._device_data.copy()

    def set_pending_command(self, command: Dict[str, Any]) -> None:
        self._pending_command = command

    def pop_pending_command(self) -> Optional[Dict[str, Any]]:
        command = self._pending_command
        self._pending_command = None
        return command

    def get_sensor_history(self, limit: int = 100, offset: int = 0) -> tuple[list[Dict[str, Any]], int]:
        return self._db_manager.get_sensor_history(limit, offset)
