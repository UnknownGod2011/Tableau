"""
Treasury Analytics API endpoints - Cash optimization and forecasting
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

from app.services.analytics import TreasuryAnalyticsEngine, OptimizationResult, CashFlowForecast, LiquidityAnalysis
from app.services.market_data import MarketDataIngestionPipeline
from app.models import CashPosition
from app.core.database import get_db
from sqlalchemy.orm import Session

logger = structlog.get_logger(__name__)

router = APIRouter()

# Global services
market_data_service = MarketDataIngestionPipeline()
analytics_engine = TreasuryAnalyticsEngine(market_data_service)


@router.post("/cash-optimization", response_model=Dict[str, Any])
async def optimize_cash_allocation(
    entity_id: str,
    constraints: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db)
):
    """
    Calculate optimal cash allocation for an entity
    
    This endpoint implements Property 1: Cash Optimization Detection
    """
    try:
        # Get cash positions for entity (mock data for demo)
        cash_positions = _get_demo_cash_positions(entity_id)
        
        if not cash_positions:
            raise HTTPException(status_code=404, detail=f"No cash positions found for entity {entity_id}")
        
        # Run optimization
        optimization_result = await analytics_engine.calculate_optimal_cash_allocation(
            cash_positions, constraints
        )
        
        return {
            "entity_id": entity_id,
            "optimization_timestamp": optimization_result.analysis_date.isoformat(),
            "current_yield": float(optimization_result.current_yield),
            "optimal_yield": float(optimization_result.optimal_yield),
            "opportunity_cost": float(optimization_result.opportunity_cost),
            "annual_savings_potential": float(optimization_result.opportunity_cost),
            "confidence_score": optimization_result.confidence,
            "recommendations": optimization_result.recommendations,
            "summary": {
                "total_positions": len(cash_positions),
                "total_balance": float(sum(pos.balance for pos in cash_positions)),
                "yield_improvement": float(optimization_result.optimal_yield - optimization_result.current_yield),
                "optimization_quality": "excellent" if optimization_result.confidence > 0.8 else "good" if optimization_result.confidence > 0.6 else "fair"
            }
        }
        
    except Exception as e:
        logger.error("Cash optimization failed", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Cash optimization failed: {str(e)}")


@router.get("/opportunities/{entity_id}", response_model=Dict[str, Any])
async def detect_optimization_opportunities(
    entity_id: str,
    threshold_amount: float = Query(1000000, description="Minimum opportunity cost threshold in USD"),
    db: Session = Depends(get_db)
):
    """
    Detect cash optimization opportunities above threshold
    
    This endpoint implements Property 1: Cash Optimization Detection
    """
    try:
        # Get cash positions
        cash_positions = _get_demo_cash_positions(entity_id)
        
        if not cash_positions:
            raise HTTPException(status_code=404, detail=f"No cash positions found for entity {entity_id}")
        
        # Detect opportunities
        opportunities = await analytics_engine.detect_optimization_opportunities(
            cash_positions, 
            threshold_amount=threshold_amount
        )
        
        # Calculate summary metrics
        total_opportunity_cost = sum(opp["opportunity_cost"] for opp in opportunities)
        high_priority_count = sum(1 for opp in opportunities if opp["priority"] == "high")
        
        return {
            "entity_id": entity_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "threshold_amount": threshold_amount,
            "opportunities_found": len(opportunities),
            "total_opportunity_cost": total_opportunity_cost,
            "high_priority_opportunities": high_priority_count,
            "opportunities": opportunities,
            "summary": {
                "potential_annual_savings": total_opportunity_cost,
                "average_opportunity_size": total_opportunity_cost / len(opportunities) if opportunities else 0,
                "largest_opportunity": max((opp["opportunity_cost"] for opp in opportunities), default=0),
                "recommendation": "Immediate action recommended" if high_priority_count > 0 else "Monitor opportunities"
            }
        }
        
    except Exception as e:
        logger.error("Opportunity detection failed", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Opportunity detection failed: {str(e)}")


@router.post("/cash-flow-forecast", response_model=Dict[str, Any])
async def generate_cash_flow_forecast(
    entity_id: str,
    forecast_days: int = Query(90, ge=1, le=365, description="Number of days to forecast"),
    include_confidence_intervals: bool = Query(True, description="Include confidence intervals"),
    db: Session = Depends(get_db)
):
    """
    Generate cash flow forecast for an entity
    
    This endpoint implements Property 16: Cash Flow Forecasting
    """
    try:
        # Generate forecast (using synthetic data for demo)
        forecast = await analytics_engine.forecast_cash_flow(
            entity_id=entity_id,
            historical_data=[],  # Will generate synthetic data
            forecast_days=forecast_days
        )
        
        # Prepare response
        response = {
            "entity_id": entity_id,
            "forecast_generated": datetime.now().isoformat(),
            "forecast_horizon_days": forecast.forecast_horizon_days,
            "forecast_accuracy": forecast.forecast_accuracy,
            "key_assumptions": forecast.key_assumptions,
            "daily_forecasts": forecast.daily_forecasts if forecast_days <= 30 else forecast.daily_forecasts[::7],  # Weekly for long forecasts
            "summary": {
                "total_forecasted_flow": sum(f["forecasted_cash_flow"] for f in forecast.daily_forecasts),
                "average_daily_flow": sum(f["forecasted_cash_flow"] for f in forecast.daily_forecasts) / len(forecast.daily_forecasts),
                "positive_flow_days": sum(1 for f in forecast.daily_forecasts if f["forecasted_cash_flow"] > 0),
                "negative_flow_days": sum(1 for f in forecast.daily_forecasts if f["forecasted_cash_flow"] < 0),
                "volatility_assessment": "high" if forecast.forecast_accuracy < 0.7 else "medium" if forecast.forecast_accuracy < 0.85 else "low"
            }
        }
        
        if not include_confidence_intervals:
            # Remove confidence interval data to reduce response size
            for forecast_day in response["daily_forecasts"]:
                forecast_day.pop("confidence_lower", None)
                forecast_day.pop("confidence_upper", None)
        
        return response
        
    except Exception as e:
        logger.error("Cash flow forecasting failed", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Cash flow forecasting failed: {str(e)}")


@router.post("/liquidity-analysis", response_model=Dict[str, Any])
async def analyze_liquidity_requirements(
    entity_id: str,
    include_stress_tests: bool = Query(True, description="Include stress test scenarios"),
    stress_scenarios: Optional[List[str]] = Query(None, description="Custom stress scenarios"),
    db: Session = Depends(get_db)
):
    """
    Analyze liquidity requirements and stress test scenarios
    
    This endpoint implements Property 3: Liquidity Shortfall Response
    """
    try:
        # Get cash positions
        cash_positions = _get_demo_cash_positions(entity_id)
        
        if not cash_positions:
            raise HTTPException(status_code=404, detail=f"No cash positions found for entity {entity_id}")
        
        # Run liquidity analysis
        liquidity_analysis = await analytics_engine.analyze_liquidity_requirements(
            cash_positions=cash_positions,
            stress_scenarios=stress_scenarios if include_stress_tests else []
        )
        
        return {
            "entity_id": entity_id,
            "analysis_timestamp": datetime.now().isoformat(),
            "current_liquidity_ratio": liquidity_analysis.current_liquidity_ratio,
            "liquidity_gap": float(liquidity_analysis.liquidity_gap),
            "recommended_buffer": float(liquidity_analysis.recommended_buffer),
            "risk_level": liquidity_analysis.risk_level,
            "stress_test_results": liquidity_analysis.stress_test_results if include_stress_tests else {},
            "assessment": {
                "liquidity_adequacy": "adequate" if liquidity_analysis.current_liquidity_ratio >= 0.25 else "insufficient",
                "buffer_adequacy": "adequate" if liquidity_analysis.liquidity_gap >= 0 else "insufficient",
                "overall_risk": liquidity_analysis.risk_level,
                "immediate_action_required": liquidity_analysis.risk_level in ["high", "critical"]
            },
            "recommendations": _generate_liquidity_recommendations(liquidity_analysis)
        }
        
    except Exception as e:
        logger.error("Liquidity analysis failed", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Liquidity analysis failed: {str(e)}")


@router.get("/comprehensive-analysis/{entity_id}", response_model=Dict[str, Any])
async def get_comprehensive_treasury_analysis(
    entity_id: str,
    include_forecasting: bool = Query(True, description="Include cash flow forecasting"),
    include_liquidity: bool = Query(True, description="Include liquidity analysis"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive treasury analysis combining all analytics
    
    This endpoint implements Property 4: Comprehensive Optimization Recommendations
    """
    try:
        # Get cash positions
        cash_positions = _get_demo_cash_positions(entity_id)
        
        if not cash_positions:
            raise HTTPException(status_code=404, detail=f"No cash positions found for entity {entity_id}")
        
        # Generate comprehensive recommendations
        recommendations = await analytics_engine.generate_comprehensive_recommendations(
            entity_id=entity_id,
            cash_positions=cash_positions,
            include_forecasting=include_forecasting,
            include_liquidity_analysis=include_liquidity
        )
        
        return recommendations
        
    except Exception as e:
        logger.error("Comprehensive analysis failed", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")


@router.post("/market-recalculation", response_model=Dict[str, Any])
async def trigger_market_driven_recalculation(
    entity_id: str,
    previous_analysis_date: str,
    market_change_threshold: float = Query(0.25, description="Market change threshold in basis points"),
    db: Session = Depends(get_db)
):
    """
    Trigger recalculation when market conditions change significantly
    
    This endpoint implements Property 2: Market-Driven Recalculation
    """
    try:
        # Get cash positions
        cash_positions = _get_demo_cash_positions(entity_id)
        
        if not cash_positions:
            raise HTTPException(status_code=404, detail=f"No cash positions found for entity {entity_id}")
        
        # Create mock previous optimization for comparison
        previous_optimization = OptimizationResult(
            current_yield=Decimal("3.5"),
            optimal_yield=Decimal("4.2"),
            opportunity_cost=Decimal("500000"),
            recommendations=[],
            confidence=0.85,
            analysis_date=datetime.fromisoformat(previous_analysis_date)
        )
        
        # Check for market-driven recalculation
        new_optimization = await analytics_engine.recalculate_on_market_change(
            positions=cash_positions,
            previous_optimization=previous_optimization,
            market_change_threshold=market_change_threshold
        )
        
        if new_optimization is None:
            return {
                "entity_id": entity_id,
                "recalculation_triggered": False,
                "message": "No significant market change detected",
                "threshold_used": market_change_threshold,
                "analysis_timestamp": datetime.now().isoformat()
            }
        
        return {
            "entity_id": entity_id,
            "recalculation_triggered": True,
            "previous_analysis_date": previous_analysis_date,
            "new_analysis_date": new_optimization.analysis_date.isoformat(),
            "market_change_threshold": market_change_threshold,
            "optimization_changes": {
                "previous_optimal_yield": float(previous_optimization.optimal_yield),
                "new_optimal_yield": float(new_optimization.optimal_yield),
                "yield_change": float(new_optimization.optimal_yield - previous_optimization.optimal_yield),
                "previous_opportunity_cost": float(previous_optimization.opportunity_cost),
                "new_opportunity_cost": float(new_optimization.opportunity_cost),
                "opportunity_cost_change": float(new_optimization.opportunity_cost - previous_optimization.opportunity_cost)
            },
            "new_recommendations": new_optimization.recommendations,
            "confidence_score": new_optimization.confidence
        }
        
    except Exception as e:
        logger.error("Market-driven recalculation failed", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Market-driven recalculation failed: {str(e)}")


def _get_demo_cash_positions(entity_id: str) -> List[CashPosition]:
    """Generate demo cash positions for testing"""
    from app.models.cash import AccountType, LiquidityTier
    from decimal import Decimal
    import uuid
    
    # Generate consistent demo data based on entity_id
    seed = hash(entity_id) % 1000
    
    positions = [
        CashPosition(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            account_name=f"Primary Checking - {entity_id}",
            account_type=AccountType.CHECKING,
            currency="USD",
            balance=Decimal(str(5000000 + seed * 1000)),  # $5M base
            interest_rate=Decimal("0.50"),
            bank_name="JPMorgan Chase",
            liquidity_tier=LiquidityTier.IMMEDIATE,
            maturity_date=None
        ),
        CashPosition(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            account_name=f"High-Yield Savings - {entity_id}",
            account_type=AccountType.SAVINGS,
            currency="USD",
            balance=Decimal(str(15000000 + seed * 2000)),  # $15M base
            interest_rate=Decimal("3.25"),
            bank_name="Goldman Sachs",
            liquidity_tier=LiquidityTier.SHORT_TERM,
            maturity_date=None
        ),
        CashPosition(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            account_name=f"Money Market Fund - {entity_id}",
            account_type=AccountType.MONEY_MARKET,
            currency="USD",
            balance=Decimal(str(25000000 + seed * 3000)),  # $25M base
            interest_rate=Decimal("4.15"),
            bank_name="Fidelity",
            liquidity_tier=LiquidityTier.SHORT_TERM,
            maturity_date=None
        ),
        CashPosition(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            account_name=f"6-Month CD - {entity_id}",
            account_type=AccountType.CD,
            currency="USD",
            balance=Decimal(str(10000000 + seed * 1500)),  # $10M base
            interest_rate=Decimal("4.75"),
            bank_name="Bank of America",
            liquidity_tier=LiquidityTier.MEDIUM_TERM,
            maturity_date=datetime.now() + timedelta(days=180)
        ),
        CashPosition(
            id=str(uuid.uuid4()),
            entity_id=entity_id,
            account_name=f"Treasury Bills - {entity_id}",
            account_type=AccountType.TREASURY,
            currency="USD",
            balance=Decimal(str(20000000 + seed * 2500)),  # $20M base
            interest_rate=Decimal("5.10"),
            bank_name="US Treasury",
            liquidity_tier=LiquidityTier.SHORT_TERM,
            maturity_date=datetime.now() + timedelta(days=91)
        )
    ]
    
    return positions


def _generate_liquidity_recommendations(analysis: LiquidityAnalysis) -> List[Dict[str, Any]]:
    """Generate liquidity management recommendations"""
    recommendations = []
    
    if analysis.risk_level == "critical":
        recommendations.extend([
            {
                "priority": "immediate",
                "action": "Increase immediate liquidity reserves",
                "description": f"Current liquidity ratio of {analysis.current_liquidity_ratio:.1%} is critically low",
                "target": "Achieve minimum 20% immediate liquidity ratio"
            },
            {
                "priority": "immediate", 
                "action": "Review and extend credit facilities",
                "description": "Establish backup liquidity sources",
                "target": "Secure committed credit lines equal to 30-day cash needs"
            }
        ])
    
    elif analysis.risk_level == "high":
        recommendations.append({
            "priority": "high",
            "action": "Optimize liquidity buffer",
            "description": f"Increase liquidity buffer by ${float(analysis.recommended_buffer - analysis.liquidity_gap):,.0f}",
            "target": f"Maintain ${float(analysis.recommended_buffer):,.0f} liquidity buffer"
        })
    
    elif analysis.risk_level == "medium":
        recommendations.append({
            "priority": "medium",
            "action": "Monitor liquidity trends",
            "description": "Liquidity levels are adequate but should be monitored",
            "target": "Maintain current liquidity levels with regular review"
        })
    
    else:  # low risk
        recommendations.append({
            "priority": "low",
            "action": "Consider yield optimization",
            "description": "Excess liquidity may be optimized for higher returns",
            "target": "Balance liquidity needs with yield optimization"
        })
    
    return recommendations