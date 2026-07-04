import time

from redis.asyncio import Redis

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsError, TokenError, UserExistsError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginResponse, TokenResponse
from app.schemas.user import UserResponse


class AuthService:

    def __init__(self):
        self.repo = UserRepository()

    async def register(self, username: str, email: str, password: str) -> User:
        existing = await self.repo.get_by_username(username)
        if existing:
            raise UserExistsError()
        existing = await self.repo.get_by_email(email)
        if existing:
            raise UserExistsError()

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )
        return await self.repo.create(user)

    async def login(self, username: str, password: str, redis: Redis) -> LoginResponse:
        user = await self.repo.get_by_username(username)
        if not user:
            raise InvalidCredentialsError()
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        if user.status == 0:
            raise InvalidCredentialsError()

        access_token = create_access_token(user.id, user.username, user.role)
        refresh_token = create_refresh_token(user.id)

        await redis.set(f"refresh_token:{user.id}", refresh_token)

        user.last_login_time = int(time.time() * 1000)
        await user.save()

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse.model_validate(user),
        )

    async def logout(self, user_id: str, access_token: str, redis: Redis) -> None:
        await redis.delete(f"refresh_token:{user_id}")
        await redis.setex(f"blacklist:{access_token}", settings.JWT_ACCESS_EXPIRE, "1")

    async def refresh_token(self, refresh_token: str, redis: Redis) -> TokenResponse:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise TokenError()

        if payload.get("type") != "refresh":
            raise TokenError()

        user_id = payload["sub"]
        stored = await redis.get(f"refresh_token:{user_id}")
        if stored != refresh_token:
            raise TokenError()

        user = await self.repo.get_by_id(user_id)
        if not user or user.status == 0:
            raise TokenError()

        new_access = create_access_token(user.id, user.username, user.role)
        new_refresh = create_refresh_token(user.id)
        await redis.set(f"refresh_token:{user.id}", new_refresh)

        return TokenResponse(access_token=new_access, refresh_token=new_refresh)
