"""
Investment models
"""

from sqlalchemy import Column, String, Enum, Numeric, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class InstrumentType(str, enum.Enum):
    """Investment instrument types"""
    TREASURY_BILL = "treasury_bill"
    TREASURY_NOTE = "treasury_note"
    TREASURY_BOND = "treasury_bond"
    CORPORATE_BOND = "corporate_bond"
    MONEY_MARKET_FUND = "money_market_fund"
    CERTIFICATE_DEPOSIT = "cd"
    COMMERCIAL_PAPER = "commercial_paper"
    REPO_AGREEMENT = "repo_agreement"


class CreditRating(str, enum.Enum):
    """Credit ratings (S&P scale)"""
    AAA = "AAA"
    AA_PLUS = "AA+"
    AA = "AA"
    AA_MINUS = "AA-"
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    BBB_PLUS = "BBB+"
    BBB = "BBB"
    BBB_MINUS = "BBB-"
    BB_PLUS = "BB+"
    BB = "BB"
    BB_MINUS = "BB-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    CCC = "CCC"
    CC = "CC"
    C = "C"
    D = "D"
    NR = "NR"  # Not Rated


class Investment(BaseModel):
    """Investment model"""
    
    __tablename__ = "investments"
    
    # Foreign keys
    entity_id = Column(String(36), ForeignKey("corporate_entities.id"), nullable=False, index=True)
    entity = relationship("CorporateEntity", backref="investments")
    
    # Investment identification
    cusip = Column(String(9), nullable=True, index=True)  # CUSIP identifier
    isin = Column(String(12), nullable=True, index=True)  # ISIN identifier
    ticker_symbol = Column(String(20), nullable=True)
    investment_name = Column(String(200), nullable=False)
    
    # Investment details
    instrument_type = Column(Enum(InstrumentType), nullable=False)
    issuer_name = Column(String(200), nullable=False)
    currency = Column(String(3), nullable=False)
    
    # Financial details
    principal_amount = Column(Numeric(20, 2), nullable=False)
    purchase_price = Column(Numeric(20, 6), nullable=False)  # Price per unit
    current_price = Column(Numeric(20, 6), nullable=True)
    market_value = Column(Numeric(20, 2), nullable=True)
    
    # Interest and yield
    coupon_rate = Column(Numeric(8, 6), nullable=True)  # Annual coupon rate
    yield_to_maturity = Column(Numeric(8, 6), nullable=True)
    accrued_interest = Column(Numeric(20, 2), nullable=True, default=0)
    
    # Dates
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    issue_date = Column(DateTime(timezone=True), nullable=True)
    maturity_date = Column(DateTime(timezone=True), nullable=True)
    next_coupon_date = Column(DateTime(timezone=True), nullable=True)
    
    # Risk metrics
    credit_rating = Column(Enum(CreditRating), nullable=True)
    duration = Column(Numeric(8, 4), nullable=True)  # Modified duration
    convexity = Column(Numeric(8, 4), nullable=True)
    
    # Performance tracking
    unrealized_gain_loss = Column(Numeric(20, 2), nullable=True, default=0)
    realized_gain_loss = Column(Numeric(20, 2), nullable=True, default=0)
    ytd_income = Column(Numeric(20, 2), nullable=True, default=0)
    
    # Additional metadata
    investment_strategy = Column(String(100), nullable=True)  # e.g., "liquidity", "yield", "duration_matching"
    risk_classification = Column(String(50), nullable=True)
    regulatory_capital_treatment = Column(JSON, nullable=True)
    
    __table_args__ = (
        Index('ix_investments_entity_type', 'entity_id', 'instrument_type'),
        Index('ix_investments_maturity', 'maturity_date'),
        Index('ix_investments_rating', 'credit_rating'),
    )
    
    def __repr__(self):
        return f"<Investment(name='{self.investment_name}', value={self.market_value} {self.currency})>"
    
    @property
    def is_mature(self) -> bool:
        """Check if investment has matured"""
        if not self.maturity_date:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) >= self.maturity_date
    
    @property
    def days_to_maturity(self) -> int:
        """Calculate days to maturity"""
        if not self.maturity_date:
            return 0
        from datetime import datetime, timezone
        delta = self.maturity_date - datetime.now(timezone.utc)
        return max(0, delta.days)
    
    @property
    def current_yield(self) -> float:
        """Calculate current yield"""
        if not self.current_price or not self.coupon_rate:
            return 0.0
        return float(self.coupon_rate) / float(self.current_price) * 100