"""
АСБН - Автоматизированная Система Балансировки Нагрузок
Точка входа FastAPI приложения
Разработчик: Голдашевский Н.С., гр. 4331
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base, SessionLocal
from backend.app.api import auth, monitoring, forecast, balancing, notifications, reports, admin
from backend.app.models import BalancingRecommendation, NetworkNode
from backend.app.core.config import config
import logging
import asyncio
from datetime import datetime
import random

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


# === ФОНОВАЯ ЗАДАЧА: генерация рекомендаций ===
async def generate_recommendations_task():
    """Фоновая задача: создание рекомендаций каждые 10 секунд (макс. 2 в очереди)"""
    while True:
        try:
            await asyncio.sleep(10)
            
            db = SessionLocal()
            try:
                # Считаем pending рекомендации
                pending_count = db.query(BalancingRecommendation).filter(
                    BalancingRecommendation.status == "pending"
                ).count()
                
                # Если меньше или равно 2 - создаём новую
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
                            
                            logger.info(f"Создана рекомендация #{recommendation.id}: {source.name} → {target.name}")
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Ошибка в задаче генерации рекомендаций: {e}")


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
    """Запуск фоновых задач при старте приложения"""
    logger.info("Запуск фоновой задачи генерации рекомендаций...")
    asyncio.create_task(generate_recommendations_task())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)