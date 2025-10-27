"""
Конфигурация приложения БЕЗ использования .env файлов
Все настройки зашиты напрямую для простоты использования
"""
import os
from typing import List

class Settings:
    """Настройки приложения"""
    
    # === DATABASE ===
    # Среда Emergent использует MongoDB
    MONGO_URL: str = os.getenv(
        "MONGO_URL",
        "mongodb://localhost:27017"
    )
    DB_NAME: str = os.getenv("DB_NAME", "dm_cloud_mvp")
    
    # === APPLICATION ===
    APP_NAME: str = "DataMetrics Cloud MVP"
    APP_VERSION: str = "2.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "production")
    DEBUG: bool = APP_ENV == "development"
    
    # === SECURITY ===
    # В production замените на свой секретный ключ!
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "dm_cloud_mvp_secret_key_change_in_production_min_32_chars_here_2024"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 дней
    
    # === CORS ===
    # Разрешаем все источники для упрощения работы с preview
    CORS_ORIGINS: List[str] = ["*"]
    
    # === API ===
    API_VERSION_STR: str = "/api"
    
    # === FILE UPLOADS ===
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10 MB
    UPLOAD_PATH: str = "/app/uploads"
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf", ".doc", ".docx", ".xls", ".xlsx",
        ".jpg", ".jpeg", ".png", ".gif",
        ".zip", ".rar", ".7z"
    ]
    
    # === TELEGRAM (опционально) ===
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    TELEGRAM_ENABLED: bool = bool(TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
    
    # === PAGINATION ===
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # === LOGGING ===
    LOG_LEVEL: str = "INFO" if APP_ENV == "production" else "DEBUG"

# Создаем глобальный экземпляр настроек
settings = Settings()

# Для удобства экспортируем settings
__all__ = ["settings"]
