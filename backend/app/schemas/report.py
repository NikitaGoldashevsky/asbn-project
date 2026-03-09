"""
Схемы отчётов
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ReportGenerate(BaseModel):
    report_type: str
    start_date: datetime
    end_date: datetime
    node_ids: Optional[List[int]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "state",
                "start_date": "2026-03-09T00:00:00",
                "end_date": "2026-03-09T23:59:59",
                "node_ids": [1, 2, 3]
            }
        }


class ReportResponse(BaseModel):
    message: str
    file_path: str
    report_type: str
    records: int