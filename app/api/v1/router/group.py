# app/api/routes/group.py
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.schema.group import GroupCreate, GroupUpdate, GroupResponse
from app.services.group import GroupService
from app.core.security import get_current_user
from app.models.auth import Auth
from app.services.group import *

router = APIRouter()


@router.post("/", response_model=GroupResponse, status_code=status.HTTP_201_CREATED)
async def create_group(
    group_data: GroupCreate,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Create a new group"""
    return await GroupService.create(db, group_data)


# @router.get("/", response_model=List[GroupResponse])
# async def get_groups(
#     skip: int = 0,
#     limit: int = 100,
#     db: AsyncSession = Depends(get_db),
#     # current_user: Auth = Depends(get_current_user)
# ):
#     """Get all groups with pagination"""
#     return await GroupService.get_all(db, skip, limit)


# @router.get("/{group_id}", response_model=GroupResponse)
# async def get_group(
#     group_id: int,
#     db: AsyncSession = Depends(get_db),
#     # current_user: Auth = Depends(get_current_user)
# ):
#     """Get a group by ID"""
#     return await GroupService.get_by_id(db, group_id)


@router.get("/by-group-id/{group_id}", response_model=GroupResponse)
async def get_group_by_group_id(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Get a group by group_id"""
    return await GroupService.get_by_group_id(db, group_id)


@router.put("/{group_id}/edit", response_model=GroupResponse)
async def update_group(
    group_id: int,
    group_data: GroupUpdate,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Update a group"""
    return await GroupService.update(db, group_id, group_data)


@router.delete("/{group_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_group(
    group_id: int,
    db: AsyncSession = Depends(get_db),
    # current_user: Auth = Depends(get_current_user)
):
    """Delete a group"""
    await GroupService.delete(db, group_id)

@router.get("/all")
async def get_groups_endpoint(
    db: AsyncSession = Depends(get_db)
):
    return await get_groups(db=db)