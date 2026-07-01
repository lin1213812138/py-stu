from app.core.exceptions import AppException
from app.models.role import Role
from app.repositories.role_repository import RoleRepository
from app.schemas.role import RoleCreate, RoleUpdate
from app.utils.pagination import PageParams


class RoleService:

    def __init__(self):
        self.repo = RoleRepository()

    async def get_list(self, params: PageParams, name: str | None = None):
        return await self.repo.get_list(params, name)

    async def get_all(self) -> list[Role]:
        return await self.repo.get_all()

    async def get_by_id(self, role_id: str) -> Role:
        role = await self.repo.get_by_id(role_id)
        if not role:
            raise AppException(code=10012, message="Role not found")
        return role

    async def create(self, data: RoleCreate) -> Role:
        existing = await self.repo.get_by_code(data.code)
        if existing:
            raise AppException(code=10014, message="Duplicate role code")
        role = Role(**data.model_dump())
        return await self.repo.create(role)

    async def update(self, role_id: str, data: RoleUpdate) -> Role:
        update_dict = data.model_dump(exclude_unset=True)
        if "code" in update_dict:
            existing = await self.repo.get_by_code(update_dict["code"])
            if existing and existing.id != role_id:
                raise AppException(code=10014, message="Duplicate role code")
        role = await self.repo.update(role_id, update_dict)
        if not role:
            raise AppException(code=10012, message="Role not found")
        return role

    async def delete(self, role_id: str) -> None:
        deleted = await self.repo.delete(role_id)
        if not deleted:
            raise AppException(code=10012, message="Role not found")
