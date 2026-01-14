"""
Market Data API endpoints - Real-time data ingestion and quality monitoring
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from typing import Dict, Any, List
from datetime import datetime
import structlog

from app.services.market_data import MarketDataIngestionPipeline, DataIngestionResult
from app.services.data_quality import DataQualityReport

logger = structlog.get_logger(__name__)

router = APIRouter()

# Global market data service instance
market_data_service = MarketDataIngestionPipeline()


@router.get("/summary", response_model=Dict[str, Any])
async def get_market_summary():
    """
    Get comprehensive market data summary with quality indicators
    """
    try:
        summary = await market_data_service.get_market_summary()
        return summary
    except Exception as e:
        logger.error("Failed to get market summary", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch market data: {str(e)}")


@router.post("/ingest", response_model=Dict[str, Any])
async def trigger_data_ingestion(
    force_refresh: bool = False,
    background_tasks: BackgroundTasks = None
):
    """
    Trigger market data ingestion pipeline
    
    Args:
        force_refresh: Force refresh even if cached data is available
        background_tasks: FastAPI background tasks for async processing
    """
    try:
        # Run ingestion pipeline
        result = await market_data_service.ingest_market_data(force_refresh=force_refresh)
        
        return {
            "success": result.success,
            "message": "Data ingestion completed" if result.success else "Data ingestion failed",
            "source": result.source,
            "records_processed": result.records_processed,
            "timestamp": result.timestamp.isoformat(),
            "quality_score": result.quality_report.quality_score if result.quality_report else None,
            "critical_issues": len(result.quality_report.critical_issues) if result.quality_report else 0,
            "total_issues": len(result.quality_report.issues) if result.quality_report else 0,
            "errors": result.errors
        }
    except Exception as e:
        logger.error("Data ingestion failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Data ingestion failed: {str(e)}")


@router.get("/quality-report", response_model=Dict[str, Any])
async def get_data_quality_report():
    """
    Get the latest data quality report
    """
    try:
        # Trigger a fresh ingestion to get current quality report
        result = await market_data_service.ingest_market_data()
        
        if not result.quality_report:
            raise HTTPException(status_code=404, detail="No quality report available")
        
        report = result.quality_report
        
        return {
            "source": report.source,
            "timestamp": report.timestamp.isoformat(),
            "total_records": report.total_records,
            "quality_score": report.quality_score,
            "passed_validation": report.passed_validation,
            "issues": [
                {
                    "type": issue.issue_type.value,
                    "severity": issue.severity.value,
                    "field": issue.field_name,
                    "value": str(issue.value),
                    "message": issue.message,
                    "timestamp": issue.timestamp.isoformat(),
                    "expected_range": issue.expected_range
                }
                for issue in report.issues
            ],
            "critical_issues_count": len(report.critical_issues),
            "high_issues_count": len(report.high_issues)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get quality report", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get quality report: {str(e)}")


@router.get("/rates/federal-reserve", response_model=Dict[str, Any])
async def get_federal_reserve_rates():
    """
    Get current Federal Reserve interest rates
    """
    try:
        rates = await market_data_service.get_federal_reserve_rates()
        return {
            "timestamp": datetime.now().isoformat(),
            "rates": {
                name: {
                    "rate": float(rate.rate),
                    "date": rate.date.isoformat(),
                    "source": rate.source,
                    "series_id": rate.series_id
                }
                for name, rate in rates.items()
            }
        }
    except Exception as e:
        logger.error("Failed to get Federal Reserve rates", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch Federal Reserve rates: {str(e)}")


@router.get("/rates/exchange", response_model=Dict[str, Any])
async def get_exchange_rates(base_currency: str = "USD"):
    """
    Get current exchange rates
    
    Args:
        base_currency: Base currency for exchange rates (default: USD)
    """
    try:
        rates = await market_data_service.get_exchange_rates(base_currency)
        return {
            "timestamp": datetime.now().isoformat(),
            "base_currency": base_currency,
            "rates": {
                currency: {
                    "rate": float(rate.rate),
                    "timestamp": rate.timestamp.isoformat(),
                    "source": rate.source,
                    "target_currency": rate.target_currency
                }
                for currency, rate in rates.items()
            }
        }
    except Exception as e:
        logger.error("Failed to get exchange rates", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch exchange rates: {str(e)}")


@router.get("/yield-curve", response_model=Dict[str, Any])
async def get_treasury_yield_curve():
    """
    Get current Treasury yield curve
    """
    try:
        yield_curve = await market_data_service.get_treasury_yield_curve()
        return {
            "timestamp": datetime.now().isoformat(),
            "yield_curve": [
                {
                    "maturity": yc.maturity,
                    "yield_rate": float(yc.yield_rate),
                    "date": yc.date.isoformat()
                }
                for yc in yield_curve
            ],
            "curve_indicators": {
                "slope_2y_10y": market_data_service._calculate_yield_curve_slope(yield_curve),
                "total_points": len(yield_curve)
            }
        }
    except Exception as e:
        logger.error("Failed to get Treasury yield curve", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to fetch Treasury yield curve: {str(e)}")


@router.get("/health", response_model=Dict[str, Any])
async def get_market_data_health():
    """
    Get health status of market data sources and ingestion pipeline
    """
    try:
        # Check circuit breaker status
        circuit_status = {}
        for service, breaker in market_data_service._circuit_breaker.items():
            circuit_status[service] = {
                "is_open": breaker.get("is_open", False),
                "failures": breaker.get("failures", 0),
                "last_failure": breaker.get("last_failure").isoformat() if breaker.get("last_failure") else None
            }
        
        # Check cache status
        cache_status = {
            "cached_items": len(market_data_service._cache),
            "historical_records": len(market_data_service._historical_data)
        }
        
        # Try a quick data fetch to test connectivity
        health_checks = {}
        try:
            # Quick test of FRED API (just check if we can make a request)
            if market_data_service.fred_api_key:
                health_checks["fred_api"] = "configured"
            else:
                health_checks["fred_api"] = "demo_mode"
            
            # Quick test of Exchange API
            if market_data_service.exchange_api_key:
                health_checks["exchange_api"] = "configured"
            else:
                health_checks["exchange_api"] = "demo_mode"
                
        except Exception as e:
            health_checks["connectivity_test"] = f"failed: {str(e)}"
        
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "healthy",
            "circuit_breakers": circuit_status,
            "cache_status": cache_status,
            "api_health": health_checks,
            "data_quality_service": "active"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "unhealthy",
            "error": str(e)
        }


@router.post("/validate", response_model=Dict[str, Any])
async def validate_market_data(data: Dict[str, Any]):
    """
    Validate provided market data using data quality service
    
    Args:
        data: Market data to validate
    """
    try:
        quality_report = await market_data_service.data_quality.validate_market_data(data, "api_validation")
        
        return {
            "validation_result": {
                "passed": quality_report.passed_validation,
                "quality_score": quality_report.quality_score,
                "total_records": quality_report.total_records,
                "issues_count": len(quality_report.issues),
                "critical_issues_count": len(quality_report.critical_issues)
            },
            "issues": [
                {
                    "type": issue.issue_type.value,
                    "severity": issue.severity.value,
                    "field": issue.field_name,
                    "message": issue.message
                }
                for issue in quality_report.issues
            ],
            "timestamp": quality_report.timestamp.isoformat()
        }
    except Exception as e:
        logger.error("Data validation failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Data validation failed: {str(e)}")