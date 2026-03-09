"""
API авторизации и регистрации
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from backend.app.database import get_db
from backend.app.models import User
from backend.app.schemas.user import UserRegister, UserLogin, Token, UserResponse
from backend.app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    decode_access_token
)
from backend.app.core.config import config
from backend.app.core.exceptions import AuthenticationError, BlockedUserError
import re

router = APIRouter()


# === Валидация пароля (по ТЗ 4.2.2.2) ===
def validate_password(password: str) -> bool:
    """Проверка сложности пароля"""
    if len(password) < 8 or len(password) > 32:
        return False
    if not re.search(r"[A-Z]", password):  # Заглавная буква
        return False
    if not re.search(r"[a-z]", password):  # Строчная буква
        return False
    if not re.search(r"\d", password):  # Цифра
        return False
    if not re.search(r"[!@#$%^&*]", password):  # Спецсимвол
        return False
    return True


# === Регистрация ===
@router.post("/register", response_model=dict)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Регистрация нового пользователя"""
    # Проверка сложности пароля
    if not validate_password(user_data.password):
        raise HTTPException(
            status_code=422,
            detail="Пароль должен содержать 8-32 символа, заглавную букву, строчную букву, цифру и спецсимвол (!@#$%^&*)"
        )
    
    # Проверка существующего пользователя
    existing_user = db.query(User).filter(
        (User.login == user_data.login) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким логином или email уже существует"
        )
    
    # Создание пользователя (роль по умолчанию - analyst)
    new_user = User(
        login=user_data.login,
        password_hash=get_password_hash(user_data.password),
        email=user_data.email,
        role="analyst"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "Регистрация успешно завершена", "user_id": new_user.id}


# === Вход ===
@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Вход в систему"""
    # Поиск пользователя
    user = db.query(User).filter(User.login == credentials.login).first()
    
    if not user:
        raise AuthenticationError()
    
    # Проверка блокировки
    if user.locked_until and user.locked_until > datetime.utcnow():
        raise BlockedUserError()
    
    # Проверка пароля
    if not verify_password(credentials.password, user.password_hash):
        # Увеличение счётчика неудачных попыток
        user.failed_login_attempts += 1
        
        # Блокировка после 3 попыток
        if user.failed_login_attempts >= 3:
            user.locked_until = datetime.utcnow() + timedelta(minutes=10)
        
        db.commit()
        raise AuthenticationError()
    
    # Сброс счётчика при успешном входе
    user.failed_login_attempts = 0
    user.locked_until = None
    db.commit()
    
    # Создание токена
    access_token = create_access_token(
        data={"sub": user.login, "role": user.role.value}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role.value
    }


# === Получение текущего пользователя ===
@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str,
    db: Session = Depends(get_db)
):
    """Получение информации о текущем пользователе"""
    payload = decode_access_token(token)
    
    if not payload:
        raise AuthenticationError("Неверный токен")
    
    user = db.query(User).filter(User.login == payload.get("sub")).first()
    
    if not user or not user.is_active:
        raise AuthenticationError("Пользователь не найден")
    
    return user