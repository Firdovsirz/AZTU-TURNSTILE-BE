# app/services/user_access.py
from typing import List, Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func, distinct, cast, String
from fastapi import HTTPException, status
from app.models.user_access import UserAccess
from app.models.user import User
from app.api.v1.schema.user_access import UserAccessCreate, UserAccessUpdate, UserAccessStatus


class UserAccessService:
    @staticmethod
    async def create(db: AsyncSession, access_data: UserAccessCreate) -> UserAccess:
        """Create a new user access record"""
        new_access = UserAccess(**access_data.model_dump())
        db.add(new_access)
        await db.commit()
        await db.refresh(new_access)
        return new_access

    @staticmethod
    async def get_by_id(db: AsyncSession, access_id: str) -> UserAccess:
        """Get a user access record by ID"""
        result = await db.execute(
            select(UserAccess).filter(UserAccess.id == access_id)
        )
        access = result.scalar_one_or_none()

        if not access:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Access record with id {access_id} not found"
            )
        return access

    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        employee_id: Optional[str] = None,
        card_no: Optional[str] = None,
        direction: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        device_name: Optional[str] = None
    ) -> List[UserAccess]:
        """Get all user access records with pagination and filters"""
        query = select(UserAccess)

        if employee_id is not None:
            query = query.filter(UserAccess.employee_id == employee_id)
        if card_no:
            query = query.filter(UserAccess.card_no == card_no)
        if direction is not None:
            query = query.filter(UserAccess.direction == direction)
        if device_name:
            query = query.filter(UserAccess.device_name.ilike(f"%{device_name}%"))
        if start_date and end_date:
            query = query.filter(
                and_(
                    UserAccess.access_date >= str(start_date),
                    UserAccess.access_date <= str(end_date)
                )
            )
        elif start_date:
            query = query.filter(UserAccess.access_date == str(start_date))

        query = query.order_by(UserAccess.access_date_time.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_access_status(
        db: AsyncSession,
        accessed: bool = True,
        target_date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[UserAccessStatus]:
        """
        Get users based on access status for a specific date or date range.

        Args:
            accessed: True to get users who accessed, False to get users who didn't
            target_date: Single date to check (defaults to today)
            start_date: Start of date range
            end_date: End of date range

        Returns:
            List of UserAccessStatus with employee info and access status
        """
        if start_date and end_date:
            date_start = str(start_date)
            date_end = str(end_date)
        elif target_date:
            date_start = str(target_date)
            date_end = str(target_date)
        else:
            today = str(date.today())
            date_start = today
            date_end = today

        if accessed:
            query = select(
                UserAccess.employee_id,
                UserAccess.person_name,
                UserAccess.card_no,
                func.max(UserAccess.access_date_time).label('last_access'),
                UserAccess.direction
            ).filter(
                and_(
                    UserAccess.access_date >= date_start,
                    UserAccess.access_date <= date_end
                )
            ).group_by(
                UserAccess.employee_id,
                UserAccess.person_name,
                UserAccess.card_no,
                UserAccess.direction
            ).order_by(
                func.max(UserAccess.access_date_time).desc()
            )

            result = await db.execute(query)
            rows = result.all()

            return [
                UserAccessStatus(
                    employee_id=row.employee_id,
                    person_name=row.person_name,
                    card_no=row.card_no,
                    has_access=True,
                    last_access=row.last_access,
                    direction=row.direction
                )
                for row in rows
            ]
        else:
            # Get all employee_ids (strings) who accessed during the period
            accessed_ids_query = select(distinct(UserAccess.employee_id)).filter(
                and_(
                    UserAccess.access_date >= date_start,
                    UserAccess.access_date <= date_end
                )
            )
            accessed_result = await db.execute(accessed_ids_query)
            accessed_ids = [row[0] for row in accessed_result.all()]

            # Cast User.id (Integer) to String to compare against VARCHAR employee_ids
            if accessed_ids:
                query = select(User).filter(cast(User.id, String).not_in(accessed_ids))
            else:
                query = select(User)

            result = await db.execute(query)
            users = result.scalars().all()

            return [
                UserAccessStatus(
                    employee_id=str(user.id),
                    person_name=f"{user.name} {user.surname}",
                    card_no=user.card_no,
                    has_access=False,
                    last_access=None,
                    direction=None
                )
                for user in users
            ]

    @staticmethod
    async def get_by_employee(
        db: AsyncSession,
        employee_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[UserAccess]:
        """Get all access records for a specific employee"""
        query = select(UserAccess).filter(UserAccess.employee_id == employee_id)

        if start_date and end_date:
            query = query.filter(
                and_(
                    UserAccess.access_date >= str(start_date),
                    UserAccess.access_date <= str(end_date)
                )
            )
        elif start_date:
            query = query.filter(UserAccess.access_date == str(start_date))

        query = query.order_by(UserAccess.access_date_time.desc())
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def update(
        db: AsyncSession,
        access_id: str,
        access_data: UserAccessUpdate
    ) -> UserAccess:
        """Update a user access record"""
        result = await db.execute(
            select(UserAccess).filter(UserAccess.id == access_id)
        )
        access = result.scalar_one_or_none()

        if not access:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Access record with id {access_id} not found"
            )

        for field, value in access_data.model_dump(exclude_unset=True).items():
            setattr(access, field, value)

        await db.commit()
        await db.refresh(access)
        return access

    @staticmethod
    async def delete(db: AsyncSession, access_id: str) -> None:
        """Delete a user access record"""
        result = await db.execute(
            select(UserAccess).filter(UserAccess.id == access_id)
        )
        access = result.scalar_one_or_none()

        if not access:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Access record with id {access_id} not found"
            )

        await db.delete(access)
        await db.commit()

    @staticmethod
    async def get_count(
        db: AsyncSession,
        employee_id: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        direction: Optional[str] = None
    ) -> int:
        """Get total count of access records with filters"""
        query = select(func.count(UserAccess.id))

        if employee_id is not None:
            query = query.filter(UserAccess.employee_id == employee_id)
        if direction is not None:
            query = query.filter(UserAccess.direction == direction)
        if start_date and end_date:
            query = query.filter(
                and_(
                    UserAccess.access_date >= str(start_date),
                    UserAccess.access_date <= str(end_date)
                )
            )
        elif start_date:
            query = query.filter(UserAccess.access_date == str(start_date))

        result = await db.execute(query)
        return result.scalar()
