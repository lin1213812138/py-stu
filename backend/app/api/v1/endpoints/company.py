from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.company import CompanyCreate, CompanyResponse, CompanyUpdate
from app.services.company_service import CompanyService
from app.utils.pagination import PageParams
from app.utils.response import APIResponse

router = APIRouter(prefix="/companies", tags=["Company"])
service = CompanyService()


@router.get("")
async def list_companies(
    current_user: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    name: Optional[str] = Query(None),
) -> APIResponse:
    params = PageParams(page=page, page_size=page_size)
    result = await service.get_list(params, name)
    items = [CompanyResponse.model_validate(u).model_dump() for u in result.items]
    data = result.model_dump()
    data["items"] = items
    return APIResponse(data=data)


@router.get("/all")
async def all_companies(current_user: Annotated[User, Depends(get_current_user)]) -> APIResponse:
    items = await service.get_all()
    return APIResponse(data=[CompanyResponse.model_validate(u).model_dump() for u in items])


@router.post("")
async def create_company(
    body: CompanyCreate,
    current_user: Annotated[User, Depends(require_permission("system:company:create"))],
) -> APIResponse:
    company = await service.create(body)
    return APIResponse(data=CompanyResponse.model_validate(company))


@router.get("/{company_id}")
async def get_company(
    company_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
) -> APIResponse:
    company = await service.get_by_id(company_id)
    return APIResponse(data=CompanyResponse.model_validate(company))


@router.put("/{company_id}")
async def update_company(
    company_id: str,
    body: CompanyUpdate,
    current_user: Annotated[User, Depends(require_permission("system:company:update"))],
) -> APIResponse:
    company = await service.update(company_id, body)
    return APIResponse(data=CompanyResponse.model_validate(company))


@router.delete("/{company_id}")
async def delete_company(
    company_id: str,
    current_user: Annotated[User, Depends(require_permission("system:company:delete"))],
) -> APIResponse:
    await service.delete(company_id)
    return APIResponse(message="删除成功")
