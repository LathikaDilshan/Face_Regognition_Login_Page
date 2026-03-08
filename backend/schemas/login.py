from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AttendCreate(BaseModel):
    username: str
    position: str

class AttendOut(BaseModel):
    id: int
    username: str
    attend_date: datetime
    attend_time: datetime
    position: str

    class Config:
        from_attributes = True
