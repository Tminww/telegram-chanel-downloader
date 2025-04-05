from pathlib import Path
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_PATH = Path(__file__).resolve().parent
print(BASE_PATH)

class Config(BaseSettings):
    # Обязательные параметры
    API_ID: int
    API_HASH: str
    PHONE: str
    CHANNEL_USERNAME: str
    
    SESSION_NAME: str = "telegram_session"
    PROXY: Optional[str] = None
    
    # Настройки загрузки
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="TELEGRAM_",  # Все переменные должны начинаться с TELEGRAM_
        extra="ignore"
    )

    @field_validator('PHONE')
    def validate_phone(cls, v):
        if not v.startswith('+'):
            raise ValueError("Номер телефона должен начинаться с '+'")
        return v

    @field_validator('CHANNEL_USERNAME')
    def validate_username(cls, v):
        if v and (v.startswith('@') or ' ' in v):
            raise ValueError("Username канала не должен содержать @ или пробелы")
        return v


settings = Config()