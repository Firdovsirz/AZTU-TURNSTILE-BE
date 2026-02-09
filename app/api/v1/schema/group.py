# app/schemas/group.py
from pydantic import BaseModel, Field
from datetime import datetime


class GroupBase(BaseModel):
    group_id: int = Field(..., gt=0)
    group: str = Field(..., min_length=1, max_length=255)


class GroupCreate(GroupBase):
    pass


class GroupUpdate(BaseModel):
    group_id: int | None = Field(None, gt=0)
    group: str | None = Field(None, min_length=1, max_length=255)


class GroupResponse(GroupBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True