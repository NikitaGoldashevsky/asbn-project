"""
Топология энергосети (эмуляция)
Разработчик: Голдашевский Н.С., гр. 4331
"""
from sqlalchemy.orm import Session
from backend.app.models import NetworkNode
from backend.app.database import SessionLocal

class NetworkTopology:
    """Класс для создания тестовой топологии сети"""
    
    def __init__(self):
        self.substations = [
            {"name": "ПС-1 Северная", "voltage": 110, "power": 50.0, "lat": 59.95, "lon": 30.35},
            {"name": "ПС-2 Центральная", "voltage": 110, "power": 75.0, "lat": 59.93, "lon": 30.33},
            {"name": "ПС-3 Южная", "voltage": 110, "power": 60.0, "lat": 59.91, "lon": 30.35},
            {"name": "ПС-4 Восточная", "voltage": 35, "power": 40.0, "lat": 59.93, "lon": 30.40},
            {"name": "ПС-5 Западная", "voltage": 35, "power": 45.0, "lat": 59.93, "lon": 30.28},
        ]
    
    def seed_topology(self):
        """Заполнение БД тестовой топологией"""
        db = SessionLocal()
        try:
            # Проверяем есть ли уже данные
            existing = db.query(NetworkNode).count()
            if existing > 0:
                return {"message": "Топология уже существует", "count": existing}
            
            # Создаём узлы
            for i, sub in enumerate(self.substations, 1):
                node = NetworkNode(
                    object_type="substation",
                    name=sub["name"],
                    nominal_voltage=sub["voltage"],
                    nominal_power=sub["power"],
                    latitude=sub["lat"],
                    longitude=sub["lon"],
                    status="norma"
                )
                db.add(node)
            
            db.commit()
            return {"message": "Топология создана", "count": len(self.substations)}
        
        finally:
            db.close()