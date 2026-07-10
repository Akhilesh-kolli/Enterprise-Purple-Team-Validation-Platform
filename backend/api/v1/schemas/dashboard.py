"""
Schemas for dashboard and execution summary endpoints.
"""
from datetime import datetime

from pydantic import BaseModel


class LatestExecutionResponse(BaseModel):
    """Latest execution/activity entry for dashboard surfaces."""

    id: int
    user_id: int
    username: str | None = None
    action: str
    resource_type: str
    resource_id: str | None = None
    status: str
    created_at: datetime


class DashboardSummaryResponse(BaseModel):
    """High-level dashboard summary payload."""

    total_assets: int
    executed_tests: int
    detection_success_rate: float
    latest_executions: list[LatestExecutionResponse]
