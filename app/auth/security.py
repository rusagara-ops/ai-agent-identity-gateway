"""
Security utilities for password hashing and JWT token management.

Key concepts:
- Password hashing: One-way encryption (can't reverse it)
- JWT tokens: Signed JSON that proves identity
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context using bcrypt
# bcrypt is a slow hashing algorithm (intentionally!) to prevent brute-force attacks
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Example:
        "mypassword123" -> "$2b$12$abc...xyz"

    Args:
        password: Plain text password

    Returns:
        str: Hashed password (safe to store in database)
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Password user provided
        hashed_password: Hash stored in database

    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    JWT Structure:
    {
        "sub": "agent_id",      # Subject (who this token is for)
        "scopes": ["read"],     # Permissions
        "exp": 1234567890       # Expiration timestamp
    }

    Args:
        data: Data to encode in the token (agent_id, scopes, etc.)
        expires_delta: How long until token expires

    Returns:
        str: Encoded JWT token
    """
    to_encode = data.copy()

    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})

    # Create and sign the JWT
    # This uses the SECRET_KEY from .env to sign the token
    # Anyone with the secret can verify the token is authentic
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.

    Args:
        token: JWT token string

    Returns:
        dict: Decoded token data if valid, None if invalid
    """
    try:
        # Decode and verify the signature
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
