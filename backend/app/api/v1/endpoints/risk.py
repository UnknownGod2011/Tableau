"""
Risk management API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Optional
from datetime import datetime, timedelta
import structlog

from app.core.database import get_db
from app.models import CorporateEntity, CashPosition, Investment, FXExposure, RiskMetrics, RiskAlert
from app.services.risk import RiskCalculationService
from app.services.market_data import MarketDataService

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/calculate-var/{entity_id}")
async def calculate_portfolio_var(
    entity_id: str,
    confidence_level: float = Query(0.95, ge=0.01, le=0.99),
    time_horizon: int = Query(1, ge=1, le=30),
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate Value at Risk for entity's portfolio
    Property 9: Continuous VaR Monitoring
    """
    try:
        # Verify entity exists
        entity_result = await db.execute(
            select(CorporateEntity).where(CorporateEntity.id == entity_id)
        )
        entity = entity_result.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Get portfolio components
        cash_result = await db.execute(
            select(CashPosition).where(CashPosition.entity_id == entity_id)
        )
        cash_positions = cash_result.scalars().all()
        
        investments_result = await db.execute(
            select(Investment).where(Investment.entity_id == entity_id)
        )
        investments = investments_result.scalars().all()
        
        fx_result = await db.execute(
            select(FXExposure).where(FXExposure.entity_id == entity_id)
        )
        fx_exposures = fx_result.scalars().all()
        
        # Initialize services
        market_data_service = MarketDataService()
        risk_service = RiskCalculationService(market_data_service)
        
        # Calculate VaR
        var_result = await risk_service.calculate_portfolio_var(
            cash_positions=list(cash_positions),
            investments=list(investments),
            fx_exposures=list(fx_exposures),
            confidence_level=confidence_level,
            time_horizon=time_horizon
        )
        
        # Store results in database
        risk_metrics = RiskMetrics(
            entity_id=entity_id,
            calculation_date=datetime.utcnow(),
            calculation_method=var_result.calculation_method,
            confidence_level=confidence_level,
            time_horizon_days=time_horizon,
            portfolio_var_1d=var_result.portfolio_var_1d,
            portfolio_var_10d=var_result.portfolio_var_10d,
            expected_shortfall_1d=var_result.expected_shortfall,
            cash_var_1d=var_result.component_vars.get("cash_var"),
            investment_var_1d=var_result.component_vars.get("investments_var"),
            fx_var_1d=var_result.component_vars.get("fx_var"),
            stress_test_results=dict(var_result.stress_test_results)
        )
        
        db.add(risk_metrics)
        await db.commit()
        await db.refresh(risk_metrics)
        
        return {
            "entity_id": entity_id,
            "calculation_date": risk_metrics.calculation_date,
            "var_results": {
                "portfolio_var_1d": float(var_result.portfolio_var_1d),
                "portfolio_var_10d": float(var_result.portfolio_var_10d),
                "expected_shortfall": float(var_result.expected_shortfall),
                "confidence_level": var_result.confidence_level,
                "calculation_method": var_result.calculation_method
            },
            "component_vars": {k: float(v) for k, v in var_result.component_vars.items()},
            "stress_test_results": {k: float(v) for k, v in var_result.stress_test_results.items()},
            "risk_metrics_id": risk_metrics.id
        }
        
    except Exception as e:
        logger.error("VaR calculation failed", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"VaR calculation failed: {str(e)}")


@router.post("/assess-currency-risk/{entity_id}")
async def assess_currency_risk(
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Assess currency risk for entity's FX exposures
    Property 6: Risk Threshold Response
    """
    try:
        # Verify entity exists
        entity_result = await db.execute(
            select(CorporateEntity).where(CorporateEntity.id == entity_id)
        )
        entity = entity_result.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Get FX exposures
        fx_result = await db.execute(
            select(FXExposure).where(FXExposure.entity_id == entity_id)
        )
        fx_exposures = fx_result.scalars().all()
        
        # Initialize services
        market_data_service = MarketDataService()
        risk_service = RiskCalculationService(market_data_service)
        
        # Assess currency risk
        currency_risk = await risk_service.assess_currency_risk(list(fx_exposures))
        
        # Update risk metrics
        risk_metrics = RiskMetrics(
            entity_id=entity_id,
            calculation_date=datetime.utcnow(),
            calculation_method="currency_risk_assessment",
            total_fx_exposure=currency_risk.total_exposure,
            hedged_fx_exposure=currency_risk.hedged_exposure,
            unhedged_fx_exposure=currency_risk.unhedged_exposure,
            fx_hedge_ratio=currency_risk.hedge_ratio
        )
        
        db.add(risk_metrics)
        await db.commit()
        
        return {
            "entity_id": entity_id,
            "currency_risk_analysis": {
                "total_exposure": float(currency_risk.total_exposure),
                "hedged_exposure": float(currency_risk.hedged_exposure),
                "unhedged_exposure": float(currency_risk.unhedged_exposure),
                "hedge_ratio": currency_risk.hedge_ratio,
                "currency_vars": {k: float(v) for k, v in currency_risk.currency_vars.items()},
                "correlation_matrix": currency_risk.correlation_matrix,
                "hedging_recommendations": currency_risk.hedging_recommendations
            }
        }
        
    except Exception as e:
        logger.error("Currency risk assessment failed", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Currency risk assessment failed: {str(e)}")


@router.get("/metrics/{entity_id}")
async def get_risk_metrics(
    entity_id: str,
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get historical risk metrics for entity"""
    try:
        # Get recent risk metrics
        result = await db.execute(
            select(RiskMetrics)
            .where(RiskMetrics.entity_id == entity_id)
            .order_by(desc(RiskMetrics.calculation_date))
            .limit(limit)
        )
        metrics = result.scalars().all()
        
        return {
            "entity_id": entity_id,
            "metrics": [
                {
                    "id": metric.id,
                    "calculation_date": metric.calculation_date,
                    "calculation_method": metric.calculation_method,
                    "confidence_level": float(metric.confidence_level) if metric.confidence_level else None,
                    "portfolio_var_1d": float(metric.portfolio_var_1d) if metric.portfolio_var_1d else None,
                    "portfolio_var_10d": float(metric.portfolio_var_10d) if metric.portfolio_var_10d else None,
                    "expected_shortfall_1d": float(metric.expected_shortfall_1d) if metric.expected_shortfall_1d else None,
                    "total_fx_exposure": float(metric.total_fx_exposure) if metric.total_fx_exposure else None,
                    "fx_hedge_ratio": float(metric.fx_hedge_ratio) if metric.fx_hedge_ratio else None,
                    "risk_score": metric.risk_score,
                    "stress_test_results": metric.stress_test_results
                }
                for metric in metrics
            ]
        }
        
    except Exception as e:
        logger.error("Failed to get risk metrics", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get risk metrics: {str(e)}")


@router.get("/alerts/{entity_id}")
async def get_risk_alerts(
    entity_id: str,
    active_only: bool = Query(True),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get risk alerts for entity"""
    try:
        # Build query
        query = select(RiskAlert).where(RiskAlert.entity_id == entity_id)
        
        if active_only:
            query = query.where(RiskAlert.resolved_date.is_(None))
        
        if severity:
            query = query.where(RiskAlert.severity == severity)
        
        query = query.order_by(desc(RiskAlert.alert_date)).limit(limit)
        
        result = await db.execute(query)
        alerts = result.scalars().all()
        
        return {
            "entity_id": entity_id,
            "alerts": [
                {
                    "id": alert.id,
                    "alert_type": alert.alert_type,
                    "severity": alert.severity,
                    "title": alert.title,
                    "description": alert.description,
                    "current_value": float(alert.current_value) if alert.current_value else None,
                    "threshold_value": float(alert.threshold_value) if alert.threshold_value else None,
                    "breach_percentage": float(alert.breach_percentage) if alert.breach_percentage else None,
                    "alert_date": alert.alert_date,
                    "acknowledged_date": alert.acknowledged_date,
                    "resolved_date": alert.resolved_date,
                    "is_active": alert.is_active,
                    "days_open": alert.days_open,
                    "recommended_actions": alert.recommended_actions
                }
                for alert in alerts
            ]
        }
        
    except Exception as e:
        logger.error("Failed to get risk alerts", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get risk alerts: {str(e)}")


@router.post("/alerts/{entity_id}/create")
async def create_risk_alert(
    entity_id: str,
    alert_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Create a new risk alert"""
    try:
        # Verify entity exists
        entity_result = await db.execute(
            select(CorporateEntity).where(CorporateEntity.id == entity_id)
        )
        entity = entity_result.scalar_one_or_none()
        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        # Create alert
        alert = RiskAlert(
            entity_id=entity_id,
            alert_type=alert_data.get("alert_type"),
            severity=alert_data.get("severity"),
            title=alert_data.get("title"),
            description=alert_data.get("description"),
            current_value=alert_data.get("current_value"),
            threshold_value=alert_data.get("threshold_value"),
            breach_percentage=alert_data.get("breach_percentage"),
            alert_date=datetime.utcnow(),
            recommended_actions=alert_data.get("recommended_actions")
        )
        
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        
        return {
            "alert_id": alert.id,
            "entity_id": entity_id,
            "message": "Risk alert created successfully"
        }
        
    except Exception as e:
        logger.error("Failed to create risk alert", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create risk alert: {str(e)}")


@router.put("/alerts/{alert_id}/acknowledge")
async def acknowledge_risk_alert(
    alert_id: str,
    acknowledged_by: str,
    db: AsyncSession = Depends(get_db)
):
    """Acknowledge a risk alert"""
    try:
        # Get alert
        result = await db.execute(
            select(RiskAlert).where(RiskAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Update alert
        alert.acknowledged_date = datetime.utcnow()
        alert.acknowledged_by = acknowledged_by
        
        await db.commit()
        
        return {
            "alert_id": alert_id,
            "message": "Alert acknowledged successfully"
        }
        
    except Exception as e:
        logger.error("Failed to acknowledge alert", alert_id=alert_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")


@router.put("/alerts/{alert_id}/resolve")
async def resolve_risk_alert(
    alert_id: str,
    resolved_by: str,
    actions_taken: Optional[dict] = None,
    db: AsyncSession = Depends(get_db)
):
    """Resolve a risk alert"""
    try:
        # Get alert
        result = await db.execute(
            select(RiskAlert).where(RiskAlert.id == alert_id)
        )
        alert = result.scalar_one_or_none()
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        # Update alert
        alert.resolved_date = datetime.utcnow()
        alert.resolved_by = resolved_by
        if actions_taken:
            alert.actions_taken = actions_taken
        
        await db.commit()
        
        return {
            "alert_id": alert_id,
            "message": "Alert resolved successfully"
        }
        
    except Exception as e:
        logger.error("Failed to resolve alert", alert_id=alert_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to resolve alert: {str(e)}")


@router.get("/dashboard/{entity_id}")
async def get_risk_dashboard(
    entity_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get comprehensive risk dashboard data"""
    try:
        # Get latest risk metrics
        metrics_result = await db.execute(
            select(RiskMetrics)
            .where(RiskMetrics.entity_id == entity_id)
            .order_by(desc(RiskMetrics.calculation_date))
            .limit(1)
        )
        latest_metrics = metrics_result.scalar_one_or_none()
        
        # Get active alerts
        alerts_result = await db.execute(
            select(RiskAlert)
            .where(RiskAlert.entity_id == entity_id)
            .where(RiskAlert.resolved_date.is_(None))
            .order_by(desc(RiskAlert.alert_date))
        )
        active_alerts = alerts_result.scalars().all()
        
        # Get portfolio summary
        cash_result = await db.execute(
            select(CashPosition).where(CashPosition.entity_id == entity_id)
        )
        cash_positions = cash_result.scalars().all()
        
        investments_result = await db.execute(
            select(Investment).where(Investment.entity_id == entity_id)
        )
        investments = investments_result.scalars().all()
        
        fx_result = await db.execute(
            select(FXExposure).where(FXExposure.entity_id == entity_id)
        )
        fx_exposures = fx_result.scalars().all()
        
        # Calculate portfolio totals
        total_cash = sum(pos.balance for pos in cash_positions)
        total_investments = sum(inv.market_value or inv.principal_amount for inv in investments)
        total_fx_exposure = sum(fx.notional_amount for fx in fx_exposures)
        
        dashboard_data = {
            "entity_id": entity_id,
            "last_updated": latest_metrics.calculation_date if latest_metrics else None,
            "portfolio_summary": {
                "total_cash": float(total_cash),
                "total_investments": float(total_investments),
                "total_fx_exposure": float(total_fx_exposure),
                "total_portfolio_value": float(total_cash + total_investments)
            },
            "risk_metrics": {
                "portfolio_var_1d": float(latest_metrics.portfolio_var_1d) if latest_metrics and latest_metrics.portfolio_var_1d else None,
                "portfolio_var_10d": float(latest_metrics.portfolio_var_10d) if latest_metrics and latest_metrics.portfolio_var_10d else None,
                "expected_shortfall": float(latest_metrics.expected_shortfall_1d) if latest_metrics and latest_metrics.expected_shortfall_1d else None,
                "fx_hedge_ratio": float(latest_metrics.fx_hedge_ratio) if latest_metrics and latest_metrics.fx_hedge_ratio else None,
                "risk_score": latest_metrics.risk_score if latest_metrics else "Unknown"
            },
            "active_alerts": {
                "total_count": len(active_alerts),
                "by_severity": {
                    "critical": len([a for a in active_alerts if a.severity == "critical"]),
                    "high": len([a for a in active_alerts if a.severity == "high"]),
                    "medium": len([a for a in active_alerts if a.severity == "medium"]),
                    "low": len([a for a in active_alerts if a.severity == "low"])
                },
                "recent_alerts": [
                    {
                        "id": alert.id,
                        "type": alert.alert_type,
                        "severity": alert.severity,
                        "title": alert.title,
                        "days_open": alert.days_open
                    }
                    for alert in active_alerts[:5]
                ]
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error("Failed to get risk dashboard", entity_id=entity_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get risk dashboard: {str(e)}")