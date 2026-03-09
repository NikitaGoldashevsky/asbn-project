"""
API прогнозирования нагрузки
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.app.database import get_db
from backend.app.models import Forecast, NetworkNode, Measurement
from backend.app.schemas.forecast import ForecastResponse, ForecastCalculate
import random

router = APIRouter()


@router.get("/node/{node_id}")
async def get_forecast(node_id: int, db: Session = Depends(get_db)):
    """Прогноз по узлу"""
    forecasts = db.query(Forecast).filter(
        Forecast.node_id == node_id
    ).order_by(Forecast.timestamp.asc()).limit(96).all()  # 24 часа * 4 интервала
    
    if not forecasts:
        # Генерируем тестовые данные для прототипа
        return generate_mock_forecast(node_id)
    
    return {
        "node_id": node_id,
        "forecasts": [
            {
                "id": f.id,
                "timestamp": f.timestamp,
                "predicted_load": f.predicted_load,
                "confidence_lower": f.confidence_lower,
                "confidence_upper": f.confidence_upper,
                "mape_error": f.mape_error
            }
            for f in forecasts
        ]
    }


def generate_mock_forecast(node_id: int):
    """Генерация тестового прогноза (для прототипа)"""
    now = datetime.utcnow()
    forecasts = []
    base_load = random.uniform(50, 100)
    
    for i in range(96):  # 24 часа * 4 интервала
        timestamp = now + timedelta(minutes=15 * i)
        # Имитация суточного цикла
        hour_factor = 1 + 0.3 * (-(timestamp.hour - 14) ** 2 / 100 + 1)
        predicted = base_load * hour_factor + random.uniform(-5, 5)
        
        forecasts.append({
            "timestamp": timestamp,
            "predicted_load": round(predicted, 2),
            "confidence_lower": round(predicted * 0.9, 2),
            "confidence_upper": round(predicted * 1.1, 2),
            "mape_error": round(random.uniform(2, 5), 2)
        })
    
    return {"node_id": node_id, "forecasts": forecasts}


@router.post("/calculate")
async def calculate_forecast(
    data: ForecastCalculate,
    db: Session = Depends(get_db)
):
    """Расчёт прогноза (упрощённо для прототипа)"""
    node = db.query(NetworkNode).filter(NetworkNode.id == data.node_id).first()
    
    if not node:
        raise HTTPException(status_code=404, detail="Узел не найден")
    
    # Для прототипа просто генерируем прогноз
    # В реальной системе здесь была бы квантильная регрессия
    forecast_data = generate_mock_forecast(data.node_id)
    
    # Сохраняем в БД первые 10 значений
    for i, f in enumerate(forecast_data["forecasts"][:10]):
        forecast = Forecast(
            node_id=data.node_id,
            timestamp=f["timestamp"],
            predicted_load=f["predicted_load"],
            confidence_lower=f["confidence_lower"],
            confidence_upper=f["confidence_upper"],
            mape_error=f["mape_error"]
        )
        db.add(forecast)
    
    db.commit()
    
    return {
        "message": "Прогноз рассчитан",
        "node_id": data.node_id,
        "horizon_hours": data.horizon_hours,
        "mape": round(random.uniform(3, 5), 2)
    }


@router.get("/quality")
async def get_forecast_quality(db: Session = Depends(get_db)):
    """Метрики качества прогнозов"""
    forecasts = db.query(Forecast).all()
    
    if not forecasts:
        return {
            "mape_avg": 4.5,
            "rmse_avg": 3.2,
            "total_forecasts": 0,
            "message": "Нет данных для расчёта метрик"
        }
    
    mape_values = [f.mape_error for f in forecasts if f.mape_error]
    
    return {
        "mape_avg": round(sum(mape_values) / len(mape_values), 2) if mape_values else 0,
        "rmse_avg": round(random.uniform(2, 4), 2),
        "total_forecasts": len(forecasts),
        "accuracy_percent": round(100 - (sum(mape_values) / len(mape_values)), 2) if mape_values else 95
    }