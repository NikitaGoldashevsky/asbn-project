"""
Конфигурация приложения
"""
import yaml
from pathlib import Path
from typing import List


class Config:
    """Класс конфигурации приложения"""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = self._load_config()
    
    def _load_config(self) -> dict:
        """Загрузка конфигурации из YAML файла"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}
    
    def get(self, key: str, default=None):
        """Получение значения по ключу"""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    @property
    def app_name(self) -> str:
        return self.get('app.name', 'АСБН')
    
    @property
    def app_version(self) -> str:
        return self.get('app.version', '1.0.0')
    
    @property
    def debug(self) -> bool:
        return self.get('app.debug', False)
    
    @property
    def database_url(self) -> str:
        return self.get('database.url', 'sqlite:///./database/asbn.db')
    
    @property
    def jwt_secret_key(self) -> str:
        return self.get('security.jwt_secret_key', 'secret')
    
    @property
    def jwt_algorithm(self) -> str:
        return self.get('security.jwt_algorithm', 'HS256')
    
    @property
    def access_token_expire_minutes(self) -> int:
        return self.get('security.access_token_expire_minutes', 30)
    
    @property
    def warning_load_percent(self) -> float:
        return self.get('thresholds.warning_load_percent', 85.0)
    
    @property
    def emergency_load_percent(self) -> float:
        return self.get('thresholds.emergency_load_percent', 95.0)


# Глобальный экземпляр конфигурации
config = Config()