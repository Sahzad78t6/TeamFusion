from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the user")


class UserSignup(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, description="User login password")


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: Optional[datetime | str] = None
    updated_at: Optional[datetime | str] = None

    class Config:
        from_attributes = True
