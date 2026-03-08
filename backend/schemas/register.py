from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    position: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    position: str

    class Config:
        from_attributes = True
