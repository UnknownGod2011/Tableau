"""
TreasuryIQ Data Sources Integration
Comprehensive data ingestion from multiple financial data sources
"""

import asyncio
import aiohttp
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass
import yfinance as yf
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class DataSource:
    """Data source configuration"""
    name: str
    url: str
    api_key: Optional[str] = None
    rate_limit: int = 60  # requests per minute
    description: str = ""

class TreasuryDataIngestion:
    """
    Comprehensive treasury data ingestion service
    Integrates with multiple financial data sources
    """
    
    def __init__(self):
        self.data_sources = {
            'treasury_gov': DataSource(
                name="US Treasury Fiscal Data",
                url="https://api.fiscaldata.treasury.gov/services/api/v1",
                description="Official US Treasury financial data"
            ),
            'fred': DataSource(
                name="Federal Reserve Economic Data",
                url="https://api.stlouisfed.org/fred",
                api_key=settings.FEDERAL_RESERVE_API_KEY,
                description="Federal Reserve economic indicators"
            ),
            'alpha_vantage': DataSource(
                name="Alpha Vantage",
                url="https://www.alphavantage.co/query",
                api_key=settings.ALPHA_VANTAGE_API_KEY,
                description="Financial market data and indicators"
            ),
            'exchange_rates': DataSource(
                name="Exchange Rates API",
                url="https://api.exchangerate-api.com/v4",
                api_key=settings.EXCHANGE_RATES_API_KEY,
                description="Real-time currency exchange rates"
            )
        }
    
    async def get_treasury_cash_balances(self) -> Dict[str, Any]:
        """
        Get US Treasury daily cash balances
        Source: Treasury.gov Fiscal Data API
        """
        try:
            url = f"{self.data_sources['treasury_gov'].url}/accounting/dts/operating_cash_balance"
            params = {
                'filter': f'record_date:gte:{(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")}',
                'sort': '-record_date',
                'page[size]': '30'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'source': 'treasury_gov',
                            'data_type': 'cash_balances',
                            'records': data.get('data', []),
                            'timestamp': datetime.now().isoformat(),
                            'status': 'success'
                        }
                    else:
                        logger.error(f"Treasury API error: {response.status}")
                        return {'status': 'error', 'message': f'API error: {response.status}'}
        
        except Exception as e:
            logger.error(f"Error fetching treasury cash balances: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_interest_rates(self) -> Dict[str, Any]:
        """
        Get current interest rates from multiple sources
        Sources: FRED API, Alpha Vantage
        """
        try:
            rates_data = {}
            
            # Treasury rates from FRED
            if self.data_sources['fred'].api_key:
                fred_rates = await self._get_fred_rates()
                rates_data.update(fred_rates)
            
            # Market rates from Alpha Vantage
            if self.data_sources['alpha_vantage'].api_key:
                market_rates = await self._get_alpha_vantage_rates()
                rates_data.update(market_rates)
            
            # Fallback to Yahoo Finance (free)
            yf_rates = await self._get_yahoo_finance_rates()
            rates_data.update(yf_rates)
            
            return {
                'source': 'multiple',
                'data_type': 'interest_rates',
                'rates': rates_data,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error fetching interest rates: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_exchange_rates(self) -> Dict[str, Any]:
        """
        Get current foreign exchange rates
        Source: Exchange Rates API, Yahoo Finance
        """
        try:
            base_currency = 'USD'
            target_currencies = ['EUR', 'GBP', 'JPY', 'SGD', 'CAD', 'CHF', 'AUD']
            
            # Try Exchange Rates API first
            if self.data_sources['exchange_rates'].api_key:
                fx_data = await self._get_exchange_rates_api(base_currency, target_currencies)
            else:
                # Fallback to Yahoo Finance
                fx_data = await self._get_yahoo_finance_fx(base_currency, target_currencies)
            
            return {
                'source': 'exchange_rates_api',
                'data_type': 'fx_rates',
                'base_currency': base_currency,
                'rates': fx_data,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def get_economic_indicators(self) -> Dict[str, Any]:
        """
        Get key economic indicators for treasury analysis
        Source: FRED API, Alpha Vantage
        """
        try:
            indicators = {}
            
            # Key indicators for treasury management
            fred_series = {
                'GDP': 'GDP',
                'INFLATION': 'CPIAUCSL',
                'UNEMPLOYMENT': 'UNRATE',
                'FED_FUNDS_RATE': 'FEDFUNDS',
                'TREASURY_10Y': 'GS10',
                'TREASURY_2Y': 'GS2',
                'TREASURY_3M': 'GS3M'
            }
            
            if self.data_sources['fred'].api_key:
                for indicator, series_id in fred_series.items():
                    data = await self._get_fred_series(series_id)
                    if data:
                        indicators[indicator] = data
            
            return {
                'source': 'fred',
                'data_type': 'economic_indicators',
                'indicators': indicators,
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error fetching economic indicators: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _get_fred_rates(self) -> Dict[str, float]:
        """Get interest rates from FRED API"""
        try:
            rates = {}
            series_ids = {
                'treasury_3m': 'GS3M',
                'treasury_6m': 'GS6M',
                'treasury_1y': 'GS1',
                'treasury_2y': 'GS2',
                'treasury_5y': 'GS5',
                'treasury_10y': 'GS10',
                'fed_funds': 'FEDFUNDS'
            }
            
            for rate_name, series_id in series_ids.items():
                data = await self._get_fred_series(series_id, limit=1)
                if data and len(data) > 0:
                    rates[rate_name] = float(data[0]['value'])
            
            return rates
        except Exception as e:
            logger.error(f"Error fetching FRED rates: {str(e)}")
            return {}
    
    async def _get_fred_series(self, series_id: str, limit: int = 10) -> List[Dict]:
        """Get data from FRED API series"""
        try:
            url = f"{self.data_sources['fred'].url}/series/observations"
            params = {
                'series_id': series_id,
                'api_key': self.data_sources['fred'].api_key,
                'file_type': 'json',
                'limit': limit,
                'sort_order': 'desc'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get('observations', [])
                    else:
                        logger.error(f"FRED API error for {series_id}: {response.status}")
                        return []
        
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {str(e)}")
            return []
    
    async def _get_alpha_vantage_rates(self) -> Dict[str, float]:
        """Get market rates from Alpha Vantage"""
        try:
            # Alpha Vantage treasury rates
            url = self.data_sources['alpha_vantage'].url
            params = {
                'function': 'TREASURY_YIELD',
                'interval': 'daily',
                'maturity': '10year',
                'apikey': self.data_sources['alpha_vantage'].api_key
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Process Alpha Vantage response
                        return self._process_alpha_vantage_treasury(data)
                    else:
                        logger.error(f"Alpha Vantage API error: {response.status}")
                        return {}
        
        except Exception as e:
            logger.error(f"Error fetching Alpha Vantage rates: {str(e)}")
            return {}
    
    async def _get_yahoo_finance_rates(self) -> Dict[str, float]:
        """Get rates from Yahoo Finance (free fallback)"""
        try:
            rates = {}
            
            # Treasury ETF tickers as proxy for rates
            tickers = {
                'treasury_3m': '^IRX',  # 13 Week Treasury Bill
                'treasury_10y': '^TNX', # 10 Year Treasury Note
                'treasury_30y': '^TYX'  # 30 Year Treasury Bond
            }
            
            for rate_name, ticker in tickers.items():
                try:
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        rates[rate_name] = float(hist['Close'].iloc[-1])
                except Exception as e:
                    logger.warning(f"Could not fetch {ticker}: {str(e)}")
            
            return rates
        
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance rates: {str(e)}")
            return {}
    
    async def _get_exchange_rates_api(self, base: str, targets: List[str]) -> Dict[str, float]:
        """Get FX rates from Exchange Rates API"""
        try:
            url = f"{self.data_sources['exchange_rates'].url}/latest/{base}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rates = data.get('rates', {})
                        return {currency: rates.get(currency, 0.0) for currency in targets}
                    else:
                        logger.error(f"Exchange Rates API error: {response.status}")
                        return {}
        
        except Exception as e:
            logger.error(f"Error fetching exchange rates: {str(e)}")
            return {}
    
    async def _get_yahoo_finance_fx(self, base: str, targets: List[str]) -> Dict[str, float]:
        """Get FX rates from Yahoo Finance"""
        try:
            rates = {}
            
            for target in targets:
                try:
                    ticker = f"{base}{target}=X"
                    fx = yf.Ticker(ticker)
                    hist = fx.history(period="1d")
                    if not hist.empty:
                        rates[target] = float(hist['Close'].iloc[-1])
                except Exception as e:
                    logger.warning(f"Could not fetch {ticker}: {str(e)}")
            
            return rates
        
        except Exception as e:
            logger.error(f"Error fetching Yahoo Finance FX: {str(e)}")
            return {}
    
    def _process_alpha_vantage_treasury(self, data: Dict) -> Dict[str, float]:
        """Process Alpha Vantage treasury yield response"""
        try:
            if 'data' in data:
                latest = data['data'][0] if data['data'] else {}
                return {
                    'treasury_10y_av': float(latest.get('value', 0.0))
                }
            return {}
        except Exception as e:
            logger.error(f"Error processing Alpha Vantage data: {str(e)}")
            return {}
    
    async def get_comprehensive_market_data(self) -> Dict[str, Any]:
        """
        Get comprehensive market data for treasury analysis
        Combines all data sources
        """
        try:
            # Fetch all data concurrently
            tasks = [
                self.get_treasury_cash_balances(),
                self.get_interest_rates(),
                self.get_exchange_rates(),
                self.get_economic_indicators()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            return {
                'treasury_balances': results[0] if not isinstance(results[0], Exception) else {'status': 'error'},
                'interest_rates': results[1] if not isinstance(results[1], Exception) else {'status': 'error'},
                'exchange_rates': results[2] if not isinstance(results[2], Exception) else {'status': 'error'},
                'economic_indicators': results[3] if not isinstance(results[3], Exception) else {'status': 'error'},
                'timestamp': datetime.now().isoformat(),
                'status': 'success'
            }
        
        except Exception as e:
            logger.error(f"Error fetching comprehensive market data: {str(e)}")
            return {'status': 'error', 'message': str(e)}

# Global instance
treasury_data_ingestion = TreasuryDataIngestion()