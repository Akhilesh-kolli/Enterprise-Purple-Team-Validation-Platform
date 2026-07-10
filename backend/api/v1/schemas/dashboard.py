"""
Schemas for dashboard and execution summary endpoints.
"""
from datetime import datetime

from pydantic import BaseModel


class LatestExecutionResponse(BaseModel):
    """Latest execution entry for dashboard and execution surfaces."""

    id: int
    execution_name: str
    attack_type: str
    target_asset: str
    status: str
    progress: int
    findings_count: int
    severity: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_by: str


class DashboardSummaryResponse(BaseModel):
    """High-level dashboard summary payload."""

    total_assets: int
    executed_tests: int
    detection_success_rate: float
    latest_executions: list[LatestExecutionResponse]
    running_executions: int = 0
    completed_executions: int = 0
    failed_executions: int = 0
    latest_execution: LatestExecutionResponse | None = None
