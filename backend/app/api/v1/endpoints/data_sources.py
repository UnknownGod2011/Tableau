"""
TreasuryIQ Data Sources API Endpoints
Real-time financial data ingestion endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import asyncio
from datetime import datetime

from app.services.data_sources import treasury_data_ingestion
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/treasury/cash-balances")
async def get_treasury_cash_balances() -> Dict[str, Any]:
    """
    Get US Treasury daily cash balances
    Real-time data from Treasury.gov Fiscal Data API
    """
    try:
        data = await treasury_data_ingestion.get_treasury_cash_balances()
        return data
    except Exception as e:
        logger.error(f"Error fetching treasury cash balances: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/interest-rates")
async def get_interest_rates() -> Dict[str, Any]:
    """
    Get current interest rates from multiple sources
    Includes Treasury rates, Fed funds rate, and market rates
    """
    try:
        data = await treasury_data_ingestion.get_interest_rates()
        return data
    except Exception as e:
        logger.error(f"Error fetching interest rates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/exchange-rates")
async def get_exchange_rates() -> Dict[str, Any]:
    """
    Get current foreign exchange rates
    Base currency: USD, includes major trading pairs
    """
    try:
        data = await treasury_data_ingestion.get_exchange_rates()
        return data
    except Exception as e:
        logger.error(f"Error fetching exchange rates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/economic/indicators")
async def get_economic_indicators() -> Dict[str, Any]:
    """
    Get key economic indicators for treasury analysis
    Includes GDP, inflation, unemployment, and treasury yields
    """
    try:
        data = await treasury_data_ingestion.get_economic_indicators()
        return data
    except Exception as e:
        logger.error(f"Error fetching economic indicators: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market/comprehensive")
async def get_comprehensive_market_data() -> Dict[str, Any]:
    """
    Get comprehensive market data for treasury analysis
    Combines all available data sources in a single call
    """
    try:
        data = await treasury_data_ingestion.get_comprehensive_market_data()
        return data
    except Exception as e:
        logger.error(f"Error fetching comprehensive market data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources/status")
async def get_data_sources_status() -> Dict[str, Any]:
    """
    Get status of all configured data sources
    Shows availability and rate limits
    """
    try:
        sources_status = {}
        
        for source_name, source_config in treasury_data_ingestion.data_sources.items():
            sources_status[source_name] = {
                'name': source_config.name,
                'description': source_config.description,
                'has_api_key': source_config.api_key is not None,
                'rate_limit': source_config.rate_limit,
                'status': 'configured' if source_config.api_key else 'available_free'
            }
        
        return {
            'sources': sources_status,
            'timestamp': datetime.now().isoformat(),
            'total_sources': len(sources_status)
        }
    
    except Exception as e:
        logger.error(f"Error getting data sources status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/data/refresh")
async def refresh_all_data(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Trigger refresh of all market data
    Runs in background to avoid timeout
    """
    try:
        # Add background task to refresh data
        background_tasks.add_task(treasury_data_ingestion.get_comprehensive_market_data)
        
        return {
            'message': 'Data refresh initiated',
            'status': 'processing',
            'timestamp': datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error initiating data refresh: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/demo/sample-data")
async def get_sample_treasury_data() -> Dict[str, Any]:
    """
    Get sample treasury data for demo purposes
    Returns realistic sample data when external APIs are not available
    """
    try:
        sample_data = {
            'treasury_balances': {
                'operating_cash_balance': 450000000000,  # $450B
                'treasury_general_account': 420000000000,  # $420B
                'federal_reserve_account': 30000000000,   # $30B
                'last_updated': datetime.now().isoformat()
            },
            'interest_rates': {
                'treasury_3m': 5.25,
                'treasury_6m': 5.35,
                'treasury_1y': 5.15,
                'treasury_2y': 4.95,
                'treasury_5y': 4.75,
                'treasury_10y': 4.65,
                'treasury_30y': 4.85,
                'fed_funds': 5.50
            },
            'exchange_rates': {
                'EUR': 0.92,
                'GBP': 0.79,
                'JPY': 148.50,
                'SGD': 1.34,
                'CAD': 1.36,
                'CHF': 0.88,
                'AUD': 1.52
            },
            'economic_indicators': {
                'gdp_growth': 2.4,
                'inflation_rate': 3.2,
                'unemployment_rate': 3.7,
                'consumer_confidence': 102.3
            },
            'market_volatility': {
                'vix': 18.5,
                'treasury_volatility': 12.3,
                'fx_volatility': 8.7
            },
            'timestamp': datetime.now().isoformat(),
            'source': 'demo_data',
            'status': 'success'
        }
        
        return sample_data
    
    except Exception as e:
        logger.error(f"Error generating sample data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))