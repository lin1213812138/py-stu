from typing import Annotated
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.position import PositionCreate, PositionResponse, PositionUpdate
from app.services.position_service import PositionService
from app.utils.response import APIResponse

router = APIRouter(prefix="/positions", tags=["Position"])
service = PositionService()


@router.get("")
async def list_positions(
    current_user: Annotated[User, Depends(get_current_user)],
    department_id: str = Query(...),
) -> APIResponse:
    items = await service.get_by_department(department_id)
    return APIResponse(data=[PositionResponse.model_validate(u).model_dump() for u in items])


@router.post("")
async def create_position(
    body: PositionCreate,
    current_user: Annotated[User, Depends(require_permission("system:position:create"))],
) -> APIResponse:
    pos = await service.create(body)
    return APIResponse(data=PositionResponse.model_validate(pos))


@router.get("/{pos_id}")
async def get_position(
    pos_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    pos = await service.get_by_id(pos_id)
    return APIResponse(data=PositionResponse.model_validate(pos))


@router.put("/{pos_id}")
async def update_position(
    pos_id: str,
    body: PositionUpdate,
    current_user: Annotated[User, Depends(require_permission("system:position:update"))],
) -> APIResponse:
    pos = await service.update(pos_id, body)
    return APIResponse(data=PositionResponse.model_validate(pos))


@router.delete("/{pos_id}")
async def delete_position(
    pos_id: str,
    current_user: Annotated[User, Depends(require_permission("system:position:delete"))],
) -> APIResponse:
    await service.delete(pos_id)
    return APIResponse(message="删除成功")
