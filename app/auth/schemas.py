"""
Pydantic schemas for request/response validation.

Schemas define the shape of data for API requests and responses.
Pydantic automatically validates data types and required fields.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class AgentCreate(BaseModel):
    """
    Schema for creating a new agent.

    This is what the client sends when registering an agent.
    """
    name: str = Field(..., min_length=3, max_length=50, description="Agent name (unique identifier)")
    password: str = Field(..., min_length=8, description="Agent password (min 8 characters)")
    scopes: List[str] = Field(default=["read"], description="Permissions for this agent")
    description: Optional[str] = Field(None, description="Optional description of agent's purpose")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "data-analyzer-agent",
                "password": "secure_password_123",
                "scopes": ["read", "write"],
                "description": "Agent for analyzing customer data"
            }
        }


class AgentResponse(BaseModel):
    """
    Schema for agent data in responses.

    NOTE: We NEVER return the hashed_password in responses!
    """
    id: str
    name: str
    scopes: List[str]
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]
    description: Optional[str]

    class Config:
        from_attributes = True  # Allows creating from SQLAlchemy models


class Token(BaseModel):
    """
    Schema for JWT token response.

    This is what's returned when an agent logs in.
    """
    access_token: str
    token_type: str = "bearer"

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """
    Schema for decoded token data.

    This represents what's inside a JWT token.
    """
    agent_id: Optional[str] = None
    scopes: List[str] = []


class LoginRequest(BaseModel):
    """
    Schema for login requests.

    OAuth2 standard uses 'username' and 'password' fields,
    but we'll use 'name' for consistency with agent registration.
    """
    name: str = Field(..., description="Agent name")
    password: str = Field(..., description="Agent password")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "data-analyzer-agent",
                "password": "secure_password_123"
            }
        }
