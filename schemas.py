from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class AdminCreate(BaseModel):
    username: str
    password: str

class AdminResponse(BaseModel):
    id: int
    username: str
    class Config:
        orm_mode = True

class StaffBase(BaseModel):
    name: str
    age: int
    gender: str
    department_or_role: str

class StaffCreate(StaffBase):
    pass

class StaffResponse(StaffBase):
    id: int
    image_path: str
    created_at: datetime
    class Config:
        orm_mode = True
