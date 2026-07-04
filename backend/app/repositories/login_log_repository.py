from typing import Optional

from app.models.login_log import LoginLog
from app.utils.pagination import PageParams, PageResult


class LoginLogRepository:

    @staticmethod
    async def create(log: LoginLog) -> LoginLog:
        return await log.insert()

    @staticmethod
    async def get_list(
        params: PageParams,
        username: Optional[str] = None,
        status: Optional[int] = None,
    ) -> PageResult:
        query = {}
        if username:
            query["username"] = {"$regex": username, "$options": "i"}
        if status is not None:
            query["status"] = status

        total = await LoginLog.find(query).count()
        items = (
            await LoginLog.find(query)
            .sort(-LoginLog.login_time)
            .skip((params.page - 1) * params.page_size)
            .limit(params.page_size)
            .to_list()
        )

        return PageResult(
            items=items,
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=(total + params.page_size - 1) // params.page_size,
        )
