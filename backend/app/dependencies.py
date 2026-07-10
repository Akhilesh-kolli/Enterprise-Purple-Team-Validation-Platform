"""
Dependency injection for FastAPI.
"""
from typing import AsyncGenerator
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.config import settings
from domain.models.user import User
from domain.services.user_service import UserService
from utils.exceptions import AppException
from utils.security import decode_token

security = HTTPBearer(auto_error=False)


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


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get currently authenticated user from JWT bearer token."""
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(credentials.credentials)
        subject = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=401, detail="Invalid authentication token")

        service = UserService(db)
        user = await service.get_user_by_id(int(subject))
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Inactive user")
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except AppException:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
