from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MenuCreate(BaseModel):
    parent_id: Optional[str] = None
    type: str
    name: str
    permission_key: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    sort: int = 0
    visible: int = 1
    is_frame: int = 0
    is_cache: int = 0
    is_affix: int = 0
    query: Optional[str] = None
    remark: Optional[str] = None


class MenuUpdate(BaseModel):
    parent_id: Optional[str] = None
    type: Optional[str] = None
    name: Optional[str] = None
    permission_key: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    sort: Optional[int] = None
    visible: Optional[int] = None
    is_frame: Optional[int] = None
    is_cache: Optional[int] = None
    is_affix: Optional[int] = None
    query: Optional[str] = None
    remark: Optional[str] = None
    status: Optional[int] = None


class MenuResponse(BaseModel):
    id: str
    parent_id: Optional[str] = None
    type: str
    name: str
    permission_key: Optional[str] = None
    path: Optional[str] = None
    component: Optional[str] = None
    icon: Optional[str] = None
    sort: int
    visible: int
    is_frame: int
    is_cache: int
    is_affix: int
    query: Optional[str] = None
    remark: Optional[str] = None
    status: int
    children: list["MenuResponse"] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
