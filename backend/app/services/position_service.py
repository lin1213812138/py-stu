from uuid import UUID

from app.core.exceptions import AppException
from app.models.position import Position
from app.repositories.position_repository import PositionRepository
from app.schemas.position import PositionCreate, PositionUpdate


class PositionService:

    def __init__(self):
        self.repo = PositionRepository()

    async def get_by_department(self, department_id: UUID) -> list[Position]:
        return await self.repo.get_by_department(department_id)

    async def get_by_id(self, pos_id: UUID) -> Position:
        pos = await self.repo.get_by_id(pos_id)
        if not pos:
            raise AppException(code=10010, message="Position not found")
        return pos

    async def create(self, data: PositionCreate) -> Position:
        pos = Position(**data.model_dump())
        return await self.repo.create(pos)

    async def update(self, pos_id: UUID, data: PositionUpdate) -> Position:
        pos = await self.repo.update(pos_id, data.model_dump(exclude_unset=True))
        if not pos:
            raise AppException(code=10010, message="Position not found")
        return pos

    async def delete(self, pos_id: UUID) -> None:
        deleted = await self.repo.delete(pos_id)
        if not deleted:
            raise AppException(code=10010, message="Position not found")
