"""
Asset model for infrastructure inventory.
"""
import enum

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from domain.models.base import Base, TimestampMixin


class AssetCriticality(str, enum.Enum):
    """Allowed criticality levels for assets."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AssetStatus(str, enum.Enum):
    """Allowed operational states for assets."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"


class Asset(Base, TimestampMixin):
    """Tracked infrastructure asset."""

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    hostname: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    ip_address: Mapped[str] = mapped_column(
        String(45), unique=True, nullable=False, index=True
    )
    operating_system: Mapped[str] = mapped_column(String(255), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(100), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    environment: Mapped[str] = mapped_column(String(100), nullable=False)
    criticality: Mapped[AssetCriticality] = mapped_column(
        Enum(AssetCriticality), nullable=False
    )
    status: Mapped[AssetStatus] = mapped_column(Enum(AssetStatus), nullable=False)

    def __repr__(self) -> str:
        return f"<Asset(id={self.id}, hostname={self.hostname}, ip={self.ip_address})>"
