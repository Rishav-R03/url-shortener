# app/config.py
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic-settings for robust configuration management.
    """
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+asyncpg://postgres:root123@localhost:5432/url_shortener_db"
    REDIS_HOST: str = "redis-19852.c17.us-east-1-4.ec2.redns.redis-cloud.com"
    REDIS_PORT: int = 19852
    REDIS_DB: int = 0
    SHORT_CODE_LENGTH: int = 8
    RATE_LIMIT_PER_MINUTE: int = 10

settings = Settings()

