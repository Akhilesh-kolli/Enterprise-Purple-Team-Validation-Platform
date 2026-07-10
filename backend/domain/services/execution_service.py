"""
Execution service - business logic layer.
"""
import asyncio
import random
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.dashboard import LatestExecutionResponse
from api.v1.schemas.execution import ExecutionCreateRequest
from app.database import AsyncSessionLocal
from domain.models.execution import Execution, ExecutionSeverity, ExecutionStatus
from domain.repositories.asset_repository import AssetRepository
from domain.repositories.execution_repository import ExecutionRepository
from utils.exceptions import NotFoundError, ValidationError


class ExecutionService:
    """Service for attack execution lifecycle."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ExecutionRepository(session)
        self.asset_repository = AssetRepository(session)

    async def create_execution(
        self, payload: ExecutionCreateRequest, created_by: str
    ) -> Execution:
        """Create and start an execution."""
        target_asset = await self.asset_repository.get_by_hostname(payload.target_asset)
        if not target_asset:
            raise ValidationError(
                f"Target asset {payload.target_asset} does not exist"
            )

        execution = Execution(
            execution_name=payload.execution_name,
            attack_type=payload.attack_type,
            target_asset=payload.target_asset,
            status=ExecutionStatus.QUEUED,
            progress=0,
            findings_count=0,
            severity=None,
            created_by=created_by,
        )
        await self.repository.create_execution(execution)
        await self.session.commit()
        await self.session.refresh(execution)

        await self.repository.update_execution(
            execution,
            {
                "status": ExecutionStatus.RUNNING,
                "started_at": datetime.now(timezone.utc),
                "progress": 0,
            },
        )
        await self.session.commit()
        await self.session.refresh(execution)
        return execution

    async def list_executions(self, limit: int = 100) -> list[Execution]:
        """List executions newest-first."""
        return await self.repository.list_executions(limit=limit)

    async def get_execution(self, execution_id: int) -> Execution:
        """Get execution by id."""
        execution = await self.repository.get_execution(execution_id)
        if not execution:
            raise NotFoundError(f"Execution {execution_id} not found")
        return execution

    async def delete_execution(self, execution_id: int) -> None:
        """Delete execution by id."""
        execution = await self.get_execution(execution_id)
        await self.repository.delete_execution(execution)
        await self.session.commit()

    async def list_latest_executions(self, limit: int = 20) -> list[Execution]:
        """List latest executions."""
        return await self.repository.list_latest_executions(limit=limit)

    async def run_execution_simulation(self, execution_id: int) -> None:
        """Simulate execution progress in background."""
        execution = await self.repository.get_execution(execution_id)
        if not execution:
            return

        for progress_value in [20, 40, 60, 80, 100]:
            await asyncio.sleep(2)
            updates: dict = {"progress": progress_value, "status": ExecutionStatus.RUNNING}
            if progress_value == 100:
                updates["status"] = ExecutionStatus.COMPLETED
                updates["completed_at"] = datetime.now(timezone.utc)
                updates["findings_count"] = random.randint(1, 15)
                updates["severity"] = random.choice(
                    [
                        ExecutionSeverity.LOW,
                        ExecutionSeverity.MEDIUM,
                        ExecutionSeverity.HIGH,
                        ExecutionSeverity.CRITICAL,
                    ]
                )

            await self.repository.update_execution(execution, updates)
            await self.session.commit()
            await self.session.refresh(execution)


async def simulate_execution_progress(execution_id: int) -> None:
    """Background entrypoint for execution simulation."""
    async with AsyncSessionLocal() as session:
        service = ExecutionService(session)
        await service.run_execution_simulation(execution_id)


def to_latest_execution_response(execution: Execution) -> LatestExecutionResponse:
    """Map execution model to latest execution schema."""
    severity = execution.severity.value if execution.severity else None
    return LatestExecutionResponse(
        id=execution.id,
        execution_name=execution.execution_name,
        attack_type=execution.attack_type,
        target_asset=execution.target_asset,
        status=execution.status.value,
        progress=execution.progress,
        findings_count=execution.findings_count,
        severity=severity,
        started_at=execution.started_at,
        completed_at=execution.completed_at,
        created_by=execution.created_by,
    )
