from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "python-stu"
    ENV: str = "development"

    MONGODB_URL: str = "mongodb://mongo:27017"
    MONGODB_DATABASE: str = "app"

    REDIS_URL: str = "redis://redis:6379"

    JWT_SECRET: str = "change-this-in-production"
    JWT_ACCESS_EXPIRE: int = 1800
    JWT_REFRESH_EXPIRE: int = 604800

    CORS_ORIGINS: list[str] = ["*"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
