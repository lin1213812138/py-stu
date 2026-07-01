from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.role import RoleCreate, RoleResponse, RoleUpdate
from app.services.role_service import RoleService
from app.utils.pagination import PageParams
from app.utils.response import APIResponse

router = APIRouter(prefix="/roles", tags=["Role"])
service = RoleService()


@router.get("")
async def list_roles(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
) -> APIResponse:
    params = PageParams(page=page, page_size=page_size)
    result = await service.get_list(params, name)
    items = [RoleResponse.model_validate(u).model_dump() for u in result.items]
    data = result.model_dump()
    data["items"] = items
    return APIResponse(data=data)


@router.get("/all")
async def all_roles(current_user: Annotated[User, Depends(get_current_user)]) -> APIResponse:
    items = await service.get_all()
    return APIResponse(data=[RoleResponse.model_validate(u).model_dump() for u in items])


@router.post("")
async def create_role(
    body: RoleCreate,
    current_user: Annotated[User, Depends(require_permission("system:role:create"))],
) -> APIResponse:
    role = await service.create(body)
    return APIResponse(data=RoleResponse.model_validate(role))


@router.get("/{role_id}")
async def get_role(
    role_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    role = await service.get_by_id(role_id)
    return APIResponse(data=RoleResponse.model_validate(role))


@router.put("/{role_id}")
async def update_role(
    role_id: UUID,
    body: RoleUpdate,
    current_user: Annotated[User, Depends(require_permission("system:role:update"))],
) -> APIResponse:
    role = await service.update(role_id, body)
    return APIResponse(data=RoleResponse.model_validate(role))


@router.delete("/{role_id}")
async def delete_role(
    role_id: UUID,
    current_user: Annotated[User, Depends(require_permission("system:role:delete"))],
) -> APIResponse:
    await service.delete(role_id)
    return APIResponse(message="Role deleted")
