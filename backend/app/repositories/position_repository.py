import time
from typing import Optional
from app.models.position import Position


class PositionRepository:

    @staticmethod
    async def create(pos: Position) -> Position:
        return await pos.insert()

    @staticmethod
    async def get_by_id(pos_id: str) -> Optional[Position]:
        return await Position.get(pos_id)

    @staticmethod
    async def get_by_department(department_id: str) -> list[Position]:
        return await Position.find({"department_id": department_id, "status": 1}).sort("sort").to_list()

    @staticmethod
    async def update(pos_id: str, update_data: dict) -> Optional[Position]:
        pos = await Position.get(pos_id)
        if not pos:
            return None
        update_data["updated_at"] = int(time.time() * 1000)
        await pos.update({"$set": update_data})
        return await Position.get(pos_id)

    @staticmethod
    async def delete(pos_id: str) -> bool:
        pos = await Position.get(pos_id)
        if not pos:
            return False
        await pos.delete()
        return True
