from typing import Optional, Union

from pydantic import BaseModel, Field


class DeviceData(BaseModel):
    timestamp: float = Field(..., description="Unix timestamp from device")
    temperature: Optional[float] = Field(None, description="Temperature in Celsius")
    humidity: Optional[float] = Field(None, description="Relative humidity (%)")
    soil_moisture: Optional[int] = Field(None, description="Soil moisture level (0-100%)")
    light_level: Optional[int] = Field(None, description="Light level (0-4096)")
    pump_state: int = Field(0, description="Pump state: 0=off, 1=on")
    pump_mode: str = Field("manual", description="Pump mode: manual, auto, scheduled")
    humidity_threshold: float = Field(50.0, description="Humidity threshold for auto mode")


class DeviceStatus(BaseModel):
    timestamp: Union[float, str]
    temperature: Optional[float]
    humidity: Optional[float]
    soil_moisture: Optional[int]
    light_level: Optional[int]
    pump_state: int
    pump_mode: str
    humidity_threshold: float
