"""
Pydantic schemas for asset endpoints.
"""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, IPvAnyAddress, field_validator


AllowedCriticality = Literal["low", "medium", "high", "critical"]
AllowedStatus = Literal["active", "inactive", "maintenance", "retired"]


class AssetBase(BaseModel):
    """Shared asset fields."""

    hostname: str = Field(..., min_length=1, max_length=255)
    ip_address: IPvAnyAddress
    operating_system: str = Field(..., min_length=1, max_length=255)
    asset_type: str = Field(..., min_length=1, max_length=100)
    owner: str = Field(..., min_length=1, max_length=255)
    environment: str = Field(..., min_length=1, max_length=100)
    criticality: AllowedCriticality
    status: AllowedStatus

    @field_validator(
        "hostname",
        "operating_system",
        "asset_type",
        "owner",
        "environment",
        mode="before",
    )
    @classmethod
    def strip_required_strings(cls, value: str) -> str:
        if isinstance(value, str):
            value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value


class AssetCreate(AssetBase):
    """Create asset payload."""


class AssetUpdate(BaseModel):
    """Update asset payload."""

    hostname: str | None = Field(default=None, min_length=1, max_length=255)
    ip_address: IPvAnyAddress | None = None
    operating_system: str | None = Field(default=None, min_length=1, max_length=255)
    asset_type: str | None = Field(default=None, min_length=1, max_length=100)
    owner: str | None = Field(default=None, min_length=1, max_length=255)
    environment: str | None = Field(default=None, min_length=1, max_length=100)
    criticality: AllowedCriticality | None = None
    status: AllowedStatus | None = None

    @field_validator(
        "hostname",
        "operating_system",
        "asset_type",
        "owner",
        "environment",
        mode="before",
    )
    @classmethod
    def strip_optional_strings(cls, value: str | None) -> str | None:
        if value is None:
            return value
        value = value.strip()
        if not value:
            raise ValueError("Field cannot be empty")
        return value


class AssetResponse(BaseModel):
    """Asset response payload."""

    id: int
    hostname: str
    ip_address: str
    operating_system: str
    asset_type: str
    owner: str
    environment: str
    criticality: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
