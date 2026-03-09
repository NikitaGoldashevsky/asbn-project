"""
АСБН - Автоматизированная Система Балансировки Нагрузок
Точка входа FastAPI приложения
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base, SessionLocal
from backend.app.api import auth, monitoring, forecast, balancing, notifications, reports, admin
from backend.app.models import BalancingRecommendation, NetworkNode, Measurement
from backend.app.services.forecast_service import forecast_service
from backend.app.core.config import config
import logging
import asyncio
from datetime import datetime, timedelta
import random
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


# === ФОНОВАЯ ЗАДАЧА 1: Генерация рекомендаций ===
async def generate_recommendations_task():
    """Создание рекомендаций каждые 10 секунд (макс. 2 в очереди)"""
    while True:
        try:
            await asyncio.sleep(10)
            db = SessionLocal()
            try:
                pending_count = db.query(BalancingRecommendation).filter(
                    BalancingRecommendation.status == "pending"
                ).count()
                
                if pending_count <= 2:
                    nodes = db.query(NetworkNode).limit(5).all()
                    if len(nodes) >= 2:
                        source = random.choice(nodes)
                        target = random.choice([n for n in nodes if n.id != source.id])
                        if target:
                            recommendation = BalancingRecommendation(
                                source_node_id=source.id,
                                target_node_id=target.id,
                                power_transfer=round(random.uniform(5, 25), 1),
                                command_type=random.choice([
                                    "переключение фидера",
                                    "регулировка трансформатора",
                                    "перераспределение мощности"
                                ]),
                                status="pending",
                                effect_description=f"Снижение загрузки узла на {random.randint(8, 15)}%"
                            )
                            db.add(recommendation)
                            db.commit()
                            logger.info(f"Рекомендация #{recommendation.id}: {source.name} → {target.name}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Ошибка генерации рекомендаций: {e}")


# === ФОНОВАЯ ЗАДАЧА 2: Пересчёт прогноза каждые 15 минут ===
async def recalculate_forecasts_task():
    """Автоматический пересчёт прогнозов каждые 15 минут (ТЗ 4.2.3)"""
    while True:
        try:
            await asyncio.sleep(900)  # 15 минут
            db = SessionLocal()
            try:
                nodes = db.query(NetworkNode).limit(5).all()
                for node in nodes:
                    measurements = db.query(Measurement).filter(
                        Measurement.node_id == node.id
                    ).order_by(Measurement.timestamp.desc()).limit(3000).all()
                    
                    if len(measurements) >= 100:
                        timestamps = [m.timestamp for m in measurements]
                        loads = [m.active_power or 50.0 for m in measurements]
                        forecast_service.train_model(node.id, loads, timestamps)
                        logger.info(f"Прогноз обновлён для узла {node.name}")
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Ошибка пересчёта прогноза: {e}")


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


@app.on_event("startup")
async def startup_event():
    """Запуск фоновых задач при старте (ТЗ 4.2.1)"""
    logger.info("Запуск фоновых задач...")
    asyncio.create_task(generate_recommendations_task())
    asyncio.create_task(recalculate_forecasts_task())
    logger.info("Фоновые задачи запущены")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)