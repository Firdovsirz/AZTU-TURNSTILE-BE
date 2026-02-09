# app/schemas/user_access.py
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, date, time
from typing import Optional


class UserAccessBase(BaseModel):
    employee_id: int = Field(..., gt=0)
    access_date_time: datetime
    access_date: date
    access_time: time
    device_name: str = Field(..., min_length=1, max_length=255)
    device_serial_number: str = Field(..., min_length=1, max_length=255)
    person_name: str = Field(..., min_length=1, max_length=255)
    card_no: str = Field(..., min_length=1, max_length=255)
    direction: int = Field(..., ge=1, le=2)
    
    @field_validator('access_date_time', mode='before')
    @classmethod
    def remove_timezone_from_datetime(cls, v):
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v
    
    @field_validator('access_time', mode='before')
    @classmethod
    def remove_timezone_from_time(cls, v):
        if isinstance(v, time) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class UserAccessCreate(UserAccessBase):
    pass


class UserAccessUpdate(BaseModel):
    employee_id: Optional[int] = Field(None, gt=0)
    access_date_time: Optional[datetime] = None
    access_date: Optional[date] = None
    access_time: Optional[time] = None
    device_name: Optional[str] = Field(None, min_length=1, max_length=255)
    device_serial_number: Optional[str] = Field(None, min_length=1, max_length=255)
    person_name: Optional[str] = Field(None, min_length=1, max_length=255)
    card_no: Optional[str] = Field(None, min_length=1, max_length=255)
    direction: Optional[int] = Field(None, ge=1, le=2)
    
    @field_validator('access_date_time', mode='before')
    @classmethod
    def remove_timezone_from_datetime(cls, v):
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v
    
    @field_validator('access_time', mode='before')
    @classmethod
    def remove_timezone_from_time(cls, v):
        if isinstance(v, time) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class UserAccessResponse(UserAccessBase):
    id: int
    
    class Config:
        from_attributes = True


class UserAccessStatus(BaseModel):
    employee_id: int
    person_name: str
    card_no: str
    has_access: bool
    last_access: Optional[datetime] = None
    direction: Optional[int] = None