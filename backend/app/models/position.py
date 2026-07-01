from datetime import datetime
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class Position(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    name: str
    department_id: UUID
    status: int = 1
    sort: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "positions"
        indexes = ["department_id"]

    model_config = {"populate_by_name": True}
