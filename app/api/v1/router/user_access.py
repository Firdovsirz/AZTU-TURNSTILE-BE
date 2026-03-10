# app/api/routes/user_access.py
from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.schema.user_access import (
    UserAccessCreate,
    UserAccessUpdate,
    UserAccessResponse,
    UserAccessStatus
)
from app.services.user_access import UserAccessService
from app.core.security import get_current_user
from app.models.auth import Auth

router = APIRouter()


@router.post("/create", response_model=UserAccessResponse, status_code=status.HTTP_201_CREATED)
async def create_access_record(
    access_data: UserAccessCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Create a new user access record"""
    return await UserAccessService.create(db, access_data)


@router.get("/details/", response_model=List[UserAccessResponse])
async def get_access_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    employee_id: Optional[str] = Query(None),
    card_no: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    device_name: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get all user access records with pagination and filters"""
    return await UserAccessService.get_all(
        db, skip, limit, employee_id, card_no, direction, start_date, end_date, device_name
    )

@router.get("/status", response_model=List[UserAccessStatus])
async def get_access_status(
    accessed: bool = Query(True, description="True for users who accessed, False for users who didn't"),
    target_date: Optional[date] = Query(None, description="Single date to check (defaults to today)"),
    start_date: Optional[date] = Query(None, description="Start of date range"),
    end_date: Optional[date] = Query(None, description="End of date range"),
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """
    Get users based on access status.
    - accessed=true: Returns users who have access records
    - accessed=false: Returns users who don't have access records
    - Default date is today if no date parameters provided
    - Can query single date or date range
    """
    return await UserAccessService.get_access_status(
        db, accessed, target_date, start_date, end_date
    )


@router.get("/employee/{employee_id}", response_model=List[UserAccessResponse])
async def get_employee_access(
    employee_id: str,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get all access records for a specific employee"""
    return await UserAccessService.get_by_employee(db, employee_id, start_date, end_date)


@router.get("/count")
async def get_access_count(
    employee_id: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    direction: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get total count of access records with filters"""
    count = await UserAccessService.get_count(db, employee_id, start_date, end_date, direction)
    return {"count": count}


@router.get("/details/{access_id}", response_model=UserAccessResponse)
async def get_access_record(
    access_id: str,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get a user access record by ID"""
    return await UserAccessService.get_by_id(db, access_id)


@router.put("/edit/details/{access_id}", response_model=UserAccessResponse)
async def update_access_record(
    access_id: str,
    access_data: UserAccessUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Update a user access record"""
    return await UserAccessService.update(db, access_id, access_data)


@router.delete("/{access_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_access_record(
    access_id: str,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Delete a user access record"""
    await UserAccessService.delete(db, access_id)
