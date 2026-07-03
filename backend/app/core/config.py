import os
from pathlib import Path

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENV: str = "development"
    APP_NAME: str = "python-stu"
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "app"
    REDIS_URL: str = "redis://localhost:6379"
    JWT_SECRET: str = "change-this-in-production"
    JWT_ACCESS_EXPIRE: int = 1800
    JWT_REFRESH_EXPIRE: int = 604800
    PORT: int = 8000
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
    )

    def __init__(self, **kwargs: object) -> None:
        env = os.getenv("ENV", "development")
        env_files = [".env"]
        env_specific = f".env.{env}"
        if Path(env_specific).exists():
            env_files.append(env_specific)
        if not Path(".env").exists():
            logger.warning("No .env file found, using defaults")
            super().__init__(**kwargs)
            return
        super().__init__(_env_file=env_files, **kwargs)


settings = Settings()
