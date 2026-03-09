"""
API балансировки нагрузок
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.database import get_db
from backend.app.models import BalancingRecommendation, NetworkNode, CommandLog, User
from backend.app.core.config import config

router = APIRouter()


@router.get("/recommendations")
async def get_recommendations(db: Session = Depends(get_db)):
    """Получение рекомендаций по балансировке"""
    recommendations = db.query(BalancingRecommendation).filter(
        BalancingRecommendation.status == "pending"
    ).order_by(BalancingRecommendation.created_at.desc()).limit(20).all()
    
    return {
        "recommendations": [
            {
                "id": r.id,
                "source_node_id": r.source_node_id,
                "target_node_id": r.target_node_id,
                "power_transfer": r.power_transfer,
                "command_type": r.command_type,
                "status": r.status,
                "created_at": r.created_at,
                "effect_description": r.effect_description
            }
            for r in recommendations
        ],
        "total": len(recommendations)
    }

@router.post("/confirm")
async def confirm_recommendation(
    recommendation_id: int,
    operator_id: int = 1,
    db: Session = Depends(get_db)
):
    """Подтверждение рекомендации диспетчером"""
    rec = db.query(BalancingRecommendation).filter(
        BalancingRecommendation.id == recommendation_id
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Рекомендация не найдена")
    
    rec.status = "confirmed"
    rec.confirmed_by = operator_id
    rec.executed_at = datetime.utcnow()
    
    command = CommandLog(
        command_type=rec.command_type,
        parameters={"source": rec.source_node_id, "target": rec.target_node_id, "power": rec.power_transfer},
        status="sent",
        operator_id=operator_id
    )
    db.add(command)
    db.commit()
    
    return {
        "message": "Рекомендация подтверждена",
        "recommendation_id": recommendation_id,
        "status": "confirmed"
    }


@router.post("/reject")
async def reject_recommendation(
    recommendation_id: int,
    reason: str = "Не подходит по параметрам",
    db: Session = Depends(get_db)
):
    """Отклонение рекомендации"""
    rec = db.query(BalancingRecommendation).filter(
        BalancingRecommendation.id == recommendation_id
    ).first()
    
    if not rec:
        raise HTTPException(status_code=404, detail="Рекомендация не найдена")
    
    rec.status = "rejected"
    db.commit()
    
    return {
        "message": "Рекомендация отклонена",
        "recommendation_id": recommendation_id,
        "reason": reason
    }


@router.get("/commands")
async def get_commands(limit: int = 50, db: Session = Depends(get_db)):
    """Журнал управляющих команд"""
    commands = db.query(CommandLog).order_by(
        CommandLog.sent_at.desc()
    ).limit(limit).all()
    
    return {
        "commands": [
            {
                "id": c.id,
                "command_type": c.command_type,
                "parameters": c.parameters,
                "status": c.status,
                "sent_at": c.sent_at,
                "executed_at": c.executed_at,
                "operator_id": c.operator_id
            }
            for c in commands
        ],
        "total": len(commands)
    }


@router.post("/simulate")
async def simulate_balancing(
    source_node_id: int,
    target_node_id: int,
    power_transfer: float,
    db: Session = Depends(get_db)
):
    """Режим симуляции балансировки"""
    return {
        "mode": "simulation",
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "power_transfer": power_transfer,
        "predicted_effect": {
            "source_load_change": f"-{power_transfer} МВт",
            "target_load_change": f"+{power_transfer} МВт",
            "estimated_efficiency": "92%"
        },
        "message": "Симуляция выполнена. Команды не отправлялись в SCADA."
    }