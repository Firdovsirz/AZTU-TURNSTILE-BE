# app/services/group.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status, Depends
from app.models.groups import Group
from app.core.session import get_db
from fastapi.responses import JSONResponse
from app.api.v1.schema.group import GroupCreate, GroupUpdate


class GroupService:
    @staticmethod
    async def create(db: AsyncSession, group_data: GroupCreate) -> Group:
        """Create a new group"""
        # Check if group_id already exists
        result = await db.execute(
            select(Group).filter(Group.group_id == group_data.group_id)
        )
        existing_group = result.scalar_one_or_none()
        
        if existing_group:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Group with group_id {group_data.group_id} already exists"
            )
        
        new_group = Group(**group_data.model_dump())
        db.add(new_group)
        await db.commit()
        await db.refresh(new_group)
        return new_group
    
    @staticmethod
    async def get_by_id(db: AsyncSession, group_id: int) -> Group:
        """Get a group by ID"""
        result = await db.execute(
            select(Group).filter(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {group_id} not found"
            )
        return group
    
    @staticmethod
    async def get_by_group_id(db: AsyncSession, group_id: int) -> Group:
        """Get a group by group_id"""
        result = await db.execute(
            select(Group).filter(Group.group_id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with group_id {group_id} not found"
            )
        return group
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Group]:
        """Get all groups with pagination"""
        result = await db.execute(
            select(Group).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update(
        db: AsyncSession,
        group_id: int,
        group_data: GroupUpdate
    ) -> Group:
        """Update a group"""
        # Get existing group
        result = await db.execute(
            select(Group).filter(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {group_id} not found"
            )
        
        # Check if new group_id conflicts with existing
        if group_data.group_id and group_data.group_id != group.group_id:
            result = await db.execute(
                select(Group).filter(Group.group_id == group_data.group_id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Group with group_id {group_data.group_id} already exists"
                )
        
        # Update fields
        update_data = group_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(group, field, value)
        
        await db.commit()
        await db.refresh(group)
        return group
    
    @staticmethod
    async def delete(db: AsyncSession, group_id: int) -> None:
        """Delete a group"""
        result = await db.execute(
            select(Group).filter(Group.id == group_id)
        )
        group = result.scalar_one_or_none()
        
        if not group:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Group with id {group_id} not found"
            )
        
        await db.delete(group)
        await db.commit()

async def get_groups(
    db: AsyncSession = Depends(get_db)
):
    try:
        group_query = await db.execute(
            select(Group)
        )

        groups = group_query.scalars().all()

        groups_arr = []

        for group in groups:
            group_obj = {
                "group_id": group.group_id,
                "group_name": group.group_name
            }

            groups_arr.append(group_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "groups": groups_arr
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }
        )