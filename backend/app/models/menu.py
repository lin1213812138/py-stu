from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class Menu(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    parent_id: Optional[UUID] = None
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
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "menus"
        indexes = ["parent_id"]

    model_config = {"populate_by_name": True}
