import time
from typing import Optional
from uuid import uuid4

from beanie import Document
from pydantic import Field


class Menu(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    parent_id: Optional[str] = None
    type: str
    name: str
    permission_key: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    sort: int = 0
    visible: int = 1
    is_frame: int = 0
    is_cache: int = 0
    is_affix: int = 0
    query: Optional[str] = None
    remark: Optional[str] = None
    status: int = 1
    created_at: float = Field(default_factory=lambda: time.time() * 1000)
    updated_at: float = Field(default_factory=lambda: time.time() * 1000)

    class Settings:
        name = "menus"
        indexes = ["parent_id"]

    model_config = {"populate_by_name": True}
