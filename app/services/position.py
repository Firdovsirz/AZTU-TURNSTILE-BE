# app/services/position.py
from typing import List
from sqlalchemy import select
from app.core.session import get_db
from app.models.positions import Position
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status, Depends
from app.api.v1.schema.position import PositionCreate, PositionUpdate


class PositionService:
    @staticmethod
    async def create(db: AsyncSession, position_data: PositionCreate) -> Position:
        """Create a new position"""
        # Check if position_id already exists
        result = await db.execute(
            select(Position).filter(Position.position_id == position_data.position_id)
        )
        existing_position = result.scalar_one_or_none()
        
        if existing_position:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Position with position_id {position_data.position_id} already exists"
            )
        
        new_position = Position(**position_data.model_dump())
        db.add(new_position)
        await db.commit()
        await db.refresh(new_position)
        return new_position
    
    @staticmethod
    async def get_by_id(db: AsyncSession, position_id: int) -> Position:
        """Get a position by ID"""
        result = await db.execute(
            select(Position).filter(Position.id == position_id)
        )
        position = result.scalar_one_or_none()
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Position with id {position_id} not found"
            )
        return position
    
    @staticmethod
    async def get_by_position_id(db: AsyncSession, position_id: int) -> Position:
        """Get a position by position_id"""
        result = await db.execute(
            select(Position).filter(Position.position_id == position_id)
        )
        position = result.scalar_one_or_none()
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Position with position_id {position_id} not found"
            )
        return position
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Position]:
        """Get all positions with pagination"""
        result = await db.execute(
            select(Position).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def update(
        db: AsyncSession,
        position_id: int,
        position_data: PositionUpdate
    ) -> Position:
        """Update a position"""
        # Get existing position
        result = await db.execute(
            select(Position).filter(Position.id == position_id)
        )
        position = result.scalar_one_or_none()
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Position with id {position_id} not found"
            )
        
        # Check if new position_id conflicts with existing
        if position_data.position_id and position_data.position_id != position.position_id:
            result = await db.execute(
                select(Position).filter(Position.position_id == position_data.position_id)
            )
            existing = result.scalar_one_or_none()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Position with position_id {position_data.position_id} already exists"
                )
        
        # Update fields
        update_data = position_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(position, field, value)
        
        await db.commit()
        await db.refresh(position)
        return position
    
    @staticmethod
    async def delete(db: AsyncSession, position_id: int) -> None:
        """Delete a position"""
        result = await db.execute(
            select(Position).filter(Position.id == position_id)
        )
        position = result.scalar_one_or_none()
        
        if not position:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Position with id {position_id} not found"
            )
        
        await db.delete(position)
        await db.commit()

async def get_positions(
    db: AsyncSession = Depends(get_db)
):
    try:
        group_query = await db.execute(
            select(Position)
        )

        positions = group_query.scalars().all()

        position_arr = []

        for position in positions:
            position_obj = {
                "position_id": position.position_id,
                "position": position.position
            }

            position_arr.append(position_obj)
        
        return JSONResponse(
            content={
                "status_code": 200,
                "positions": position_arr
            }, status_code=status.HTTP_200_OK
        )
    
    except Exception as e:
        return JSONResponse(
            content={
                "status_code": 500,
                "error": str(e)
            }
        )