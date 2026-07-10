"""
Schemas for execution endpoints.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ExecutionCreateRequest(BaseModel):
    """Execution creation payload."""

    execution_name: str = Field(..., min_length=1, max_length=255)
    attack_type: str = Field(..., min_length=1, max_length=255)
    target_asset: str = Field(..., min_length=1, max_length=255)

    @field_validator("execution_name", "attack_type", "target_asset", mode="before")
    @classmethod
    def strip_values(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value


ExecutionStatusValue = Literal["queued", "running", "completed", "failed"]
ExecutionSeverityValue = Literal["Low", "Medium", "High", "Critical"] | None


class ExecutionResponse(BaseModel):
    """Execution response payload."""

    id: int
    execution_name: str
    attack_type: str
    target_asset: str
    status: ExecutionStatusValue
    progress: int
    started_at: datetime | None
    completed_at: datetime | None
    findings_count: int
    severity: ExecutionSeverityValue = None
    created_by: str

    class Config:
        from_attributes = True
