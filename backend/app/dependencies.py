"""
Dependency injection for FastAPI.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
from app.database import AsyncSessionLocal
from app.config import settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with AsyncSessionLocal() as session:
        yield session


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    """Get Redis client."""
    pool = redis.ConnectionPool.from_url(settings.REDIS_URL)
    client = redis.Redis(connection_pool=pool)
    try:
        yield client
    finally:
        await client.close()
