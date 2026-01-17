"""
AI interaction and insight models
"""

from sqlalchemy import Column, String, Enum, Numeric, DateTime, ForeignKey, Index, JSON, Text
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class ConversationStatus(str, enum.Enum):
    """Conversation status"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class InsightType(str, enum.Enum):
    """AI insight types"""
    ANOMALY = "anomaly"
    OPPORTUNITY = "opportunity"
    RISK_ALERT = "risk_alert"
    PERFORMANCE_VARIANCE = "performance_variance"
    MARKET_TREND = "market_trend"
    OPTIMIZATION_SUGGESTION = "optimization_suggestion"


class ConversationContext(BaseModel):
    """Conversation context model for AI interactions"""
    
    __tablename__ = "conversation_contexts"
    
    # Session identification
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    
    # Entity scope
    entity_scope = Column(JSON, nullable=True)  # List of entity IDs user has access to
    active_entity_id = Column(String(36), ForeignKey("corporate_entities.id"), nullable=True)
    active_entity = relationship("CorporateEntity")
    
    # Conversation state
    status = Column(Enum(ConversationStatus), nullable=False, default=ConversationStatus.ACTIVE)
    conversation_title = Column(String(200), nullable=True)
    
    # User preferences and context
    user_preferences = Column(JSON, nullable=True)
    active_filters = Column(JSON, nullable=True)
    dashboard_context = Column(JSON, nullable=True)  # Current dashboard state
    
    # Activity tracking
    last_activity = Column(DateTime(timezone=True), nullable=False)
    total_interactions = Column(Numeric(10, 0), nullable=False, default=0)
    
    # AI model context
    model_version = Column(String(50), nullable=True)
    conversation_summary = Column(Text, nullable=True)  # AI-generated summary
    
    __table_args__ = (
        Index('ix_conversations_user_status', 'user_id', 'status'),
        Index('ix_conversations_activity', 'last_activity'),
        Index('ix_conversations_entity', 'active_entity_id'),
    )
    
    def __repr__(self):
        return f"<ConversationContext(session='{self.session_id}', user='{self.user_id}')>"


class ConversationTurn(BaseModel):
    """Individual conversation turn model"""
    
    __tablename__ = "conversation_turns"
    
    # Foreign keys
    context_id = Column(String(36), ForeignKey("conversation_contexts.id"), nullable=False, index=True)
    context = relationship("ConversationContext", backref="turns")
    
    # Turn details
    turn_number = Column(Numeric(10, 0), nullable=False)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    
    # Processing metadata
    processing_time_ms = Column(Numeric(10, 0), nullable=True)
    model_used = Column(String(50), nullable=True)
    confidence_score = Column(Numeric(5, 4), nullable=True)
    
    # Intent and entities
    detected_intent = Column(String(100), nullable=True)
    extracted_entities = Column(JSON, nullable=True)
    query_complexity = Column(String(20), nullable=True)  # "simple", "medium", "complex"
    
    # Data access
    data_sources_accessed = Column(JSON, nullable=True)
    calculations_performed = Column(JSON, nullable=True)
    
    # User feedback
    user_rating = Column(Numeric(3, 2), nullable=True)  # 1.0 to 5.0
    user_feedback = Column(Text, nullable=True)
    
    __table_args__ = (
        Index('ix_turns_context_number', 'context_id', 'turn_number'),
        Index('ix_turns_intent', 'detected_intent'),
        Index('ix_turns_rating', 'user_rating'),
    )
    
    def __repr__(self):
        return f"<ConversationTurn(turn={self.turn_number}, intent='{self.detected_intent}')>"


class AIInsight(BaseModel):
    """AI-generated insight model"""
    
    __tablename__ = "ai_insights"
    
    # Foreign keys
    entity_id = Column(String(36), ForeignKey("corporate_entities.id"), nullable=False, index=True)
    entity = relationship("CorporateEntity", backref="ai_insights")
    
    # Insight details
    insight_type = Column(Enum(InsightType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # AI metadata
    confidence = Column(Numeric(5, 4), nullable=False)
    model_version = Column(String(50), nullable=True)
    generation_method = Column(String(100), nullable=True)  # "pattern_detection", "anomaly_detection", etc.
    
    # Supporting data
    supporting_data = Column(JSON, nullable=True)
    data_sources = Column(JSON, nullable=True)
    calculation_details = Column(JSON, nullable=True)
    
    # Business impact
    financial_impact = Column(Numeric(20, 2), nullable=True)
    risk_impact = Column(String(20), nullable=True)  # "low", "medium", "high"
    urgency_score = Column(Numeric(5, 4), nullable=True)
    
    # Recommendations
    recommended_actions = Column(JSON, nullable=True)
    implementation_complexity = Column(String(20), nullable=True)  # "low", "medium", "high"
    
    # Lifecycle
    generated_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    viewed_by = Column(JSON, nullable=True)  # List of users who viewed
    acted_upon = Column(String(1), nullable=False, default='N')  # Y/N
    
    # Validation and feedback
    human_validated = Column(String(1), nullable=True)  # Y/N/P (Partial)
    validation_comments = Column(Text, nullable=True)
    accuracy_score = Column(Numeric(5, 4), nullable=True)  # Post-validation accuracy
    
    __table_args__ = (
        Index('ix_insights_entity_type', 'entity_id', 'insight_type'),
        Index('ix_insights_confidence', 'confidence'),
        Index('ix_insights_generated', 'generated_at'),
        Index('ix_insights_urgency', 'urgency_score'),
    )
    
    def __repr__(self):
        return f"<AIInsight(type='{self.insight_type}', confidence={self.confidence})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if insight has expired"""
        if not self.expires_at:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) > self.expires_at
    
    @property
    def age_hours(self) -> int:
        """Calculate age of insight in hours"""
        from datetime import datetime, timezone
        delta = datetime.now(timezone.utc) - self.generated_at
        return int(delta.total_seconds() / 3600)


class AIModelPerformance(BaseModel):
    """AI model performance tracking"""
    
    __tablename__ = "ai_model_performance"
    
    # Model identification
    model_name = Column(String(100), nullable=False, index=True)
    model_version = Column(String(50), nullable=False)
    
    # Performance metrics
    accuracy_score = Column(Numeric(5, 4), nullable=True)
    precision_score = Column(Numeric(5, 4), nullable=True)
    recall_score = Column(Numeric(5, 4), nullable=True)
    f1_score = Column(Numeric(5, 4), nullable=True)
    
    # Usage statistics
    total_predictions = Column(Numeric(15, 0), nullable=False, default=0)
    correct_predictions = Column(Numeric(15, 0), nullable=False, default=0)
    user_feedback_count = Column(Numeric(10, 0), nullable=False, default=0)
    avg_user_rating = Column(Numeric(5, 4), nullable=True)
    
    # Performance period
    measurement_start = Column(DateTime(timezone=True), nullable=False)
    measurement_end = Column(DateTime(timezone=True), nullable=False)
    
    # Additional metrics
    avg_response_time_ms = Column(Numeric(10, 0), nullable=True)
    error_rate = Column(Numeric(5, 4), nullable=True)
    
    __table_args__ = (
        Index('ix_model_performance_name_version', 'model_name', 'model_version'),
        Index('ix_model_performance_period', 'measurement_start', 'measurement_end'),
    )
    
    def __repr__(self):
        return f"<AIModelPerformance(model='{self.model_name}', accuracy={self.accuracy_score})>"