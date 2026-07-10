"""
Dashboard routes.
"""
from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.dashboard import DashboardSummaryResponse, LatestExecutionResponse
from app.dependencies import get_db
from domain.models.asset import Asset
from domain.models.execution import Execution, ExecutionStatus
from domain.services.execution_service import to_latest_execution_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(db: AsyncSession = Depends(get_db)) -> DashboardSummaryResponse:
    """
    Return dashboard summary metrics for the frontend.
    """
    total_assets = (await db.scalar(select(func.count(Asset.id)))) or 0

    running_executions = (
        await db.scalar(
            select(func.count(Execution.id)).where(Execution.status == ExecutionStatus.RUNNING)
        )
    ) or 0
    completed_executions = (
        await db.scalar(
            select(func.count(Execution.id)).where(
                Execution.status == ExecutionStatus.COMPLETED
            )
        )
    ) or 0
    failed_executions = (
        await db.scalar(
            select(func.count(Execution.id)).where(Execution.status == ExecutionStatus.FAILED)
        )
    ) or 0
    executed_tests = (await db.scalar(select(func.count(Execution.id)))) or 0

    detection_success_rate = (
        round((completed_executions / executed_tests) * 100, 2) if executed_tests else 0.0
    )

    latest_executions_result = await db.execute(
        select(Execution).order_by(Execution.id.desc()).limit(5)
    )
    latest_executions_models = latest_executions_result.scalars().all()
    latest_executions: list[LatestExecutionResponse] = [
        to_latest_execution_response(execution) for execution in latest_executions_models
    ]
    latest_execution = latest_executions[0] if latest_executions else None

    return DashboardSummaryResponse(
        total_assets=total_assets,
        executed_tests=executed_tests,
        detection_success_rate=detection_success_rate,
        latest_executions=latest_executions,
        running_executions=running_executions,
        completed_executions=completed_executions,
        failed_executions=failed_executions,
        latest_execution=latest_execution,
    )
