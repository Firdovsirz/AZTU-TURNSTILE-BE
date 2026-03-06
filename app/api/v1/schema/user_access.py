# app/schemas/user_access.py
from pydantic import BaseModel, Field
from typing import Optional


class UserAccessBase(BaseModel):
    employee_id: str = Field(..., min_length=1, max_length=256)
    access_date_time: str = Field(..., min_length=1, max_length=256)
    access_date: str = Field(..., min_length=1, max_length=256)
    access_time: str = Field(..., min_length=1, max_length=256)
    device_name: str = Field(..., min_length=1, max_length=256)
    device_serial_number: str = Field(..., min_length=1, max_length=256)
    person_name: str = Field(..., min_length=1, max_length=256)
    card_no: str = Field(..., min_length=1, max_length=256)
    direction: str = Field(..., min_length=1, max_length=256)


class UserAccessCreate(UserAccessBase):
    id: str = Field(..., min_length=1, max_length=256)


class UserAccessUpdate(BaseModel):
    employee_id: Optional[str] = Field(None, min_length=1, max_length=256)
    access_date_time: Optional[str] = Field(None, min_length=1, max_length=256)
    access_date: Optional[str] = Field(None, min_length=1, max_length=256)
    access_time: Optional[str] = Field(None, min_length=1, max_length=256)
    device_name: Optional[str] = Field(None, min_length=1, max_length=256)
    device_serial_number: Optional[str] = Field(None, min_length=1, max_length=256)
    person_name: Optional[str] = Field(None, min_length=1, max_length=256)
    card_no: Optional[str] = Field(None, min_length=1, max_length=256)
    direction: Optional[str] = Field(None, min_length=1, max_length=256)


class UserAccessResponse(UserAccessBase):
    id: Optional[str] = None

    class Config:
        from_attributes = True


class UserAccessStatus(BaseModel):
    employee_id: str
    person_name: str
    card_no: str
    has_access: bool
    last_access: Optional[str] = None
    direction: Optional[str] = None
