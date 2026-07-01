import time
from typing import Optional
from uuid import uuid4

from beanie import Document, Indexed
from pydantic import BaseModel, Field


class RolePermission(BaseModel):
    menu_id: str
    button_keys: list[str] = []


class Role(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    name: str
    code: str = Indexed(unique=True)
    permissions: list[RolePermission] = []
    status: int = 1
    remark: Optional[str] = None
    created_at: float = Field(default_factory=lambda: time.time() * 1000)
    updated_at: float = Field(default_factory=lambda: time.time() * 1000)

    class Settings:
        name = "roles"

    model_config = {"populate_by_name": True}
