#!/usr/bin/env python3
"""
Simple demo of the data ingestion pipeline functionality
This demonstrates the core features without requiring the full application setup
"""

import asyncio
import json
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Mock numpy for demo
class MockNumpy:
    @staticmethod
    def mean(values):
        return sum(values) / len(values) if values else 0
    
    @staticmethod
    def std(values):
        if not values or len(values) < 2:
            return 0
        mean_val = MockNumpy.mean(values)
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    @staticmethod
    def diff(values):
        return [values[i+1] - values[i] for i in range(len(values)-1)]
    
    @staticmethod
    def log(x):
        import math
        if isinstance(x, list):
            return [math.log(val) for val in x]
        return math.log(x)

# Replace numpy import
import sys
sys.modules['numpy'] = MockNumpy()
np = MockNumpy()

# Mock structlog
class MockLogger:
    def info(self, msg, **kwargs):
        print(f"INFO: {msg} {kwargs}")
    
    def warning(self, msg, **kwargs):
        print(f"WARNING: {msg} {kwargs}")
    
    def error(self, msg, **kwargs):
        print(f"ERROR: {msg} {kwargs}")

class MockStructlog:
    @staticmethod
    def get_logger():
        return MockLogger()

sys.modules['structlog'] = MockStructlog()

# Data Quality Classes (simplified versions)
class DataQualitySeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DataQualityIssueType(Enum):
    MISSING_DATA = "missing_data"
    OUTLIER = "outlier"
    STALE_DATA = "stale_data"
    INVALID_FORMAT = "invalid_format"

@dataclass
class DataQualityIssue:
    issue_type: DataQualityIssueType
    severity: DataQualitySeverity
    field_name: str
    value: Any
    message: str = ""
    expected_range: Optional[Tuple[Any, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

@dataclass
class DataQualityReport:
    source: str
    timestamp: datetime
    total_records: int
    issues: List[DataQualityIssue]
    quality_score: float
    passed_validation: bool
    
    @property
    def critical_issues(self) -> List[DataQualityIssue]:
        return [issue for issue in self.issues if issue.severity == DataQualitySeverity.CRITICAL]

@dataclass
class DataIngestionResult:
    success: bool
    source: str
    records_processed: int
    quality_report: Optional[DataQualityReport]
    errors: List[str]
    timestamp: datetime

# Simplified Data Quality Service
class DataQualityService:
    def __init__(self):
        self.validation_rules = {
            "interest_rates": {
                "min_value": -5.0,
                "max_value": 25.0,
                "max_age_hours": 24,
                "required_fields": ["rate", "date", "source"]
            },
            "exchange_rates": {
                "min_value": 0.001,
                "max_value": 1000.0,
                "max_age_hours": 1,
                "required_fields": ["rate", "timestamp", "base_currency", "target_currency"]
            }
        }
    
    async def validate_market_data(self, data: Dict[str, Any], source: str) -> DataQualityReport:
        issues = []
        total_records = 0
        
        # Validate interest rates
        if "interest_rates" in data:
            rate_issues, rate_count = self._validate_interest_rates(data["interest_rates"])
            issues.extend(rate_issues)
            total_records += rate_count
        
        # Validate exchange rates
        if "exchange_rates" in data:
            fx_issues, fx_count = self._validate_exchange_rates(data["exchange_rates"])
            issues.extend(fx_issues)
            total_records += fx_count
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(issues, total_records)
        passed_validation = quality_score >= 80.0 and len([i for i in issues if i.severity == DataQualitySeverity.CRITICAL]) == 0
        
        return DataQualityReport(
            source=source,
            timestamp=datetime.now(),
            total_records=total_records,
            issues=issues,
            quality_score=quality_score,
            passed_validation=passed_validation
        )
    
    def _validate_interest_rates(self, rates: Dict[str, Any]) -> Tuple[List[DataQualityIssue], int]:
        issues = []
        rules = self.validation_rules["interest_rates"]
        
        for rate_name, rate_data in rates.items():
            # Check required fields
            for field in rules["required_fields"]:
                if field not in rate_data:
                    issues.append(DataQualityIssue(
                        issue_type=DataQualityIssueType.MISSING_DATA,
                        severity=DataQualitySeverity.CRITICAL,
                        field_name=f"{rate_name}.{field}",
                        value=None,
                        message=f"Missing required field: {field}"
                    ))
            
            # Validate rate value
            if "rate" in rate_data:
                rate_value = float(rate_data["rate"])
                if rate_value < rules["min_value"] or rate_value > rules["max_value"]:
                    issues.append(DataQualityIssue(
                        issue_type=DataQualityIssueType.OUTLIER,
                        severity=DataQualitySeverity.HIGH,
                        field_name=f"{rate_name}.rate",
                        value=rate_value,
                        expected_range=(rules["min_value"], rules["max_value"]),
                        message=f"Rate value outside expected range"
                    ))
        
        return issues, len(rates)
    
    def _validate_exchange_rates(self, rates: Dict[str, Any]) -> Tuple[List[DataQualityIssue], int]:
        issues = []
        rules = self.validation_rules["exchange_rates"]
        
        for currency, rate_data in rates.items():
            # Check required fields
            for field in rules["required_fields"]:
                if field not in rate_data:
                    issues.append(DataQualityIssue(
                        issue_type=DataQualityIssueType.MISSING_DATA,
                        severity=DataQualitySeverity.CRITICAL,
                        field_name=f"{currency}.{field}",
                        value=None,
                        message=f"Missing required field: {field}"
                    ))
            
            # Validate rate value
            if "rate" in rate_data:
                rate_value = float(rate_data["rate"])
                if rate_value < rules["min_value"] or rate_value > rules["max_value"]:
                    issues.append(DataQualityIssue(
                        issue_type=DataQualityIssueType.OUTLIER,
                        severity=DataQualitySeverity.HIGH,
                        field_name=f"{currency}.rate",
                        value=rate_value,
                        expected_range=(rules["min_value"], rules["max_value"]),
                        message=f"Exchange rate outside expected range"
                    ))
        
        return issues, len(rates)
    
    def _calculate_quality_score(self, issues: List[DataQualityIssue], total_records: int) -> float:
        if total_records == 0:
            return 0.0
        
        severity_weights = {
            DataQualitySeverity.CRITICAL: 25,
            DataQualitySeverity.HIGH: 10,
            DataQualitySeverity.MEDIUM: 5,
            DataQualitySeverity.LOW: 1
        }
        
        total_penalty = sum(severity_weights[issue.severity] for issue in issues)
        max_possible_penalty = total_records * severity_weights[DataQualitySeverity.CRITICAL]
        
        if max_possible_penalty == 0:
            return 100.0
        
        penalty_ratio = min(total_penalty / max_possible_penalty, 1.0)
        score = (1.0 - penalty_ratio) * 100.0
        
        return round(score, 2)

# Simplified Market Data Pipeline
class MarketDataIngestionPipeline:
    def __init__(self):
        self.data_quality = DataQualityService()
        self._circuit_breaker = {}
        self._historical_data = []
    
    async def ingest_market_data(self, force_refresh: bool = False) -> DataIngestionResult:
        try:
            # Step 1: Generate demo market data
            market_data = self._generate_demo_market_data()
            
            # Step 2: Validate data quality
            quality_report = await self.data_quality.validate_market_data(market_data, "demo_pipeline")
            
            # Step 3: Store data (simulated)
            if quality_report.passed_validation:
                self._historical_data.append(market_data)
                print(f"✓ Market data stored successfully")
            
            return DataIngestionResult(
                success=quality_report.passed_validation,
                source="demo_pipeline",
                records_processed=quality_report.total_records,
                quality_report=quality_report,
                errors=[issue.message for issue in quality_report.critical_issues],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            return DataIngestionResult(
                success=False,
                source="demo_pipeline",
                records_processed=0,
                quality_report=None,
                errors=[str(e)],
                timestamp=datetime.now()
            )
    
    def _generate_demo_market_data(self) -> Dict[str, Any]:
        """Generate realistic demo market data"""
        return {
            "timestamp": datetime.now().isoformat(),
            "interest_rates": {
                "fed_funds": {
                    "rate": 5.25,
                    "date": datetime.now().isoformat(),
                    "source": "FRED_DEMO"
                },
                "treasury_10y": {
                    "rate": 4.25,
                    "date": datetime.now().isoformat(),
                    "source": "FRED_DEMO"
                },
                "treasury_2y": {
                    "rate": 4.75,
                    "date": datetime.now().isoformat(),
                    "source": "FRED_DEMO"
                }
            },
            "exchange_rates": {
                "EUR": {
                    "rate": 0.85,
                    "timestamp": datetime.now().isoformat(),
                    "source": "DEMO_API",
                    "base_currency": "USD",
                    "target_currency": "EUR"
                },
                "GBP": {
                    "rate": 0.78,
                    "timestamp": datetime.now().isoformat(),
                    "source": "DEMO_API",
                    "base_currency": "USD",
                    "target_currency": "GBP"
                },
                "JPY": {
                    "rate": 150.0,
                    "timestamp": datetime.now().isoformat(),
                    "source": "DEMO_API",
                    "base_currency": "USD",
                    "target_currency": "JPY"
                }
            }
        }
    
    def _is_circuit_open(self, service: str) -> bool:
        return self._circuit_breaker.get(service, {}).get("is_open", False)
    
    def _record_circuit_breaker_failure(self, service: str):
        if service not in self._circuit_breaker:
            self._circuit_breaker[service] = {"failures": 0, "is_open": False}
        
        breaker = self._circuit_breaker[service]
        breaker["failures"] += 1
        
        if breaker["failures"] >= 3:
            breaker["is_open"] = True
            print(f"⚠️  Circuit breaker opened for {service}")
    
    def _reset_circuit_breaker(self, service: str):
        if service in self._circuit_breaker:
            self._circuit_breaker[service] = {"failures": 0, "is_open": False}
            print(f"✓ Circuit breaker reset for {service}")

async def demo_data_quality():
    print("=== Data Quality Validation Demo ===")
    
    data_quality = DataQualityService()
    
    # Test with good data
    good_data = {
        "interest_rates": {
            "fed_funds": {
                "rate": 5.25,
                "date": datetime.now().isoformat(),
                "source": "FRED"
            }
        },
        "exchange_rates": {
            "EUR": {
                "rate": 0.85,
                "timestamp": datetime.now().isoformat(),
                "source": "ExchangeAPI",
                "base_currency": "USD",
                "target_currency": "EUR"
            }
        }
    }
    
    print("Testing good data...")
    quality_report = await data_quality.validate_market_data(good_data, "demo_good")
    print(f"  Quality Score: {quality_report.quality_score}")
    print(f"  Passed Validation: {quality_report.passed_validation}")
    print(f"  Issues Found: {len(quality_report.issues)}")
    
    # Test with bad data
    bad_data = {
        "interest_rates": {
            "fed_funds": {
                "rate": 50.0,  # Unrealistic rate
                "source": "FRED"
                # Missing date field
            }
        },
        "exchange_rates": {
            "EUR": {
                "rate": -1.0,  # Invalid negative rate
                "timestamp": datetime.now().isoformat(),
                "source": "ExchangeAPI"
                # Missing required fields
            }
        }
    }
    
    print("\nTesting bad data...")
    quality_report = await data_quality.validate_market_data(bad_data, "demo_bad")
    print(f"  Quality Score: {quality_report.quality_score}")
    print(f"  Passed Validation: {quality_report.passed_validation}")
    print(f"  Issues Found: {len(quality_report.issues)}")
    
    for issue in quality_report.issues[:3]:
        print(f"    - {issue.severity.value}: {issue.message}")

async def demo_ingestion_pipeline():
    print("\n=== Market Data Ingestion Pipeline Demo ===")
    
    pipeline = MarketDataIngestionPipeline()
    
    print("Running data ingestion pipeline...")
    result = await pipeline.ingest_market_data()
    
    print(f"\nIngestion Results:")
    print(f"  Success: {result.success}")
    print(f"  Records Processed: {result.records_processed}")
    print(f"  Timestamp: {result.timestamp}")
    
    if result.quality_report:
        print(f"  Quality Score: {result.quality_report.quality_score}")
        print(f"  Validation Passed: {result.quality_report.passed_validation}")
        print(f"  Issues: {len(result.quality_report.issues)}")
    
    if result.errors:
        print(f"  Errors: {result.errors}")

async def demo_circuit_breaker():
    print("\n=== Circuit Breaker Demo ===")
    
    pipeline = MarketDataIngestionPipeline()
    service_name = "demo_service"
    
    print(f"Circuit breaker status: {pipeline._is_circuit_open(service_name)}")
    
    print("Recording failures...")
    for i in range(3):
        pipeline._record_circuit_breaker_failure(service_name)
    
    print(f"Circuit breaker status after failures: {pipeline._is_circuit_open(service_name)}")
    
    pipeline._reset_circuit_breaker(service_name)
    print(f"Circuit breaker status after reset: {pipeline._is_circuit_open(service_name)}")

async def main():
    print("TreasuryIQ Market Data Ingestion Pipeline Demo")
    print("=" * 50)
    
    try:
        await demo_data_quality()
        await demo_ingestion_pipeline()
        await demo_circuit_breaker()
        
        print("\n" + "=" * 50)
        print("✅ Demo completed successfully!")
        print("\nKey Features Demonstrated:")
        print("  ✓ Data quality validation with scoring")
        print("  ✓ Multi-source market data ingestion")
        print("  ✓ Circuit breaker pattern for resilience")
        print("  ✓ Comprehensive error handling")
        print("  ✓ Real-time data processing pipeline")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())