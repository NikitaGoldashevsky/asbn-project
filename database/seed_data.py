"""
Инициализация БД тестовыми данными
Разработчик: Голдашевский Н.С., гр. 4331
"""
import sys
sys.path.append('.')

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User, Measurement
from backend.app.core.security import get_password_hash
from backend.simulator.network_topology import NetworkTopology
from backend.simulator.data_generator import DataGenerator
from datetime import datetime, timedelta
import random

def create_admin_user():
    """Создание администратора по умолчанию"""
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.login == "admin").first()
        if existing:
            return {"message": "Админ уже существует"}
        
        admin = User(
            login="admin",
            password_hash=get_password_hash("Admin123!"),
            email="admin@asbn.local",
            role="admin"
        )
        db.add(admin)
        db.commit()
        return {"message": "Админ создан", "login": "admin", "password": "Admin123!"}
    finally:
        db.close()

def create_test_users():
    """Создание тестовых пользователей"""
    db = SessionLocal()
    try:
        users = [
            {"login": "dispatcher1", "password": "Disp123!", "email": "disp@asbn.local", "role": "dispatcher"},
            {"login": "analyst1", "password": "Anal123!", "email": "anal@asbn.local", "role": "analyst"},
        ]
        
        for u in users:
            existing = db.query(User).filter(User.login == u["login"]).first()
            if not existing:
                user = User(
                    login=u["login"],
                    password_hash=get_password_hash(u["password"]),
                    email=u["email"],
                    role=u["role"]
                )
                db.add(user)
        
        db.commit()
        return {"message": "Тестовые пользователи созданы"}
    finally:
        db.close()

def create_test_notifications():
    """Создание тестовых уведомлений"""
    from backend.app.models import Notification
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    try:
        existing = db.query(Notification).count()
        if existing > 0:
            return {"message": "Уведомления уже существуют"}
        
        notifications = [
            Notification(
                user_id=1,
                type="alert",
                message="Перегрузка узла ПС-2 Центральная: 97%",
                channel="interface",
                status="sent",
                created_at=datetime.utcnow() - timedelta(minutes=5),
                is_read=False
            ),
            Notification(
                user_id=1,
                type="warning",
                message="Прогнозируемая перегрузка: ПС-3 Южная",
                channel="interface",
                status="sent",
                created_at=datetime.utcnow() - timedelta(minutes=30),
                is_read=False
            ),
            Notification(
                user_id=1,
                type="info",
                message="Рекомендация #1 подтверждена",
                channel="interface",
                status="delivered",
                created_at=datetime.utcnow() - timedelta(hours=2),
                is_read=True
            ),
        ]
        
        for n in notifications:
            db.add(n)
        
        db.commit()
        return {"message": f"Создано {len(notifications)} уведомлений"}
    finally:
        db.close()
        
def create_test_recommendations():
    """Создание тестовых рекомендаций"""
    from backend.app.models import BalancingRecommendation
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    try:
        existing = db.query(BalancingRecommendation).count()
        if existing > 0:
            return {"message": "Рекомендации уже существуют"}
        
        recommendations = [
            BalancingRecommendation(
                source_node_id=1,
                target_node_id=2,
                power_transfer=15.5,
                command_type="переключение фидера",
                status="pending",
                effect_description="Снижение загрузки узла на 12%"
            ),
            BalancingRecommendation(
                source_node_id=2,
                target_node_id=3,
                power_transfer=10.2,
                command_type="регулировка трансформатора",
                status="pending",
                effect_description="Балансировка нагрузки"
            ),
        ]
        
        for r in recommendations:
            db.add(r)
        
        db.commit()
        return {"message": f"Создано {len(recommendations)} рекомендаций"}
    finally:
        db.close()

def create_historical_measurements():
    """
    Создание исторических измерений для обучения модели прогноза
    ТЗ 4.3.1.2: не менее 30 суток измерений для каждого узла
    """
    db = SessionLocal()
    try:
        from backend.app.models import NetworkNode
        nodes = db.query(NetworkNode).all()
        
        total = 0
        for node in nodes:
            # Проверяем есть ли уже данные
            existing = db.query(Measurement).filter(
                Measurement.node_id == node.id
            ).count()
            
            if existing > 100:
                continue
            
            # Генерируем 30 суток * 96 интервалов = 2880 измерений
            now = datetime.utcnow()
            base_power = node.nominal_power or 50.0
            
            for i in range(2880):
                timestamp = now - timedelta(minutes=15 * (2880 - i))
                hour = timestamp.hour
                
                # Суточный цикл нагрузки
                hour_factor = 0.6 + 0.4 * (1 - ((hour - 14) ** 2) / 144)
                power = base_power * hour_factor * random.uniform(0.9, 1.1)
                
                measurement = Measurement(
                    node_id=node.id,
                    timestamp=timestamp,
                    current=random.uniform(150, 250),
                    voltage=random.uniform(108, 112),
                    active_power=power,
                    reactive_power=power * 0.3,
                    frequency=random.uniform(49.9, 50.1),
                    power_factor=random.uniform(0.9, 0.95),
                    is_valid=True
                )
                db.add(measurement)
                total += 1
        
        db.commit()
        return {"message": f"Создано {total} исторических измерений (30 суток)"}
    finally:
        db.close()


if __name__ == "__main__":
    print("=== Инициализация БД АСБН ===")
    print("Разработчик: Голдашевский Н.С., гр. 4331\n")
    
    # Создание таблиц
    Base.metadata.create_all(bind=engine)
    print("✓ Таблицы БД созданы")
    
    # Топология
    topo = NetworkTopology()
    result = topo.seed_topology()
    print(f"✓ {result}")
    
    # Измерения (последние 20)
    gen = DataGenerator()
    result = gen.seed_measurements(count_per_node=20)
    print(f"✓ {result}")
    
    # Исторические данные для обучения модели (30 суток)
    result = create_historical_measurements()
    print(f"✓ {result}")
    
    # Пользователи
    result = create_admin_user()
    print(f"✓ {result}")
    
    result = create_test_users()
    print(f"✓ {result}")

    result = create_test_notifications()
    print(f"✓ {result}")

    result = create_test_recommendations()
    print(f"✓ {result}")
    
    # Тестовые события
    gen.generate_event("system_start", "low", "Система запущена")
    gen.generate_event("topology_loaded", "low", "Топология сети загружена")
    print("✓ Системные события созданы")
    
    print("\n=== Инициализация завершена ===")
    print("\nТестовые учётные данные:")
    print("  admin / Admin123!")
    print("  dispatcher1 / Disp123!")
    print("  analyst1 / Anal123!")
    print("\nДанные для обучения модели прогноза:")
    print("  30 суток измерений (2880 записей на узел)")