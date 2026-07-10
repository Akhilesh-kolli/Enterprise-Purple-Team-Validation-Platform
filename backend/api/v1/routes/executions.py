"""
Execution activity routes.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.dashboard import LatestExecutionResponse
from app.dependencies import get_db
from domain.models.user import AuditLog, User

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get("/latest", response_model=list[LatestExecutionResponse])
async def get_latest_executions(
    limit: int = Query(default=10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> list[LatestExecutionResponse]:
    """
    Return latest execution-like activity records.

    Uses audit log records as the current canonical execution timeline.
    """
    result = await db.execute(
        select(AuditLog, User.username)
        .outerjoin(User, User.id == AuditLog.user_id)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )

    latest = []
    for audit_log, username in result.all():
        latest.append(
            LatestExecutionResponse(
                id=audit_log.id,
                user_id=audit_log.user_id,
                username=username,
                action=audit_log.action,
                resource_type=audit_log.resource_type,
                resource_id=audit_log.resource_id,
                status=audit_log.status,
                created_at=audit_log.created_at,
            )
        )

    return latest
