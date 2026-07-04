import time
from typing import Optional
from uuid import uuid4

from beanie import Document
from pydantic import Field


class LoginLog(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    user_id: str
    username: str
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    status: int = 1  # 1=成功, 0=失败
    message: str = ""
    login_time: float = Field(default_factory=lambda: time.time() * 1000)
    created_at: float = Field(default_factory=lambda: time.time() * 1000)

    class Settings:
        name = "login_logs"

    model_config = {
        "populate_by_name": True,
    }
