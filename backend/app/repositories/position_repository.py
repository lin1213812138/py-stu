from datetime import datetime
from typing import Optional
from uuid import UUID

from app.models.position import Position


class PositionRepository:

    @staticmethod
    async def create(pos: Position) -> Position:
        return await pos.insert()

    @staticmethod
    async def get_by_id(pos_id: UUID) -> Optional[Position]:
        return await Position.get(pos_id)

    @staticmethod
    async def get_by_department(department_id: UUID) -> list[Position]:
        return await Position.find({"department_id": department_id, "status": 1}).sort("sort").to_list()

    @staticmethod
    async def update(pos_id: UUID, update_data: dict) -> Optional[Position]:
        pos = await Position.get(pos_id)
        if not pos:
            return None
        update_data["updated_at"] = datetime.utcnow()
        await pos.update({"$set": update_data})
        return await Position.get(pos_id)

    @staticmethod
    async def delete(pos_id: UUID) -> bool:
        pos = await Position.get(pos_id)
        if not pos:
            return False
        await pos.delete()
        return True
