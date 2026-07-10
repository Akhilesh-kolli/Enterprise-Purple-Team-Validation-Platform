"""
Asset repository - data access layer.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.models.asset import Asset


class AssetRepository:
    """Repository for asset persistence and querying."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_asset(self, asset: Asset) -> Asset:
        """Create and flush a new asset."""
        self.session.add(asset)
        await self.session.flush()
        return asset

    async def get_asset(self, asset_id: int) -> Asset | None:
        """Get asset by id."""
        result = await self.session.execute(select(Asset).where(Asset.id == asset_id))
        return result.scalar_one_or_none()

    async def list_assets(self) -> list[Asset]:
        """Get all assets ordered by hostname."""
        result = await self.session.execute(select(Asset).order_by(Asset.hostname.asc()))
        return result.scalars().all()

    async def get_by_hostname(self, hostname: str) -> Asset | None:
        """Get asset by hostname."""
        result = await self.session.execute(
            select(Asset).where(Asset.hostname == hostname)
        )
        return result.scalar_one_or_none()

    async def get_by_ip_address(self, ip_address: str) -> Asset | None:
        """Get asset by ip address."""
        result = await self.session.execute(
            select(Asset).where(Asset.ip_address == ip_address)
        )
        return result.scalar_one_or_none()

    async def update_asset(self, asset: Asset, updates: dict) -> Asset:
        """Update mutable asset fields and flush."""
        for field, value in updates.items():
            setattr(asset, field, value)
        await self.session.flush()
        return asset

    async def delete_asset(self, asset: Asset) -> None:
        """Delete an existing asset."""
        await self.session.delete(asset)
