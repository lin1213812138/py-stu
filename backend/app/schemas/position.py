from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PositionCreate(BaseModel):
    name: str
    department_id: UUID
    sort: int = 0


class PositionUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[int] = None
    sort: Optional[int] = None


class PositionResponse(BaseModel):
    id: UUID
    name: str
    department_id: UUID
    status: int
    sort: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
