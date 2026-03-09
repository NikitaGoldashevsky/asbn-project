"""
АСБН - Автоматизированная Система Балансировки Нагрузок
Точка входа FastAPI приложения
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base
from backend.app.api import auth, monitoring, forecast, balancing, notifications, reports, admin
from backend.app.core.config import config
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Создание таблиц БД
Base.metadata.create_all(bind=engine)

# Инициализация приложения
app = FastAPI(
    title=config.app_name,
    version=config.app_version,
    description="Автоматизированная система управления балансировкой нагрузок в энергосети"
)

# CORS middleware (для frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Для прототипа можно все
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(auth.router, prefix="/api/auth", tags=["Авторизация"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Мониторинг"])
app.include_router(forecast.router, prefix="/api/forecast", tags=["Прогнозирование"])
app.include_router(balancing.router, prefix="/api/balancing", tags=["Балансировка"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Уведомления"])
app.include_router(reports.router, prefix="/api/reports", tags=["Отчёты"])
app.include_router(admin.router, prefix="/api/admin", tags=["Администрирование"])


@app.get("/")
async def root():
    """Главная страница API"""
    return {
        "message": "АСБН API",
        "version": config.app_version,
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Проверка работоспособности"""
    return {"status": "ok", "service": "asbn-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)