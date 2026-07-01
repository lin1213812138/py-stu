from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from app.core.exceptions import TokenError, PermissionDeniedError
from app.core.security import decode_token
from app.database.redis import get_redis
from app.models.user import User
from app.repositories.user_repository import UserRepository

security_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security_scheme)],
    redis: Annotated[Redis, Depends(get_redis)],
) -> User:
    token = credentials.credentials
    try:
        payload = decode_token(token)
    except Exception:
        raise TokenError()

    blacklisted = await redis.get(f"blacklist:{token}")
    if blacklisted:
        raise TokenError()

    user = await UserRepository.get_by_id(UUID(payload["sub"]))
    if not user or user.status == 0:
        raise TokenError()

    return user


def require_role(required_role: str):
    async def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role != required_role and current_user.role != "admin":
            raise PermissionDeniedError()
        return current_user
    return role_checker
