"""
Execution model for attack simulation runs.
"""
import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.models.base import Base, TimestampMixin


class ExecutionStatus(str, enum.Enum):
    """Execution lifecycle states."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ExecutionSeverity(str, enum.Enum):
    """Execution finding severity levels."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Execution(Base, TimestampMixin):
    """Attack execution record."""

    __tablename__ = "executions"

    id: Mapped[int] = mapped_column(primary_key=True)
    execution_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    attack_type: Mapped[str] = mapped_column(String(255), nullable=False)
    target_asset: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(ExecutionStatus), nullable=False, default=ExecutionStatus.QUEUED
    )
    progress: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    findings_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    severity: Mapped[ExecutionSeverity | None] = mapped_column(
        Enum(ExecutionSeverity), nullable=True
    )
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Execution(id={self.id}, execution_name={self.execution_name}, "
            f"status={self.status}, progress={self.progress})>"
        )
