"""
User repository - data access layer.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from domain.models.user import User, AuditLog
from utils.exceptions import NotFoundError


class UserRepository:
    """Repository for user data access."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> User | None:
        """Get user by username."""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> User | None:
        """Get user by email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def create(self, user: User) -> User:
        """Create a new user."""
        self.session.add(user)
        await self.session.flush()
        return user
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users with pagination."""
        result = await self.session.execute(
            select(User).offset(skip).limit(limit)
        )
        return result.scalars().all()
    
    async def update(self, user: User) -> User:
        """Update a user."""
        await self.session.merge(user)
        return user
    
    async def delete(self, user_id: int) -> bool:
        """Delete a user."""
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        await self.session.delete(user)
        return True


class AuditLogRepository:
    """Repository for audit log data access."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, audit_log: AuditLog) -> AuditLog:
        """Create an audit log entry."""
        self.session.add(audit_log)
        await self.session.flush()
        return audit_log
    
    async def get_by_user(self, user_id: int, limit: int = 100) -> list[AuditLog]:
        """Get audit logs for a user."""
        result = await self.session.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_recent(self, limit: int = 100) -> list[AuditLog]:
        """Get recent audit logs."""
        result = await self.session.execute(
            select(AuditLog)
            .order_by(AuditLog.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()
