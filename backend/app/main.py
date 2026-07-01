from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.core.exceptions import global_exception_handler, AppException
from app.database.mongodb import init_db
from app.database.redis import init_redis, close_redis
from app.middleware.auth import request_logging_middleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}...")
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"MongoDB connection failed (start Docker for DB): {e}")
    try:
        await init_redis()
    except Exception as e:
        logger.warning(f"Redis connection failed (start Docker for Redis): {e}")
    yield
    await close_redis()
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.middleware("http")(request_logging_middleware)

app.add_exception_handler(AppException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(v1_router)
