"""
API уведомлений и оповещений
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from backend.app.database import get_db
from backend.app.models import Notification, User
from typing import List

router = APIRouter()


@router.get("/")
async def get_notifications(
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Получение списка уведомлений"""
    notifications = db.query(Notification).order_by(
        Notification.created_at.desc()
    ).limit(limit).all()
    
    return {
        "notifications": [
            {
                "id": n.id,
                "user_id": n.user_id,
                "type": n.type,
                "message": n.message,
                "channel": n.channel,
                "status": n.status,
                "created_at": n.created_at,
                "is_read": n.is_read
            }
            for n in notifications
        ],
        "total": len(notifications)
    }


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: int,
    db: Session = Depends(get_db)
):
    """Отметить уведомление как прочитанное"""
    notification = db.query(Notification).filter(
        Notification.id == notification_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    
    notification.is_read = True
    db.commit()
    
    return {"message": "Уведомление отмечено как прочитанное"}


@router.get("/rules")
async def get_notification_rules():
    """Правила уведомлений (для прототипа - статичные)"""
    return {
        "rules": [
            {
                "id": 1,
                "event_type": "overload",
                "threshold": 95,
                "channels": ["interface", "email"],
                "roles": ["dispatcher", "admin"]
            },
            {
                "id": 2,
                "event_type": "warning",
                "threshold": 85,
                "channels": ["interface"],
                "roles": ["dispatcher", "analyst", "admin"]
            },
            {
                "id": 3,
                "event_type": "emergency",
                "threshold": 100,
                "channels": ["interface", "email", "sms"],
                "roles": ["dispatcher", "admin"]
            }
        ]
    }


@router.post("/create")
async def create_notification(
    user_id: int,
    type: str,
    message: str,
    channel: str = "interface",
    db: Session = Depends(get_db)
):
    """Создание уведомления (внутренний API)"""
    notification = Notification(
        user_id=user_id,
        type=type,
        message=message,
        channel=channel
    )
    db.add(notification)
    db.commit()
    
    return {"message": "Уведомление создано", "id": notification.id}