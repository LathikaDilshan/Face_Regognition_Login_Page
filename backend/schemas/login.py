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

    class Config:
        from_attributes = True
