"""
Optimization recommendation models
"""

from sqlalchemy import Column, String, Enum, Numeric, DateTime, ForeignKey, Index, JSON, Text
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class RecommendationType(str, enum.Enum):
    """Recommendation types"""
    CASH_PLACEMENT = "cash_placement"
    FX_HEDGE = "fx_hedge"
    INVESTMENT_REBALANCE = "investment_rebalance"
    LIQUIDITY_MANAGEMENT = "liquidity_management"
    RISK_MITIGATION = "risk_mitigation"
    YIELD_OPTIMIZATION = "yield_optimization"


class UrgencyLevel(str, enum.Enum):
    """Urgency levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationStatus(str, enum.Enum):
    """Recommendation status"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    EXPIRED = "expired"


class OptimizationRecommendation(BaseModel):
    """Optimization recommendation model"""
    
    __tablename__ = "optimization_recommendations"
    
    # Foreign keys
    entity_id = Column(String(36), ForeignKey("corporate_entities.id"), nullable=False, index=True)
    entity = relationship("CorporateEntity", backref="recommendations")
    
    # Recommendation details
    recommendation_type = Column(Enum(RecommendationType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Current state and recommended action
    current_state = Column(JSON, nullable=True)  # Current position/configuration
    recommended_action = Column(JSON, nullable=False)  # Detailed action steps
    implementation_steps = Column(JSON, nullable=True)  # Step-by-step implementation
    
    # Expected benefits
    expected_financial_impact = Column(Numeric(20, 2), nullable=True)  # Expected P&L impact
    expected_risk_reduction = Column(Numeric(20, 2), nullable=True)    # Risk reduction amount
    confidence_level = Column(Numeric(5, 4), nullable=False, default=0.8)  # AI confidence
    
    # Urgency and timing
    urgency = Column(Enum(UrgencyLevel), nullable=False, default=UrgencyLevel.MEDIUM)
    valid_until = Column(DateTime(timezone=True), nullable=True)
    optimal_implementation_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status tracking
    status = Column(Enum(RecommendationStatus), nullable=False, default=RecommendationStatus.PENDING)
    assigned_to = Column(String(100), nullable=True)
    reviewed_by = Column(String(100), nullable=True)
    review_date = Column(DateTime(timezone=True), nullable=True)
    implementation_date = Column(DateTime(timezone=True), nullable=True)
    
    # Performance tracking
    actual_financial_impact = Column(Numeric(20, 2), nullable=True)
    actual_risk_reduction = Column(Numeric(20, 2), nullable=True)
    implementation_success_rate = Column(Numeric(5, 4), nullable=True)
    
    # AI and analytics metadata
    model_version = Column(String(50), nullable=True)
    calculation_inputs = Column(JSON, nullable=True)
    sensitivity_analysis = Column(JSON, nullable=True)
    
    # Approval workflow
    approval_required = Column(String(1), nullable=False, default='Y')  # Y/N
    approval_threshold = Column(Numeric(20, 2), nullable=True)
    approver_comments = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('ix_recommendations_entity_type', 'entity_id', 'recommendation_type'),
        Index('ix_recommendations_status_urgency', 'status', 'urgency'),
        Index('ix_recommendations_valid_until', 'valid_until'),
        Index('ix_recommendations_assigned', 'assigned_to', 'status'),
    )
    
    def __repr__(self):
        return f"<OptimizationRecommendation(type='{self.recommendation_type}', impact={self.expected_financial_impact})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if recommendation has expired"""
        if not self.valid_until:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.valid_until
    
    @property
    def days_until_expiry(self) -> int:
        """Calculate days until expiry"""
        if not self.valid_until:
            return 999  # No expiry
        from datetime import datetime, timezone
        delta = self.valid_until - datetime.now(timezone.utc)
        return max(0, delta.days)
    
    @property
    def roi_percentage(self) -> float:
        """Calculate expected ROI percentage"""
        if not self.expected_financial_impact or not self.current_state:
            return 0.0
        
        # This would need to be calculated based on the specific recommendation type
        # For now, return a placeholder
        return float(self.expected_financial_impact) / 1000000 * 100  # Simplified calculation


class RecommendationFeedback(BaseModel):
    """Recommendation feedback model for ML improvement"""
    
    __tablename__ = "recommendation_feedback"
    
    # Foreign keys
    recommendation_id = Column(String(36), ForeignKey("optimization_recommendations.id"), nullable=False, index=True)
    recommendation = relationship("OptimizationRecommendation", backref="feedback")
    
    # Feedback details
    feedback_type = Column(String(50), nullable=False)  # "accuracy", "usefulness", "implementation_ease"
    rating = Column(Numeric(3, 2), nullable=False)      # 1.0 to 5.0 scale
    comments = Column(Text, nullable=True)
    
    # Feedback metadata
    feedback_date = Column(DateTime(timezone=True), nullable=False)
    feedback_by = Column(String(100), nullable=False)
    
    # Implementation outcome
    was_implemented = Column(String(1), nullable=True)  # Y/N/P (Partial)
    implementation_challenges = Column(Text, nullable=True)
    actual_vs_expected_variance = Column(Numeric(8, 4), nullable=True)
    
    __table_args__ = (
        Index('ix_feedback_recommendation_type', 'recommendation_id', 'feedback_type'),
        Index('ix_feedback_date_rating', 'feedback_date', 'rating'),
    )
    
    def __repr__(self):
        return f"<RecommendationFeedback(rating={self.rating}, type='{self.feedback_type}')>"