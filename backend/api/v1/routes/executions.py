"""
Execution routes.
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.dashboard import LatestExecutionResponse
from api.v1.schemas.execution import ExecutionCreateRequest, ExecutionResponse
from app.dependencies import get_current_user, get_db
from domain.models.user import User
from domain.services.execution_service import (
    ExecutionService,
    simulate_execution_progress,
    to_latest_execution_response,
)
from utils.exceptions import AppException

router = APIRouter(prefix="/executions", tags=["Executions"])


@router.get("/latest", response_model=list[LatestExecutionResponse])
async def get_latest_executions(
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[LatestExecutionResponse]:
    """
    Return latest executions with runtime status.
    """
    try:
        service = ExecutionService(db)
        latest = await service.list_latest_executions(limit=limit)
        return [to_latest_execution_response(execution) for execution in latest]
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("", response_model=list[ExecutionResponse])
async def list_executions(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[ExecutionResponse]:
    """
    List executions newest-first.
    """
    try:
        service = ExecutionService(db)
        executions = await service.list_executions(limit=100)
        return [ExecutionResponse.model_validate(execution) for execution in executions]
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{id}", response_model=ExecutionResponse)
async def get_execution(
    id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> ExecutionResponse:
    """
    Get execution by id.
    """
    try:
        service = ExecutionService(db)
        execution = await service.get_execution(id)
        return ExecutionResponse.model_validate(execution)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("", response_model=ExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_execution(
    request: ExecutionCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ExecutionResponse:
    """
    Create and start a new attack execution.
    """
    try:
        service = ExecutionService(db)
        execution = await service.create_execution(
            payload=request,
            created_by=current_user.username,
        )
        background_tasks.add_task(simulate_execution_progress, execution.id)
        return ExecutionResponse.model_validate(execution)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution(
    id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> Response:
    """
    Delete execution by id.
    """
    try:
        service = ExecutionService(db)
        await service.delete_execution(id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
