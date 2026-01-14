"""
Risk metrics and assessment models
"""

from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel


class RiskMetrics(BaseModel):
    """Risk metrics model"""
    
    __tablename__ = "risk_metrics"
    
    # Foreign keys
    entity_id = Column(String(36), ForeignKey("corporate_entities.id"), nullable=False, index=True)
    entity = relationship("CorporateEntity", backref="risk_metrics")
    
    # Calculation metadata
    calculation_date = Column(DateTime(timezone=True), nullable=False)
    calculation_method = Column(String(100), nullable=False)  # e.g., "monte_carlo", "historical", "parametric"
    confidence_level = Column(Numeric(5, 4), nullable=False, default=0.95)
    time_horizon_days = Column(Numeric(5, 0), nullable=False, default=1)
    
    # Value at Risk metrics
    portfolio_var_1d = Column(Numeric(20, 2), nullable=True)      # 1-day VaR
    portfolio_var_10d = Column(Numeric(20, 2), nullable=True)     # 10-day VaR
    cash_var_1d = Column(Numeric(20, 2), nullable=True)          # Cash positions VaR
    investment_var_1d = Column(Numeric(20, 2), nullable=True)     # Investment VaR
    fx_var_1d = Column(Numeric(20, 2), nullable=True)            # FX exposure VaR
    
    # Expected Shortfall (Conditional VaR)
    expected_shortfall_1d = Column(Numeric(20, 2), nullable=True)
    expected_shortfall_10d = Column(Numeric(20, 2), nullable=True)
    
    # Currency risk metrics
    total_fx_exposure = Column(Numeric(20, 2), nullable=True)
    hedged_fx_exposure = Column(Numeric(20, 2), nullable=True)
    unhedged_fx_exposure = Column(Numeric(20, 2), nullable=True)
    fx_hedge_ratio = Column(Numeric(5, 4), nullable=True)
    
    # Credit risk metrics
    total_counterparty_exposure = Column(Numeric(20, 2), nullable=True)
    weighted_avg_credit_rating = Column(String(10), nullable=True)
    credit_concentration_risk = Column(Numeric(20, 2), nullable=True)
    expected_credit_loss = Column(Numeric(20, 2), nullable=True)
    
    # Liquidity risk metrics
    liquidity_buffer = Column(Numeric(20, 2), nullable=True)
    liquidity_coverage_ratio = Column(Numeric(8, 4), nullable=True)
    net_stable_funding_ratio = Column(Numeric(8, 4), nullable=True)
    stress_test_liquidity_gap = Column(Numeric(20, 2), nullable=True)
    
    # Interest rate risk metrics
    duration_risk = Column(Numeric(8, 4), nullable=True)
    convexity_risk = Column(Numeric(8, 4), nullable=True)
    basis_point_value = Column(Numeric(20, 2), nullable=True)
    
    # Operational risk indicators
    system_availability = Column(Numeric(5, 4), nullable=True)
    data_quality_score = Column(Numeric(5, 4), nullable=True)
    process_automation_ratio = Column(Numeric(5, 4), nullable=True)
    
    # Risk limits and utilization
    risk_limits = Column(JSON, nullable=True)  # Store risk limits as JSON
    limit_utilization = Column(JSON, nullable=True)  # Store utilization percentages
    
    # Stress testing results
    stress_test_results = Column(JSON, nullable=True)
    scenario_analysis = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_risk_metrics_entity_date', 'entity_id', 'calculation_date'),
        Index('ix_risk_metrics_date', 'calculation_date'),
    )
    
    def __repr__(self):
        return f"<RiskMetrics(entity_id='{self.entity_id}', date='{self.calculation_date}', var_1d={self.portfolio_var_1d})>"
    
    @property
    def total_hedge_ratio(self) -> float:
        """Calculate overall hedge ratio"""
        if not self.total_fx_exposure or self.total_fx_exposure == 0:
            return 0.0
        return float(self.hedged_fx_exposure or 0) / float(self.total_fx_exposure)
    
    @property
    def risk_score(self) -> str:
        """Calculate overall risk score"""
        # Simple risk scoring based on VaR relative to portfolio size
        if not self.portfolio_var_1d:
            return "Unknown"
        
        # This would be more sophisticated in practice
        var_ratio = float(self.portfolio_var_1d) / 1000000  # Assuming $1M baseline
        
        if var_ratio < 0.01:
            return "Low"
        elif var_ratio < 0.05:
            return "Medium"
        elif var_ratio < 0.10:
            return "High"
        else:
            return "Critical"


class RiskAlert(BaseModel):
    """Risk alert model"""
    
    __tablename__ = "risk_alerts"
    
    # Foreign keys
    entity_id = Column(String(36), ForeignKey("corporate_entities.id"), nullable=False, index=True)
    entity = relationship("CorporateEntity", backref="risk_alerts")
    
    risk_metrics_id = Column(String(36), ForeignKey("risk_metrics.id"), nullable=True)
    risk_metrics = relationship("RiskMetrics", backref="alerts")
    
    # Alert details
    alert_type = Column(String(100), nullable=False)  # e.g., "var_breach", "limit_exceeded", "concentration_risk"
    severity = Column(String(20), nullable=False)     # "low", "medium", "high", "critical"
    title = Column(String(200), nullable=False)
    description = Column(String(1000), nullable=False)
    
    # Risk values
    current_value = Column(Numeric(20, 2), nullable=True)
    threshold_value = Column(Numeric(20, 2), nullable=True)
    breach_percentage = Column(Numeric(8, 4), nullable=True)
    
    # Alert lifecycle
    alert_date = Column(DateTime(timezone=True), nullable=False)
    acknowledged_date = Column(DateTime(timezone=True), nullable=True)
    resolved_date = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by = Column(String(100), nullable=True)
    resolved_by = Column(String(100), nullable=True)
    
    # Actions and recommendations
    recommended_actions = Column(JSON, nullable=True)
    actions_taken = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_risk_alerts_entity_severity', 'entity_id', 'severity'),
        Index('ix_risk_alerts_date_type', 'alert_date', 'alert_type'),
        Index('ix_risk_alerts_unresolved', 'resolved_date'),  # NULL values for unresolved alerts
    )
    
    def __repr__(self):
        return f"<RiskAlert(type='{self.alert_type}', severity='{self.severity}', resolved={self.resolved_date is not None})>"
    
    @property
    def is_active(self) -> bool:
        """Check if alert is still active"""
        return self.resolved_date is None
    
    @property
    def days_open(self) -> int:
        """Calculate days since alert was created"""
        from datetime import datetime, timezone
        end_date = self.resolved_date or datetime.now(timezone.utc)
        delta = end_date - self.alert_date
        return delta.days