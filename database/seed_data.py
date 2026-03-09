"""
Инициализация БД тестовыми данными
Разработчик: Голдашевский Н.С., гр. 4331
"""
import sys
sys.path.append('.')

from backend.app.database import engine, Base, SessionLocal
from backend.app.models import User
from backend.app.core.security import get_password_hash
from backend.simulator.network_topology import NetworkTopology
from backend.simulator.data_generator import DataGenerator

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
    
    # Измерения
    gen = DataGenerator()
    result = gen.seed_measurements(count_per_node=20)
    print(f"✓ {result}")
    
    # Пользователи
    result = create_admin_user()
    print(f"✓ {result}")
    
    result = create_test_users()
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