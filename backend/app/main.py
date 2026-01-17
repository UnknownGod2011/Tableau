"""
TreasuryIQ - AI-Powered Corporate Treasury Management
Main FastAPI application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.api import api_router
from app.core.database import engine, Base
from app.core.redis import redis_client

# Setup structured logging
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting TreasuryIQ application", version="1.0.0")
    
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Test Redis connection
    try:
        await redis_client.ping()
        logger.info("Redis connection established")
    except Exception as e:
        logger.error("Redis connection failed", error=str(e))
    
    yield
    
    # Shutdown
    logger.info("Shutting down TreasuryIQ application")
    await redis_client.close()


# Create FastAPI application
app = FastAPI(
    title="TreasuryIQ API",
    description="AI-Powered Corporate Treasury Management Platform",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS,
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        async with engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        # Check Redis connection
        await redis_client.ping()
        
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "service": "TreasuryIQ API",
                "version": "1.0.0",
                "environment": settings.ENVIRONMENT,
            }
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TreasuryIQ - AI-Powered Corporate Treasury Management",
        "version": "1.0.0",
        "docs": "/docs" if settings.ENVIRONMENT == "development" else None,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.ENVIRONMENT == "development",
        log_config=None,  # Use our custom logging
    )