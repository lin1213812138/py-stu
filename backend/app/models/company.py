from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class Company(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    name: str
    short_name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    status: int = 1
    sort: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "companies"
        indexes = ["name"]

    model_config = {"populate_by_name": True}
