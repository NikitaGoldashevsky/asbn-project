"""
Схемы прогнозов
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ForecastResponse(BaseModel):
    id: int
    node_id: int
    timestamp: datetime
    predicted_load: float
    confidence_lower: Optional[float] = None
    confidence_upper: Optional[float] = None
    mape_error: Optional[float] = None
    
    class Config:
        from_attributes = True


class ForecastCalculate(BaseModel):
    node_id: int
    horizon_hours: int = 24
    interval_minutes: int = 15