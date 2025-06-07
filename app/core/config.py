from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Настройки базы данных
    DATABASE_URL: str

    # Настройки JWT
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # Настройки приложения
    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool
    ENVIRONMENT: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()

