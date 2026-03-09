"""
Точка входа для запуска АСБН
Разработчик: Голдашевский Н.С., гр. 4331
"""
import uvicorn
from backend.app.core.config import config

if __name__ == "__main__":
    print("=" * 50)
    print("АСБН - Автоматизированная Система Балансировки Нагрузок")
    print("Разработчик: Голдашевский Н.С., гр. 4331")
    print("=" * 50)
    print(f"\nЗапуск сервера на {config.get('server.host')}:{config.get('server.port')}")
    print(f"Документация API: http://127.0.0.1:8000/docs")
    print("\nНажмите Ctrl+C для остановки\n")
    
    uvicorn.run(
        "backend.app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )