from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import HTTPAuthorizationCredentials
from redis.asyncio import Redis

from app.api.deps import get_current_user, require_permission, security_scheme
from app.database.redis import get_redis
from app.models.user import User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterRequest
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.utils.response import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])
service = AuthService()


@router.post("/register")
async def register(
    body: RegisterRequest,
    request: Request,
) -> APIResponse:
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    user = await service.register(body.username, body.email, body.password, ip, user_agent)
    return APIResponse(data=UserResponse.model_validate(user))


@router.post("/login")
async def login(
    body: LoginRequest,
    redis: Annotated[Redis, Depends(get_redis)],
    request: Request,
) -> APIResponse:
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    tokens = await service.login(body.username, body.password, redis, ip, user_agent)
    return APIResponse(data=tokens.model_dump())


@router.post("/logout")
async def logout(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    current_user: Annotated[User, Depends(get_current_user)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> APIResponse:
    await service.logout(current_user.id, credentials.credentials, redis)
    return APIResponse(message="退出成功")


@router.get("/online")
async def get_online_users(
    current_user: Annotated[User, Depends(require_permission("system:user:list"))],
    redis: Annotated[Redis, Depends(get_redis)],
) -> APIResponse:
    users = await service.get_online_users(redis)
    return APIResponse(data=users)


@router.post("/refresh")
async def refresh(body: RefreshRequest, redis: Annotated[Redis, Depends(get_redis)]) -> APIResponse:
    tokens = await service.refresh_token(body.refresh_token, redis)
    return APIResponse(data=tokens.model_dump())
