from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class User(Base):
    """User model for authentication and authorization.
    
    Attributes:
        id: Primary key, auto-incremented integer
        username: Unique username for login
        password_hash: Hashed password for security
        email: Optional email address
        full_name: Optional full name of the user
        is_active: Boolean flag for account status
        is_admin: Boolean flag for admin privileges
        created_at: Timestamp of account creation
        updated_at: Timestamp of last update
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=True, index=True)
    full_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', is_active={self.is_active})>"
