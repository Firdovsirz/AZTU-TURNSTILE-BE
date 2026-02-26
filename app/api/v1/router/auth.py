# app/api/routes/auth.py (or app/api/v1/router/auth.py)
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.schema.auth import UserSignUp, UserSignIn, Token, UserResponse
from app.services.auth import AuthService
from app.core.security import get_current_user
from app.models.auth import Auth

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(user_data: UserSignUp, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    user = await AuthService.sign_up(db, user_data)
    return user


@router.post("/signin", response_model=Token)
async def sign_in(credentials: UserSignIn, db: AsyncSession = Depends(get_db)):
    """Login and get access token"""
    return await AuthService.sign_in(db, credentials)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Auth = Depends(get_current_user)):
    """Get current authenticated user info"""
    return current_user