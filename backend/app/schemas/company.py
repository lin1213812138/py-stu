from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CompanyCreate(BaseModel):
    name: str
    short_name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    sort: int = 0


class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    short_name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    status: Optional[int] = None
    sort: Optional[int] = None


class CompanyResponse(BaseModel):
    id: str
    name: str
    short_name: Optional[str] = None
    address: Optional[str] = None
    contact: Optional[str] = None
    status: int
    sort: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
