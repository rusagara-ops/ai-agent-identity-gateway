"""
Authentication API routes.

Endpoints:
- POST /auth/register - Register a new agent
- POST /auth/login - Get access token
- GET /auth/me - Get current agent info (protected)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.database.models import Agent, get_db
from app.auth.schemas import AgentCreate, AgentResponse, LoginRequest, Token
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.dependencies import get_current_agent

# Create router with /auth prefix
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def register_agent(agent_data: AgentCreate, db: Session = Depends(get_db)):
    """
    Register a new AI agent.

    This endpoint:
    1. Checks if agent name is available
    2. Hashes the password (NEVER store plain text!)
    3. Creates agent in database
    4. Returns agent info (without password)

    Args:
        agent_data: Agent registration data
        db: Database session

    Returns:
        AgentResponse: Created agent information

    Raises:
        HTTPException: 400 if agent name already exists
    """
    # Check if agent name already exists
    existing_agent = db.query(Agent).filter(Agent.name == agent_data.name).first()
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Agent with name '{agent_data.name}' already exists"
        )

    # Create new agent
    new_agent = Agent(
        name=agent_data.name,
        hashed_password=hash_password(agent_data.password),
        scopes=agent_data.scopes,
        description=agent_data.description
    )

    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    return new_agent


@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate an agent and return JWT access token.

    This is how agents "log in":
    1. Find agent by name
    2. Verify password
    3. Generate JWT token
    4. Return token

    The agent then uses this token in subsequent requests:
    Authorization: Bearer <token>

    Args:
        login_data: Login credentials
        db: Database session

    Returns:
        Token: JWT access token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Find agent by name
    agent = db.query(Agent).filter(Agent.name == login_data.name).first()

    # Verify agent exists and password is correct
    if not agent or not verify_password(login_data.password, agent.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect agent name or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if agent is active
    if not agent.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent has been deactivated"
        )

    # Update last login timestamp
    agent.last_login = datetime.utcnow()
    db.commit()

    # Create access token
    access_token = create_access_token(
        data={"sub": agent.id, "scopes": agent.scopes}
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=AgentResponse)
async def get_current_agent_info(current_agent: Agent = Depends(get_current_agent)):
    """
    Get information about the currently authenticated agent.

    This is a PROTECTED endpoint - requires valid JWT token.

    Usage:
        curl -H "Authorization: Bearer <your_token>" http://localhost:8001/auth/me

    Args:
        current_agent: Injected by get_current_agent dependency

    Returns:
        AgentResponse: Current agent information
    """
    return current_agent


@router.post("/revoke/{agent_id}", status_code=status.HTTP_200_OK)
async def revoke_agent(
    agent_id: str,
    current_agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db)
):
    """
    Deactivate an agent (revoke access).

    This is a PROTECTED endpoint - requires authentication.
    In production, you'd check if current_agent has "admin" scope.

    Args:
        agent_id: ID of agent to revoke
        current_agent: Currently authenticated agent
        db: Database session

    Returns:
        dict: Success message

    Raises:
        HTTPException: 404 if agent not found
    """
    agent = db.query(Agent).filter(Agent.id == agent_id).first()

    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with ID '{agent_id}' not found"
        )

    agent.is_active = False
    db.commit()

    return {"message": f"Agent '{agent.name}' has been revoked"}
