from uuid import UUID

from app.models.menu import Menu
from app.models.role import Role


class PermissionService:

    @staticmethod
    async def get_user_permissions(role_ids: list[UUID]) -> set[str]:
        if not role_ids:
            return set()
        roles = await Role.find({"_id": {"$in": role_ids}, "status": 1}).to_list()
        keys: set[str] = set()
        menu_ids = set()
        for role in roles:
            for perm in role.permissions:
                menu_ids.add(perm.menu_id)
                keys.update(perm.button_keys)
        if menu_ids:
            menus = await Menu.find({"_id": {"$in": list(menu_ids)}, "status": 1}).to_list()
            for m in menus:
                if m.permission_key:
                    keys.add(m.permission_key)
        return keys

    @staticmethod
    async def get_user_menu_ids(role_ids: list[UUID]) -> set[UUID]:
        if not role_ids:
            return set()
        roles = await Role.find({"_id": {"$in": role_ids}, "status": 1}).to_list()
        menu_ids = set()
        for role in roles:
            for perm in role.permissions:
                menu_ids.add(perm.menu_id)
        return menu_ids
