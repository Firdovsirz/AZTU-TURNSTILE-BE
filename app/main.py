import os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router.user import router as user_router
from app.api.v1.router.auth import router as auth_router
from app.api.v1.router.group import router as group_router
from app.api.v1.router.position import router as position_router
from app.api.v1.router.user_access import router as user_access_router

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

app = FastAPI(
    title="AzTU University API",
    description="Backend API for AzTU website (news, announcements, sliders, etc.)",
    version="1.0.0"
)

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(user_router, prefix="/api/user", tags=["User"])
app.include_router(group_router, prefix="/api/group", tags=["Group"])
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(position_router, prefix="/api/position", tags=["Positions"])
app.include_router(user_access_router, prefix="/api/user-access", tags=["User Access"])

@app.get("/")
async def root():
    return {"message": "Welcome to AzTU TURNSTILE  API!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}