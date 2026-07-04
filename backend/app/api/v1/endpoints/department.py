from typing import Annotated
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.department import DepartmentCreate, DepartmentResponse, DepartmentUpdate
from app.services.department_service import DepartmentService
from app.utils.response import APIResponse

router = APIRouter(prefix="/departments", tags=["Department"])
service = DepartmentService()


@router.get("")
async def list_departments(
    current_user: Annotated[User, Depends(get_current_user)],
    company_id: str = Query(...),
) -> APIResponse:
    tree = await service.get_tree(company_id)
    return APIResponse(data=tree)


@router.post("")
async def create_department(
    body: DepartmentCreate,
    current_user: Annotated[User, Depends(require_permission("system:dept:create"))],
) -> APIResponse:
    dept = await service.create(body)
    return APIResponse(data=DepartmentResponse.model_validate(dept))


@router.get("/{dept_id}")
async def get_department(
    dept_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    dept = await service.get_by_id(dept_id)
    return APIResponse(data=DepartmentResponse.model_validate(dept))


@router.put("/{dept_id}")
async def update_department(
    dept_id: str,
    body: DepartmentUpdate,
    current_user: Annotated[User, Depends(require_permission("system:dept:update"))],
) -> APIResponse:
    dept = await service.update(dept_id, body)
    return APIResponse(data=DepartmentResponse.model_validate(dept))


@router.delete("/{dept_id}")
async def delete_department(
    dept_id: str,
    current_user: Annotated[User, Depends(require_permission("system:dept:delete"))],
) -> APIResponse:
    await service.delete(dept_id)
    return APIResponse(message="删除成功")
