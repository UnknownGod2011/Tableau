#!/usr/bin/env python3
"""
Demo script for market data ingestion pipeline
This script demonstrates the data ingestion functionality without requiring external dependencies
"""

import asyncio
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any

# Mock the external dependencies for demo purposes
class MockHttpxClient:
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, *args):
        pass
    
    async def get(self, url, params=None):
        # Mock response for FRED API
        if "stlouisfed.org" in url:
            return MockResponse({
                "observations": [{
                    "date": "2024-01-07",
                    "value": "5.25"
                }]
            })
        # Mock response for exchange rates
        elif "exchangeratesapi.io" in url:
            return MockResponse({
                "success": True,
                "timestamp": int(datetime.now().timestamp()),
                "rates": {
                    "EUR": 0.85,
                    "GBP": 0.78,
                    "JPY": 150.0
                }
            })
        else:
            raise Exception("Unknown API")

class MockResponse:
    def __init__(self, data):
        self._data = data
        self.status_code = 200
    
    def json(self):
        return self._data
    
    def raise_for_status(self):
        pass

# Mock httpx module
import sys
from unittest.mock import MagicMock
sys.modules['httpx'] = MagicMock()
sys.modules['httpx'].AsyncClient = MockHttpxClient

# Mock structlog
sys.modules['structlog'] = MagicMock()
sys.modules['structlog'].get_logger.return_value = MagicMock()

# Mock numpy for data quality service
sys.modules['numpy'] = MagicMock()
import numpy as np
np.mean = lambda x: sum(x) / len(x)
np.std = lambda x: (sum((i - np.mean(x))**2 for i in x) / len(x))**0.5
np.diff = lambda x: [x[i+1] - x[i] for i in range(len(x)-1)]
np.log = lambda x: [__import__('math').log(i) if hasattr(x, '__iter__') else __import__('math').log(x) for i in x] if hasattr(x, '__iter__') else __import__('math').log(x)

# Mock settings
class MockSettings:
    FEDERAL_RESERVE_API_KEY = None
    EXCHANGE_RATES_API_KEY = None

sys.modules['app.core.config'] = MagicMock()
sys.modules['app.core.config'].settings = MockSettings()

# Now import our services
from app.services.data_quality import DataQualityService
from app.services.market_data import MarketDataIngestionPipeline


async def demo_data_quality_validation():
    """Demonstrate data quality validation"""
    print("=== Data Quality Validation Demo ===")
    
    data_quality = DataQualityService()
    
    # Test with good data
    good_data = {
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
                "yield_rate": 4.75,
                "date": datetime.now().isoformat()
            },
            {
                "maturity": "10Y",
                "yield_rate": 4.25,
                "date": datetime.now().isoformat()
            }
        ]
    }
    
    print("Testing good data...")
    quality_report = await data_quality.validate_market_data(good_data, "demo_good_data")
    print(f"Quality Score: {quality_report.quality_score}")
    print(f"Passed Validation: {quality_report.passed_validation}")
    print(f"Issues Found: {len(quality_report.issues)}")
    
    # Test with bad data
    bad_data = {
        "interest_rates": {
            "fed_funds": {
                "rate": 50.0,  # Unrealistic rate
                "date": "invalid-date",  # Invalid date
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
    
    print("\nTesting bad data...")
    quality_report = await data_quality.validate_market_data(bad_data, "demo_bad_data")
    print(f"Quality Score: {quality_report.quality_score}")
    print(f"Passed Validation: {quality_report.passed_validation}")
    print(f"Issues Found: {len(quality_report.issues)}")
    
    for issue in quality_report.issues[:3]:  # Show first 3 issues
        print(f"  - {issue.severity.value}: {issue.message}")


async def demo_market_data_ingestion():
    """Demonstrate market data ingestion pipeline"""
    print("\n=== Market Data Ingestion Demo ===")
    
    pipeline = MarketDataIngestionPipeline()
    
    # Test Federal Reserve rates (demo mode)
    print("Fetching Federal Reserve rates...")
    rates = await pipeline.get_federal_reserve_rates()
    print(f"Retrieved {len(rates)} interest rates:")
    for name, rate in list(rates.items())[:3]:  # Show first 3
        print(f"  {name}: {rate.rate}% (source: {rate.source})")
    
    # Test exchange rates (demo mode)
    print("\nFetching exchange rates...")
    fx_rates = await pipeline.get_exchange_rates()
    print(f"Retrieved {len(fx_rates)} exchange rates:")
    for currency, rate in list(fx_rates.items())[:3]:  # Show first 3
        print(f"  USD/{currency}: {rate.rate} (source: {rate.source})")
    
    # Test yield curve
    print("\nFetching Treasury yield curve...")
    yield_curve = await pipeline.get_treasury_yield_curve()
    print(f"Retrieved {len(yield_curve)} yield points:")
    for yc in yield_curve[:4]:  # Show first 4
        print(f"  {yc.maturity}: {yc.yield_rate}%")
    
    # Test full market summary
    print("\nGenerating market summary...")
    summary = await pipeline.get_market_summary()
    print(f"Market summary generated at: {summary['timestamp']}")
    print(f"Yield curve slope (10Y-2Y): {summary['market_indicators']['yield_curve_slope']:.2f}%")
    print(f"Risk sentiment: {summary['market_indicators']['risk_sentiment']}")


async def demo_full_ingestion_pipeline():
    """Demonstrate the complete ingestion pipeline with quality validation"""
    print("\n=== Full Ingestion Pipeline Demo ===")
    
    pipeline = MarketDataIngestionPipeline()
    
    print("Running complete data ingestion pipeline...")
    result = await pipeline.ingest_market_data()
    
    print(f"Ingestion Result:")
    print(f"  Success: {result.success}")
    print(f"  Records Processed: {result.records_processed}")
    print(f"  Source: {result.source}")
    print(f"  Timestamp: {result.timestamp}")
    
    if result.quality_report:
        print(f"  Quality Score: {result.quality_report.quality_score}")
        print(f"  Validation Passed: {result.quality_report.passed_validation}")
        print(f"  Total Issues: {len(result.quality_report.issues)}")
        print(f"  Critical Issues: {len(result.quality_report.critical_issues)}")
    
    if result.errors:
        print(f"  Errors: {result.errors}")


async def demo_circuit_breaker():
    """Demonstrate circuit breaker functionality"""
    print("\n=== Circuit Breaker Demo ===")
    
    pipeline = MarketDataIngestionPipeline()
    
    # Test circuit breaker
    service_name = "demo_service"
    print(f"Circuit breaker for {service_name} is open: {pipeline._is_circuit_open(service_name)}")
    
    # Record some failures
    print("Recording 3 failures...")
    for i in range(3):
        pipeline._record_circuit_breaker_failure(service_name)
        print(f"  Failure {i+1} recorded")
    
    print(f"Circuit breaker is now open: {pipeline._is_circuit_open(service_name)}")
    
    # Reset circuit breaker
    print("Resetting circuit breaker...")
    pipeline._reset_circuit_breaker(service_name)
    print(f"Circuit breaker is open: {pipeline._is_circuit_open(service_name)}")


async def main():
    """Run all demos"""
    print("TreasuryIQ Market Data Ingestion Pipeline Demo")
    print("=" * 50)
    
    try:
        await demo_data_quality_validation()
        await demo_market_data_ingestion()
        await demo_full_ingestion_pipeline()
        await demo_circuit_breaker()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✓ Data quality validation with scoring")
        print("✓ Multi-source market data ingestion")
        print("✓ Circuit breaker pattern for resilience")
        print("✓ Anomaly detection capabilities")
        print("✓ Comprehensive error handling")
        print("✓ Real-time data processing pipeline")
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())