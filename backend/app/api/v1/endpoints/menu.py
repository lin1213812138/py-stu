from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.menu import MenuCreate, MenuResponse, MenuUpdate
from app.services.menu_service import MenuService
from app.services.permission_service import PermissionService
from app.utils.response import APIResponse

router = APIRouter(prefix="/menus", tags=["Menu"])
service = MenuService()


@router.get("")
async def list_menus(current_user: Annotated[User, Depends(get_current_user)]) -> APIResponse:
    tree = await service.get_tree()
    return APIResponse(data=tree)


@router.get("/user")
async def user_menus(current_user: Annotated[User, Depends(get_current_user)]) -> APIResponse:
    menu_ids = await PermissionService.get_user_menu_ids(current_user.role_ids)
    tree = await service.get_user_menu_tree(menu_ids)
    return APIResponse(data=tree)


@router.post("")
async def create_menu(
    body: MenuCreate,
    current_user: Annotated[User, Depends(require_permission("system:menu:create"))],
) -> APIResponse:
    menu = await service.create(body)
    return APIResponse(data=MenuResponse.model_validate(menu))


@router.get("/{menu_id}")
async def get_menu(
    menu_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    menu = await service.get_by_id(menu_id)
    return APIResponse(data=MenuResponse.model_validate(menu))


@router.put("/{menu_id}")
async def update_menu(
    menu_id: UUID,
    body: MenuUpdate,
    current_user: Annotated[User, Depends(require_permission("system:menu:update"))],
) -> APIResponse:
    menu = await service.update(menu_id, body)
    return APIResponse(data=MenuResponse.model_validate(menu))


@router.delete("/{menu_id}")
async def delete_menu(
    menu_id: UUID,
    current_user: Annotated[User, Depends(require_permission("system:menu:delete"))],
) -> APIResponse:
    await service.delete(menu_id)
    return APIResponse(message="Menu deleted")
