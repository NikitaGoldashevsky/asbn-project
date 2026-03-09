"""
API администрирования системы
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import APIRouter, Depends, HTTPException, Body 
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import User, SystemEvent, CommandLog
from backend.app.core.security import get_password_hash
from typing import List, Optional

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
    db.refresh(new_user)
    
    return {"message": "Пользователь создан", "id": new_user.id, "login": new_user.login}


@router.put("/users/{user_id}")
async def update_user(
    user_id: int,
    login: Optional[str] = Body(None),
    email: Optional[str] = Body(None),
    role: Optional[str] = Body(None),
    password: Optional[str] = Body(None),
    is_active: Optional[bool] = Body(None),
    db: Session = Depends(get_db)
):
    """Редактирование пользователя (админ)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Обновляем только переданные поля
    if login is not None:
        # Проверка уникальности логина
        existing = db.query(User).filter(User.login == login, User.id != user_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Такой логин уже занят")
        user.login = login
    
    if email is not None:
        user.email = email
    
    if role is not None:
        user.role = role
    
    if password is not None and len(password) > 0:
        user.password_hash = get_password_hash(password)
    
    if is_active is not None:
        user.is_active = is_active
    
    db.commit()
    db.refresh(user)
    
    return {
        "message": "Пользователь обновлён",
        "id": user.id,
        "login": user.login,
        "email": user.email,
        "role": user.role
    }


@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """Удаление пользователя"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    # Нельзя удалить самого себя
    if user.login == "admin":
        raise HTTPException(status_code=400, detail="Нельзя удалить главного администратора")
    
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