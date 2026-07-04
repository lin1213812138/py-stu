from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_current_user, require_permission
from app.models.user import User
from app.schemas.login_log import LoginLogResponse
from app.services.login_log_service import LoginLogService
from app.utils.pagination import PageParams
from app.utils.response import APIResponse

router = APIRouter(prefix="/login-logs", tags=["登录日志"])
service = LoginLogService()


@router.get("")
async def get_login_logs(
    current_user: Annotated[User, Depends(require_permission("system:user:list"))],
    params: Annotated[PageParams, Depends()],
    username: Optional[str] = Query(None),
    status: Optional[int] = Query(None),
) -> APIResponse:
    result = await service.get_list(params, username, status)
    return APIResponse(data=result.model_dump())
