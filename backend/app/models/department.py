import time
from typing import Optional
from uuid import uuid4

from beanie import Document
from pydantic import Field


class Department(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    name: str
    company_id: str
    parent_id: Optional[str] = None
    leader_id: Optional[str] = None
    status: int = 1
    sort: int = 0
    created_at: int = Field(default_factory=lambda: int(time.time() * 1000))
    updated_at: int = Field(default_factory=lambda: int(time.time() * 1000))

    class Settings:
        name = "departments"
        indexes = ["company_id"]

    model_config = {"populate_by_name": True}
