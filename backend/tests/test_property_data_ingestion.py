"""
Property-based tests for data ingestion pipeline
Feature: treasuryiq-corporate-ai

This module contains property-based tests that validate universal correctness properties
for the market data ingestion pipeline across all valid inputs.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, Any, List
from unittest.mock import AsyncMock, patch, MagicMock
import random
import string

# Import hypothesis for property-based testing
from hypothesis import given, strategies as st, settings, assume, example, HealthCheck
from hypothesis.strategies import composite

from app.services.market_data import MarketDataIngestionPipeline, DataIngestionResult
from app.services.data_quality import DataQualityService, DataQualityReport, DataQualityIssue, DataQualitySeverity


# Custom strategies for generating test data
@composite
def market_data_strategy(draw):
    """Generate realistic market data for property testing"""
    timestamp = draw(st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ))
    
    # Generate interest rates
    interest_rates = {}
    rate_names = ["fed_funds", "treasury_1y", "treasury_2y", "treasury_10y", "prime_rate"]
    for rate_name in draw(st.lists(st.sampled_from(rate_names), min_size=1, max_size=5, unique=True)):
        interest_rates[rate_name] = {
            "rate": draw(st.floats(min_value=-2.0, max_value=15.0)),
            "date": timestamp.isoformat(),
            "source": draw(st.sampled_from(["FRED", "DEMO", "BACKUP"]))
        }
    
    # Generate exchange rates
    exchange_rates = {}
    currencies = ["EUR", "GBP", "JPY", "CAD", "AUD", "CHF"]
    for currency in draw(st.lists(st.sampled_from(currencies), min_size=1, max_size=4, unique=True)):
        exchange_rates[currency] = {
            "rate": draw(st.floats(min_value=0.01, max_value=200.0)),
            "timestamp": timestamp.isoformat(),
            "source": draw(st.sampled_from(["ExchangeRatesAPI", "DEMO", "BACKUP"])),
            "base_currency": "USD",
            "target_currency": currency
        }
    
    return {
        "timestamp": timestamp.isoformat(),
        "interest_rates": interest_rates,
        "exchange_rates": exchange_rates
    }


@composite
def corrupted_market_data_strategy(draw):
    """Generate market data with various quality issues for testing"""
    base_data = draw(market_data_strategy())
    
    # Randomly corrupt some fields
    corruption_type = draw(st.sampled_from([
        "missing_fields", "invalid_values", "stale_data", "wrong_types"
    ]))
    
    if corruption_type == "missing_fields":
        # Remove required fields randomly
        for rate_name, rate_data in base_data["interest_rates"].items():
            if draw(st.booleans()):
                field_to_remove = draw(st.sampled_from(["rate", "date", "source"]))
                if field_to_remove in rate_data:
                    del rate_data[field_to_remove]
    
    elif corruption_type == "invalid_values":
        # Add invalid values
        for rate_name, rate_data in base_data["interest_rates"].items():
            if draw(st.booleans()):
                rate_data["rate"] = draw(st.floats(min_value=50.0, max_value=1000.0))  # Unrealistic rates
    
    elif corruption_type == "stale_data":
        # Make data very old
        old_date = datetime.now() - timedelta(days=draw(st.integers(min_value=30, max_value=365)))
        for rate_name, rate_data in base_data["interest_rates"].items():
            rate_data["date"] = old_date.isoformat()
    
    elif corruption_type == "wrong_types":
        # Use wrong data types
        for rate_name, rate_data in base_data["interest_rates"].items():
            if draw(st.booleans()):
                rate_data["rate"] = "invalid_string"
    
    return base_data


@composite
def historical_data_strategy(draw):
    """Generate historical market data for anomaly detection testing"""
    num_records = draw(st.integers(min_value=5, max_value=20))
    historical_data = []
    
    base_timestamp = datetime.now() - timedelta(days=num_records)
    
    for i in range(num_records):
        timestamp = base_timestamp + timedelta(days=i)
        
        # Generate consistent historical rates with small variations
        fed_funds_base = draw(st.floats(min_value=2.0, max_value=6.0))
        
        data = {
            "timestamp": timestamp.isoformat(),
            "interest_rates": {
                "fed_funds": {
                    "rate": fed_funds_base + draw(st.floats(min_value=-0.5, max_value=0.5)),
                    "date": timestamp.isoformat(),
                    "source": "FRED"
                }
            },
            "exchange_rates": {
                "EUR": {
                    "rate": 0.85 + draw(st.floats(min_value=-0.1, max_value=0.1)),
                    "timestamp": timestamp.isoformat(),
                    "source": "ExchangeRatesAPI",
                    "base_currency": "USD",
                    "target_currency": "EUR"
                }
            }
        }
        historical_data.append(data)
    
    return historical_data


class TestDataIngestionProperties:
    """Property-based tests for data ingestion pipeline"""
    
    @pytest.fixture
    def pipeline(self):
        """Create a market data ingestion pipeline for testing"""
        return MarketDataIngestionPipeline()
    
    @pytest.fixture
    def data_quality_service(self):
        """Create a data quality service for testing"""
        return DataQualityService()
    
    @given(market_data=market_data_strategy())
    @settings(max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @example(market_data={
        "timestamp": "2024-01-07T10:00:00",
        "interest_rates": {
            "fed_funds": {"rate": 5.25, "date": "2024-01-07T10:00:00", "source": "FRED"}
        },
        "exchange_rates": {
            "EUR": {"rate": 0.85, "timestamp": "2024-01-07T10:00:00", "source": "ExchangeRatesAPI", "base_currency": "USD", "target_currency": "EUR"}
        }
    })
    async def test_property_21_real_time_risk_calculation_performance(self, pipeline, market_data):
        """
        Feature: treasuryiq-corporate-ai, Property 21: Real-time Risk Calculation Performance
        For any market data feed update, the Treasury_System should refresh risk calculations within 60 seconds
        **Validates: Requirements 5.1**
        """
        # Mock the data fetching to return our test data
        with patch.object(pipeline, '_fetch_all_market_data', return_value=market_data):
            with patch.object(pipeline, '_store_market_data', return_value=None):
                
                start_time = datetime.now()
                
                # Run the ingestion pipeline
                result = await pipeline.ingest_market_data()
                
                end_time = datetime.now()
                processing_time = (end_time - start_time).total_seconds()
                
                # Property: Processing time should be within 60 seconds
                assert processing_time < 60.0, f"Processing took {processing_time:.2f} seconds, exceeding 60-second limit"
                
                # Property: Result should be successful for valid data
                if result.quality_report and result.quality_report.passed_validation:
                    assert result.success, "Ingestion should succeed for valid data"
                
                # Property: Records should be processed
                assert result.records_processed > 0, "Should process at least one record"
                
                # Property: Timestamp should be recent (within last minute)
                time_diff = (datetime.now() - result.timestamp).total_seconds()
                assert time_diff < 60, "Result timestamp should be recent"
    
    @given(
        current_data=market_data_strategy(),
        updated_data=market_data_strategy()
    )
    @settings(max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_22_data_synchronization(self, pipeline, current_data, updated_data):
        """
        Feature: treasuryiq-corporate-ai, Property 22: Data Synchronization
        For any internal financial system change, the Integration_Hub should automatically synchronize data
        **Validates: Requirements 5.2**
        """
        # Mock the data fetching to simulate system changes
        with patch.object(pipeline, '_fetch_all_market_data', side_effect=[current_data, updated_data]):
            with patch.object(pipeline, '_store_market_data', return_value=None):
                
                # First ingestion
                result1 = await pipeline.ingest_market_data()
                
                # Simulate system change and second ingestion
                result2 = await pipeline.ingest_market_data(force_refresh=True)
                
                # Property: Both ingestions should complete
                assert result1.timestamp is not None, "First ingestion should complete"
                assert result2.timestamp is not None, "Second ingestion should complete"
                
                # Property: Second ingestion should be more recent
                assert result2.timestamp > result1.timestamp, "Second ingestion should be more recent"
                
                # Property: Data should be synchronized (different timestamps indicate updates)
                if result1.success and result2.success:
                    # If both successful, they should have processed data
                    assert result1.records_processed > 0, "First ingestion should process records"
                    assert result2.records_processed > 0, "Second ingestion should process records"
                
                # Property: System should handle multiple synchronizations without errors
                assert len(result1.errors) == 0 or not result1.success, "Successful ingestion should have no errors"
                assert len(result2.errors) == 0 or not result2.success, "Successful ingestion should have no errors"
    
    @given(corrupted_data=corrupted_market_data_strategy())
    @settings(max_examples=100, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_property_25_data_quality_flagging(self, data_quality_service, corrupted_data):
        """
        Feature: treasuryiq-corporate-ai, Property 25: Data Quality Flagging
        For any detected data quality issue, the Treasury_System should flag all affected analyses and recommendations
        **Validates: Requirements 5.5**
        """
        # Run data quality validation on corrupted data
        quality_report = await data_quality_service.validate_market_data(corrupted_data, "property_test")
        
        # Property: Quality report should be generated
        assert quality_report is not None, "Quality report should always be generated"
        assert isinstance(quality_report, DataQualityReport), "Should return DataQualityReport instance"
        
        # Property: Quality score should be between 0 and 100
        assert 0 <= quality_report.quality_score <= 100, f"Quality score {quality_report.quality_score} should be between 0 and 100"
        
        # Property: If data has issues, they should be flagged
        has_missing_fields = any(
            field not in rate_data 
            for rate_data in corrupted_data.get("interest_rates", {}).values()
            for field in ["rate", "date", "source"]
        )
        
        has_invalid_rates = any(
            (isinstance(rate_data.get("rate"), (int, float)) and 
             (rate_data["rate"] < -5.0 or rate_data["rate"] > 25.0)) or
            isinstance(rate_data.get("rate"), str)
            for rate_data in corrupted_data.get("interest_rates", {}).values()
        )
        
        if has_missing_fields or has_invalid_rates:
            # Property: Issues should be detected and flagged
            assert len(quality_report.issues) > 0, "Data quality issues should be flagged"
            
            # Property: Critical issues should prevent validation from passing
            if any(issue.severity == DataQualitySeverity.CRITICAL for issue in quality_report.issues):
                assert not quality_report.passed_validation, "Critical issues should prevent validation from passing"
        
        # Property: Total records should match input data size
        expected_records = len(corrupted_data.get("interest_rates", {})) + len(corrupted_data.get("exchange_rates", {}))
        if expected_records > 0:
            assert quality_report.total_records == expected_records, "Total records should match input data size"
        
        # Property: Issues should have proper structure
        for issue in quality_report.issues:
            assert isinstance(issue, DataQualityIssue), "Each issue should be a DataQualityIssue instance"
            assert issue.field_name is not None, "Issue should have a field name"
            assert issue.message is not None, "Issue should have a message"
            assert issue.severity in DataQualitySeverity, "Issue should have valid severity"
    
    @given(
        historical_data=historical_data_strategy(),
        anomaly_multiplier=st.floats(min_value=5.0, max_value=20.0)
    )
    @settings(max_examples=50, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_anomaly_detection_property(self, data_quality_service, historical_data, anomaly_multiplier):
        """
        Property test for anomaly detection functionality
        For any historical data pattern, significant deviations should be detected as anomalies
        """
        assume(len(historical_data) >= 5)  # Need enough historical data
        
        # Calculate baseline from historical data
        fed_funds_rates = [
            float(data["interest_rates"]["fed_funds"]["rate"]) 
            for data in historical_data 
            if "fed_funds" in data.get("interest_rates", {})
        ]
        
        assume(len(fed_funds_rates) >= 5)  # Need enough rate data
        
        # Create anomalous current data
        mean_rate = sum(fed_funds_rates) / len(fed_funds_rates)
        anomalous_rate = mean_rate * anomaly_multiplier  # Significant deviation
        
        current_data = {
            "interest_rates": {
                "fed_funds": {
                    "rate": anomalous_rate,
                    "date": datetime.now().isoformat(),
                    "source": "FRED"
                }
            }
        }
        
        # Test anomaly detection
        anomalies = await data_quality_service.detect_anomalies(current_data, historical_data)
        
        # Property: Significant anomalies should be detected
        fed_funds_anomalies = [a for a in anomalies if "fed_funds" in a.field_name]
        
        if anomaly_multiplier > 10.0:  # Very large anomaly
            assert len(fed_funds_anomalies) > 0, f"Large anomaly (rate={anomalous_rate:.2f}, mean={mean_rate:.2f}) should be detected"
        
        # Property: All detected anomalies should have proper structure
        for anomaly in anomalies:
            assert isinstance(anomaly, DataQualityIssue), "Anomaly should be a DataQualityIssue"
            assert anomaly.field_name is not None, "Anomaly should have field name"
            assert anomaly.message is not None, "Anomaly should have message"
            assert "anomaly" in anomaly.message.lower() or "outlier" in anomaly.message.lower(), "Message should indicate anomaly"
    
    @given(
        service_name=st.text(min_size=1, max_size=20, alphabet=string.ascii_letters),
        failure_count=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_circuit_breaker_property(self, pipeline, service_name, failure_count):
        """
        Property test for circuit breaker functionality
        For any service, circuit breaker should open after threshold failures and reset properly
        """
        # Property: Initially circuit should be closed
        assert not pipeline._is_circuit_open(service_name), "Circuit should initially be closed"
        
        # Record failures
        for _ in range(failure_count):
            pipeline._record_circuit_breaker_failure(service_name)
        
        # Property: Circuit should open after 3 or more failures
        if failure_count >= 3:
            assert pipeline._is_circuit_open(service_name), f"Circuit should open after {failure_count} failures"
        else:
            assert not pipeline._is_circuit_open(service_name), f"Circuit should remain closed with only {failure_count} failures"
        
        # Property: Reset should always close the circuit
        pipeline._reset_circuit_breaker(service_name)
        assert not pipeline._is_circuit_open(service_name), "Circuit should be closed after reset"
    
    @given(data_batch=st.lists(market_data_strategy(), min_size=1, max_size=10))
    @settings(max_examples=30, deadline=15000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    async def test_batch_processing_property(self, pipeline, data_batch):
        """
        Property test for batch data processing
        For any batch of market data, processing should be consistent and maintain data integrity
        """
        results = []
        
        # Process each data item in the batch
        for i, market_data in enumerate(data_batch):
            with patch.object(pipeline, '_fetch_all_market_data', return_value=market_data):
                with patch.object(pipeline, '_store_market_data', return_value=None):
                    result = await pipeline.ingest_market_data()
                    results.append(result)
        
        # Property: All results should have timestamps
        for i, result in enumerate(results):
            assert result.timestamp is not None, f"Result {i} should have timestamp"
            assert isinstance(result, DataIngestionResult), f"Result {i} should be DataIngestionResult"
        
        # Property: Timestamps should be in chronological order (or very close)
        for i in range(1, len(results)):
            time_diff = (results[i].timestamp - results[i-1].timestamp).total_seconds()
            assert time_diff >= -1.0, f"Timestamps should be chronological (diff: {time_diff}s)"
        
        # Property: Successful results should have processed records
        successful_results = [r for r in results if r.success]
        for result in successful_results:
            assert result.records_processed > 0, "Successful results should have processed records"
        
        # Property: Quality reports should exist for all results
        for i, result in enumerate(results):
            if result.success:
                assert result.quality_report is not None, f"Successful result {i} should have quality report"


# Async test runner helper
def run_async_test(coro):
    """Helper to run async tests in property-based testing"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Sync wrappers for property tests (Hypothesis doesn't support async directly)
class TestDataIngestionPropertiesSync:
    """Synchronous wrappers for property-based tests"""
    
    @pytest.fixture
    def pipeline(self):
        return MarketDataIngestionPipeline()
    
    @pytest.fixture
    def data_quality_service(self):
        return DataQualityService()
    
    @given(market_data=market_data_strategy())
    @settings(max_examples=100, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_21_sync(self, pipeline, market_data):
        """Sync wrapper for Property 21 test"""
        async def async_test():
            test_instance = TestDataIngestionProperties()
            await test_instance.test_property_21_real_time_risk_calculation_performance(pipeline, market_data)
        
        run_async_test(async_test())
    
    @given(
        current_data=market_data_strategy(),
        updated_data=market_data_strategy()
    )
    @settings(max_examples=50, deadline=15000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_22_sync(self, pipeline, current_data, updated_data):
        """Sync wrapper for Property 22 test"""
        async def async_test():
            test_instance = TestDataIngestionProperties()
            await test_instance.test_property_22_data_synchronization(pipeline, current_data, updated_data)
        
        run_async_test(async_test())
    
    @given(corrupted_data=corrupted_market_data_strategy())
    @settings(max_examples=100, deadline=10000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_25_sync(self, data_quality_service, corrupted_data):
        """Sync wrapper for Property 25 test"""
        async def async_test():
            test_instance = TestDataIngestionProperties()
            await test_instance.test_property_25_data_quality_flagging(data_quality_service, corrupted_data)
        
        run_async_test(async_test())


# Integration test to verify all properties work together
@pytest.mark.asyncio
async def test_integrated_data_ingestion_properties():
    """
    Integration test that verifies all data ingestion properties work together
    This test ensures the complete pipeline maintains all correctness properties
    """
    pipeline = MarketDataIngestionPipeline()
    
    # Test data that should pass all properties
    good_data = {
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
        }
    }
    
    with patch.object(pipeline, '_fetch_all_market_data', return_value=good_data):
        with patch.object(pipeline, '_store_market_data', return_value=None):
            
            start_time = datetime.now()
            result = await pipeline.ingest_market_data()
            end_time = datetime.now()
            
            # Verify Property 21: Performance
            processing_time = (end_time - start_time).total_seconds()
            assert processing_time < 60.0, "Should meet performance requirement"
            
            # Verify Property 22: Synchronization
            assert result.success, "Should successfully synchronize data"
            assert result.records_processed > 0, "Should process records"
            
            # Verify Property 25: Quality Flagging
            assert result.quality_report is not None, "Should generate quality report"
            assert result.quality_report.passed_validation, "Good data should pass validation"
            assert len(result.quality_report.critical_issues) == 0, "Good data should have no critical issues"
            
            print("✅ All data ingestion properties verified successfully!")


if __name__ == "__main__":
    # Run a quick test to verify the property tests work
    import sys
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))