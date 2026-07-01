from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str = "user"


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: Optional[str] = None
    status: Optional[int] = None


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    status: int
    last_login_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
