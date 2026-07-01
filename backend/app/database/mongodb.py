from beanie import init_beanie
from loguru import logger
from pymongo import AsyncMongoClient

from app.core.config import settings


async def init_db() -> None:
    client = AsyncMongoClient(settings.MONGODB_URL, serverSelectionTimeoutMS=3000)
    db = client.get_database(settings.MONGODB_DATABASE)
    await init_beanie(
        database=db,
        document_models=[
            "app.models.user.User",
        ],
    )
    logger.info(f"MongoDB connected: {settings.MONGODB_URL}/{settings.MONGODB_DATABASE}")
