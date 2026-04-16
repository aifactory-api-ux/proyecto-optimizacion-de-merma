"""
Authentication API Module

Provides REST endpoints for user authentication and token management.
Implements JWT-based authentication for the waste optimization system.
"""

from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import authenticate_user, create_token_for_user
from app.db.session import get_db
from app.schemas.auth import UserLoginRequest, UserLoginResponse
from sqlalchemy.orm import Session

# Create router with prefix and tags
router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

# OAuth2 scheme for dependency injection
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post(
    "/login",
    response_model=UserLoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user and return JWT access token"
)
def login(
    user_credentials: UserLoginRequest,
    db: Annotated[Session, Depends(get_db)]
) -> UserLoginResponse:
    """
    Authenticate a user with username and password.
    
    Args:
        user_credentials: UserLoginRequest containing username and password
        db: Database session
    
    Returns:
        UserLoginResponse with access token and token type
    
    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Authenticate user using the security module
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token for authenticated user
    access_token_expires = timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    # Create token with user information
    access_token = create_token_for_user(
        user_id=user["id"],
        username=user["username"],
        is_admin=user.get("is_admin", False)
    )
    
    return UserLoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user["id"],
        username=user["username"],
        is_admin=user.get("is_admin", False)
    )
