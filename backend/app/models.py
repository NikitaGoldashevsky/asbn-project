"""
SQLAlchemy модели базы данных
Разработчик: Голдашевский Н.С., гр. 4331
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, 
    DateTime, ForeignKey, Text, Enum, JSON
)
from sqlalchemy.orm import relationship
import enum
from backend.app.database import Base


# === ENUM типы ===
class UserRole(str, enum.Enum):
    """Роли пользователей"""
    DISPATCHER = "dispatcher"
    ANALYST = "analyst"
    ADMIN = "admin"


class NodeStatus(str, enum.Enum):
    """Статусы узлов сети"""
    NORMA = "norma"
    WARNING = "warning"
    OVERLOAD = "overload"
    EMERGENCY = "emergency"
    OFFLINE = "offline"


class NotificationType(str, enum.Enum):
    """Типы уведомлений"""
    INFO = "info"
    WARNING = "warning"
    ALERT = "alert"


class CommandStatus(str, enum.Enum):
    """Статусы команд"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class NotificationStatus(str, enum.Enum):
    """Статусы уведомлений"""
    SENT = "sent"
    DELIVERED = "delivered"
    ERROR = "error"


# === Таблица: users ===
class User(Base):
    """Пользователи системы"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.ANALYST)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Связи
    notifications = relationship("Notification", back_populates="user")
    commands = relationship("CommandLog", back_populates="operator")


# === Таблица: network_topology ===
class NetworkNode(Base):
    """Узлы энергосети"""
    __tablename__ = "network_topology"
    
    id = Column(Integer, primary_key=True, index=True)
    object_type = Column(String(30), nullable=False)  # substation, line, transformer, node
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("network_topology.id"), nullable=True)
    nominal_voltage = Column(Float, nullable=True)  # кВ
    nominal_current = Column(Float, nullable=True)  # А
    nominal_power = Column(Float, nullable=True)  # МВт
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    status = Column(Enum(NodeStatus), default=NodeStatus.NORMA)
    
    # Связи
    measurements = relationship("Measurement", back_populates="node")
    forecasts = relationship("Forecast", back_populates="node")


# === Таблица: measurements ===
class Measurement(Base):
    """Измерения с датчиков"""
    __tablename__ = "measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("network_topology.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    current = Column(Float, nullable=True)  # А
    voltage = Column(Float, nullable=True)  # кВ
    active_power = Column(Float, nullable=True)  # МВт
    reactive_power = Column(Float, nullable=True)  # Мвар
    frequency = Column(Float, nullable=True)  # Гц
    power_factor = Column(Float, nullable=True)
    is_valid = Column(Boolean, default=True)
    
    # Связи
    node = relationship("NetworkNode", back_populates="measurements")


# === Таблица: forecasts ===
class Forecast(Base):
    """Прогнозы нагрузки"""
    __tablename__ = "forecasts"
    
    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(Integer, ForeignKey("network_topology.id"), nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    predicted_load = Column(Float, nullable=False)
    confidence_lower = Column(Float, nullable=True)  # 5-й процентиль
    confidence_upper = Column(Float, nullable=True)  # 95-й процентиль
    mape_error = Column(Float, nullable=True)
    model_params = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    node = relationship("NetworkNode", back_populates="forecasts")


# === Таблица: balancing_recommendations ===
class BalancingRecommendation(Base):
    """Рекомендации по балансировке"""
    __tablename__ = "balancing_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("network_topology.id"), nullable=False)
    target_node_id = Column(Integer, ForeignKey("network_topology.id"), nullable=False)
    power_transfer = Column(Float, nullable=False)  # МВт
    command_type = Column(String(50), nullable=False)
    status = Column(Enum(CommandStatus), default=CommandStatus.PENDING)
    confirmed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    effect_description = Column(Text, nullable=True)


# === Таблица: commands_log ===
class CommandLog(Base):
    """Журнал управляющих команд"""
    __tablename__ = "commands_log"
    
    id = Column(Integer, primary_key=True, index=True)
    command_type = Column(String(50), nullable=False)
    parameters = Column(JSON, nullable=True)
    status = Column(String(30), default="sent")
    sent_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Связи
    operator = relationship("User", back_populates="commands")


# === Таблица: notifications ===
class Notification(Base):
    """Уведомления пользователей"""
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    message = Column(Text, nullable=False)
    channel = Column(String(20), nullable=False)  # interface, email, sms
    status = Column(Enum(NotificationStatus), default=NotificationStatus.SENT)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Boolean, default=False)
    
    # Связи
    user = relationship("User", back_populates="notifications")


# === Таблица: system_events ===
class SystemEvent(Base):
    """Системные события"""
    __tablename__ = "system_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    timestamp = Column(DateTime, default=datetime.utcnow)
    source_module = Column(String(50), nullable=True)