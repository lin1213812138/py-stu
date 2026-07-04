from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    def __init__(self, code: int = 10001, message: str = "业务异常"):
        self.code = code
        self.message = message


class UserExistsError(AppException):
    def __init__(self):
        super().__init__(code=10002, message="用户已存在")


class UserNotFoundError(AppException):
    def __init__(self):
        super().__init__(code=10003, message="用户不存在")


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(code=10004, message="用户名或密码错误")


class TokenError(AppException):
    def __init__(self):
        super().__init__(code=10005, message="Token 已过期或无效")


class PermissionDeniedError(AppException):
    def __init__(self):
        super().__init__(code=10006, message="权限不足")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=400,
            content={"code": exc.code, "message": exc.message, "data": None},
        )
    logger.opt(exception=True).error(f"Unhandled: {exc}")
    return JSONResponse(
        status_code=500,
        content={"code": 10001, "message": "服务器内部错误", "data": None},
    )
