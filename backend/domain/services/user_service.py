"""
User service - business logic layer.
"""
from datetime import timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from domain.models.user import User, UserRole, AuditLog
from domain.repositories.user_repository import UserRepository, AuditLogRepository
from utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from utils.exceptions import AuthenticationError, ValidationError, ConflictError, NotFoundError
from app.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """Service for user management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = UserRepository(session)
        self.audit_repo = AuditLogRepository(session)
    
    async def register(self, username: str, email: str, password: str, full_name: str | None = None) -> User:
        """Register a new user."""
        # Check if user already exists
        existing = await self.repository.get_by_username(username)
        if existing:
            raise ConflictError(f"User {username} already exists")
        
        existing = await self.repository.get_by_email(email)
        if existing:
            raise ConflictError(f"Email {email} is already registered")
        
        # Validate password
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters")
        
        # Create user
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password),
            role=UserRole.READ_ONLY,
            is_active=True,
        )
        
        try:
            await self.repository.create(user)
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            raise ConflictError("Username or email is already registered")
        except Exception:
            await self.session.rollback()
            raise
        
        logger.info("user_registered", username=username, email=email)
        return user
    
    async def authenticate(self, username: str, password: str) -> User:
        """Authenticate user and return user object."""
        user = await self.repository.get_by_username(username)
        
        if not user or not verify_password(password, user.hashed_password):
            logger.warning("authentication_failed", username=username)
            raise AuthenticationError("Invalid username or password")
        
        if not user.is_active:
            logger.warning("authentication_failed_inactive", username=username)
            raise AuthenticationError("User is inactive")
        
        logger.info("authentication_success", username=username)
        return user
    
    async def login(self, username: str, password: str) -> dict:
        """Login user and return tokens."""
        user = await self.authenticate(username, password)
        
        # Create tokens
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value}
        )
        refresh_token = create_refresh_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        # Create audit log
        await self.audit_repo.create(
            AuditLog(
                user_id=user.id,
                action="login",
                resource_type="user",
                resource_id=str(user.id),
                status="success",
            )
        )
        await self.session.commit()
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 30 * 60,  # 30 minutes
        }
    
    async def get_user_by_id(self, user_id: int) -> User:
        """Get user by ID."""
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return user
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all users."""
        return await self.repository.get_all(skip=skip, limit=limit)
    
    async def audit_action(
        self,
        user_id: int,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        details: str | None = None,
        status: str = "success",
    ) -> AuditLog:
        """Create an audit log entry."""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            status=status,
        )
        await self.audit_repo.create(audit_log)
        await self.session.commit()
        return audit_log
