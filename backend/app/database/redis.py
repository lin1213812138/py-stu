from redis.asyncio import Redis
from loguru import logger

from app.core.config import settings

redis_client: Redis | None = None


async def init_redis() -> None:
    global redis_client
    redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis_client.ping()
    logger.info(f"Redis connected: {settings.REDIS_URL}")


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()


async def get_redis() -> Redis:
    return redis_client
