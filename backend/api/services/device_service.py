from typing import Any, Dict, Optional

from backend.api.repositories.memory_repository import MemoryDeviceRepository
from backend.api.schemas.command import Command
from backend.api.schemas.device import DeviceData


class DeviceService:
    def __init__(self, repository: MemoryDeviceRepository) -> None:
        self._repository = repository

    def save_device_data(self, device_data: DeviceData) -> None:
        payload: Dict[str, Any] = device_data.model_dump()
        self._repository.save_device_data(payload)

    def get_current_status(self) -> Dict[str, Any]:
        return self._repository.get_device_status()

    def queue_command(self, command: Command) -> None:
        self._repository.set_pending_command(command.model_dump())

    def pop_pending_command(self) -> Optional[Dict[str, Any]]:
        return self._repository.pop_pending_command()
