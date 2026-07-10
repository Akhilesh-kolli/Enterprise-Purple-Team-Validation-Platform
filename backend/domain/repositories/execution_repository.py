"""
Execution repository - data access layer.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.execution import Execution


class ExecutionRepository:
    """Repository for execution persistence and querying."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_execution(self, execution: Execution) -> Execution:
        """Create and flush new execution."""
        self.session.add(execution)
        await self.session.flush()
        return execution

    async def get_execution(self, execution_id: int) -> Execution | None:
        """Get execution by id."""
        result = await self.session.execute(
            select(Execution).where(Execution.id == execution_id)
        )
        return result.scalar_one_or_none()

    async def list_executions(self, limit: int = 100) -> list[Execution]:
        """List executions newest-first."""
        result = await self.session.execute(
            select(Execution).order_by(Execution.id.desc()).limit(limit)
        )
        return result.scalars().all()

    async def list_latest_executions(self, limit: int = 20) -> list[Execution]:
        """List latest executions newest-first."""
        return await self.list_executions(limit=limit)

    async def update_execution(self, execution: Execution, updates: dict) -> Execution:
        """Apply updates to execution and flush."""
        for field, value in updates.items():
            setattr(execution, field, value)
        await self.session.flush()
        return execution

    async def delete_execution(self, execution: Execution) -> None:
        """Delete execution."""
        await self.session.delete(execution)
