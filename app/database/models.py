"""
Database models for the AI Agent Identity Gateway.

Using SQLAlchemy ORM (Object Relational Mapper) to interact with the database.
ORM lets us use Python classes instead of raw SQL queries.
"""

from sqlalchemy import Column, String, DateTime, Boolean, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import uuid

from app.config import settings

# Create the database engine
# Engine manages connections to the database
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

# SessionLocal is a factory for creating database sessions
# A session is like a "workspace" for database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models
Base = declarative_base()


class Agent(Base):
    """
    Agent model - represents an AI agent in the system.

    Each agent has:
    - Unique ID (primary key)
    - Name (identifier, like a username)
    - Hashed password (NEVER store plain text!)
    - Scopes/permissions (what they can do)
    - Active status (can be deactivated)
    - Timestamps (when created, last login)
    """
    __tablename__ = "agents"

    # Primary key - unique identifier for each agent
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Agent name - must be unique (like a username)
    name = Column(String, unique=True, index=True, nullable=False)

    # Hashed password - stored securely using bcrypt
    hashed_password = Column(String, nullable=False)

    # Scopes define what this agent can do
    # Stored as JSON: ["read", "write", "execute"]
    scopes = Column(JSON, default=list)

    # Is this agent active? Can be deactivated without deletion
    is_active = Column(Boolean, default=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Optional: Description of what this agent does
    description = Column(String, nullable=True)

    def __repr__(self):
        """String representation for debugging."""
        return f"<Agent(id={self.id}, name={self.name}, active={self.is_active})>"


# Create all tables in the database
# This runs CREATE TABLE statements
Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency function that provides a database session.

    This is used in FastAPI endpoints like:
    def my_endpoint(db: Session = Depends(get_db)):
        ...

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
