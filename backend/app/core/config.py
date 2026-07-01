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
    CORS_ORIGINS: list[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file_encoding="utf-8",
    )

    def __init__(self, **kwargs: object) -> None:
        env = os.getenv("ENV", "development")
        env_file = f".env.{env}"
        if not Path(env_file).exists():
            env_file = ".env"
            if not Path(env_file).exists():
                logger.warning(
                    "No .env.{} or .env file found, using defaults", env
                )
                super().__init__(**kwargs)
                return
        super().__init__(_env_file=env_file, **kwargs)


settings = Settings()
