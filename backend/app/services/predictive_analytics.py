"""
Predictive Analytics Service for Treasury Management
Implements cash flow forecasting, market volatility prediction, and supplier default probability models
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from dataclasses import dataclass
import logging
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, accuracy_score, roc_auc_score
import joblib
import os

from ..models.cash import CashPosition
from ..models.investments import Investment
from ..models.corporate import CorporateEntity
from ..services.market_data import MarketDataService

logger = logging.getLogger(__name__)


@dataclass
class CashFlowForecast:
    """Cash flow forecast result"""
    entity_id: str
    forecast_horizon_days: int
    daily_forecasts: List[Dict[str, Any]]
    confidence_intervals: Dict[str, List[float]]
    key_assumptions: List[str]
    forecast_accuracy: Optional[float] = None
    model_version: str = "1.0"
    generated_at: datetime = None

    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now(timezone.utc)


@dataclass
class VolatilityForecast:
    """Market volatility forecast result"""
    asset_class: str
    forecast_horizon_days: int
    predicted_volatility: float
    confidence_level: float
    historical_volatility: float
    volatility_regime: str  # "low", "medium", "high"
    key_drivers: List[str]
    model_accuracy: Optional[float] = None


@dataclass
class DefaultProbability:
    """Supplier default probability assessment"""
    supplier_id: str
    probability_1y: float
    probability_3y: float
    probability_5y: float
    risk_grade: str  # "AAA", "AA", "A", "BBB", "BB", "B", "CCC", "D"
    key_risk_factors: List[str]
    financial_ratios: Dict[str, float]
    model_confidence: float


class PredictiveAnalyticsService:
    """Advanced predictive analytics for treasury management"""
    
    def __init__(self, market_data_service: MarketDataService):
        self.market_data_service = market_data_service
        self.models_path = "models/"
        self.scaler = StandardScaler()
        
        # Model configurations
        self.cash_flow_model = None
        self.volatility_model = None
        self.default_model = None
        
        # Model performance tracking
        self.model_performance = {
            "cash_flow": {"accuracy": 0.85, "last_retrain": None},
            "volatility": {"accuracy": 0.78, "last_retrain": None},
            "default": {"accuracy": 0.82, "last_retrain": None}
        }
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize or load existing models"""
        try:
            # Try to load existing models
            if os.path.exists(f"{self.models_path}cash_flow_model.pkl"):
                self.cash_flow_model = joblib.load(f"{self.models_path}cash_flow_model.pkl")
                logger.info("Loaded existing cash flow model")
            else:
                self.cash_flow_model = RandomForestRegressor(
                    n_estimators=100,
                    max_depth=10,
                    random_state=42
                )
                logger.info("Initialized new cash flow model")
            
            if os.path.exists(f"{self.models_path}volatility_model.pkl"):
                self.volatility_model = joblib.load(f"{self.models_path}volatility_model.pkl")
                logger.info("Loaded existing volatility model")
            else:
                self.volatility_model = GradientBoostingClassifier(
                    n_estimators=100,
                    learning_rate=0.1,
                    max_depth=6,
                    random_state=42
                )
                logger.info("Initialized new volatility model")
            
            if os.path.exists(f"{self.models_path}default_model.pkl"):
                self.default_model = joblib.load(f"{self.models_path}default_model.pkl")
                logger.info("Loaded existing default probability model")
            else:
                self.default_model = LogisticRegression(
                    random_state=42,
                    max_iter=1000
                )
                logger.info("Initialized new default probability model")
                
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            # Fallback to new models
            self._create_new_models()
    
    def _create_new_models(self):
        """Create new models with default configurations"""
        self.cash_flow_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.volatility_model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.default_model = LogisticRegression(
            random_state=42,
            max_iter=1000
        )
    
    async def forecast_cash_flows(
        self,
        entity_id: str,
        forecast_horizon_days: int = 90,
        confidence_level: float = 0.95
    ) -> CashFlowForecast:
        """
        Generate cash flow forecasts using time series analysis and machine learning
        """
        try:
            # Generate historical cash flow data (mock for demo)
            historical_data = self._generate_historical_cash_flows(entity_id, 365)
            
            # Prepare features for forecasting
            features = self._prepare_cash_flow_features(historical_data)
            
            # Generate forecasts
            daily_forecasts = []
            confidence_intervals = {"lower": [], "upper": []}
            
            base_date = datetime.now(timezone.utc)
            
            for day in range(forecast_horizon_days):
                forecast_date = base_date + timedelta(days=day)
                
                # Create features for this day
                day_features = self._create_day_features(forecast_date, historical_data)
                
                # Generate prediction (mock implementation)
                predicted_flow = self._predict_daily_cash_flow(day_features)
                
                # Calculate confidence intervals
                std_error = abs(predicted_flow) * 0.15  # 15% standard error
                z_score = 1.96 if confidence_level == 0.95 else 2.58  # 95% or 99%
                
                lower_bound = predicted_flow - (z_score * std_error)
                upper_bound = predicted_flow + (z_score * std_error)
                
                daily_forecasts.append({
                    "date": forecast_date.isoformat(),
                    "predicted_flow": float(predicted_flow),
                    "day_of_week": forecast_date.weekday(),
                    "is_month_end": forecast_date.day >= 28,
                    "seasonal_factor": self._get_seasonal_factor(forecast_date)
                })
                
                confidence_intervals["lower"].append(float(lower_bound))
                confidence_intervals["upper"].append(float(upper_bound))
            
            # Key assumptions
            key_assumptions = [
                "Historical patterns continue with normal market conditions",
                "No major operational changes or disruptions",
                "Seasonal patterns based on 2-year historical analysis",
                "Economic indicators remain within current ranges",
                f"Model accuracy: {self.model_performance['cash_flow']['accuracy']:.1%}"
            ]
            
            return CashFlowForecast(
                entity_id=entity_id,
                forecast_horizon_days=forecast_horizon_days,
                daily_forecasts=daily_forecasts,
                confidence_intervals=confidence_intervals,
                key_assumptions=key_assumptions,
                forecast_accuracy=self.model_performance['cash_flow']['accuracy']
            )
            
        except Exception as e:
            logger.error(f"Error generating cash flow forecast: {e}")
            raise
    
    async def predict_market_volatility(
        self,
        asset_class: str,
        forecast_horizon_days: int = 30
    ) -> VolatilityForecast:
        """
        Predict market volatility changes using machine learning models
        """
        try:
            # Get historical market data
            market_data = await self._get_market_data_for_volatility(asset_class)
            
            # Calculate current volatility
            returns = np.diff(np.log(market_data['prices']))
            current_volatility = np.std(returns) * np.sqrt(252)  # Annualized
            
            # Prepare features for volatility prediction
            features = self._prepare_volatility_features(market_data)
            
            # Predict volatility regime (mock implementation)
            predicted_volatility = self._predict_volatility(features, current_volatility)
            
            # Determine volatility regime
            if predicted_volatility < 0.15:
                regime = "low"
            elif predicted_volatility < 0.25:
                regime = "medium"
            else:
                regime = "high"
            
            # Key drivers analysis
            key_drivers = self._analyze_volatility_drivers(asset_class, market_data)
            
            return VolatilityForecast(
                asset_class=asset_class,
                forecast_horizon_days=forecast_horizon_days,
                predicted_volatility=predicted_volatility,
                confidence_level=0.85,
                historical_volatility=current_volatility,
                volatility_regime=regime,
                key_drivers=key_drivers,
                model_accuracy=self.model_performance['volatility']['accuracy']
            )
            
        except Exception as e:
            logger.error(f"Error predicting market volatility: {e}")
            raise
    
    async def calculate_default_probability(
        self,
        supplier_id: str,
        financial_data: Dict[str, Any]
    ) -> DefaultProbability:
        """
        Calculate supplier default probability using credit risk models
        """
        try:
            # Extract financial ratios
            financial_ratios = self._calculate_financial_ratios(financial_data)
            
            # Prepare features for default prediction
            features = self._prepare_default_features(financial_ratios, financial_data)
            
            # Predict default probabilities (mock implementation)
            prob_1y = self._predict_default_probability(features, horizon=1)
            prob_3y = self._predict_default_probability(features, horizon=3)
            prob_5y = self._predict_default_probability(features, horizon=5)
            
            # Determine risk grade
            risk_grade = self._determine_risk_grade(prob_1y)
            
            # Identify key risk factors
            key_risk_factors = self._identify_risk_factors(financial_ratios, financial_data)
            
            return DefaultProbability(
                supplier_id=supplier_id,
                probability_1y=prob_1y,
                probability_3y=prob_3y,
                probability_5y=prob_5y,
                risk_grade=risk_grade,
                key_risk_factors=key_risk_factors,
                financial_ratios=financial_ratios,
                model_confidence=self.model_performance['default']['accuracy']
            )
            
        except Exception as e:
            logger.error(f"Error calculating default probability: {e}")
            raise
    
    async def generate_scenario_analysis(
        self,
        entity_id: str,
        scenarios: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate scenario analysis for different market conditions
        """
        try:
            results = {}
            
            for scenario in scenarios:
                scenario_name = scenario.get("name", "Unnamed Scenario")
                
                # Adjust model parameters based on scenario
                adjusted_forecast = await self._forecast_under_scenario(
                    entity_id, scenario
                )
                
                results[scenario_name] = {
                    "cash_flow_impact": adjusted_forecast["cash_flow_change"],
                    "volatility_impact": adjusted_forecast["volatility_change"],
                    "risk_impact": adjusted_forecast["risk_change"],
                    "probability": scenario.get("probability", 0.1),
                    "key_assumptions": adjusted_forecast["assumptions"]
                }
            
            return {
                "entity_id": entity_id,
                "scenarios": results,
                "base_case": await self.forecast_cash_flows(entity_id, 90),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating scenario analysis: {e}")
            raise
    
    async def retrain_models(self, force_retrain: bool = False) -> Dict[str, Any]:
        """
        Retrain predictive models when accuracy falls below threshold
        """
        try:
            retrain_results = {}
            
            # Check if retraining is needed
            for model_name, performance in self.model_performance.items():
                if performance["accuracy"] < 0.85 or force_retrain:
                    logger.info(f"Retraining {model_name} model")
                    
                    if model_name == "cash_flow":
                        new_accuracy = await self._retrain_cash_flow_model()
                    elif model_name == "volatility":
                        new_accuracy = await self._retrain_volatility_model()
                    elif model_name == "default":
                        new_accuracy = await self._retrain_default_model()
                    
                    retrain_results[model_name] = {
                        "old_accuracy": performance["accuracy"],
                        "new_accuracy": new_accuracy,
                        "retrained_at": datetime.now(timezone.utc).isoformat()
                    }
                    
                    # Update performance tracking
                    self.model_performance[model_name]["accuracy"] = new_accuracy
                    self.model_performance[model_name]["last_retrain"] = datetime.now(timezone.utc)
            
            return retrain_results
            
        except Exception as e:
            logger.error(f"Error retraining models: {e}")
            raise
    
    # Helper methods for mock implementations
    
    def _generate_historical_cash_flows(self, entity_id: str, days: int) -> List[Dict[str, Any]]:
        """Generate mock historical cash flow data"""
        np.random.seed(42)  # For reproducible results
        
        base_flow = 1000000  # $1M base daily flow
        data = []
        
        for i in range(days):
            date = datetime.now(timezone.utc) - timedelta(days=days-i)
            
            # Add seasonality and trends
            seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * i / 365)
            trend_factor = 1 + 0.001 * i  # Slight upward trend
            noise = np.random.normal(0, 0.1)
            
            daily_flow = base_flow * seasonal_factor * trend_factor * (1 + noise)
            
            data.append({
                "date": date,
                "cash_flow": daily_flow,
                "day_of_week": date.weekday(),
                "month": date.month,
                "is_month_end": date.day >= 28
            })
        
        return data
    
    def _prepare_cash_flow_features(self, historical_data: List[Dict[str, Any]]) -> np.ndarray:
        """Prepare features for cash flow forecasting"""
        features = []
        
        for record in historical_data[-30:]:  # Last 30 days
            features.append([
                record["day_of_week"],
                record["month"],
                int(record["is_month_end"]),
                record["cash_flow"]
            ])
        
        return np.array(features)
    
    def _create_day_features(self, date: datetime, historical_data: List[Dict[str, Any]]) -> List[float]:
        """Create features for a specific forecast day"""
        return [
            date.weekday(),
            date.month,
            int(date.day >= 28),
            np.mean([d["cash_flow"] for d in historical_data[-7:]])  # 7-day average
        ]
    
    def _predict_daily_cash_flow(self, features: List[float]) -> float:
        """Predict daily cash flow (mock implementation)"""
        # Simple mock prediction based on features
        base_flow = features[3]  # Use 7-day average as base
        
        # Adjust for day of week (weekends typically lower)
        day_adjustment = 0.8 if features[0] >= 5 else 1.0
        
        # Adjust for month-end (typically higher)
        month_end_adjustment = 1.2 if features[2] else 1.0
        
        return base_flow * day_adjustment * month_end_adjustment * np.random.uniform(0.9, 1.1)
    
    def _get_seasonal_factor(self, date: datetime) -> float:
        """Calculate seasonal factor for a given date"""
        day_of_year = date.timetuple().tm_yday
        return 1 + 0.1 * np.sin(2 * np.pi * day_of_year / 365)
    
    async def _get_market_data_for_volatility(self, asset_class: str) -> Dict[str, Any]:
        """Get market data for volatility analysis (mock)"""
        np.random.seed(42)
        
        # Generate mock price series
        days = 252  # 1 year of trading days
        initial_price = 100
        returns = np.random.normal(0.0005, 0.02, days)  # Daily returns
        prices = [initial_price]
        
        for ret in returns:
            prices.append(prices[-1] * (1 + ret))
        
        return {
            "asset_class": asset_class,
            "prices": prices,
            "returns": returns,
            "dates": [datetime.now(timezone.utc) - timedelta(days=days-i) for i in range(days)]
        }
    
    def _prepare_volatility_features(self, market_data: Dict[str, Any]) -> List[float]:
        """Prepare features for volatility prediction"""
        returns = market_data["returns"]
        
        # Calculate various volatility measures
        vol_5d = np.std(returns[-5:]) * np.sqrt(252)
        vol_20d = np.std(returns[-20:]) * np.sqrt(252)
        vol_60d = np.std(returns[-60:]) * np.sqrt(252)
        
        # Calculate other features
        skewness = float(pd.Series(returns[-60:]).skew())
        kurtosis = float(pd.Series(returns[-60:]).kurtosis())
        
        return [vol_5d, vol_20d, vol_60d, skewness, kurtosis]
    
    def _predict_volatility(self, features: List[float], current_vol: float) -> float:
        """Predict future volatility (mock implementation)"""
        # Simple mock prediction
        short_term_vol = features[0]
        medium_term_vol = features[1]
        
        # Weighted average with some noise
        predicted = 0.3 * short_term_vol + 0.5 * medium_term_vol + 0.2 * current_vol
        return predicted * np.random.uniform(0.95, 1.05)
    
    def _analyze_volatility_drivers(self, asset_class: str, market_data: Dict[str, Any]) -> List[str]:
        """Analyze key volatility drivers"""
        drivers = [
            "Interest rate uncertainty",
            "Economic policy changes",
            "Market sentiment shifts",
            "Geopolitical events",
            "Sector-specific factors"
        ]
        
        # Return top 3 drivers for the asset class
        return drivers[:3]
    
    def _calculate_financial_ratios(self, financial_data: Dict[str, Any]) -> Dict[str, float]:
        """Calculate key financial ratios for credit analysis"""
        # Mock financial ratios calculation
        revenue = financial_data.get("revenue", 100000000)
        total_debt = financial_data.get("total_debt", 20000000)
        current_assets = financial_data.get("current_assets", 30000000)
        current_liabilities = financial_data.get("current_liabilities", 15000000)
        ebitda = financial_data.get("ebitda", 15000000)
        
        return {
            "debt_to_revenue": total_debt / revenue if revenue > 0 else 0,
            "current_ratio": current_assets / current_liabilities if current_liabilities > 0 else 0,
            "debt_to_ebitda": total_debt / ebitda if ebitda > 0 else 0,
            "interest_coverage": ebitda / financial_data.get("interest_expense", 1000000),
            "working_capital_ratio": (current_assets - current_liabilities) / revenue if revenue > 0 else 0
        }
    
    def _prepare_default_features(self, ratios: Dict[str, float], financial_data: Dict[str, Any]) -> List[float]:
        """Prepare features for default probability prediction"""
        return [
            ratios["debt_to_revenue"],
            ratios["current_ratio"],
            ratios["debt_to_ebitda"],
            ratios["interest_coverage"],
            ratios["working_capital_ratio"],
            financial_data.get("years_in_business", 10),
            financial_data.get("industry_risk_score", 5)  # 1-10 scale
        ]
    
    def _predict_default_probability(self, features: List[float], horizon: int) -> float:
        """Predict default probability (mock implementation)"""
        # Simple scoring model
        debt_ratio = features[0]
        current_ratio = features[1]
        debt_to_ebitda = features[2]
        
        # Base probability calculation
        base_prob = 0.02  # 2% base probability
        
        # Adjust for financial health
        if debt_ratio > 0.5:
            base_prob *= 2
        if current_ratio < 1.2:
            base_prob *= 1.5
        if debt_to_ebitda > 4:
            base_prob *= 1.8
        
        # Adjust for time horizon
        horizon_adjustment = 1 + (horizon - 1) * 0.3
        
        return min(base_prob * horizon_adjustment, 0.5)  # Cap at 50%
    
    def _determine_risk_grade(self, prob_1y: float) -> str:
        """Determine credit risk grade based on 1-year default probability"""
        if prob_1y < 0.01:
            return "AAA"
        elif prob_1y < 0.02:
            return "AA"
        elif prob_1y < 0.05:
            return "A"
        elif prob_1y < 0.10:
            return "BBB"
        elif prob_1y < 0.20:
            return "BB"
        elif prob_1y < 0.35:
            return "B"
        else:
            return "CCC"
    
    def _identify_risk_factors(self, ratios: Dict[str, float], financial_data: Dict[str, Any]) -> List[str]:
        """Identify key risk factors for default probability"""
        risk_factors = []
        
        if ratios["debt_to_revenue"] > 0.3:
            risk_factors.append("High debt-to-revenue ratio")
        if ratios["current_ratio"] < 1.2:
            risk_factors.append("Low liquidity position")
        if ratios["debt_to_ebitda"] > 4:
            risk_factors.append("High leverage relative to earnings")
        if ratios["interest_coverage"] < 2.5:
            risk_factors.append("Weak interest coverage")
        if financial_data.get("years_in_business", 10) < 5:
            risk_factors.append("Limited operating history")
        
        return risk_factors[:5]  # Return top 5 risk factors
    
    async def _forecast_under_scenario(self, entity_id: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate forecast under specific scenario conditions"""
        # Mock scenario analysis
        scenario_type = scenario.get("type", "base")
        
        adjustments = {
            "recession": {"cash_flow_change": -0.15, "volatility_change": 0.4, "risk_change": 0.3},
            "expansion": {"cash_flow_change": 0.10, "volatility_change": -0.1, "risk_change": -0.1},
            "crisis": {"cash_flow_change": -0.25, "volatility_change": 0.8, "risk_change": 0.5},
            "base": {"cash_flow_change": 0.0, "volatility_change": 0.0, "risk_change": 0.0}
        }
        
        adjustment = adjustments.get(scenario_type, adjustments["base"])
        adjustment["assumptions"] = [
            f"Scenario: {scenario.get('name', 'Unnamed')}",
            f"Probability: {scenario.get('probability', 0.1):.1%}",
            f"Duration: {scenario.get('duration_months', 12)} months"
        ]
        
        return adjustment
    
    async def _retrain_cash_flow_model(self) -> float:
        """Retrain cash flow forecasting model"""
        # Mock retraining - in practice, this would use new data
        new_accuracy = np.random.uniform(0.85, 0.92)
        logger.info(f"Cash flow model retrained with accuracy: {new_accuracy:.3f}")
        return new_accuracy
    
    async def _retrain_volatility_model(self) -> float:
        """Retrain volatility prediction model"""
        # Mock retraining
        new_accuracy = np.random.uniform(0.78, 0.85)
        logger.info(f"Volatility model retrained with accuracy: {new_accuracy:.3f}")
        return new_accuracy
    
    async def _retrain_default_model(self) -> float:
        """Retrain default probability model"""
        # Mock retraining
        new_accuracy = np.random.uniform(0.82, 0.88)
        logger.info(f"Default model retrained with accuracy: {new_accuracy:.3f}")
        return new_accuracy