from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from redis.asyncio import Redis

from app.api.deps import get_current_user, security_scheme
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.utils.response import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
service = AuthService()


@router.post("/register")
async def register(body: RegisterRequest) -> APIResponse:
    user = await service.register(body.username, body.email, body.password)
    return APIResponse(data=UserResponse.model_validate(user))


@router.post("/login")
async def login(body: LoginRequest, redis: Annotated[Redis, Depends(get_redis)]) -> APIResponse:
    tokens = await service.login(body.username, body.password, redis)
    return APIResponse(data=tokens.model_dump())


@router.post("/logout")
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    current_user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> APIResponse:
    await service.logout(current_user.id, credentials.credentials, redis)
    return APIResponse(message="logout success")


@router.post("/refresh")
async def refresh(body: RefreshRequest, redis: Annotated[Redis, Depends(get_redis)]) -> APIResponse:
    tokens = await service.refresh_token(body.refresh_token, redis)
    return APIResponse(data=tokens.model_dump())
