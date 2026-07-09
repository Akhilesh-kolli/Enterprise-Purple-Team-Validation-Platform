"""
Script to seed initial admin user and test data.

Usage:
    python scripts/seed_data.py
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.config import settings
from app.database import AsyncSessionLocal
from domain.models.base import Base
from domain.models.user import User, UserRole
from domain.repositories.user_repository import UserRepository
from utils.security import hash_password
from app.logging import configure_logging, get_logger

logger = get_logger(__name__)


async def seed_admin_user() -> None:
    """Create initial admin user."""
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        
        # Check if admin already exists
        existing = await repo.get_by_username("admin")
        if existing:
            logger.info("admin_user_already_exists")
            return
        
        # Create admin user
        admin = User(
            username="admin",
            email="admin@localhost",
            full_name="Administrator",
            hashed_password=hash_password("AdminPassword123"),
            role=UserRole.ADMIN,
            is_active=True,
            is_superuser=True,
        )
        
        await repo.create(admin)
        await session.commit()
        
        logger.info("admin_user_created", username="admin", email="admin@localhost")


async def seed_test_users() -> None:
    """Create test users for different roles."""
    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)
        
        test_users = [
            {
                "username": "purple_team_user",
                "email": "purple@localhost",
                "full_name": "Purple Team Operator",
                "role": UserRole.PURPLE_TEAM,
            },
            {
                "username": "soc_analyst",
                "email": "soc@localhost",
                "full_name": "SOC Analyst",
                "role": UserRole.SOC_ANALYST,
            },
            {
                "username": "detection_eng",
                "email": "detection@localhost",
                "full_name": "Detection Engineer",
                "role": UserRole.DETECTION_ENGINEER,
            },
            {
                "username": "read_only_user",
                "email": "readonly@localhost",
                "full_name": "Read Only User",
                "role": UserRole.READ_ONLY,
            },
        ]
        
        for user_data in test_users:
            existing = await repo.get_by_username(user_data["username"])
            if existing:
                logger.info("user_already_exists", username=user_data["username"])
                continue
            
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                hashed_password=hash_password("TestPassword123"),
                role=user_data["role"],
                is_active=True,
            )
            
            await repo.create(user)
            logger.info("test_user_created", username=user_data["username"], role=user_data["role"].value)
        
        await session.commit()


async def main() -> None:
    """Main seeding function."""
    configure_logging()
    
    logger.info("seed_data_starting", env=settings.ENV)
    
    try:
        await seed_admin_user()
        await seed_test_users()
        logger.info("seed_data_completed_successfully")
    except Exception as e:
        logger.exception("seed_data_failed", error=str(e))
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
