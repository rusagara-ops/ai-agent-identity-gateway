"""
Configuration management for the AI Agent Identity Gateway.

This module loads settings from environment variables using Pydantic Settings.
Pydantic validates the types and provides defaults, making configuration safe and predictable.
"""

from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic automatically:
    - Loads values from .env file
    - Validates types (str, int, bool, etc.)
    - Provides defaults if values aren't set
    - Raises errors for missing required fields
    """

    # Application Metadata
    app_name: str = "AI Agent Identity Gateway"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # API Server Settings
    api_host: str = "0.0.0.0"  # 0.0.0.0 means accessible from any network interface
    api_port: int = 8000

    # Security & Authentication
    secret_key: str  # Required - no default for security
    algorithm: str = "HS256"  # HMAC with SHA-256 for JWT signing
    access_token_expire_minutes: int = 30

    # Database
    database_url: str = "sqlite:///./identityrag.db"

    # OpenAI (for embeddings)
    openai_api_key: str = ""  # Optional for now

    # Vector Store
    vector_store_type: str = "faiss"
    faiss_index_path: str = "./data/faiss_index"

    # Observability
    log_level: str = "INFO"
    enable_tracing: bool = True
    otel_service_name: str = "agent-identity-gateway"

    # CORS (Cross-Origin Resource Sharing)
    cors_origins: str = '["http://localhost:3000"]'

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from JSON string to list."""
        try:
            return json.loads(self.cors_origins)
        except json.JSONDecodeError:
            return ["http://localhost:3000"]

    class Config:
        # Tell Pydantic to load from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"
        # Make field names case-insensitive
        case_sensitive = False


# Create a single instance to use throughout the app
# This is the Singleton pattern - one config object for the whole application
settings = Settings()
