"""
Application configuration settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "TreasuryIQ"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENCRYPTION_KEY: str = "your-32-character-encryption-key"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://your-domain.com"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://treasuryiq:password@localhost:5432/treasuryiq"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Tableau Integration
    TABLEAU_SERVER_URL: Optional[str] = None
    TABLEAU_USERNAME: Optional[str] = None
    TABLEAU_PASSWORD: Optional[str] = None
    TABLEAU_SITE_ID: Optional[str] = None
    TABLEAU_API_VERSION: str = "3.19"
    
    # AI and External APIs
    AGENTFORCE_API_KEY: Optional[str] = None
    AGENTFORCE_BASE_URL: str = "https://api.salesforce.com/agentforce/v1"
    FEDERAL_RESERVE_API_KEY: Optional[str] = None
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    EXCHANGE_RATES_API_KEY: Optional[str] = None
    
    # Notification Services
    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_SIGNING_SECRET: Optional[str] = None
    SENDGRID_API_KEY: Optional[str] = None
    FROM_EMAIL: str = "noreply@treasuryiq.com"
    
    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_METRICS: bool = True
    
    # Demo Configuration
    DEMO_MODE: bool = True
    DEMO_COMPANY_NAME: str = "GlobalTech Industries"
    DEMO_TREASURY_SIZE: int = 500_000_000  # $500M
    
    # Risk Management
    DEFAULT_VAR_CONFIDENCE: float = 0.95
    DEFAULT_VAR_HORIZON: int = 1  # days
    RISK_CALCULATION_TIMEOUT: int = 30  # seconds
    
    # Performance
    MAX_CONCURRENT_REQUESTS: int = 100
    REQUEST_TIMEOUT: int = 30
    CACHE_DEFAULT_TTL: int = 300  # 5 minutes
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()


def get_database_url() -> str:
    """Get database URL with proper formatting"""
    return settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


def get_redis_url() -> str:
    """Get Redis URL"""
    return settings.REDIS_URL


def is_development() -> bool:
    """Check if running in development mode"""
    return settings.ENVIRONMENT.lower() == "development"


def is_production() -> bool:
    """Check if running in production mode"""
    return settings.ENVIRONMENT.lower() == "production"