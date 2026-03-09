"""
Схемы пользователей
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    DISPATCHER = "dispatcher"
    ANALYST = "analyst"
    ADMIN = "admin"


# Для регистрации
class UserRegister(BaseModel):
    login: str = Field(..., min_length=4, max_length=20, pattern="^[a-zA-Z0-9]+$")
    password: str = Field(..., min_length=8, max_length=32)
    email: EmailStr
    
    class Config:
        json_schema_extra = {
            "example": {
                "login": "user123",
                "password": "Pass123!",
                "email": "user@example.com"
            }
        }


# Для входа
class UserLogin(BaseModel):
    login: str = Field(..., min_length=4, max_length=20)
    password: str = Field(..., min_length=8, max_length=32)


# Токен доступа
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


# Информация о пользователе
class UserResponse(BaseModel):
    id: int
    login: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True