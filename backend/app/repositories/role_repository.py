import time
from typing import Optional
from app.models.role import Role
from app.utils.pagination import PageParams, PageResult


class RoleRepository:

    @staticmethod
    async def create(role: Role) -> Role:
        return await role.insert()

    @staticmethod
    async def get_by_id(role_id: str) -> Optional[Role]:
        return await Role.get(role_id)

    @staticmethod
    async def get_by_code(code: str) -> Optional[Role]:
        return await Role.find_one(Role.code == code)

    @staticmethod
    async def get_list(params: PageParams, name: Optional[str] = None) -> PageResult:
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        total = await Role.find(query).count()
        items = await Role.find(query).skip((params.page - 1) * params.page_size).limit(params.page_size).to_list()
        return PageResult(items=items, total=total, page=params.page, page_size=params.page_size, total_pages=(total + params.page_size - 1) // params.page_size)

    @staticmethod
    async def get_all() -> list[Role]:
        return await Role.find({"status": 1}).to_list()

    @staticmethod
    async def get_by_ids(role_ids: list[str]) -> list[Role]:
        return await Role.find({"_id": {"$in": role_ids}, "status": 1}).to_list()

    @staticmethod
    async def update(role_id: str, update_data: dict) -> Optional[Role]:
        role = await Role.get(role_id)
        if not role:
            return None
        update_data["updated_at"] = int(time.time())
        await role.update({"$set": update_data})
        return await Role.get(role_id)

    @staticmethod
    async def delete(role_id: str) -> bool:
        role = await Role.get(role_id)
        if not role:
            return False
        await role.delete()
        return True
