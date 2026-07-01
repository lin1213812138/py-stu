from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from app.core.config import settings


async def init_db() -> None:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DATABASE]
    await init_beanie(
        database=db,
        document_models=[
            "app.models.user.User",
        ],
    )
    logger.info(f"MongoDB connected: {settings.MONGODB_URL}/{settings.MONGODB_DATABASE}")
