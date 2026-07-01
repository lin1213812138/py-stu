from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str
    company_id: UUID
    parent_id: Optional[UUID] = None
    leader_id: Optional[UUID] = None
    sort: int = 0


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[UUID] = None
    leader_id: Optional[UUID] = None
    status: Optional[int] = None
    sort: Optional[int] = None


class DepartmentResponse(BaseModel):
    id: UUID
    name: str
    company_id: UUID
    parent_id: Optional[UUID] = None
    leader_id: Optional[UUID] = None
    status: int
    sort: int
    children: list["DepartmentResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
