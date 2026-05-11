import os
from pathlib import Path

from api.repositories.memory_repository import MemoryDeviceRepository
from api.services.device_service import DeviceService
from db.db_manager import DBManager


project_root = Path(__file__).resolve().parents[2]
db_path = project_root / "iot_data.db"

db_manager = DBManager(db_path)
repository = MemoryDeviceRepository(db_manager)
device_service = DeviceService(repository)


def get_device_service() -> DeviceService:
    return device_service
