import time
from typing import Optional
from uuid import uuid4

from beanie import Document, Indexed
from pydantic import Field


class User(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    username: str = Indexed(unique=True)
    email: str = Indexed(unique=True)
    password_hash: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    company_id: Optional[str] = None
    department_id: Optional[str] = None
    position_id: Optional[str] = None
    role_ids: list[str] = []
    role: str = "user"
    status: int = 1
    last_login_time: Optional[float] = None
    created_at: float = Field(default_factory=lambda: time.time() * 1000)
    updated_at: float = Field(default_factory=lambda: time.time() * 1000)

    class Settings:
        name = "users"

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "alice",
                "email": "alice@example.com",
            }
        },
        "populate_by_name": True,
    }
