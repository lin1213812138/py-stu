from app.core.exceptions import AppException
from app.models.menu import Menu
from app.repositories.menu_repository import MenuRepository
from app.schemas.menu import MenuCreate, MenuResponse, MenuUpdate


class MenuService:

    def __init__(self):
        self.repo = MenuRepository()

    def _build_tree(self, menus: list[Menu]) -> list[dict]:
        menu_map = {str(m.id): MenuResponse.model_validate(m).model_dump() for m in menus}
        for m in menus:
            menu_map[str(m.id)]["children"] = []
        tree = []
        for m in menus:
            node = menu_map[str(m.id)]
            if m.parent_id and str(m.parent_id) in menu_map:
                menu_map[str(m.parent_id)]["children"].append(node)
            else:
                tree.append(node)
        return tree

    async def get_tree(self) -> list[dict]:
        menus = await self.repo.get_all()
        return self._build_tree(menus)

    async def get_user_menu_tree(self, menu_ids: set[str]) -> list[dict]:
        ids = list(menu_ids)
        if not ids:
            return []
        menus = await Menu.find(
            {"_id": {"$in": ids}, "type": {"$in": ["dir", "menu", "link"]}, "visible": 1, "status": 1}
        ).sort("sort").to_list()
        return self._build_tree(menus)

    async def get_by_id(self, menu_id: str) -> Menu:
        menu = await self.repo.get_by_id(menu_id)
        if not menu:
            raise AppException(code=10011, message="Menu not found")
        return menu

    async def create(self, data: MenuCreate) -> Menu:
        menu = Menu(**data.model_dump())
        return await self.repo.create(menu)

    async def update(self, menu_id: str, data: MenuUpdate) -> Menu:
        menu = await self.repo.update(menu_id, data.model_dump(exclude_unset=True))
        if not menu:
            raise AppException(code=10011, message="Menu not found")
        return menu

    async def delete(self, menu_id: str) -> None:
        deleted = await self.repo.delete(menu_id)
        if not deleted:
            raise AppException(code=10011, message="Menu not found")
