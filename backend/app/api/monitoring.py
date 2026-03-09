"""
API мониторинга состояния энергосети
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from backend.app.database import get_db
from backend.app.models import NetworkNode, Measurement, SystemEvent
from backend.app.schemas.measurement import MeasurementResponse, MeasurementList
from backend.app.core.config import config

router = APIRouter()


@router.get("/topology")
async def get_topology(db: Session = Depends(get_db)):
    """Получение топологии сети (упрощённо для прототипа)"""
    nodes = db.query(NetworkNode).all()
    
    return {
        "nodes": [
            {
                "id": node.id,
                "name": node.name,
                "type": node.object_type,
                "status": node.status,
                "voltage": node.nominal_voltage,
                "power": node.nominal_power
            }
            for node in nodes
        ]
    }


@router.get("/measurements", response_model=MeasurementList)
async def get_measurements(
    node_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получение измерений"""
    query = db.query(Measurement).order_by(Measurement.timestamp.desc())
    
    if node_id:
        query = query.filter(Measurement.node_id == node_id)
    
    measurements = query.limit(limit).all()
    
    return {
        "measurements": [
            {
                "id": m.id,
                "node_id": m.node_id,
                "timestamp": m.timestamp,
                "current": m.current,
                "voltage": m.voltage,
                "active_power": m.active_power,
                "reactive_power": m.reactive_power,
                "frequency": m.frequency,
                "power_factor": m.power_factor,
                "is_valid": m.is_valid
            }
            for m in measurements
        ],
        "total": len(measurements)
    }


@router.get("/nodes/{node_id}")
async def get_node_details(node_id: int, db: Session = Depends(get_db)):
    """Детали узла сети"""
    node = db.query(NetworkNode).filter(NetworkNode.id == node_id).first()
    
    if not node:
        raise HTTPException(status_code=404, detail="Узел не найден")
    
    # Последние измерения
    last_measurement = db.query(Measurement).filter(
        Measurement.node_id == node_id
    ).order_by(Measurement.timestamp.desc()).first()
    
    # Расчёт загрузки
    load_percent = 0
    if last_measurement and node.nominal_power:
        load_percent = (last_measurement.active_power / node.nominal_power) * 100
    
    return {
        "id": node.id,
        "name": node.name,
        "type": node.object_type,
        "status": node.status,
        "nominal_voltage": node.nominal_voltage,
        "nominal_power": node.nominal_power,
        "current_load_percent": round(load_percent, 2),
        "last_measurement": {
            "timestamp": last_measurement.timestamp if last_measurement else None,
            "active_power": last_measurement.active_power if last_measurement else None,
            "voltage": last_measurement.voltage if last_measurement else None
        } if last_measurement else None
    }


@router.get("/status")
async def get_network_status(db: Session = Depends(get_db)):
    """Сводный статус сети"""
    nodes = db.query(NetworkNode).all()
    
    status_counts = {"norma": 0, "warning": 0, "overload": 0, "emergency": 0, "offline": 0}
    
    for node in nodes:
        status_counts[node.status] = status_counts.get(node.status, 0) + 1
    
    return {
        "total_nodes": len(nodes),
        "status_distribution": status_counts,
        "healthy_percent": round((status_counts["norma"] / len(nodes) * 100) if nodes else 0, 2),
        "updated_at": datetime.utcnow()
    }


@router.get("/incidents")
async def get_incidents(limit: int = 50, db: Session = Depends(get_db)):
    """Список инцидентов"""
    events = db.query(SystemEvent).filter(
        SystemEvent.severity.in_(["high", "critical"])
    ).order_by(SystemEvent.timestamp.desc()).limit(limit).all()
    
    return {
        "incidents": [
            {
                "id": e.id,
                "type": e.event_type,
                "description": e.description,
                "severity": e.severity,
                "timestamp": e.timestamp,
                "module": e.source_module
            }
            for e in events
        ],
        "total": len(events)
    }