from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AttendCreate(BaseModel):
    username: str
    position: str
    password: str

class AttendOut(BaseModel):
    id: int
    username: str
    attend_time: datetime
    position: str
    logout_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    attend_id: Optional[int] = None

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    attendance: AttendOut
