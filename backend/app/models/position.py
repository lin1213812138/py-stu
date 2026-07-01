import time
from uuid import uuid4

from beanie import Document
from pydantic import Field


class Position(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    name: str
    department_id: str
    status: int = 1
    sort: int = 0
    created_at: int = Field(default_factory=lambda: int(time.time()))
    updated_at: int = Field(default_factory=lambda: int(time.time()))

    class Settings:
        name = "positions"
        indexes = ["department_id"]

    model_config = {"populate_by_name": True}
