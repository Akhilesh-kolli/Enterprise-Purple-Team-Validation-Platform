"""
Asset service - business logic layer.
"""
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.v1.schemas.asset import AssetCreate, AssetUpdate
from domain.models.asset import Asset, AssetCriticality, AssetStatus
from domain.repositories.asset_repository import AssetRepository
from utils.exceptions import ConflictError, NotFoundError, ValidationError


class AssetService:
    """Service for asset inventory operations."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = AssetRepository(session)

    async def create_asset(self, payload: AssetCreate) -> Asset:
        """Create asset with duplicate checks."""
        hostname_exists = await self.repository.get_by_hostname(payload.hostname)
        if hostname_exists:
            raise ConflictError(f"Hostname {payload.hostname} already exists")

        ip_address = str(payload.ip_address)
        ip_exists = await self.repository.get_by_ip_address(ip_address)
        if ip_exists:
            raise ConflictError(f"IP address {ip_address} already exists")

        asset = Asset(
            hostname=payload.hostname,
            ip_address=ip_address,
            operating_system=payload.operating_system,
            asset_type=payload.asset_type,
            owner=payload.owner,
            environment=payload.environment,
            criticality=AssetCriticality(payload.criticality),
            status=AssetStatus(payload.status),
        )

        try:
            await self.repository.create_asset(asset)
            await self.session.commit()
            await self.session.refresh(asset)
            return asset
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Hostname or IP address already exists")
        except Exception:
            await self.session.rollback()
            raise

    async def get_asset(self, asset_id: int) -> Asset:
        """Get asset by id."""
        asset = await self.repository.get_asset(asset_id)
        if not asset:
            raise NotFoundError(f"Asset {asset_id} not found")
        return asset

    async def list_assets(self) -> list[Asset]:
        """List all assets."""
        return await self.repository.list_assets()

    async def update_asset(self, asset_id: int, payload: AssetUpdate) -> Asset:
        """Update asset with duplicate checks."""
        asset = await self.get_asset(asset_id)
        updates = payload.model_dump(exclude_unset=True)
        if not updates:
            raise ValidationError("At least one field must be provided for update")

        if "hostname" in updates:
            existing_hostname = await self.repository.get_by_hostname(updates["hostname"])
            if existing_hostname and existing_hostname.id != asset_id:
                raise ConflictError(f"Hostname {updates['hostname']} already exists")

        if "ip_address" in updates:
            updates["ip_address"] = str(updates["ip_address"])
            existing_ip = await self.repository.get_by_ip_address(updates["ip_address"])
            if existing_ip and existing_ip.id != asset_id:
                raise ConflictError(f"IP address {updates['ip_address']} already exists")

        if "criticality" in updates:
            updates["criticality"] = AssetCriticality(updates["criticality"])

        if "status" in updates:
            updates["status"] = AssetStatus(updates["status"])

        try:
            updated = await self.repository.update_asset(asset, updates)
            await self.session.commit()
            await self.session.refresh(updated)
            return updated
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Hostname or IP address already exists")
        except Exception:
            await self.session.rollback()
            raise

    async def delete_asset(self, asset_id: int) -> None:
        """Delete asset by id."""
        asset = await self.get_asset(asset_id)
        await self.repository.delete_asset(asset)
        await self.session.commit()

    async def seed_assets_if_empty(self) -> None:
        """Insert placeholder assets when inventory is empty."""
        existing = await self.repository.list_assets()
        if existing:
            return

        seed_assets = [
            Asset(
                hostname="wkstn-nyc-01",
                ip_address="10.10.1.25",
                operating_system="Windows 11 Enterprise",
                asset_type="Windows Workstation",
                owner="IT Operations",
                environment="Production",
                criticality=AssetCriticality.MEDIUM,
                status=AssetStatus.ACTIVE,
            ),
            Asset(
                hostname="srv-ubuntu-app-01",
                ip_address="10.10.2.40",
                operating_system="Ubuntu Server 22.04 LTS",
                asset_type="Ubuntu Server",
                owner="Platform Team",
                environment="Production",
                criticality=AssetCriticality.HIGH,
                status=AssetStatus.ACTIVE,
            ),
            Asset(
                hostname="dc-core-01",
                ip_address="10.10.0.10",
                operating_system="Windows Server 2022",
                asset_type="Domain Controller",
                owner="Identity Team",
                environment="Production",
                criticality=AssetCriticality.CRITICAL,
                status=AssetStatus.ACTIVE,
            ),
            Asset(
                hostname="fw-edge-01",
                ip_address="10.10.0.1",
                operating_system="PAN-OS 11",
                asset_type="Firewall",
                owner="Network Security",
                environment="Production",
                criticality=AssetCriticality.CRITICAL,
                status=AssetStatus.ACTIVE,
            ),
            Asset(
                hostname="web-public-01",
                ip_address="10.10.3.15",
                operating_system="Rocky Linux 9",
                asset_type="Web Server",
                owner="Web Platform",
                environment="DMZ",
                criticality=AssetCriticality.HIGH,
                status=AssetStatus.ACTIVE,
            ),
        ]

        try:
            for seed_asset in seed_assets:
                await self.repository.create_asset(seed_asset)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            raise
