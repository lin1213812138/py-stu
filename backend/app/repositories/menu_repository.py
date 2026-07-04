import time
from typing import Optional

from app.models.menu import Menu


class MenuRepository:

    @staticmethod
    async def create(menu: Menu) -> Menu:
        return await menu.insert()

    @staticmethod
    async def get_by_id(menu_id: str) -> Optional[Menu]:
        return await Menu.get(menu_id)

    @staticmethod
    async def get_all() -> list[Menu]:
        return await Menu.find({"status": 1}).sort("sort").to_list()

    @staticmethod
    async def get_by_ids(menu_ids: list[str]) -> list[Menu]:
        return await Menu.find({"_id": {"$in": menu_ids}, "status": 1}).to_list()

    @staticmethod
    async def update(menu_id: str, update_data: dict) -> Optional[Menu]:
        menu = await Menu.get(menu_id)
        if not menu:
            return None
        update_data["updated_at"] = time.time() * 1000
        await menu.update({"$set": update_data})
        return await Menu.get(menu_id)

    @staticmethod
    async def delete(menu_id: str) -> bool:
        menu = await Menu.get(menu_id)
        if not menu:
            return False
        await menu.delete()
        return True
