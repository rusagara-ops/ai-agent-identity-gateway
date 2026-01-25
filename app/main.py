"""
Main FastAPI application entry point.

This file creates and configures the FastAPI app with:
- Health check endpoints
- CORS middleware for frontend access
- Global exception handling
- API documentation
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.config import settings

# Set up logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create the FastAPI application instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A production-grade backend for AI agent authentication, authorization, and RAG",
    docs_url="/docs",  # Swagger UI at http://localhost:8000/docs
    redoc_url="/redoc",  # ReDoc at http://localhost:8000/redoc
)


# Add CORS middleware
# CORS (Cross-Origin Resource Sharing) allows your API to be accessed from web browsers
# This is needed if you build a frontend that runs on a different port/domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Which origins can access the API
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


@app.on_event("startup")
async def startup_event():
    """
    Runs when the application starts.

    Good place to:
    - Initialize database connections
    - Load ML models
    - Set up background tasks
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the application shuts down.

    Good place to:
    - Close database connections
    - Save state
    - Clean up resources
    """
    logger.info("Shutting down gracefully...")


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - basic API information.

    Returns:
        dict: Basic API metadata
    """
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "environment": settings.environment
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.

    In production, this would check:
    - Database connectivity
    - External service availability
    - Memory/CPU usage

    Returns:
        dict: Health status information
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version
    }


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness check - is the service ready to accept traffic?

    Different from health check:
    - Health: Is the service alive?
    - Ready: Can it handle requests?

    Returns:
        dict: Readiness status
    """
    # In production, we'd check:
    # - Database is connected
    # - Required services are available
    # - ML models are loaded

    return {
        "ready": True,
        "checks": {
            "database": "not_implemented",
            "vector_store": "not_implemented"
        }
    }


# ============================================================================
# FUTURE ROUTE INCLUDES
# ============================================================================

# As we build more features, we'll add routes here like:
# app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
# app.include_router(agents_router, prefix="/agents", tags=["Agent Management"])
# app.include_router(rag_router, prefix="/rag", tags=["RAG Pipeline"])


if __name__ == "__main__":
    """
    This allows running the file directly with: python app/main.py
    But we'll usually use: uvicorn app.main:app --reload
    """
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,  # Auto-reload on code changes in debug mode
        log_level=settings.log_level.lower()
    )
