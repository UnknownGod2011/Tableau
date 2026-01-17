"""
Data quality validation and anomaly detection service
"""

import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import structlog
from dataclasses import dataclass
from enum import Enum

logger = structlog.get_logger(__name__)


class DataQualitySeverity(Enum):
    """Data quality issue severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DataQualityIssueType(Enum):
    """Types of data quality issues"""
    MISSING_DATA = "missing_data"
    OUTLIER = "outlier"
    STALE_DATA = "stale_data"
    INVALID_FORMAT = "invalid_format"
    INCONSISTENT_DATA = "inconsistent_data"
    DUPLICATE_DATA = "duplicate_data"


@dataclass
class DataQualityIssue:
    """Data quality issue details"""
    issue_type: DataQualityIssueType
    severity: DataQualitySeverity
    field_name: str
    value: Any
    expected_range: Optional[Tuple[Any, Any]] = None
    message: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class DataQualityReport:
    """Comprehensive data quality assessment report"""
    source: str
    timestamp: datetime
    total_records: int
    issues: List[DataQualityIssue]
    quality_score: float  # 0-100
    passed_validation: bool
    
    @property
    def critical_issues(self) -> List[DataQualityIssue]:
        return [issue for issue in self.issues if issue.severity == DataQualitySeverity.CRITICAL]
    
    @property
    def high_issues(self) -> List[DataQualityIssue]:
        return [issue for issue in self.issues if issue.severity == DataQualitySeverity.HIGH]


class DataQualityService:
    """Service for validating data quality and detecting anomalies"""
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.historical_stats = {}
    
    def _initialize_validation_rules(self) -> Dict[str, Dict]:
        """Initialize validation rules for different data types"""
        return {
            "interest_rates": {
                "min_value": -5.0,  # Negative rates possible
                "max_value": 25.0,  # Extreme high rate
                "max_age_hours": 24,
                "required_fields": ["rate", "date", "source"]
            },
            "exchange_rates": {
                "min_value": 0.001,  # Very weak currency
                "max_value": 1000.0,  # Very strong currency
                "max_age_hours": 1,  # FX data should be very fresh
                "required_fields": ["rate", "timestamp", "base_currency", "target_currency"]
            },
            "cash_positions": {
                "min_value": 0.0,  # No negative cash
                "max_value": 10_000_000_000.0,  # $10B max position
                "max_age_hours": 24,
                "required_fields": ["balance", "currency", "entity_id"]
            },
            "treasury_yields": {
                "min_value": -2.0,  # Negative yields possible
                "max_value": 15.0,  # High yield scenario
                "max_age_hours": 24,
                "required_fields": ["yield_rate", "maturity", "date"]
            }
        }
    
    async def validate_market_data(self, data: Dict[str, Any], source: str) -> DataQualityReport:
        """Validate market data quality"""
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
        
        # Validate yield curve
        if "yield_curve" in data:
            yield_issues, yield_count = self._validate_yield_curve(data["yield_curve"])
            issues.extend(yield_issues)
            total_records += yield_count
        
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
        """Validate interest rate data"""
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
                    continue
            
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
            
            # Check data freshness
            if "date" in rate_data:
                try:
                    if isinstance(rate_data["date"], str):
                        rate_date = datetime.fromisoformat(rate_data["date"].replace('Z', '+00:00'))
                    else:
                        rate_date = rate_data["date"]
                    
                    age_hours = (datetime.now() - rate_date.replace(tzinfo=None)).total_seconds() / 3600
                    if age_hours > rules["max_age_hours"]:
                        issues.append(DataQualityIssue(
                            issue_type=DataQualityIssueType.STALE_DATA,
                            severity=DataQualitySeverity.MEDIUM,
                            field_name=f"{rate_name}.date",
                            value=rate_date,
                            message=f"Data is {age_hours:.1f} hours old"
                        ))
                except (ValueError, TypeError) as e:
                    issues.append(DataQualityIssue(
                        issue_type=DataQualityIssueType.INVALID_FORMAT,
                        severity=DataQualitySeverity.HIGH,
                        field_name=f"{rate_name}.date",
                        value=rate_data["date"],
                        message=f"Invalid date format: {str(e)}"
                    ))
        
        return issues, len(rates)
    
    def _validate_exchange_rates(self, rates: Dict[str, Any]) -> Tuple[List[DataQualityIssue], int]:
        """Validate exchange rate data"""
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
                    continue
            
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
            
            # Check data freshness (FX data should be very fresh)
            if "timestamp" in rate_data:
                try:
                    if isinstance(rate_data["timestamp"], str):
                        rate_timestamp = datetime.fromisoformat(rate_data["timestamp"].replace('Z', '+00:00'))
                    else:
                        rate_timestamp = rate_data["timestamp"]
                    
                    age_hours = (datetime.now() - rate_timestamp.replace(tzinfo=None)).total_seconds() / 3600
                    if age_hours > rules["max_age_hours"]:
                        issues.append(DataQualityIssue(
                            issue_type=DataQualityIssueType.STALE_DATA,
                            severity=DataQualitySeverity.HIGH,  # FX staleness is more critical
                            field_name=f"{currency}.timestamp",
                            value=rate_timestamp,
                            message=f"FX data is {age_hours:.1f} hours old"
                        ))
                except (ValueError, TypeError) as e:
                    issues.append(DataQualityIssue(
                        issue_type=DataQualityIssueType.INVALID_FORMAT,
                        severity=DataQualitySeverity.HIGH,
                        field_name=f"{currency}.timestamp",
                        value=rate_data["timestamp"],
                        message=f"Invalid timestamp format: {str(e)}"
                    ))
        
        return issues, len(rates)
    
    def _validate_yield_curve(self, yield_curve: List[Dict[str, Any]]) -> Tuple[List[DataQualityIssue], int]:
        """Validate Treasury yield curve data"""
        issues = []
        rules = self.validation_rules["treasury_yields"]
        
        if not yield_curve:
            issues.append(DataQualityIssue(
                issue_type=DataQualityIssueType.MISSING_DATA,
                severity=DataQualitySeverity.CRITICAL,
                field_name="yield_curve",
                value=None,
                message="Yield curve data is empty"
            ))
            return issues, 0
        
        # Expected maturities in order
        expected_maturities = ["1M", "3M", "6M", "1Y", "2Y", "5Y", "10Y", "30Y"]
        found_maturities = [yc.get("maturity") for yc in yield_curve if "maturity" in yc]
        
        # Check for missing maturities
        missing_maturities = set(expected_maturities) - set(found_maturities)
        if missing_maturities:
            issues.append(DataQualityIssue(
                issue_type=DataQualityIssueType.MISSING_DATA,
                severity=DataQualitySeverity.MEDIUM,
                field_name="yield_curve.maturities",
                value=list(missing_maturities),
                message=f"Missing yield curve maturities: {missing_maturities}"
            ))
        
        # Validate individual yield points
        for i, yield_point in enumerate(yield_curve):
            # Check required fields
            for field in rules["required_fields"]:
                if field not in yield_point:
                    issues.append(DataQualityIssue(
                        issue_type=DataQualityIssueType.MISSING_DATA,
                        severity=DataQualitySeverity.HIGH,
                        field_name=f"yield_curve[{i}].{field}",
                        value=None,
                        message=f"Missing required field: {field}"
                    ))
                    continue
            
            # Validate yield value
            if "yield" in yield_point or "yield_rate" in yield_point:
                yield_key = "yield" if "yield" in yield_point else "yield_rate"
                yield_value = float(yield_point[yield_key])
                
                if yield_value < rules["min_value"] or yield_value > rules["max_value"]:
                    issues.append(DataQualityIssue(
                        issue_type=DataQualityIssueType.OUTLIER,
                        severity=DataQualitySeverity.HIGH,
                        field_name=f"yield_curve[{i}].{yield_key}",
                        value=yield_value,
                        expected_range=(rules["min_value"], rules["max_value"]),
                        message=f"Yield value outside expected range"
                    ))
        
        return issues, len(yield_curve)
    
    def _calculate_quality_score(self, issues: List[DataQualityIssue], total_records: int) -> float:
        """Calculate overall data quality score (0-100)"""
        if total_records == 0:
            return 0.0
        
        # Weight issues by severity
        severity_weights = {
            DataQualitySeverity.CRITICAL: 25,
            DataQualitySeverity.HIGH: 10,
            DataQualitySeverity.MEDIUM: 5,
            DataQualitySeverity.LOW: 1
        }
        
        total_penalty = sum(severity_weights[issue.severity] for issue in issues)
        max_possible_penalty = total_records * severity_weights[DataQualitySeverity.CRITICAL]
        
        # Calculate score (higher is better)
        if max_possible_penalty == 0:
            return 100.0
        
        penalty_ratio = min(total_penalty / max_possible_penalty, 1.0)
        score = (1.0 - penalty_ratio) * 100.0
        
        return round(score, 2)
    
    async def detect_anomalies(self, current_data: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> List[DataQualityIssue]:
        """Detect anomalies by comparing current data with historical patterns"""
        anomalies = []
        
        if not historical_data or len(historical_data) < 5:
            # Not enough historical data for anomaly detection
            return anomalies
        
        # Detect interest rate anomalies
        if "interest_rates" in current_data:
            rate_anomalies = self._detect_rate_anomalies(
                current_data["interest_rates"], 
                [h.get("interest_rates", {}) for h in historical_data]
            )
            anomalies.extend(rate_anomalies)
        
        # Detect FX rate anomalies
        if "exchange_rates" in current_data:
            fx_anomalies = self._detect_fx_anomalies(
                current_data["exchange_rates"],
                [h.get("exchange_rates", {}) for h in historical_data]
            )
            anomalies.extend(fx_anomalies)
        
        return anomalies
    
    def _detect_rate_anomalies(self, current_rates: Dict[str, Any], historical_rates: List[Dict[str, Any]]) -> List[DataQualityIssue]:
        """Detect anomalies in interest rates using statistical methods"""
        anomalies = []
        
        for rate_name, current_rate_data in current_rates.items():
            if "rate" not in current_rate_data:
                continue
            
            current_rate = float(current_rate_data["rate"])
            
            # Collect historical values for this rate
            historical_values = []
            for hist_data in historical_rates:
                if rate_name in hist_data and "rate" in hist_data[rate_name]:
                    try:
                        historical_values.append(float(hist_data[rate_name]["rate"]))
                    except (ValueError, TypeError):
                        continue
            
            if len(historical_values) < 5:
                continue
            
            # Calculate statistical measures
            mean_rate = np.mean(historical_values)
            std_rate = np.std(historical_values)
            
            # Z-score anomaly detection (3-sigma rule)
            if std_rate > 0:
                z_score = abs(current_rate - mean_rate) / std_rate
                if z_score > 3.0:
                    anomalies.append(DataQualityIssue(
                        issue_type=DataQualityIssueType.OUTLIER,
                        severity=DataQualitySeverity.HIGH if z_score > 4.0 else DataQualitySeverity.MEDIUM,
                        field_name=f"{rate_name}.rate",
                        value=current_rate,
                        expected_range=(mean_rate - 2*std_rate, mean_rate + 2*std_rate),
                        message=f"Rate anomaly detected: z-score = {z_score:.2f}"
                    ))
        
        return anomalies
    
    def _detect_fx_anomalies(self, current_rates: Dict[str, Any], historical_rates: List[Dict[str, Any]]) -> List[DataQualityIssue]:
        """Detect anomalies in FX rates"""
        anomalies = []
        
        for currency, current_rate_data in current_rates.items():
            if "rate" not in current_rate_data:
                continue
            
            current_rate = float(current_rate_data["rate"])
            
            # Collect historical values
            historical_values = []
            for hist_data in historical_rates:
                if currency in hist_data and "rate" in hist_data[currency]:
                    try:
                        historical_values.append(float(hist_data[currency]["rate"]))
                    except (ValueError, TypeError):
                        continue
            
            if len(historical_values) < 5:
                continue
            
            # Calculate daily volatility
            if len(historical_values) >= 2:
                returns = np.diff(np.log(historical_values))
                volatility = np.std(returns)
                
                # Check if current rate represents a large move
                if len(historical_values) > 0:
                    last_rate = historical_values[-1]
                    daily_return = abs(np.log(current_rate / last_rate))
                    
                    # If move is more than 3x daily volatility, flag as anomaly
                    if volatility > 0 and daily_return > 3 * volatility:
                        anomalies.append(DataQualityIssue(
                            issue_type=DataQualityIssueType.OUTLIER,
                            severity=DataQualitySeverity.HIGH,
                            field_name=f"{currency}.rate",
                            value=current_rate,
                            message=f"Large FX move detected: {daily_return/volatility:.1f}x daily volatility"
                        ))
        
        return anomalies