from typing import Optional
from pydantic import BaseModel


class PositionCreate(BaseModel):
    name: str
    department_id: str
    sort: int = 0


class PositionUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[int] = None
    sort: Optional[int] = None


class PositionResponse(BaseModel):
    id: str
    name: str
    department_id: str
    status: int
    sort: int
    created_at: int
    updated_at: int

    model_config = {"from_attributes": True}
