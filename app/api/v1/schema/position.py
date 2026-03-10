# app/schemas/position.py
from pydantic import BaseModel, Field
from datetime import datetime


class PositionBase(BaseModel):
    position_id: int = Field(..., gt=0)
    position: str = Field(..., max_length=255)


class PositionCreate(PositionBase):
    pass


class PositionUpdate(BaseModel):
    position_id: int | None = Field(None, gt=0)
    position: str | None = Field(None, max_length=255)


class PositionResponse(PositionBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True