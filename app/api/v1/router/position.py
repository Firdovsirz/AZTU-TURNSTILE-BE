# app/api/routes/position.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.schema.position import PositionCreate, PositionUpdate, PositionResponse
from app.services.position import PositionService
from app.core.security import get_current_user
from app.models.auth import Auth
from app.services.position import *

router = APIRouter()


@router.post("/", response_model=PositionResponse, status_code=status.HTTP_201_CREATED)
async def create_position(
    position_data: PositionCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Create a new position"""
    return await PositionService.create(db, position_data)


# @router.get("/", response_model=List[PositionResponse])
# async def get_positions(
#     skip: int = 0,
#     limit: int = 100,
#     db: AsyncSession = Depends(get_db),
#     # current_user: Auth = Depends(get_current_user)
# ):
#     """Get all positions with pagination"""
#     return await PositionService.get_all(db, skip, limit)


@router.get("/{position_id}/details", response_model=PositionResponse)
async def get_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get a position by ID"""
    return await PositionService.get_by_id(db, position_id)


@router.get("/by-position-id/{position_id}", response_model=PositionResponse)
async def get_position_by_position_id(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get a position by position_id"""
    return await PositionService.get_by_position_id(db, position_id)


@router.put("/{position_id}/edit", response_model=PositionResponse)
async def update_position(
    position_id: int,
    position_data: PositionUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Update a position"""
    return await PositionService.update(db, position_id, position_data)


@router.delete("/{position_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_position(
    position_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Delete a position"""
    await PositionService.delete(db, position_id)


@router.get("/all")
async def get_positions_endpoint(
    db: AsyncSession = Depends(get_db)
):
    return await get_positions(db=db)