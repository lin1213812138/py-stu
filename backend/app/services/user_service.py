from typing import Optional
from uuid import UUID

from app.core.exceptions import UserNotFoundError
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.utils.pagination import PageParams, PageResult


class UserService:

    def __init__(self):
        self.repo = UserRepository()

    async def get_me(self, user_id: UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def get_user_list(
        self,
        params: PageParams,
        username: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[int] = None,
    ) -> PageResult:
        return await self.repo.get_list(params, username, email, status)

    async def get_user(self, user_id: UUID) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user

    async def create_user(self, data: UserCreate) -> User:
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            nickname=data.nickname,
            avatar=data.avatar,
            role=data.role,
        )
        return await self.repo.create(user)

    async def update_user(self, user_id: UUID, data: UserUpdate) -> User:
        update_dict = data.model_dump(exclude_unset=True)
        user = await self.repo.update(user_id, update_dict)
        if not user:
            raise UserNotFoundError()
        return user

    async def delete_user(self, user_id: UUID) -> None:
        deleted = await self.repo.delete(user_id)
        if not deleted:
            raise UserNotFoundError()
