import logging
from typing import Dict, Optional

from fastapi import APIRouter, Depends, Query

from api.schemas.command import Command
from api.schemas.device import DeviceData, DeviceStatus
from api.schemas.history import SensorHistoryRecord, SensorHistoryResponse
from api.services.device_service import DeviceService
from core.dependencies import get_device_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["device"])


@router.post("/data", response_model=Dict[str, str])
def receive_device_data(
    device_data: DeviceData,
    service: DeviceService = Depends(get_device_service),
) -> Dict[str, str]:
    logger.info(
        "[POST /api/data] temp=%.1f hum=%.1f soil=%s lux=%s pump=%d mode=%s",
        device_data.temperature or 0,
        device_data.humidity or 0,
        device_data.soil_moisture,
        device_data.light_level,
        device_data.pump_state,
        device_data.pump_mode,
    )
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


@router.get("/history", response_model=SensorHistoryResponse)
def get_sensor_history(
    limit: int = Query(100, ge=1, le=1000, description="Số record tối đa mỗi lần"),
    offset: int = Query(0, ge=0, description="Vị trí bắt đầu"),
    service: DeviceService = Depends(get_device_service),
) -> SensorHistoryResponse:
    records, total = service.get_sensor_history(limit, offset)
    history_records = [SensorHistoryRecord(**record) for record in records]
    return SensorHistoryResponse(
        total=total,
        count=len(history_records),
        offset=offset,
        records=history_records,
    )
