from typing import Optional

from app.models.login_log import LoginLog
from app.repositories.login_log_repository import LoginLogRepository
from app.schemas.login_log import LoginLogResponse
from app.utils.pagination import PageParams, PageResult


class LoginLogService:

    def __init__(self):
        self.repo = LoginLogRepository()

    async def record_login(
        self,
        user_id: str,
        username: str,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        status: int = 1,
        fail_reason: Optional[str] = None,
    ) -> None:
        log = LoginLog(
            user_id=user_id,
            username=username,
            ip=ip,
            user_agent=user_agent,
            status=status,
            fail_reason=fail_reason,
        )
        await self.repo.create(log)

    async def get_list(
        self,
        params: PageParams,
        username: Optional[str] = None,
        status: Optional[int] = None,
    ) -> PageResult:
        result = await self.repo.get_list(params, username, status)
        result.items = [LoginLogResponse.model_validate(item) for item in result.items]
        return result
