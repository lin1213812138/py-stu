import time
from typing import Optional
from app.models.user import User
from app.utils.pagination import PageParams, PageResult


class UserRepository:

    @staticmethod
    async def create(user: User) -> User:
        return await user.insert()

    @staticmethod
    async def get_by_id(user_id: str) -> Optional[User]:
        return await User.get(user_id)

    @staticmethod
    async def get_by_username(username: str) -> Optional[User]:
        return await User.find_one(User.username == username)

    @staticmethod
    async def get_by_email(email: str) -> Optional[User]:
        return await User.find_one(User.email == email)

    @staticmethod
    async def get_list(
        params: PageParams,
        username: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[int] = None,
    ) -> PageResult:
        query = {}
        if username:
            query["username"] = {"$regex": username, "$options": "i"}
        if email:
            query["email"] = {"$regex": email, "$options": "i"}
        if status is not None:
            query["status"] = status

        total = await User.find(query).count()
        items = (
            await User.find(query)
            .skip((params.page - 1) * params.page_size)
            .limit(params.page_size)
            .to_list()
        )

        return PageResult(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size,
        )

    @staticmethod
    async def update(user_id: str, update_data: dict) -> Optional[User]:
        user = await User.get(user_id)
        if not user:
            return None
        update_data["updated_at"] = int(time.time() * 1000)
        await user.update({"$set": update_data})
        return await User.get(user_id)

    @staticmethod
    async def delete(user_id: str) -> bool:
        user = await User.get(user_id)
        if not user:
            return False
        await user.delete()
        return True

    @staticmethod
    async def count(filters: Optional[dict] = None) -> int:
        return await User.find(filters or {}).count()
