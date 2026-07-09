"""
Health check routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import redis.asyncio as redis
from app.dependencies import get_db, get_redis
from api.v1.schemas.auth import HealthCheckResponse
from app.config import settings
from app.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis),
) -> HealthCheckResponse:
    """
    Health check endpoint.
    
    Verifies database and Redis connectivity.
    """
    # Check database
    db_status = "healthy"
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        logger.error("database_health_check_failed", error=str(e))
        db_status = "unhealthy"
    
    # Check Redis
    redis_status = "healthy"
    try:
        await redis_client.ping()
    except Exception as e:
        logger.error("redis_health_check_failed", error=str(e))
        redis_status = "unhealthy"
    
    overall_status = "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded"
    
    return HealthCheckResponse(
        status=overall_status,
        database=db_status,
        redis=redis_status,
        version=settings.APP_VERSION,
    )
