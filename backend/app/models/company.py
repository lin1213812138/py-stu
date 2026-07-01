import time
from typing import Optional
from uuid import uuid4

from beanie import Document
from pydantic import Field


class Company(Document):
    id: str = Field(default_factory=lambda: str(uuid4()), alias="_id")
    name: str
    short_name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    status: int = 1
    sort: int = 0
    created_at: float = Field(default_factory=lambda: time.time() * 1000)
    updated_at: float = Field(default_factory=lambda: time.time() * 1000)

    class Settings:
        name = "companies"
        indexes = ["name"]

    model_config = {"populate_by_name": True}
