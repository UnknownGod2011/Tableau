"""
Market Data Service - Real-time data from Federal Reserve, Exchange Rates, and Financial APIs
Enhanced with data ingestion pipeline, quality validation, and anomaly detection
"""

import httpx
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from decimal import Decimal
import structlog
from dataclasses import dataclass

from app.core.config import settings
from app.services.data_quality import DataQualityService, DataQualityReport

logger = structlog.get_logger(__name__)


@dataclass
class InterestRate:
    """Interest rate data point"""
    series_id: str
    name: str
    rate: Decimal
    date: datetime
    source: str


@dataclass
class ExchangeRate:
    """Currency exchange rate"""
    base_currency: str
    target_currency: str
    rate: Decimal
    timestamp: datetime
    source: str


@dataclass
class TreasuryYield:
    """Treasury yield data"""
    maturity: str  # "1M", "3M", "6M", "1Y", "2Y", "5Y", "10Y", "30Y"
    yield_rate: Decimal
    date: datetime
    change_1d: Optional[Decimal] = None


@dataclass
class DataIngestionResult:
    """Result of data ingestion operation"""
    success: bool
    source: str
    records_processed: int
    quality_report: Optional[DataQualityReport]
    errors: List[str]
    timestamp: datetime
    
    @property
    def has_critical_issues(self) -> bool:
        return self.quality_report and len(self.quality_report.critical_issues) > 0


class MarketDataIngestionPipeline:
    """Enhanced market data service with ingestion pipeline and quality validation"""
    
    # FRED API Series IDs for key rates
    FRED_SERIES = {
        "fed_funds": "FEDFUNDS",           # Federal Funds Rate
        "prime_rate": "DPRIME",            # Prime Rate
        "treasury_1m": "DGS1MO",           # 1-Month Treasury
        "treasury_3m": "DGS3MO",           # 3-Month Treasury
        "treasury_6m": "DGS6MO",           # 6-Month Treasury
        "treasury_1y": "DGS1",             # 1-Year Treasury
        "treasury_2y": "DGS2",             # 2-Year Treasury
        "treasury_5y": "DGS5",             # 5-Year Treasury
        "treasury_10y": "DGS10",           # 10-Year Treasury
        "treasury_30y": "DGS30",           # 30-Year Treasury
        "libor_1m": "USD1MTD156N",         # 1-Month LIBOR
        "sofr": "SOFR",                    # SOFR Rate
    }
    
    # Backup data sources for failover
    BACKUP_SOURCES = {
        "treasury_data": "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/",
        "yahoo_finance": "https://query1.finance.yahoo.com/v8/finance/chart/",
        "alpha_vantage": "https://www.alphavantage.co/query"
    }
    
    def __init__(self):
        self.fred_api_key = settings.FEDERAL_RESERVE_API_KEY
        self.exchange_api_key = settings.EXCHANGE_RATES_API_KEY
        self.alpha_vantage_key = getattr(settings, 'ALPHA_VANTAGE_API_KEY', None)
        
        # Initialize data quality service
        self.data_quality = DataQualityService()
        
        # Data cache with expiry
        self._cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, datetime] = {}
        
        # Historical data for anomaly detection
        self._historical_data: List[Dict[str, Any]] = []
        self._max_historical_records = 100
        
        # Circuit breaker for failed APIs
        self._circuit_breaker = {
            "fred": {"failures": 0, "last_failure": None, "is_open": False},
            "exchange_api": {"failures": 0, "last_failure": None, "is_open": False},
            "backup_sources": {"failures": 0, "last_failure": None, "is_open": False}
        }
    
    async def ingest_market_data(self, force_refresh: bool = False) -> DataIngestionResult:
        """
        Main ingestion pipeline - fetches, validates, and processes market data
        """
        logger.info("Starting market data ingestion pipeline")
        
        try:
            # Step 1: Fetch data from multiple sources
            market_data = await self._fetch_all_market_data(force_refresh)
            
            # Step 2: Validate data quality
            quality_report = await self.data_quality.validate_market_data(market_data, "market_data_pipeline")
            
            # Step 3: Detect anomalies using historical data
            if self._historical_data:
                anomalies = await self.data_quality.detect_anomalies(market_data, self._historical_data)
                quality_report.issues.extend(anomalies)
                # Recalculate quality score with anomalies
                quality_report.quality_score = self.data_quality._calculate_quality_score(
                    quality_report.issues, quality_report.total_records
                )
            
            # Step 4: Handle data quality issues
            if quality_report.critical_issues:
                logger.error(
                    "Critical data quality issues detected",
                    critical_issues=len(quality_report.critical_issues),
                    quality_score=quality_report.quality_score
                )
                
                # Try backup sources for critical issues
                backup_data = await self._fetch_backup_data()
                if backup_data:
                    # Merge backup data and re-validate
                    market_data = self._merge_backup_data(market_data, backup_data)
                    quality_report = await self.data_quality.validate_market_data(market_data, "market_data_with_backup")
            
            # Step 5: Store validated data
            if quality_report.passed_validation:
                await self._store_market_data(market_data)
                self._update_historical_data(market_data)
                logger.info(
                    "Market data ingestion completed successfully",
                    quality_score=quality_report.quality_score,
                    records=quality_report.total_records
                )
            else:
                logger.warning(
                    "Market data failed validation",
                    quality_score=quality_report.quality_score,
                    issues=len(quality_report.issues)
                )
            
            return DataIngestionResult(
                success=quality_report.passed_validation,
                source="market_data_pipeline",
                records_processed=quality_report.total_records,
                quality_report=quality_report,
                errors=[issue.message for issue in quality_report.critical_issues],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error("Market data ingestion failed", error=str(e))
            return DataIngestionResult(
                success=False,
                source="market_data_pipeline",
                records_processed=0,
                quality_report=None,
                errors=[str(e)],
                timestamp=datetime.now()
            )
    
    async def _fetch_all_market_data(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Fetch data from all sources concurrently"""
        tasks = []
        
        # Federal Reserve rates
        if not self._is_circuit_open("fred"):
            tasks.append(self._fetch_federal_reserve_rates_with_circuit_breaker())
        
        # Exchange rates
        if not self._is_circuit_open("exchange_api"):
            tasks.append(self._fetch_exchange_rates_with_circuit_breaker())
        
        # Treasury yield curve
        tasks.append(self._fetch_treasury_yield_curve())
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        market_data = {
            "timestamp": datetime.now().isoformat(),
            "interest_rates": {},
            "exchange_rates": {},
            "yield_curve": []
        }
        
        for result in results:
            if isinstance(result, Exception):
                logger.warning("Data fetch task failed", error=str(result))
                continue
            
            if isinstance(result, dict):
                if "interest_rates" in result:
                    market_data["interest_rates"].update(result["interest_rates"])
                elif "exchange_rates" in result:
                    market_data["exchange_rates"].update(result["exchange_rates"])
                elif "yield_curve" in result:
                    market_data["yield_curve"] = result["yield_curve"]
        
        return market_data
    
    async def _fetch_federal_reserve_rates_with_circuit_breaker(self) -> Dict[str, Any]:
        """Fetch Federal Reserve rates with circuit breaker pattern"""
        try:
            rates = await self.get_federal_reserve_rates()
            self._reset_circuit_breaker("fred")
            return {"interest_rates": {k: {
                "rate": float(v.rate),
                "date": v.date.isoformat(),
                "source": v.source
            } for k, v in rates.items()}}
        except Exception as e:
            self._record_circuit_breaker_failure("fred")
            logger.warning("FRED API failed", error=str(e))
            raise
    
    async def _fetch_exchange_rates_with_circuit_breaker(self) -> Dict[str, Any]:
        """Fetch exchange rates with circuit breaker pattern"""
        try:
            rates = await self.get_exchange_rates()
            self._reset_circuit_breaker("exchange_api")
            return {"exchange_rates": {k: {
                "rate": float(v.rate),
                "timestamp": v.timestamp.isoformat(),
                "source": v.source,
                "base_currency": v.base_currency,
                "target_currency": v.target_currency
            } for k, v in rates.items()}}
        except Exception as e:
            self._record_circuit_breaker_failure("exchange_api")
            logger.warning("Exchange rates API failed", error=str(e))
            raise
    
    async def _fetch_treasury_yield_curve(self) -> Dict[str, Any]:
        """Fetch Treasury yield curve"""
        try:
            yield_curve = await self.get_treasury_yield_curve()
            return {"yield_curve": [{
                "maturity": yc.maturity,
                "yield": float(yc.yield_rate),
                "date": yc.date.isoformat()
            } for yc in yield_curve]}
        except Exception as e:
            logger.warning("Treasury yield curve fetch failed", error=str(e))
            raise
    
    async def _fetch_backup_data(self) -> Optional[Dict[str, Any]]:
        """Fetch data from backup sources when primary sources fail"""
        if self._is_circuit_open("backup_sources"):
            return None
        
        try:
            # Try Treasury.gov API for yield data
            backup_data = {}
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Fetch Treasury rates from Treasury.gov
                treasury_url = f"{self.BACKUP_SOURCES['treasury_data']}v1/accounting/od/avg_interest_rates"
                params = {
                    "filter": "record_date:gte:2024-01-01",
                    "sort": "-record_date",
                    "page[size]": "1"
                }
                
                response = await client.get(treasury_url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data"):
                        # Process Treasury backup data
                        backup_data["treasury_backup"] = data["data"][0]
            
            self._reset_circuit_breaker("backup_sources")
            return backup_data
            
        except Exception as e:
            self._record_circuit_breaker_failure("backup_sources")
            logger.warning("Backup data sources failed", error=str(e))
            return None
    
    def _merge_backup_data(self, primary_data: Dict[str, Any], backup_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge backup data with primary data to fill gaps"""
        merged_data = primary_data.copy()
        
        # Add backup Treasury data if primary is missing
        if "treasury_backup" in backup_data and not merged_data.get("interest_rates"):
            treasury_backup = backup_data["treasury_backup"]
            merged_data["interest_rates"] = {
                "treasury_backup": {
                    "rate": float(treasury_backup.get("avg_interest_rate_amt", 4.0)),
                    "date": treasury_backup.get("record_date", datetime.now().isoformat()),
                    "source": "Treasury.gov_Backup"
                }
            }
        
        return merged_data
    
    def _is_circuit_open(self, service: str) -> bool:
        """Check if circuit breaker is open for a service"""
        breaker = self._circuit_breaker.get(service, {})
        
        if not breaker.get("is_open", False):
            return False
        
        # Check if enough time has passed to try again (5 minutes)
        last_failure = breaker.get("last_failure")
        if last_failure and datetime.now() - last_failure > timedelta(minutes=5):
            breaker["is_open"] = False
            breaker["failures"] = 0
            return False
        
        return True
    
    def _record_circuit_breaker_failure(self, service: str):
        """Record a failure for circuit breaker"""
        if service not in self._circuit_breaker:
            self._circuit_breaker[service] = {"failures": 0, "last_failure": None, "is_open": False}
        
        breaker = self._circuit_breaker[service]
        breaker["failures"] += 1
        breaker["last_failure"] = datetime.now()
        
        # Open circuit after 3 failures
        if breaker["failures"] >= 3:
            breaker["is_open"] = True
            logger.warning(f"Circuit breaker opened for {service}", failures=breaker["failures"])
    
    def _reset_circuit_breaker(self, service: str):
        """Reset circuit breaker after successful operation"""
        if service in self._circuit_breaker:
            self._circuit_breaker[service] = {"failures": 0, "last_failure": None, "is_open": False}
    
    async def _store_market_data(self, market_data: Dict[str, Any]):
        """Store validated market data (placeholder for database storage)"""
        # In a real implementation, this would store to database
        # For now, we'll update the cache
        cache_key = "latest_market_data"
        self._cache[cache_key] = market_data
        self._cache_expiry[cache_key] = datetime.now() + timedelta(minutes=15)
        
        logger.info("Market data stored successfully", timestamp=market_data.get("timestamp"))
    
    def _update_historical_data(self, market_data: Dict[str, Any]):
        """Update historical data for anomaly detection"""
        self._historical_data.append(market_data)
        
        # Keep only the last N records
        if len(self._historical_data) > self._max_historical_records:
            self._historical_data = self._historical_data[-self._max_historical_records:]
    
    # Original methods (preserved for backward compatibility)
    async def get_federal_reserve_rates(self) -> Dict[str, InterestRate]:
        """Fetch current interest rates from Federal Reserve FRED API"""
        rates = {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for name, series_id in self.FRED_SERIES.items():
                try:
                    rate = await self._fetch_fred_series(client, series_id, name)
                    if rate:
                        rates[name] = rate
                except Exception as e:
                    logger.warning(f"Failed to fetch {name}", error=str(e))
                    # Use fallback demo data
                    rates[name] = self._get_demo_rate(name, series_id)
        
        return rates
    
    async def _fetch_fred_series(
        self, 
        client: httpx.AsyncClient, 
        series_id: str, 
        name: str
    ) -> Optional[InterestRate]:
        """Fetch a single FRED series"""
        if not self.fred_api_key:
            return self._get_demo_rate(name, series_id)
        
        url = "https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": self.fred_api_key,
            "file_type": "json",
            "sort_order": "desc",
            "limit": 1,
        }
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("observations"):
            obs = data["observations"][0]
            return InterestRate(
                series_id=series_id,
                name=name,
                rate=Decimal(obs["value"]) if obs["value"] != "." else Decimal("0"),
                date=datetime.strptime(obs["date"], "%Y-%m-%d"),
                source="FRED"
            )
        return None
    
    def _get_demo_rate(self, name: str, series_id: str) -> InterestRate:
        """Generate realistic demo rates for development"""
        demo_rates = {
            "fed_funds": 5.25,
            "prime_rate": 8.50,
            "treasury_1m": 5.45,
            "treasury_3m": 5.35,
            "treasury_6m": 5.15,
            "treasury_1y": 4.95,
            "treasury_2y": 4.75,
            "treasury_5y": 4.45,
            "treasury_10y": 4.25,
            "treasury_30y": 4.35,
            "libor_1m": 5.40,
            "sofr": 5.30,
        }
        
        return InterestRate(
            series_id=series_id,
            name=name,
            rate=Decimal(str(demo_rates.get(name, 4.0))),
            date=datetime.now(),
            source="DEMO"
        )
    
    async def get_exchange_rates(self, base_currency: str = "USD") -> Dict[str, ExchangeRate]:
        """Fetch current exchange rates"""
        cache_key = f"fx_rates_{base_currency}"
        
        # Check cache (5-minute expiry)
        if self._is_cached(cache_key, minutes=5):
            return self._cache[cache_key]
        
        rates = {}
        currencies = ["EUR", "GBP", "JPY", "CAD", "AUD", "CHF", "SGD"]
        
        try:
            if self.exchange_api_key:
                rates = await self._fetch_exchange_rates_api(base_currency, currencies)
            else:
                rates = self._get_demo_exchange_rates(base_currency, currencies)
        except Exception as e:
            logger.warning("Exchange rate API failed, using demo data", error=str(e))
            rates = self._get_demo_exchange_rates(base_currency, currencies)
        
        self._cache[cache_key] = rates
        self._cache_expiry[cache_key] = datetime.now() + timedelta(minutes=5)
        return rates
    
    async def _fetch_exchange_rates_api(
        self, 
        base_currency: str, 
        currencies: List[str]
    ) -> Dict[str, ExchangeRate]:
        """Fetch from exchangeratesapi.io or similar service"""
        rates = {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = "https://api.exchangeratesapi.io/v1/latest"
            params = {
                "access_key": self.exchange_api_key,
                "base": base_currency,
                "symbols": ",".join(currencies)
            }
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success") and data.get("rates"):
                for currency, rate in data["rates"].items():
                    rates[currency] = ExchangeRate(
                        base_currency=base_currency,
                        target_currency=currency,
                        rate=Decimal(str(rate)),
                        timestamp=datetime.fromtimestamp(data["timestamp"]),
                        source="ExchangeRatesAPI"
                    )
        
        return rates
    
    def _get_demo_exchange_rates(
        self, 
        base_currency: str, 
        currencies: List[str]
    ) -> Dict[str, ExchangeRate]:
        """Generate realistic demo exchange rates"""
        demo_rates = {
            "EUR": 0.85,
            "GBP": 0.78,
            "JPY": 150.0,
            "CAD": 1.35,
            "AUD": 1.52,
            "CHF": 0.88,
            "SGD": 1.32,
        }
        
        rates = {}
        for currency in currencies:
            if currency in demo_rates:
                rates[currency] = ExchangeRate(
                    base_currency=base_currency,
                    target_currency=currency,
                    rate=Decimal(str(demo_rates[currency])),
                    timestamp=datetime.now(),
                    source="DEMO"
                )
        
        return rates
    
    async def get_treasury_yield_curve(self) -> List[TreasuryYield]:
        """Get complete Treasury yield curve"""
        rates = await self.get_federal_reserve_rates()
        
        yield_curve = []
        maturities = [
            ("1M", "treasury_1m"),
            ("3M", "treasury_3m"), 
            ("6M", "treasury_6m"),
            ("1Y", "treasury_1y"),
            ("2Y", "treasury_2y"),
            ("5Y", "treasury_5y"),
            ("10Y", "treasury_10y"),
            ("30Y", "treasury_30y"),
        ]
        
        for maturity, key in maturities:
            if key in rates:
                rate = rates[key]
                yield_curve.append(TreasuryYield(
                    maturity=maturity,
                    yield_rate=rate.rate,
                    date=rate.date
                ))
        
        return yield_curve
    
    def _is_cached(self, key: str, minutes: int = 5) -> bool:
        """Check if data is cached and not expired"""
        if key not in self._cache or key not in self._cache_expiry:
            return False
        return datetime.now() < self._cache_expiry[key]
    
    async def get_market_summary(self) -> Dict[str, Any]:
        """Get comprehensive market data summary"""
        try:
            # Check if we have recent cached data
            cache_key = "latest_market_data"
            if self._is_cached(cache_key, minutes=10):
                return self._cache[cache_key]
            
            # Otherwise, run full ingestion pipeline
            ingestion_result = await self.ingest_market_data()
            
            if ingestion_result.success and cache_key in self._cache:
                market_data = self._cache[cache_key]
                
                # Add market indicators
                if "yield_curve" in market_data:
                    yield_curve_data = [TreasuryYield(
                        maturity=yc["maturity"],
                        yield_rate=Decimal(str(yc["yield"])),
                        date=datetime.fromisoformat(yc["date"])
                    ) for yc in market_data["yield_curve"]]
                    
                    market_data["market_indicators"] = {
                        "yield_curve_slope": self._calculate_yield_curve_slope(yield_curve_data),
                        "risk_sentiment": self._assess_risk_sentiment(
                            market_data.get("interest_rates", {}), 
                            market_data.get("exchange_rates", {})
                        ),
                        "volatility_index": self._calculate_volatility_index(),
                        "data_quality_score": ingestion_result.quality_report.quality_score if ingestion_result.quality_report else 0
                    }
                
                return market_data
            else:
                # Fallback to basic data if ingestion failed
                rates_task = self.get_federal_reserve_rates()
                fx_task = self.get_exchange_rates()
                yield_curve_task = self.get_treasury_yield_curve()
                
                rates, fx_rates, yield_curve = await asyncio.gather(
                    rates_task, fx_task, yield_curve_task
                )
                
                return {
                    "timestamp": datetime.now().isoformat(),
                    "interest_rates": {k: {
                        "rate": float(v.rate),
                        "date": v.date.isoformat(),
                        "source": v.source
                    } for k, v in rates.items()},
                    "exchange_rates": {k: {
                        "rate": float(v.rate),
                        "timestamp": v.timestamp.isoformat(),
                        "source": v.source
                    } for k, v in fx_rates.items()},
                    "yield_curve": [{
                        "maturity": yc.maturity,
                        "yield": float(yc.yield_rate),
                        "date": yc.date.isoformat()
                    } for yc in yield_curve],
                    "market_indicators": {
                        "yield_curve_slope": self._calculate_yield_curve_slope(yield_curve),
                        "risk_sentiment": self._assess_risk_sentiment(rates, fx_rates),
                        "volatility_index": self._calculate_volatility_index(),
                        "data_quality_score": 0  # Unknown quality for fallback data
                    }
                }
            
        except Exception as e:
            logger.error("Failed to get market summary", error=str(e))
            raise
    
    def _calculate_yield_curve_slope(self, yield_curve: List[TreasuryYield]) -> float:
        """Calculate yield curve slope (10Y - 2Y)"""
        ten_year = next((yc for yc in yield_curve if yc.maturity == "10Y"), None)
        two_year = next((yc for yc in yield_curve if yc.maturity == "2Y"), None)
        
        if ten_year and two_year:
            return float(ten_year.yield_rate - two_year.yield_rate)
        return 0.0
    
    def _assess_risk_sentiment(
        self, 
        rates: Dict[str, Any], 
        fx_rates: Dict[str, Any]
    ) -> str:
        """Assess market risk sentiment"""
        # Simple heuristic based on rates and USD strength
        fed_funds_data = rates.get("fed_funds")
        if not fed_funds_data:
            return "neutral"
        
        fed_funds_rate = fed_funds_data.get("rate", 4.0)
        if isinstance(fed_funds_rate, str):
            fed_funds_rate = float(fed_funds_rate)
        
        if fed_funds_rate > 5.0:
            return "risk_off"
        elif fed_funds_rate < 2.0:
            return "risk_on"
        else:
            return "neutral"
    
    def _calculate_volatility_index(self) -> float:
        """Calculate simple volatility index"""
        # Placeholder - would use actual VIX or calculate from price data
        import random
        return round(random.uniform(15.0, 35.0), 2)


# Maintain backward compatibility
MarketDataService = MarketDataIngestionPipeline