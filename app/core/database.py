import os
from dotenv import load_dotenv
from typing import AsyncGenerator
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set.")

parsed = urlparse(DATABASE_URL)
query_params = parse_qs(parsed.query)
query_params.pop("sslmode", None)
query_params.pop("channel_binding", None)
new_query = urlencode(query_params, doseq=True)
clean_url = urlunparse(parsed._replace(query=new_query))

async_database_url = clean_url.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    async_database_url,
    echo=True,
    future=True,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

Base = declarative_base()