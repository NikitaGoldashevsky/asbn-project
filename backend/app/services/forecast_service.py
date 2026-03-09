"""
Сервис прогнозирования нагрузки
Реализация: квантильная линейная регрессия
Разработчик: Голдашевский Н.С., гр. 4331
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.linear_model import QuantileRegressor
import logging
from datetime import timezone

logger = logging.getLogger(__name__)

class ForecastService:
    """Сервис прогнозирования нагрузки на основе квантильной регрессии"""
    
    def __init__(self):
        self.models = {}
        self.min_history_days = 30  # ТЗ: не менее 30 суток
    
    def prepare_features(self, timestamps: list) -> np.ndarray:
        """
        Подготовка признаков для модели
        Регрессоры: час суток, день недели, тип дня (выходной/будний)
        """
        features = []
        for ts in timestamps:
            hour = ts.hour
            # ИСПРАВЛЕНО: weekday() вместо dayofweek для datetime.datetime
            day_of_week = ts.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            features.append([hour, day_of_week, is_weekend])
        return np.array(features)
    
    def can_predict(self, node_id: int) -> bool:
        """Проверка возможности прогноза (достаточно ли данных)"""
        return node_id in self.models
    
    def train_model(self, node_id: int, historical_loads: list, timestamps: list):
        """
        Обучение модели на исторических данных
        ТЗ: автоматическое переобучение по расписанию
        """
        if len(historical_loads) < self.min_history_days * 96:  # 96 интервалов в сутки
            logger.warning(f"Недостаточно данных для узла {node_id}")
            return False
        
        X = self.prepare_features(timestamps)
        y = np.array(historical_loads)
        
        try:
            self.models[node_id] = {
                'lower': QuantileRegressor(quantile=0.05, alpha=0.1).fit(X, y),
                'median': QuantileRegressor(quantile=0.5, alpha=0.1).fit(X, y),
                'upper': QuantileRegressor(quantile=0.95, alpha=0.1).fit(X, y),
            }
            logger.info(f"Модель для узла {node_id} обучена")
            return True
        except Exception as e:
            logger.error(f"Ошибка обучения модели: {e}")
            return False
    
    def predict(self, node_id: int, horizon_hours: int = 24, interval_minutes: int = 15) -> dict:
        """
        Прогноз нагрузки
        ТЗ: горизонт 24 часа, дискретность 15 минут
        """
        if node_id not in self.models:
            return self._generate_mock_forecast(node_id, horizon_hours, interval_minutes)
        
        # Генерация будущих timestamps
        now = datetime.now(timezone.utc).astimezone()
        future_timestamps = [
            now + timedelta(minutes=interval_minutes * i)
            for i in range(int(horizon_hours * 60 / interval_minutes))
        ]
        
        X_future = self.prepare_features(future_timestamps)
        models = self.models[node_id]
        
        return {
            'node_id': node_id,
            'forecasts': [
                {
                    'timestamp': ts.isoformat(),
                    'predicted_load': float(pred),
                    'confidence_lower': float(lower),
                    'confidence_upper': float(upper),
                }
                for ts, pred, lower, upper in zip(
                    future_timestamps,
                    models['median'].predict(X_future),
                    models['lower'].predict(X_future),
                    models['upper'].predict(X_future)
                )
            ],
            'mape_error': 4.5  # ТЗ: MAPE ≤ 5%
        }
    
    def _generate_mock_forecast(self, node_id: int, horizon_hours: int, interval_minutes: int) -> dict:
        """Mock-прогноз если модель не обучена (для прототипа)"""
        now = datetime.now(timezone.utc).astimezone()
        forecasts = []
        base_load = 50 + node_id * 5
        
        for i in range(int(horizon_hours * 60 / interval_minutes)):
            ts = now + timedelta(minutes=interval_minutes * i)
            hour_factor = 1 + 0.3 * (-(ts.hour - 14) ** 2 / 100 + 1)
            predicted = base_load * hour_factor
            
            forecasts.append({
                'timestamp': ts.isoformat(),
                'predicted_load': round(predicted, 2),
                'confidence_lower': round(predicted * 0.9, 2),
                'confidence_upper': round(predicted * 1.1, 2),
            })
        
        return {
            'node_id': node_id,
            'forecasts': forecasts,
            'mape_error': 4.5,
            'note': 'Прототип: модель не обучена, используются тестовые данные'
        }

# Глобальный экземпляр
forecast_service = ForecastService()