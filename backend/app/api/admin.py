"""
API администрирования системы
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import APIRouter, Depends, HTTPException, Body 
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, SystemEvent, CommandLog
from backend.app.core.security import get_password_hash
from typing import List

router = APIRouter()


@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    """Список пользователей"""
    users = db.query(User).all()
    
    return {
        "users": [
            {
                "id": u.id,
                "login": u.login,
                "email": u.email,
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at
            }
            for u in users
        ],
        "total": len(users)
    }


@router.post("/users")
@router.post("/users")
async def create_user(
    login: str = Body(...),
    password: str = Body(...),
    email: str = Body(...),
    role: str = Body(default="analyst"),
    db: Session = Depends(get_db)
):
    """Создание пользователя (админ)"""
    existing = db.query(User).filter(User.login == login).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    
    new_user = User(
        login=login,
        password_hash=get_password_hash(password),
        email=email,
        role=role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # ← Добавьте это
    
    return {"message": "Пользователь создан", "id": new_user.id, "login": new_user.login}


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удаление пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    db.delete(user)
    db.commit()
    
    return {"message": "Пользователь удалён"}


@router.get("/system/status")
async def get_system_status(db: Session = Depends(get_db)):
    """Статус системы"""
    users_count = db.query(User).count()
    events_count = db.query(SystemEvent).count()
    commands_count = db.query(CommandLog).count()
    
    return {
        "status": "operational",
        "users_count": users_count,
        "events_count": events_count,
        "commands_count": commands_count,
        "database": "connected",
        "version": "1.0.0"
    }


@router.get("/logs")
async def get_system_logs(limit: int = 100, db: Session = Depends(get_db)):
    """Системные логи"""
    events = db.query(SystemEvent).order_by(
        SystemEvent.timestamp.desc()
    ).limit(limit).all()
    
    return {
        "logs": [
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