"""
Dashboard routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.dashboard import DashboardSummaryResponse, LatestExecutionResponse
from app.dependencies import get_db
from domain.models.user import AuditLog, User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)) -> DashboardSummaryResponse:
    """
    Return dashboard summary metrics for the frontend.
    """
    executed_tests = (
        await db.scalar(select(func.count(AuditLog.id)).where(AuditLog.action == "login"))
    ) or 0
    successful_tests = (
        await db.scalar(
            select(func.count(AuditLog.id)).where(
                AuditLog.action == "login",
                AuditLog.status == "success",
            )
        )
    ) or 0

    detection_success_rate = (
        round((successful_tests / executed_tests) * 100, 2) if executed_tests else 0.0
    )

    latest_result = await db.execute(
        select(AuditLog, User.username)
        .outerjoin(User, User.id == AuditLog.user_id)
        .order_by(AuditLog.created_at.desc())
        .limit(5)
    )
    latest_executions = [
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
        for audit_log, username in latest_result.all()
    ]

    # Asset domain APIs are planned for later phases; keep this stable for now.
    total_assets = 0

    return DashboardSummaryResponse(
        total_assets=total_assets,
        executed_tests=executed_tests,
        detection_success_rate=detection_success_rate,
        latest_executions=latest_executions,
    )
