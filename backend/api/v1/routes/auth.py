"""
Authentication routes.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from domain.services.user_service import UserService
from api.v1.schemas.auth import (
    LoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    UserCreateRequest,
)
from utils.exceptions import AppException, AuthenticationError
from utils.security import decode_token
from app.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """
    User login endpoint.
    
    Returns access and refresh tokens.
    """
    try:
        service = UserService(db)
        tokens = await service.login(request.username, request.password)
        return TokenResponse(**tokens)
    except AuthenticationError as e:
        raise HTTPException(status_code=401, detail=e.message)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("login_error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/register", response_model=UserResponse)
async def register(request: UserCreateRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
    """
    User registration endpoint.
    
    Creates a new user with READ_ONLY role.
    """
    try:
        service = UserService(db)
        user = await service.register(
            username=request.username,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
        )
        return UserResponse.model_validate(user)
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("register_error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """
    Refresh access token using refresh token.
    """
    try:
        payload = decode_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise AuthenticationError("Invalid token type")
        
        user_id = int(payload.get("sub"))
        service = UserService(db)
        user = await service.get_user_by_id(user_id)
        
        if not user.is_active:
            raise AuthenticationError("User is inactive")
        
        # Create new access token
        from utils.security import create_access_token
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role.value}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,
            token_type="bearer",
            expires_in=30 * 60,
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("refresh_error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")
