from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_role
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService
from app.utils.pagination import PageParams
from app.utils.response import APIResponse

router = APIRouter(prefix="/users", tags=["Users"])
service = UserService()


@router.get("/me")
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> APIResponse:
    user = await service.get_me(current_user.id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.get("")
async def list_users(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
) -> APIResponse:
    params = PageParams(page=page, page_size=page_size)
    result = await service.get_user_list(params, username, email, status)
    items = [UserResponse.model_validate(u).model_dump() for u in result.items]
    data = result.model_dump()
    data["items"] = items
    return APIResponse(data=data)


@router.get("/{user_id}")
async def get_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    user = await service.get_user(user_id)
    return APIResponse(data=UserResponse.model_validate(user))


@router.post("")
async def create_user(
    body: UserCreate,
    current_user: Annotated[User, Depends(require_role("admin"))],
) -> APIResponse:
    user = await service.create_user(body)
    return APIResponse(data=UserResponse.model_validate(user))


@router.put("/{user_id}")
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    user = await service.update_user(user_id, body)
    return APIResponse(data=UserResponse.model_validate(user))


@router.delete("/{user_id}")
async def delete_user(
    user_id: UUID,
    current_user: Annotated[User, Depends(require_role("admin"))],
) -> APIResponse:
    await service.delete_user(user_id)
    return APIResponse(message="User deleted")
