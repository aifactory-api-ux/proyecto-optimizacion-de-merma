"""
Authentication Schemas

Pydantic models for authentication requests and responses.
Implements JWT-based authentication with token generation.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class UserLoginRequest(BaseModel):
    """Request model for user login.
    
    Attributes:
        username: Unique identifier for the user account
        password: User's password for authentication
    """
    username: str = Field(
        ..., 
        min_length=1, 
        max_length=100,
        description="Username for authentication",
        examples=["admin", "manager_tienda1"]
    )
    password: str = Field(
        ..., 
        min_length=1,
        description="User password",
        examples=["secure_password_123"]
    )

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }


class UserLoginResponse(BaseModel):
    """Response model for successful user login.
    
    Attributes:
        access_token: JWT token for subsequent API requests
        token_type: Type of token (typically 'bearer')
    """
    access_token: str = Field(
        ...,
        description="JWT access token for authenticated requests"
    )
    token_type: str = Field(
        default="bearer",
        description="Token type identifier"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Internal model for token payload data.
    
    Attributes:
        user_id: Unique identifier of the user
        username: Username of the authenticated user
        is_admin: Whether the user has admin privileges
    """
    user_id: int = Field(..., description="User ID from database")
    username: str = Field(..., description="Username from database")
    is_admin: bool = Field(default=False, description="Admin flag")


class AuthSettings(BaseSettings):
    """Authentication settings loaded from environment variables.
    
    Attributes:
        secret_key: Secret key for JWT token signing
        algorithm: Algorithm used for token signing
        access_token_expire_minutes: Token expiration time in minutes
    """
    secret_key: str = Field(
        ...,
        description="Secret key for JWT token generation"
    )
    algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        ge=1,
        le=1440,
        description="Token expiration in minutes"
    )

    class Config:
        env_prefix = "AUTH_"
        case_sensitive = False
