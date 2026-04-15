"""
Authentication Service

Provides business logic for user authentication operations.
Implements password verification and user validation.
"""

import logging
from typing import Optional

from sqlalchemy.orm import Session

from app.core.security import verify_password
from app.models.user import User

logger = logging.getLogger(__name__)


def authenticate_user(
    db: Session,
    username: str,
    password: str
) -> Optional[dict]:
    """Authenticate a user with username and password.
    
    Args:
        db: Database session for querying user data
        username: The username to authenticate
        password: The plain text password to verify
    
    Returns:
        dict: A dictionary containing 'id', 'username', 'is_admin' if authentication
               successful, None if authentication fails
    """
    try:
        # Query user by username
        user = db.query(User).filter(User.username == username).first()
        
        if user is None:
            logger.debug(f"User not found: {username}")
            return None
        
        # Check if user account is active
        if not user.is_active:
            logger.debug(f"User account is inactive: {username}")
            return None
        
        # Verify password against stored hash
        if not verify_password(password, user.password_hash):
            logger.debug(f"Invalid password for user: {username}")
            return None
        
        # Authentication successful
        logger.info(f"User authenticated successfully: {username}")
        return {"id": user.id, "username": user.username, "is_admin": user.is_admin}
        
    except Exception as e:
        logger.error(f"Error authenticating user {username}: {str(e)}")
        return None


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Retrieve a user by username.
    
    Args:
        db: Database session for querying user data
        username: The username to search for
    
    Returns:
        Optional[User]: User object if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def validate_user_credentials(username: str, password: str) -> tuple[bool, str]:
    """Validate user credentials format.
    
    Args:
        username: The username to validate
        password: The password to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not username or len(username.strip()) == 0:
        return False, "Username is required"
    
    if not password or len(password.strip()) == 0:
        return False, "Password is required"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    
    if len(username) > 50:
        return False, "Username must not exceed 50 characters"
    
    return True, ""

