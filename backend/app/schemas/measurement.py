"""
Схемы измерений
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MeasurementBase(BaseModel):
    node_id: int
    current: Optional[float] = None
    voltage: Optional[float] = None
    active_power: Optional[float] = None
    reactive_power: Optional[float] = None
    frequency: Optional[float] = None
    power_factor: Optional[float] = None


class MeasurementCreate(MeasurementBase):
    timestamp: datetime


class MeasurementResponse(MeasurementBase):
    id: int
    timestamp: datetime
    is_valid: bool
    
    class Config:
        from_attributes = True


class MeasurementList(BaseModel):
    measurements: list[MeasurementResponse]
    total: int