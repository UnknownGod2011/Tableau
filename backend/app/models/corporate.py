"""
Corporate entity models
"""

from sqlalchemy import Column, String, Enum, JSON, Numeric, ForeignKey
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class EntityType(str, enum.Enum):
    """Corporate entity types"""
    SUBSIDIARY = "subsidiary"
    DIVISION = "division"
    HEADQUARTERS = "headquarters"


class RiskProfileLevel(str, enum.Enum):
    """Risk profile levels"""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class CorporateEntity(BaseModel):
    """Corporate entity model"""
    
    __tablename__ = "corporate_entities"
    
    entity_name = Column(String(200), nullable=False, index=True)
    entity_type = Column(Enum(EntityType), nullable=False)
    base_currency = Column(String(3), nullable=False)  # ISO 4217 currency codes
    reporting_currency = Column(String(3), nullable=False)
    risk_profile = Column(Enum(RiskProfileLevel), nullable=False, default=RiskProfileLevel.MODERATE)
    
    # Financial metrics
    total_assets = Column(Numeric(20, 2), nullable=True)
    annual_revenue = Column(Numeric(20, 2), nullable=True)
    credit_rating = Column(String(10), nullable=True)  # e.g., "AAA", "AA+", etc.
    
    # Compliance and regulatory
    regulatory_jurisdiction = Column(String(100), nullable=True)
    compliance_requirements = Column(JSON, nullable=True)  # Store as JSON array
    
    # Relationships
    parent_entity_id = Column(String(36), ForeignKey("corporate_entities.id"), nullable=True)
    parent_entity = relationship("CorporateEntity", remote_side="CorporateEntity.id", backref="subsidiaries")
    
    # Treasury configuration
    treasury_policies = Column(JSON, nullable=True)
    authorized_instruments = Column(JSON, nullable=True)  # Store as JSON array instead of ARRAY
    investment_limits = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<CorporateEntity(name='{self.entity_name}', type='{self.entity_type}')>"