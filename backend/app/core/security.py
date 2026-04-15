"""
Security Utilities

Implements authentication, password hashing, and JWT token utilities.
"""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.auth_service import authenticate_user as auth_service_authenticate_user
from app.services.auth_service import get_user_by_username
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[dict]:
    """Authenticate user using the authentication service."""
    user = get_user_by_username(db, username)
    if user and verify_password(password, user.password_hash) and user.is_active:
        return {"id": user.id, "username": user.username, "is_admin": getattr(user, "is_admin", False)}
    return None


def create_token_for_user(user_id: int, username: str, is_admin: bool = False) -> str:
    """Create a JWT token for the authenticated user."""
    to_encode = {
        "sub": str(user_id),
        "username": username,
        "is_admin": is_admin,
        "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT access token and return the payload."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_token_and_get_user_id(token: str) -> Optional[int]:
    """Verify JWT token and extract user ID."""
    payload = decode_access_token(token)
    if payload and "sub" in payload:
        try:
            return int(payload["sub"])
        except (ValueError, TypeError):
            return None
    return None
