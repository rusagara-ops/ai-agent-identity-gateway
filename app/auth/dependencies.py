"""
Authentication dependencies for protecting API routes.

Dependencies are functions that run before route handlers.
They can verify tokens, check permissions, etc.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from app.database.models import Agent, get_db
from app.auth.security import decode_access_token
from app.auth.schemas import TokenData

# HTTP Bearer token security scheme
# This tells FastAPI to look for "Authorization: Bearer <token>" header
security = HTTPBearer()


async def get_current_agent(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Agent:
    """
    Dependency that extracts and validates the JWT token from the request.

    This runs automatically when you use: current_agent: Agent = Depends(get_current_agent)

    Steps:
    1. Extract token from Authorization header
    2. Decode and verify the token
    3. Look up the agent in the database
    4. Return the agent if valid, raise error if not

    Args:
        credentials: HTTP Bearer credentials (contains the token)
        db: Database session

    Returns:
        Agent: The authenticated agent

    Raises:
        HTTPException: 401 if token is invalid or agent not found
    """
    # Extract the token from credentials
    token = credentials.credentials

    # Decode the token
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get agent_id from token
    agent_id: str = payload.get("sub")
    if agent_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Look up agent in database
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Agent not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent has been deactivated"
        )

    return agent


def require_scopes(required_scopes: List[str]):
    """
    Factory function that creates a dependency to check for specific scopes/permissions.

    Usage:
        @app.get("/admin", dependencies=[Depends(require_scopes(["admin"]))])
        def admin_endpoint():
            ...

    Args:
        required_scopes: List of scopes that the agent must have

    Returns:
        Dependency function that validates scopes
    """
    async def check_scopes(agent: Agent = Depends(get_current_agent)):
        """Check if agent has required scopes."""
        agent_scopes = agent.scopes or []

        # Check if agent has all required scopes
        for scope in required_scopes:
            if scope not in agent_scopes:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required scope: {scope}"
                )

        return agent

    return check_scopes
