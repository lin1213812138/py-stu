from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    nickname: str | None = None
    avatar: str | None = None
    role: str = "user"
    company_id: str | None = None
    department_id: Optional[str] = None
    position_id: Optional[str] = None
    role_ids: list[str] = []


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = None
    status: Optional[int] = None
    company_id: Optional[str] = None
    department_id: Optional[str] = None
    position_id: Optional[str] = None
    role_ids: Optional[list[str]] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    status: int
    last_login_time: Optional[float] = None
    company_id: Optional[str] = None
    department_id: Optional[str] = None
    position_id: Optional[str] = None
    role_ids: list[str] = []
    created_at: float
    updated_at: float

    model_config = {"from_attributes": True}
