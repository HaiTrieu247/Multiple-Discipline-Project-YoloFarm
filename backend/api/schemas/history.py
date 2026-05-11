from typing import Optional

from pydantic import BaseModel, Field


class SensorHistoryRecord(BaseModel):
    id: int = Field(..., description="Record ID")
    timestamp: float = Field(..., description="Unix timestamp")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Relative humidity (%)")
    soil_moisture: Optional[int] = Field(None, description="Soil moisture level (0-100%)")
    light_level: Optional[int] = Field(None, description="Light level (0-4096)")
    pump_state: int = Field(0, description="Pump state: 0=off, 1=on")
    pump_mode: str = Field("manual", description="Pump mode")
    humidity_threshold: float = Field(50.0, description="Humidity threshold")


class SensorHistoryResponse(BaseModel):
    total: int = Field(..., description="Total records in database")
    count: int = Field(..., description="Number of records in this response")
    offset: int = Field(..., description="Offset from start")
    records: list[SensorHistoryRecord] = Field(..., description="List of sensor history records")
