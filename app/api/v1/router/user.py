# app/api/routes/user.py
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.schema.user import UserCreate, UserUpdate, UserResponse
from app.services.user import UserService
from app.core.security import get_current_user
from app.models.auth import Auth
from app.services.user import *

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Create a new user"""
    return await UserService.create(db, user_data)


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    group: Optional[int] = Query(None),
    position: Optional[int] = Query(None),
    gender: Optional[int] = Query(None, ge=0, le=2),
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD) to include enter/exit access data"),
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get all users with pagination and optional filters"""
    filter_date = None
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    return await UserService.get_all(db, skip, limit, group, position, gender, filter_date)


@router.get("/search", response_model=List[UserResponse])
async def search_users(
    q: str = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Search users by name, surname, card_no, or identification"""
    return await UserService.search(db, q, skip, limit)


@router.get("/count")
async def get_users_count(
    group: Optional[int] = Query(None),
    position: Optional[int] = Query(None),
    gender: Optional[int] = Query(None, ge=0, le=2),
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get total count of users with optional filters"""
    count = await UserService.get_count(db, group, position, gender)
    return {"count": count}


@router.get("/details/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get a user by ID"""
    return await UserService.get_by_id(db, user_id)


@router.get("/by-identification/{identification}", response_model=UserResponse)
async def get_user_by_identification(
    identification: str,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get a user by identification"""
    return await UserService.get_by_identification(db, identification)


@router.get("/by-card/{card_no}", response_model=UserResponse)
async def get_user_by_card_no(
    card_no: str,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get a user by card number"""
    return await UserService.get_by_card_no(db, card_no)


@router.put("/details/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Update a user"""
    return await UserService.update(db, user_id, user_data)


@router.delete("/{user_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Delete a user"""
    await UserService.delete(db, user_id)

@router.get("/staff/all")
async def get_staff_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: Optional[str] = Query(None, description="Search by name, surname, identification, or card no"),
    gender: Optional[int] = Query(None, ge=0, le=2),
    position: Optional[int] = Query(None, ge=0),
    group: Optional[int] = Query(None, ge=0),
    date: Optional[str] = Query(None, description="Filter by specific date in YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all staff with optional pagination and filtering:
    - skip, limit for pagination
    - single `search` parameter for name, surname, identification, or card no
    - filter by gender, position, group
    - optional `date` to get first entrance and last exit for a specific date
    """
    # Convert date string to date object if provided
    filter_date: Optional[dt_date] = None
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return {
                "status_code": 400,
                "error": "Invalid date format. Use YYYY-MM-DD."
            }

    return await get_staff(
        skip=skip,
        limit=limit,
        search=search,
        gender=gender,
        position=position,
        group=group,
        date=filter_date,
        db=db
    )

@router.get("/student/all")
async def get_students_endpoint(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: Optional[str] = Query(None, description="Search by name, surname, identification, or card no"),
    gender: Optional[int] = Query(None, ge=0, le=2),
    position: Optional[int] = Query(None, ge=0),
    group_number: Optional[str] = Query(None),
    date: Optional[str] = Query(None, description="Filter by specific date in YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all students with optional pagination and filtering:
    - skip, limit for pagination
    - single `search` parameter for name, surname, identification, or card no
    - filter by gender, position, group_number
    - optional `date` to get first entrance and last exit for a specific date
    """
    # Convert date string to date object if provided
    filter_date: Optional[dt_date] = None
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return {
                "status_code": 400,
                "error": "Invalid date format. Use YYYY-MM-DD."
            }

    return await get_students(
        skip=skip,
        limit=limit,
        search=search,
        gender=gender,
        position=position,
        group_number=group_number,
        date=filter_date,
        db=db
    )