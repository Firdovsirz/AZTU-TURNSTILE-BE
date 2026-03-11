# app/schemas/user.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    card_no: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    surname: str = Field(..., max_length=255)
    gender: int = Field(..., ge=0, le=2)
    identification: str = Field(..., max_length=255)
    group_number: Optional[str] = Field(None, max_length=255)
    group: Optional[int] = None
    position: Optional[int] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    card_no: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    surname: Optional[str] = Field(None, max_length=255)
    gender: Optional[int] = Field(None, ge=0, le=2)
    identification: Optional[str] = Field(None, max_length=255)
    group_number: Optional[str] = Field(None, max_length=255)
    group: Optional[int] = None
    position: Optional[int] = None


class UserResponse(UserBase):
    id: int
    created_at: datetime
    enter: Optional[str] = None
    exit: Optional[str] = None

    class Config:
        from_attributes = True