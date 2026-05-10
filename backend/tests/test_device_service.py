import sqlite3
from pathlib import Path

from backend.api.repositories.memory_repository import MemoryDeviceRepository
from backend.api.schemas.command import Command
from backend.api.schemas.device import DeviceData
from backend.api.services.device_service import DeviceService
from backend.db.db_manager import DBManager


def test_save_device_data_updates_status_and_values(tmp_path: Path):
    db_path = tmp_path / "iot_data.db"
    db_manager = DBManager(db_path)
    repository = MemoryDeviceRepository(db_manager)
    service = DeviceService(repository)
    payload = DeviceData(
        timestamp=1700000000.0,
        temperature=25.5,
        humidity=60.0,
        soil_moisture=42,
        light_level=2100,
        pump_state=1,
        pump_mode="auto",
        humidity_threshold=55.0,
    )

    service.save_device_data(payload)
    status = service.get_current_status()

    assert status["temperature"] == 25.5
    assert status["humidity"] == 60.0
    assert status["soil_moisture"] == 42
    assert status["light_level"] == 2100
    assert status["pump_state"] == 1
    assert status["pump_mode"] == "auto"
    assert status["humidity_threshold"] == 55.0
    assert status["timestamp"] == 1700000000.0

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM SensorHistory").fetchone()
        assert row is not None
        assert row["temperature"] == 25.5
        assert row["humidity"] == 60.0
        assert row["soil_moisture"] == 42
        assert row["light_level"] == 2100
        assert row["pump_state"] == 1
        assert row["pump_mode"] == "auto"
        assert row["humidity_threshold"] == 55.0


def test_queue_and_pop_pending_command(tmp_path: Path):
    db_path = tmp_path / "iot_data.db"
    db_manager = DBManager(db_path)
    repository = MemoryDeviceRepository(db_manager)
    service = DeviceService(repository)
    command = Command(command="set_pump_mode", params={"mode": "auto"})

    service.queue_command(command)
    pending = service.pop_pending_command()

    assert pending == {"command": "set_pump_mode", "params": {"mode": "auto"}}
    assert service.pop_pending_command() is None
