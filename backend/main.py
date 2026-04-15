"""
FastAPI Application Entry Point

Main application module that initializes and configures the FastAPI application,
including middleware, routers, database connections, and caching.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.cache import get_cache_manager, init_cache, close_cache
from app.db.session import init_db, close_db
from shared.constants import (
    API_VERSION,
    API_TITLE,
    API_DESCRIPTION,
    HEALTH_MESSAGES,
)

# Configure logging
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events for the application,
    including database and cache initialization/cleanup.
    """
    # Startup
    logger.info("Starting application: %s v%s", settings.APP_NAME, settings.APP_VERSION)
    
    # Initialize database connection
    try:
        await init_db()
        logger.info("Database connection initialized")
    except Exception as e:
        logger.error("Failed to initialize database: %s", str(e))
        raise
    
    # Initialize cache connection
    try:
        cache_manager = get_cache_manager()
        if not cache_manager.is_connected:
            cache_manager.connect()
        logger.info("Cache connection initialized")
    except Exception as e:
        logger.warning("Failed to initialize cache: %s", str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    
    # Close cache connection
    try:
        close_cache()
        logger.info("Cache connection closed")
    except Exception as e:
        logger.warning("Error closing cache: %s", str(e))
    
    # Close database connection
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.warning("Error closing database: %s", str(e))


# Create FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring service status.
    
    Returns:
        dict: Health status of the service
    """
    cache_manager = get_cache_manager()
    db_status = "healthy"  # Simplified - in production would check actual DB connection
    cache_status = "healthy" if cache_manager.is_connected else "disconnected"
    
    overall_status = "healthy" if db_status == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "message": HEALTH_MESSAGES.get(overall_status, "Unknown status"),
        "checks": {
            "database": db_status,
            "cache": cache_status,
        },
    }


# Include API routers
# Note: These routers will be implemented in parallel items
# Import them lazily to avoid circular import issues
try:
    from app.api import auth, dashboard, alerts, waste, demand
    
    # Create API router with prefix
    api_router = APIRouter()
    
    # Auth router
    api_router.include_router(
        auth.router,
        prefix="/auth",
        tags=["Authentication"]
    )
    
    # Dashboard router
    api_router.include_router(
        dashboard.router,
        prefix="/dashboard",
        tags=["Dashboard"]
    )
    
    # Alerts router
    api_router.include_router(
        alerts.router,
        prefix="/alerts",
        tags=["Alerts"]
    )
    
    # Waste router
    api_router.include_router(
        waste.router,
        prefix="/waste",
        tags=["Waste"]
    )
    
    # Demand router
    api_router.include_router(
        demand.router,
        prefix="/demand",
        tags=["Demand"]
    )
    
    # Include API router with prefix
    app.include_router(
        api_router,
        prefix=settings.API_PREFIX,
    )
    
    logger.info("API routers registered successfully")
    
except ImportError as e:
    logger.warning("Some API routers not yet implemented: %s", str(e))


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint providing basic application information.
    
    Returns:
        dict: Basic application info and available endpoints
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": API_DESCRIPTION,
        "docs_url": f"{settings.API_PREFIX}/docs",
        "health_url": "/health",
        "api_endpoints": {
            "auth": f"{settings.API_PREFIX}/auth/login",
            "dashboard": f"{settings.API_PREFIX}/dashboard/metrics",
            "alerts": f"{settings.API_PREFIX}/alerts",
            "waste": f"{settings.API_PREFIX}/waste",
            "demand": f"{settings.API_PREFIX}/demand/prediction",
        },
    }


# Run validation check on startup
@app.on_event("startup")
async def validate_startup():
    """
    Validate required configuration on application startup.
    """
    # Validate critical environment variables
    missing_vars = []
    
    if not settings.POSTGRES_HOST:
        missing_vars.append("POSTGRES_HOST")
    if not settings.POSTGRES_USER:
        missing_vars.append("POSTGRES_USER")
    if not settings.POSTGRES_DB:
        missing_vars.append("POSTGRES_DB")
    if not settings.JWT_SECRET_KEY:
        missing_vars.append("JWT_SECRET_KEY")
    
    if missing_vars:
        error_msg = f"Missing required environment variables: {', '.join(missing_vars)}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    logger.info("Startup validation passed")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

