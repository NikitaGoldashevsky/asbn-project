"""
Схемы отчётов
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ReportGenerate(BaseModel):
    report_type: str  # state, distribution, forecast
    start_date: datetime
    end_date: datetime
    node_ids: Optional[list[int]] = None


class ReportResponse(BaseModel):
    id: int
    report_type: str
    file_path: str
    created_at: datetime
    created_by: int
    
    class Config:
        from_attributes = True