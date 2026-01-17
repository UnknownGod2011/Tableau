"""
Test configuration and fixtures for TreasuryIQ backend tests.
"""
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from app.models import *  # Import all models to ensure they're registered


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def analytics_engine(db_session):
    """Create analytics engine for testing."""
    from app.services.analytics import AnalyticsEngine
    return AnalyticsEngine(db_session)


@pytest.fixture(scope="function")
def risk_engine(db_session):
    """Create risk engine for testing."""
    from app.services.risk import RiskEngine
    return RiskEngine(db_session)


@pytest.fixture(scope="function")
def pipeline():
    """Create market data ingestion pipeline for testing."""
    from app.services.market_data import MarketDataIngestionPipeline
    return MarketDataIngestionPipeline()


@pytest.fixture(scope="function")
def data_quality_service():
    """Create data quality service for testing."""
    from app.services.data_quality import DataQualityService
    return DataQualityService()


# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)