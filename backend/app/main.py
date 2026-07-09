"""
FastAPI application factory and configuration.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config import settings
from app.logging import configure_logging, get_logger
from app.database import engine
from domain.models.base import Base
from api.v1.routes import auth, health

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Startup
    logger.info("application_startup", app=settings.APP_NAME, version=settings.APP_VERSION)
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("database_initialized")
    
    yield
    
    # Shutdown
    logger.info("application_shutdown")
    await engine.dispose()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    # Configure logging
    configure_logging()
    
    # Create app
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Enterprise Purple Team Validation & Detection Coverage Platform",
        lifespan=lifespan,
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Trusted host middleware
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
    
    # Include routers
    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(health.router, prefix="/api/v1")
    
    @app.get("/")
    async def root() -> dict:
        """Root endpoint."""
        return {
            "application": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "status": "running",
        }
    
    return app


# Create the FastAPI application
app = create_app()
