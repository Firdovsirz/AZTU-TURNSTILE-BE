# app/services/user.py
from typing import List, Optional
from fastapi import Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from fastapi import HTTPException, status
from app.models.user import User
from app.api.v1.schema.user import UserCreate, UserUpdate
from app.core.session import get_db
from app.models.groups import Group
from app.models.positions import Position
from fastapi.responses import JSONResponse
from fastapi import Query, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date as dt_date
from app.models.user_access import UserAccess
from app.core.database import get_db


class UserService:
    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if identification already exists
        result = await db.execute(
            select(User).filter(User.identification == user_data.identification)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with identification {user_data.identification} already exists"
            )
        
        new_user = User(**user_data.model_dump())
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User:
        """Get a user by ID"""
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return user
    
    @staticmethod
    async def get_by_identification(db: AsyncSession, identification: str) -> User:
        """Get a user by identification"""
        result = await db.execute(
            select(User).filter(User.identification == identification)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with identification {identification} not found"
            )
        return user
    
    @staticmethod
    async def get_by_card_no(db: AsyncSession, card_no: str) -> User:
        """Get a user by card number"""
        result = await db.execute(
            select(User).filter(User.card_no == card_no)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with card_no {card_no} not found"
            )
        return user
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        group: Optional[int] = None,
        position: Optional[int] = None,
        gender: Optional[int] = None
    ) -> List[User]:
        """Get all users with pagination and optional filters"""
        query = select(User)
        
        # Apply filters
        if group is not None:
            query = query.filter(User.group == group)
        if position is not None:
            query = query.filter(User.position == position)
        if gender is not None:
            query = query.filter(User.gender == gender)
        
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def search(
        db: AsyncSession,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by name, surname, card_no, or identification"""
        query = select(User).filter(
            or_(
                User.name.ilike(f"%{search_term}%"),
                User.surname.ilike(f"%{search_term}%"),
                User.card_no.ilike(f"%{search_term}%"),
                User.identification.ilike(f"%{search_term}%")
            )
        ).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update(
        db: AsyncSession,
        user_id: int,
        user_data: UserUpdate
    ) -> User:
        """Update a user"""
        # Get existing user
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        # Check if new identification conflicts with existing
        if user_data.identification and user_data.identification != user.identification:
            result = await db.execute(
                select(User).filter(User.identification == user_data.identification)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"User with identification {user_data.identification} already exists"
                )
        
        # Update fields
        update_data = user_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> None:
        """Delete a user"""
        result = await db.execute(
            select(User).filter(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        await db.delete(user)
        await db.commit()
    
    @staticmethod
    async def get_count(
        db: AsyncSession,
        group: Optional[int] = None,
        position: Optional[int] = None,
        gender: Optional[int] = None
    ) -> int:
        """Get total count of users with optional filters"""
        from sqlalchemy import func as sql_func
        
        query = select(sql_func.count(User.id))
        
        if group is not None:
            query = query.filter(User.group == group)
        if position is not None:
            query = query.filter(User.position == position)
        if gender is not None:
            query = query.filter(User.gender == gender)
        
        result = await db.execute(query)
        return result.scalar()

from fastapi import Query

async def get_staff(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: str | None = Query(None, description="Search by name, surname, identification, or card no"),
    gender: int | None = Query(None, ge=0, le=2),
    position: int | None = None,
    group: int | None = None,
    date: dt_date | None = None,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Default to today if no date provided
        filter_date = date or dt_date.today()

        # Base query
        query = select(User).where(User.group_number == None)

        # Apply search filter (single text input)
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.surname.ilike(f"%{search}%"),
                User.identification.ilike(f"%{search}%"),
                User.card_no.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Apply other filters
        if gender is not None:
            query = query.where(User.gender == gender)
        if position is not None:
            query = query.where(User.position == position)
        if group is not None:
            query = query.where(User.group == group)

        # Pagination
        query = query.offset(skip).limit(limit)

        staff_result = await db.execute(query)
        all_staff = staff_result.scalars().all()

        staff_arr = []

        for staff in all_staff:
            # Fetch first entrance (direction=1) and last exit (direction=2) from UserAccess
            access_query = await db.execute(
                select(UserAccess)
                .where(
                    UserAccess.card_no == staff.card_no,
                    UserAccess.access_date == filter_date
                )
                .order_by(UserAccess.access_time)
            )
            accesses = access_query.scalars().all()

            first_entrance = next((a for a in accesses if a.direction == 1), None)
            last_exit = next((a for a in reversed(accesses) if a.direction == 2), None)

            # Fetch group and position
            group_obj = None
            position_obj = None
            if staff.group is not None:
                group_query = await db.execute(
                    select(Group).where(Group.group_id == staff.group)
                )
                group_obj = group_query.scalar_one_or_none()
            if staff.position is not None:
                position_query = await db.execute(
                    select(Position).where(Position.position_id == staff.position)
                )
                position_obj = position_query.scalar_one_or_none()

            staff_obj = {
                "id": staff.id,
                "name": staff.name,
                "surname": staff.surname,
                "gender": staff.gender,
                "identification": staff.identification,
                "group": group_obj.group if group_obj else None,
                "position": position_obj.position if position_obj else None,
                "group_number": staff.group_number,
                "card_no": staff.card_no,
                "created_at": staff.created_at.isoformat(),
                "first_entrance": first_entrance.access_time.isoformat() if first_entrance else None,
                "last_exit": last_exit.access_time.isoformat() if last_exit else None,
                "req_date": filter_date.isoformat() if filter_date else None
            }

            staff_arr.append(staff_obj)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Staff fetched successfully.",
                "staffs": staff_arr,
                "skip": skip,
                "limit": limit,
                "total": len(staff_arr),
            }
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e),
            }
        )

async def get_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: str | None = Query(None, description="Search by name, surname, identification, or card no"),
    gender: int | None = Query(None, ge=0, le=2),
    position: int | None = None,
    group_number: int | None = None,
    date: dt_date | None = None,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Default to today if no date provided
        filter_date = date or dt_date.today()

        # Base query
        query = select(User).where(User.group_number != None)

        # Apply search filter (single text input)
        if search:
            search_filter = or_(
                User.name.ilike(f"%{search}%"),
                User.surname.ilike(f"%{search}%"),
                User.identification.ilike(f"%{search}%"),
                User.card_no.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Apply other filters
        if gender is not None:
            query = query.where(User.gender == gender)
        if position is not None:
            query = query.where(User.position == position)
        if group_number is not None:
            query = query.where(User.group_number == group_number)

        # Pagination
        query = query.offset(skip).limit(limit)

        staff_result = await db.execute(query)
        all_staff = staff_result.scalars().all()

        staff_arr = []

        for staff in all_staff:
            # Fetch first entrance (direction=1) and last exit (direction=2) from UserAccess
            access_query = await db.execute(
                select(UserAccess)
                .where(
                    UserAccess.card_no == staff.card_no,
                    UserAccess.access_date == filter_date
                )
                .order_by(UserAccess.access_time)
            )
            accesses = access_query.scalars().all()

            first_entrance = next((a for a in accesses if a.direction == 1), None)
            last_exit = next((a for a in reversed(accesses) if a.direction == 2), None)

            # Fetch group and position
            group_obj = None
            position_obj = None
            if staff.group is not None:
                group_query = await db.execute(
                    select(Group).where(Group.group_id == staff.group)
                )
                group_obj = group_query.scalar_one_or_none()
            if staff.position is not None:
                position_query = await db.execute(
                    select(Position).where(Position.position_id == staff.position)
                )
                position_obj = position_query.scalar_one_or_none()

            staff_obj = {
                "id": staff.id,
                "name": staff.name,
                "surname": staff.surname,
                "gender": staff.gender,
                "identification": staff.identification,
                "group": group_obj.group if group_obj else None,
                "position": position_obj.position if position_obj else None,
                "group_number": staff.group_number,
                "card_no": staff.card_no,
                "created_at": staff.created_at.isoformat(),
                "first_entrance": first_entrance.access_time.isoformat() if first_entrance else None,
                "last_exit": last_exit.access_time.isoformat() if last_exit else None,
                "req_date": filter_date.isoformat() if filter_date else None
            }

            staff_arr.append(staff_obj)

        return JSONResponse(
            content={
                "status_code": 200,
                "message": "Staff fetched successfully.",
                "students": staff_arr,
                "skip": skip,
                "limit": limit,
                "total": len(staff_arr),
            }
        )

    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e),
            }
        )