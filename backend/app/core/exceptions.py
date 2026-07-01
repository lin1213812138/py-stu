from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger


class AppException(Exception):
    def __init__(self, code: int = 10001, message: str = "Business error"):
        self.code = code
        self.message = message


class UserExistsError(AppException):
    def __init__(self):
        super().__init__(code=10002, message="User already exists")


class UserNotFoundError(AppException):
    def __init__(self):
        super().__init__(code=10003, message="User not found")


class InvalidCredentialsError(AppException):
    def __init__(self):
        super().__init__(code=10004, message="Invalid username or password")


class TokenError(AppException):
    def __init__(self):
        super().__init__(code=10005, message="Token expired or invalid")


class PermissionDeniedError(AppException):
    def __init__(self):
        super().__init__(code=10006, message="Insufficient permissions")


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=400,
            content={"code": exc.code, "message": exc.message, "data": None},
        )
    logger.opt(exception=True).error(f"Unhandled: {exc}")
    return JSONResponse(
        status_code=500,
        content={"code": 10001, "message": "Internal server error", "data": None},
    )
