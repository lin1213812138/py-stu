from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document, Indexed
from pydantic import Field


class User(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    username: str = Indexed(unique=True)
    email: str = Indexed(unique=True)
    password_hash: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str = "user"
    status: int = 1
    last_login_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

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
