from typing import Optional

from pydantic import BaseModel


class LoginLogResponse(BaseModel):
    id: str
    user_id: str
    username: str
    ip: Optional[str] = None
    user_agent: Optional[str] = None
    status: int
    message: str = ""
    login_time: float
    created_at: float

    model_config = {"from_attributes": True}
