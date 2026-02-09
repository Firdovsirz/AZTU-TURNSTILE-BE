# app/services/user_access.py
from typing import List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, distinct
from fastapi import HTTPException, status
from app.models.user_access import UserAccess
from app.models.user import User
from app.api.v1.schema.user_access import UserAccessCreate, UserAccessUpdate, UserAccessStatus


class UserAccessService:
    @staticmethod
    def _remove_timezone(dt):
        """Remove timezone info from datetime or time objects"""
        if dt is None:
            return None
        if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt
    
    @staticmethod
    async def create(db: AsyncSession, access_data: UserAccessCreate) -> UserAccess:
        """Create a new user access record"""
        # Convert to dict and remove timezone info
        data = access_data.model_dump()
        data['access_date_time'] = UserAccessService._remove_timezone(data['access_date_time'])
        data['access_time'] = UserAccessService._remove_timezone(data['access_time'])
        
        new_access = UserAccess(**data)
        db.add(new_access)
        await db.commit()
        await db.refresh(new_access)
        return new_access
    
    @staticmethod
    async def get_by_id(db: AsyncSession, access_id: int) -> UserAccess:
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
        employee_id: Optional[int] = None,
        card_no: Optional[str] = None,
        direction: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        device_name: Optional[str] = None
    ) -> List[UserAccess]:
        """Get all user access records with pagination and filters"""
        query = select(UserAccess)
        
        # Apply filters
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
                    UserAccess.access_date >= start_date,
                    UserAccess.access_date <= end_date
                )
            )
        elif start_date:
            query = query.filter(UserAccess.access_date == start_date)
        
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
        # Determine date range
        if start_date and end_date:
            date_start = start_date
            date_end = end_date
        elif target_date:
            date_start = target_date
            date_end = target_date
        else:
            # Default to today
            today = date.today()
            date_start = today
            date_end = today
        
        if accessed:
            # Get users who HAVE accessed
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
            # Get users who HAVE NOT accessed
            # First, get all employee_ids who accessed during the period
            accessed_ids_query = select(distinct(UserAccess.employee_id)).filter(
                and_(
                    UserAccess.access_date >= date_start,
                    UserAccess.access_date <= date_end
                )
            )
            accessed_result = await db.execute(accessed_ids_query)
            accessed_ids = [row[0] for row in accessed_result.all()]
            
            # Get all users from User table who are NOT in accessed list
            from app.models.user import User
            
            if accessed_ids:
                query = select(User).filter(User.id.not_in(accessed_ids))
            else:
                query = select(User)
            
            result = await db.execute(query)
            users = result.scalars().all()
            
            return [
                UserAccessStatus(
                    employee_id=user.id,
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
        employee_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[UserAccess]:
        """Get all access records for a specific employee"""
        query = select(UserAccess).filter(UserAccess.employee_id == employee_id)
        
        if start_date and end_date:
            query = query.filter(
                and_(
                    UserAccess.access_date >= start_date,
                    UserAccess.access_date <= end_date
                )
            )
        elif start_date:
            query = query.filter(UserAccess.access_date == start_date)
        
        query = query.order_by(UserAccess.access_date_time.desc())
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update(
        db: AsyncSession,
        access_id: int,
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
        
        # Update fields and remove timezone info
        update_data = access_data.model_dump(exclude_unset=True)
        if 'access_date_time' in update_data:
            update_data['access_date_time'] = UserAccessService._remove_timezone(update_data['access_date_time'])
        if 'access_time' in update_data:
            update_data['access_time'] = UserAccessService._remove_timezone(update_data['access_time'])
        
        for field, value in update_data.items():
            setattr(access, field, value)
        
        await db.commit()
        await db.refresh(access)
        return access
    
    @staticmethod
    async def delete(db: AsyncSession, access_id: int) -> None:
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
        employee_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        direction: Optional[int] = None
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
                    UserAccess.access_date >= start_date,
                    UserAccess.access_date <= end_date
                )
            )
        elif start_date:
            query = query.filter(UserAccess.access_date == start_date)
        
        result = await db.execute(query)
        return result.scalar()