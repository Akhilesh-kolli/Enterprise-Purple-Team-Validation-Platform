"""
Pydantic schemas for authentication endpoints.
"""
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""
    username: str = Field(..., min_length=3, max_length=255)
    password: str = Field(..., min_length=8, max_length=255)


class TokenResponse(BaseModel):
    """Token response schema."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""
    refresh_token: str


class UserResponse(BaseModel):
    """User response schema (public)."""
    id: int
    username: str
    email: str
    full_name: str | None
    role: str
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    """User creation request schema."""
    username: str = Field(..., min_length=3, max_length=255)
    email: EmailStr
    full_name: str | None = None
    password: str = Field(..., min_length=8, max_length=255)
    role: str = Field(default="read_only")


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str
    database: str
    redis: str
    version: str
