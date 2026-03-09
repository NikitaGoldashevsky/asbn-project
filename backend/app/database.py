"""
Подключение к базе данных PostgreSQL
Разработчик: Голдашевский Н.С., гр. 4331
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.core.config import config

# Создание движка БД
engine = create_engine(
    config.database_url,
    pool_pre_ping=True,  # Проверка соединения
    pool_size=10,        # Пул соединений
    max_overflow=20
)

# Сессия БД
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()


def get_db():
    """Зависимость для получения сессии БД"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()