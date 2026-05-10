from typing import Dict, Optional

from fastapi import APIRouter, Depends

from backend.api.schemas.command import Command
from backend.api.schemas.device import DeviceData, DeviceStatus
from backend.api.services.device_service import DeviceService
from backend.core.dependencies import get_device_service

router = APIRouter(prefix="/api", tags=["device"])


@router.post("/data", response_model=Dict[str, str])
def receive_device_data(
    device_data: DeviceData,
    service: DeviceService = Depends(get_device_service),
) -> Dict[str, str]:
    service.save_device_data(device_data)
    return {"status": "ok"}


@router.get("/command", response_model=Dict[str, Optional[Dict[str, object]]])
def get_pending_command(
    service: DeviceService = Depends(get_device_service),
) -> Dict[str, Optional[Dict[str, object]]]:
    command = service.pop_pending_command()
    return command or {}


@router.post("/command", response_model=Dict[str, str])
def queue_command(
    command: Command,
    service: DeviceService = Depends(get_device_service),
) -> Dict[str, str]:
    service.queue_command(command)
    return {"status": "queued"}


@router.get("/status", response_model=DeviceStatus)
def get_device_status(
    service: DeviceService = Depends(get_device_service),
) -> DeviceStatus:
    status = service.get_current_status()
    return DeviceStatus(**status)
