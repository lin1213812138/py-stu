from typing import Optional
from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    name: str
    company_id: str
    parent_id: Optional[str] = None
    leader_id: Optional[str] = None
    sort: int = 0


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[str] = None
    leader_id: Optional[str] = None
    status: Optional[int] = None
    sort: Optional[int] = None


class DepartmentResponse(BaseModel):
    id: str
    name: str
    company_id: str
    parent_id: Optional[str] = None
    leader_id: Optional[str] = None
    status: int
    sort: int
    children: list["DepartmentResponse"] = []
    created_at: int
    updated_at: int

    model_config = {"from_attributes": True}
