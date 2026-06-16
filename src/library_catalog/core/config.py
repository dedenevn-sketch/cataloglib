"""Конфигурация приложения через pydantic-settings."""

from functools import lru_cache
from typing import Literal

from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения, загружаются из .env с валидацией через типы."""

    # Базовые
    app_name: str = "Library Catalog API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # База данных
    database_url: PostgresDsn
    database_pool_size: int = 20

    # API
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    cors_origins: list[str] = ["*"]

    # Внешние сервисы
    openlibrary_base_url: str = "https://openlibrary.org"
    openlibrary_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url_str(self) -> str:
        """Строковое представление DATABASE_URL для SQLAlchemy."""
        return str(self.database_url)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Кэшированный доступ к настройкам."""
    return Settings()


settings = get_settings()
