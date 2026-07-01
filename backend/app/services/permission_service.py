from uuid import UUID


class PermissionService:

    @staticmethod
    async def get_user_menu_ids(role_ids: list[UUID]) -> set[UUID]:
        return set()

    @staticmethod
    async def get_user_permissions(role_ids: list[UUID]) -> set[str]:
        return set()
