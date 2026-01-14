"""
Tests for market data ingestion pipeline
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime
from decimal import Decimal

from app.services.market_data import MarketDataIngestionPipeline, DataIngestionResult
from app.services.data_quality import DataQualityReport, DataQualityIssue, DataQualitySeverity, DataQualityIssueType


@pytest.fixture
def market_data_service():
    """Create market data service instance for testing"""
    return MarketDataIngestionPipeline()


@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return {
        "timestamp": datetime.now().isoformat(),
        "interest_rates": {
            "fed_funds": {
                "rate": 5.25,
                "date": datetime.now().isoformat(),
                "source": "FRED"
            },
            "treasury_10y": {
                "rate": 4.25,
                "date": datetime.now().isoformat(),
                "source": "FRED"
            }
        },
        "exchange_rates": {
            "EUR": {
                "rate": 0.85,
                "timestamp": datetime.now().isoformat(),
                "source": "ExchangeRatesAPI",
                "base_currency": "USD",
                "target_currency": "EUR"
            }
        },
        "yield_curve": [
            {
                "maturity": "2Y",
                "yield": 4.75,
                "date": datetime.now().isoformat()
            },
            {
                "maturity": "10Y", 
                "yield": 4.25,
                "date": datetime.now().isoformat()
            }
        ]
    }


@pytest.mark.asyncio
async def test_data_quality_validation_success(market_data_service, sample_market_data):
    """Test successful data quality validation"""
    # Test data quality validation
    quality_report = await market_data_service.data_quality.validate_market_data(
        sample_market_data, 
        "test_source"
    )
    
    assert quality_report is not None
    assert quality_report.source == "test_source"
    assert quality_report.total_records > 0
    assert quality_report.quality_score >= 0
    assert isinstance(quality_report.passed_validation, bool)


@pytest.mark.asyncio
async def test_data_quality_validation_with_issues(market_data_service):
    """Test data quality validation with issues"""
    # Create data with quality issues
    bad_data = {
        "interest_rates": {
            "fed_funds": {
                "rate": 50.0,  # Unrealistic rate
                "date": "invalid-date",  # Invalid date format
                "source": "FRED"
            }
        },
        "exchange_rates": {
            "EUR": {
                "rate": -1.0,  # Invalid negative rate
                "timestamp": datetime.now().isoformat(),
                "source": "ExchangeRatesAPI"
                # Missing required fields
            }
        }
    }
    
    quality_report = await market_data_service.data_quality.validate_market_data(
        bad_data, 
        "test_bad_data"
    )
    
    assert quality_report is not None
    assert len(quality_report.issues) > 0
    assert quality_report.quality_score < 100
    assert not quality_report.passed_validation


@pytest.mark.asyncio
async def test_circuit_breaker_functionality(market_data_service):
    """Test circuit breaker pattern"""
    # Initially circuit should be closed
    assert not market_data_service._is_circuit_open("test_service")
    
    # Record failures
    for _ in range(3):
        market_data_service._record_circuit_breaker_failure("test_service")
    
    # Circuit should now be open
    assert market_data_service._is_circuit_open("test_service")
    
    # Reset circuit breaker
    market_data_service._reset_circuit_breaker("test_service")
    assert not market_data_service._is_circuit_open("test_service")


@pytest.mark.asyncio
async def test_federal_reserve_rates_demo_mode(market_data_service):
    """Test Federal Reserve rates in demo mode"""
    # This should work even without API keys (demo mode)
    rates = await market_data_service.get_federal_reserve_rates()
    
    assert isinstance(rates, dict)
    assert len(rates) > 0
    
    # Check that we have expected rate types
    expected_rates = ["fed_funds", "treasury_10y", "treasury_2y"]
    for rate_name in expected_rates:
        if rate_name in rates:
            rate = rates[rate_name]
            assert hasattr(rate, 'rate')
            assert hasattr(rate, 'date')
            assert hasattr(rate, 'source')
            assert isinstance(rate.rate, Decimal)


@pytest.mark.asyncio
async def test_exchange_rates_demo_mode(market_data_service):
    """Test exchange rates in demo mode"""
    rates = await market_data_service.get_exchange_rates()
    
    assert isinstance(rates, dict)
    
    # Check structure of exchange rates
    for currency, rate in rates.items():
        assert hasattr(rate, 'rate')
        assert hasattr(rate, 'timestamp')
        assert hasattr(rate, 'source')
        assert hasattr(rate, 'base_currency')
        assert hasattr(rate, 'target_currency')
        assert isinstance(rate.rate, Decimal)


@pytest.mark.asyncio
async def test_treasury_yield_curve(market_data_service):
    """Test Treasury yield curve functionality"""
    yield_curve = await market_data_service.get_treasury_yield_curve()
    
    assert isinstance(yield_curve, list)
    
    # Check yield curve structure
    for yield_point in yield_curve:
        assert hasattr(yield_point, 'maturity')
        assert hasattr(yield_point, 'yield_rate')
        assert hasattr(yield_point, 'date')
        assert isinstance(yield_point.yield_rate, Decimal)


@pytest.mark.asyncio
async def test_market_summary(market_data_service):
    """Test comprehensive market summary"""
    summary = await market_data_service.get_market_summary()
    
    assert isinstance(summary, dict)
    assert "timestamp" in summary
    assert "interest_rates" in summary
    assert "exchange_rates" in summary
    assert "yield_curve" in summary
    assert "market_indicators" in summary
    
    # Check market indicators
    indicators = summary["market_indicators"]
    assert "yield_curve_slope" in indicators
    assert "risk_sentiment" in indicators
    assert "volatility_index" in indicators


@pytest.mark.asyncio
async def test_anomaly_detection(market_data_service):
    """Test anomaly detection functionality"""
    # Create historical data with some variation
    historical_data = []
    for i in range(10):
        historical_data.append({
            "interest_rates": {
                "fed_funds": {"rate": 5.0 + (i % 3) * 0.1},  # Slight variation: 5.0, 5.1, 5.2
                "treasury_10y": {"rate": 4.0 + (i % 2) * 0.05}  # Slight variation: 4.0, 4.05
            }
        })
    
    # Current data with anomaly
    current_data = {
        "interest_rates": {
            "fed_funds": {"rate": 15.0},  # Anomalous rate (much higher than 5.0-5.2 range)
            "treasury_10y": {"rate": 4.1}
        }
    }
    
    anomalies = await market_data_service.data_quality.detect_anomalies(
        current_data, 
        historical_data
    )
    
    # Should detect the anomalous fed funds rate
    assert len(anomalies) > 0
    fed_funds_anomaly = next(
        (a for a in anomalies if "fed_funds" in a.field_name), 
        None
    )
    assert fed_funds_anomaly is not None
    assert fed_funds_anomaly.issue_type == DataQualityIssueType.OUTLIER


@pytest.mark.asyncio 
async def test_backup_data_sources(market_data_service):
    """Test backup data source functionality"""
    # Test backup data fetch (should handle gracefully even if APIs fail)
    backup_data = await market_data_service._fetch_backup_data()
    
    # Should either return data or None (if backup sources fail)
    assert backup_data is None or isinstance(backup_data, dict)


@pytest.mark.asyncio
async def test_full_ingestion_pipeline(market_data_service, sample_market_data):
    """Test the complete data ingestion pipeline"""
    # Mock the data fetching to return our sample data
    with patch.object(market_data_service, '_fetch_all_market_data', 
                     return_value=sample_market_data):
        with patch.object(market_data_service, '_store_market_data', 
                         return_value=None):
            
            result = await market_data_service.ingest_market_data()
            
            assert isinstance(result, DataIngestionResult)
            assert result.source == "market_data_pipeline"
            assert result.timestamp is not None
            assert result.quality_report is not None
            
            # Should succeed with good sample data
            assert result.success
            assert result.records_processed > 0


def test_yield_curve_slope_calculation(market_data_service):
    """Test yield curve slope calculation"""
    from app.services.market_data import TreasuryYield
    
    yield_curve = [
        TreasuryYield(maturity="2Y", yield_rate=Decimal("4.0"), date=datetime.now()),
        TreasuryYield(maturity="10Y", yield_rate=Decimal("4.5"), date=datetime.now())
    ]
    
    slope = market_data_service._calculate_yield_curve_slope(yield_curve)
    assert slope == 0.5  # 4.5 - 4.0


def test_risk_sentiment_assessment(market_data_service):
    """Test risk sentiment assessment"""
    # Test different rate scenarios
    high_rates = {"fed_funds": {"rate": 6.0}}
    low_rates = {"fed_funds": {"rate": 1.0}}
    medium_rates = {"fed_funds": {"rate": 3.5}}
    
    assert market_data_service._assess_risk_sentiment(high_rates, {}) == "risk_off"
    assert market_data_service._assess_risk_sentiment(low_rates, {}) == "risk_on"
    assert market_data_service._assess_risk_sentiment(medium_rates, {}) == "neutral"