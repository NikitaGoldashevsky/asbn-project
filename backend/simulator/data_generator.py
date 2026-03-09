"""
Генератор измерений (эмуляция датчиков)
Разработчик: Голдашевский Н.С., гр. 4331
"""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.models import Measurement, NetworkNode, SystemEvent
from backend.app.database import SessionLocal

class DataGenerator:
    """Генератор тестовых измерений"""
    
    def __init__(self):
        self.base_values = {
            "voltage": 110.0,
            "current": 200.0,
            "active_power": 40.0,
            "reactive_power": 15.0,
            "frequency": 50.0,
            "power_factor": 0.92
        }
    
    def generate_measurement(self, node_id: int, nominal_power: float = 50.0):
        """Генерация одного измерения"""
        # Добавляем случайные колебания
        load_factor = random.uniform(0.6, 0.95)  # Загрузка 60-95%
        
        return {
            "node_id": node_id,
            "timestamp": datetime.utcnow(),
            "current": self.base_values["current"] * load_factor * random.uniform(0.95, 1.05),
            "voltage": self.base_values["voltage"] * random.uniform(0.98, 1.02),
            "active_power": nominal_power * load_factor * random.uniform(0.95, 1.05),
            "reactive_power": self.base_values["reactive_power"] * random.uniform(0.9, 1.1),
            "frequency": self.base_values["frequency"] * random.uniform(0.998, 1.002),
            "power_factor": self.base_values["power_factor"] * random.uniform(0.98, 1.02),
            "is_valid": True
        }
    
    def seed_measurements(self, count_per_node: int = 10):
        """Заполнение БД тестовыми измерениями"""
        db = SessionLocal()
        try:
            nodes = db.query(NetworkNode).all()
            if not nodes:
                return {"message": "Нет узлов в топологии"}
            
            total = 0
            for node in nodes:
                for i in range(count_per_node):
                    measurement = Measurement(**self.generate_measurement(
                        node.id, 
                        node.nominal_power or 50.0
                    ))
                    measurement.timestamp = datetime.utcnow() - timedelta(minutes=i*15)
                    db.add(measurement)
                    total += 1
            
            db.commit()
            return {"message": "Измерения созданы", "count": total}
        
        finally:
            db.close()
    
    def generate_event(self, event_type: str, severity: str, description: str):
        """Создание системного события"""
        db = SessionLocal()
        try:
            event = SystemEvent(
                event_type=event_type,
                description=description,
                severity=severity,
                source_module="simulator"
            )
            db.add(event)
            db.commit()
            return {"message": "Событие создано", "id": event.id}
        finally:
            db.close()