"""
API генерации отчётов
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.database import get_db
from backend.app.models import Measurement, NetworkNode, Forecast
import csv
import os

router = APIRouter()


@router.get("/")
async def get_reports_list(db: Session = Depends(get_db)):
    """Список доступных отчётов"""
    return {
        "reports": [
            {"id": 1, "name": "Состояние нагрузки", "type": "state"},
            {"id": 2, "name": "Распределение нагрузки", "type": "distribution"},
            {"id": 3, "name": "Прогноз нагрузки", "type": "forecast"}
        ]
    }


@router.post("/generate")
async def generate_report(
    report_type: str,
    start_date: datetime,
    end_date: datetime,
    node_ids: list = None,
    db: Session = Depends(get_db)
):
    """Генерация отчёта (CSV)"""
    if report_type not in ["state", "distribution", "forecast"]:
        raise HTTPException(status_code=400, detail="Неверный тип отчёта")
    
    # Создаём директорию для экспорта
    os.makedirs("exports/reports", exist_ok=True)
    
    filename = f"exports/reports/report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if report_type == "state":
                writer.writerow(["Узел", "Напряжение (кВ)", "Ток (А)", "Мощность (МВт)", "Статус", "Время"])
                measurements = db.query(Measurement).filter(
                    Measurement.timestamp.between(start_date, end_date)
                ).limit(100).all()
                for m in measurements:
                    node = db.query(NetworkNode).filter(NetworkNode.id == m.node_id).first()
                    writer.writerow([
                        node.name if node else f"Узел {m.node_id}",
                        m.voltage, m.current, m.active_power,
                        "Норма" if m.is_valid else "Недейств.",
                        m.timestamp
                    ])
            
            elif report_type == "forecast":
                writer.writerow(["Узел", "Время", "Прогноз (МВт)", "Нижняя граница", "Верхняя граница", "MAPE"])
                forecasts = db.query(Forecast).filter(
                    Forecast.timestamp.between(start_date, end_date)
                ).limit(100).all()
                for fc in forecasts:
                    node = db.query(NetworkNode).filter(NetworkNode.id == fc.node_id).first()
                    writer.writerow([
                        node.name if node else f"Узел {fc.node_id}",
                        fc.timestamp, fc.predicted_load,
                        fc.confidence_lower, fc.confidence_upper,
                        fc.mape_error
                    ])
            
            elif report_type == "distribution":
                writer.writerow(["Источник", "Цель", "Мощность (МВт)", "Статус", "Время"])
                writer.writerow(["ПС-1", "ПС-2", "15.5", "Выполнено", datetime.now()])
                writer.writerow(["ПС-2", "ПС-3", "10.2", "Выполнено", datetime.now()])
        
        return {
            "message": "Отчёт сгенерирован",
            "file_path": filename,
            "report_type": report_type,
            "records": 100
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка генерации: {str(e)}")


@router.get("/templates")
async def get_report_templates():
    """Шаблоны отчётов"""
    return {
        "templates": [
            {
                "id": 1,
                "name": "Ежечасный отчёт по нагрузке",
                "type": "state",
                "schedule": "hourly"
            },
            {
                "id": 2,
                "name": "Дневной прогноз",
                "type": "forecast",
                "schedule": "daily"
            }
        ]
    }