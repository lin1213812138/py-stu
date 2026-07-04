from typing import Optional
from pydantic import BaseModel

from app.models.role import RolePermission


class RoleCreate(BaseModel):
    name: str
    code: str
    permissions: list[RolePermission] = []
    remark: Optional[str] = None


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    permissions: Optional[list[RolePermission]] = None
    status: Optional[int] = None
    remark: Optional[str] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    code: str
    permissions: list[RolePermission] = []
    status: int
    remark: Optional[str] = None
    created_at: float
    updated_at: float

    model_config = {"from_attributes": True}
