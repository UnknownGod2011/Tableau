"""
Predictive Analytics API endpoints
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.database import get_db
from ....services.predictive_analytics import PredictiveAnalyticsService
from ....services.market_data import MarketDataService

router = APIRouter()


# Request/Response Models
class CashFlowForecastRequest(BaseModel):
    """Cash flow forecast request"""
    entity_id: str = Field(..., description="Entity ID for forecasting")
    forecast_horizon_days: int = Field(90, ge=1, le=365, description="Forecast horizon in days")
    confidence_level: float = Field(0.95, ge=0.8, le=0.99, description="Confidence level for intervals")


class CashFlowForecastResponse(BaseModel):
    """Cash flow forecast response"""
    entity_id: str
    forecast_horizon_days: int
    daily_forecasts: List[Dict[str, Any]]
    confidence_intervals: Dict[str, List[float]]
    key_assumptions: List[str]
    forecast_accuracy: Optional[float]
    model_version: str
    generated_at: datetime


class VolatilityForecastRequest(BaseModel):
    """Market volatility forecast request"""
    asset_class: str = Field(..., description="Asset class for volatility prediction")
    forecast_horizon_days: int = Field(30, ge=1, le=180, description="Forecast horizon in days")


class VolatilityForecastResponse(BaseModel):
    """Market volatility forecast response"""
    asset_class: str
    forecast_horizon_days: int
    predicted_volatility: float
    confidence_level: float
    historical_volatility: float
    volatility_regime: str
    key_drivers: List[str]
    model_accuracy: Optional[float]


class DefaultProbabilityRequest(BaseModel):
    """Default probability calculation request"""
    supplier_id: str = Field(..., description="Supplier ID for analysis")
    financial_data: Dict[str, Any] = Field(..., description="Financial data for analysis")


class DefaultProbabilityResponse(BaseModel):
    """Default probability response"""
    supplier_id: str
    probability_1y: float
    probability_3y: float
    probability_5y: float
    risk_grade: str
    key_risk_factors: List[str]
    financial_ratios: Dict[str, float]
    model_confidence: float


class ScenarioAnalysisRequest(BaseModel):
    """Scenario analysis request"""
    entity_id: str = Field(..., description="Entity ID for analysis")
    scenarios: List[Dict[str, Any]] = Field(..., description="List of scenarios to analyze")


class ScenarioAnalysisResponse(BaseModel):
    """Scenario analysis response"""
    entity_id: str
    scenarios: Dict[str, Any]
    base_case: Dict[str, Any]
    generated_at: str


class ModelRetrainRequest(BaseModel):
    """Model retraining request"""
    force_retrain: bool = Field(False, description="Force retraining regardless of performance")
    models: Optional[List[str]] = Field(None, description="Specific models to retrain")


@router.post("/cash-flow-forecast", response_model=CashFlowForecastResponse)
async def forecast_cash_flows(
    request: CashFlowForecastRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate cash flow forecasts using time series analysis and machine learning
    """
    try:
        # Initialize services
        market_data_service = MarketDataService()
        predictive_service = PredictiveAnalyticsService(market_data_service)
        
        # Generate forecast
        forecast = await predictive_service.forecast_cash_flows(
            entity_id=request.entity_id,
            forecast_horizon_days=request.forecast_horizon_days,
            confidence_level=request.confidence_level
        )
        
        return CashFlowForecastResponse(
            entity_id=forecast.entity_id,
            forecast_horizon_days=forecast.forecast_horizon_days,
            daily_forecasts=forecast.daily_forecasts,
            confidence_intervals=forecast.confidence_intervals,
            key_assumptions=forecast.key_assumptions,
            forecast_accuracy=forecast.forecast_accuracy,
            model_version=forecast.model_version,
            generated_at=forecast.generated_at
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating cash flow forecast: {str(e)}"
        )


@router.post("/volatility-forecast", response_model=VolatilityForecastResponse)
async def predict_market_volatility(
    request: VolatilityForecastRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Predict market volatility changes using machine learning models
    """
    try:
        # Initialize services
        market_data_service = MarketDataService()
        predictive_service = PredictiveAnalyticsService(market_data_service)
        
        # Generate volatility forecast
        forecast = await predictive_service.predict_market_volatility(
            asset_class=request.asset_class,
            forecast_horizon_days=request.forecast_horizon_days
        )
        
        return VolatilityForecastResponse(
            asset_class=forecast.asset_class,
            forecast_horizon_days=forecast.forecast_horizon_days,
            predicted_volatility=forecast.predicted_volatility,
            confidence_level=forecast.confidence_level,
            historical_volatility=forecast.historical_volatility,
            volatility_regime=forecast.volatility_regime,
            key_drivers=forecast.key_drivers,
            model_accuracy=forecast.model_accuracy
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error predicting market volatility: {str(e)}"
        )


@router.post("/default-probability", response_model=DefaultProbabilityResponse)
async def calculate_default_probability(
    request: DefaultProbabilityRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate supplier default probability using credit risk models
    """
    try:
        # Initialize services
        market_data_service = MarketDataService()
        predictive_service = PredictiveAnalyticsService(market_data_service)
        
        # Calculate default probability
        result = await predictive_service.calculate_default_probability(
            supplier_id=request.supplier_id,
            financial_data=request.financial_data
        )
        
        return DefaultProbabilityResponse(
            supplier_id=result.supplier_id,
            probability_1y=result.probability_1y,
            probability_3y=result.probability_3y,
            probability_5y=result.probability_5y,
            risk_grade=result.risk_grade,
            key_risk_factors=result.key_risk_factors,
            financial_ratios=result.financial_ratios,
            model_confidence=result.model_confidence
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating default probability: {str(e)}"
        )


@router.post("/scenario-analysis", response_model=ScenarioAnalysisResponse)
async def generate_scenario_analysis(
    request: ScenarioAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Generate scenario analysis for different market conditions
    """
    try:
        # Initialize services
        market_data_service = MarketDataService()
        predictive_service = PredictiveAnalyticsService(market_data_service)
        
        # Generate scenario analysis
        result = await predictive_service.generate_scenario_analysis(
            entity_id=request.entity_id,
            scenarios=request.scenarios
        )
        
        return ScenarioAnalysisResponse(
            entity_id=result["entity_id"],
            scenarios=result["scenarios"],
            base_case=result["base_case"].__dict__,
            generated_at=result["generated_at"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating scenario analysis: {str(e)}"
        )


@router.post("/retrain-models")
async def retrain_predictive_models(
    request: ModelRetrainRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrain predictive models when accuracy falls below threshold
    """
    try:
        # Initialize services
        market_data_service = MarketDataService()
        predictive_service = PredictiveAnalyticsService(market_data_service)
        
        # Retrain models
        results = await predictive_service.retrain_models(
            force_retrain=request.force_retrain
        )
        
        return {
            "message": "Model retraining completed",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retraining models: {str(e)}"
        )


@router.get("/model-performance")
async def get_model_performance(
    db: AsyncSession = Depends(get_db)
):
    """
    Get current model performance metrics
    """
    try:
        # Initialize services
        market_data_service = MarketDataService()
        predictive_service = PredictiveAnalyticsService(market_data_service)
        
        return {
            "model_performance": predictive_service.model_performance,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving model performance: {str(e)}"
        )


@router.get("/forecast-accuracy/{entity_id}")
async def get_forecast_accuracy(
    entity_id: str,
    days_back: int = Query(30, ge=1, le=365, description="Days to look back for accuracy calculation"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get historical forecast accuracy for an entity
    """
    try:
        # Mock accuracy calculation
        # In production, this would compare historical forecasts with actual results
        accuracy_data = {
            "entity_id": entity_id,
            "days_analyzed": days_back,
            "cash_flow_accuracy": 0.87,
            "volatility_accuracy": 0.79,
            "accuracy_trend": "improving",
            "last_updated": datetime.now().isoformat(),
            "accuracy_by_horizon": {
                "1_day": 0.92,
                "7_day": 0.89,
                "30_day": 0.85,
                "90_day": 0.81
            }
        }
        
        return accuracy_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating forecast accuracy: {str(e)}"
        )


@router.get("/health")
async def predictive_health_check():
    """
    Health check for predictive analytics services
    """
    try:
        # Initialize services to check availability
        market_data_service = MarketDataService()
        predictive_service = PredictiveAnalyticsService(market_data_service)
        
        return {
            "status": "healthy",
            "models_loaded": {
                "cash_flow": predictive_service.cash_flow_model is not None,
                "volatility": predictive_service.volatility_model is not None,
                "default": predictive_service.default_model is not None
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }