from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from beanie import Document
from pydantic import Field


class Department(Document):
    id: UUID = Field(default_factory=uuid4, alias="_id")
    name: str
    company_id: UUID
    parent_id: Optional[UUID] = None
    leader_id: Optional[UUID] = None
    status: int = 1
    sort: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "departments"
        indexes = ["company_id"]

    model_config = {"populate_by_name": True}
