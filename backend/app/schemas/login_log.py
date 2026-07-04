from typing import Optional

from pydantic import BaseModel


class LoginLogResponse(BaseModel):
    id: str
    user_id: str
    username: str
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    status: int
    fail_reason: Optional[str] = None
    login_time: int
    created_at: int

    model_config = {"from_attributes": True}
