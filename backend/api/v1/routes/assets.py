"""
Asset management routes.
"""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.asset import AssetCreate, AssetResponse, AssetUpdate
from app.dependencies import get_current_user, get_db
from domain.models.user import User
from domain.services.asset_service import AssetService
from utils.exceptions import AppException

router = APIRouter(prefix="/assets", tags=["Assets"])


@router.get("", response_model=list[AssetResponse])
async def list_assets(
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> list[AssetResponse]:
    """List all assets."""
    try:
        service = AssetService(db)
        assets = await service.list_assets()
        return [AssetResponse.model_validate(asset) for asset in assets]
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> AssetResponse:
    """Get one asset by id."""
    try:
        service = AssetService(db)
        asset = await service.get_asset(asset_id)
        return AssetResponse.model_validate(asset)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    request: AssetCreate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> AssetResponse:
    """Create a new asset."""
    try:
        service = AssetService(db)
        asset = await service.create_asset(request)
        return AssetResponse.model_validate(asset)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.put("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: int,
    request: AssetUpdate,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> AssetResponse:
    """Update asset by id."""
    try:
        service = AssetService(db)
        asset = await service.update_asset(asset_id, request)
        return AssetResponse.model_validate(asset)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> Response:
    """Delete asset by id."""
    try:
        service = AssetService(db)
        await service.delete_asset(asset_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
