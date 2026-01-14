"""
Cash position models
"""

from sqlalchemy import Column, String, Enum, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class AccountType(str, enum.Enum):
    """Cash account types"""
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money_market"
    CERTIFICATE_DEPOSIT = "cd"
    TREASURY = "treasury"


class LiquidityTier(str, enum.Enum):
    """Liquidity tiers for cash positions"""
    IMMEDIATE = "immediate"      # Available within 24 hours
    SHORT_TERM = "short_term"    # Available within 1 week
    MEDIUM_TERM = "medium_term"  # Available within 1 month
    LONG_TERM = "long_term"      # Available after 1 month


class CashPosition(BaseModel):
    """Cash position model"""
    
    __tablename__ = "cash_positions"
    
    # Foreign keys
    entity_id = Column(String(36), ForeignKey("corporate_entities.id"), nullable=False, index=True)
    entity = relationship("CorporateEntity", backref="cash_positions")
    
    # Account details
    account_number = Column(String(50), nullable=False, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    bank_name = Column(String(200), nullable=False)
    bank_swift_code = Column(String(11), nullable=True)
    
    # Financial details
    currency = Column(String(3), nullable=False)  # ISO 4217
    balance = Column(Numeric(20, 2), nullable=False)
    available_balance = Column(Numeric(20, 2), nullable=True)  # May differ from balance due to holds
    interest_rate = Column(Numeric(8, 6), nullable=True)  # Annual percentage rate
    
    # Maturity and liquidity
    maturity_date = Column(DateTime(timezone=True), nullable=True)
    liquidity_tier = Column(Enum(LiquidityTier), nullable=False, default=LiquidityTier.IMMEDIATE)
    
    # Risk and compliance
    fdic_insured = Column(String(1), nullable=True)  # Y/N/U (Unknown)
    deposit_insurance_limit = Column(Numeric(20, 2), nullable=True)
    
    # Performance tracking
    ytd_interest_earned = Column(Numeric(20, 2), nullable=True, default=0)
    last_interest_payment = Column(DateTime(timezone=True), nullable=True)
    
    # Operational details
    last_updated = Column(DateTime(timezone=True), nullable=False)
    data_source = Column(String(100), nullable=True)  # Bank API, manual entry, etc.
    
    __table_args__ = (
        Index('ix_cash_positions_entity_currency', 'entity_id', 'currency'),
        Index('ix_cash_positions_liquidity', 'liquidity_tier', 'maturity_date'),
    )
    
    def __repr__(self):
        return f"<CashPosition(account='{self.account_number}', balance={self.balance} {self.currency})>"
    
    @property
    def is_mature(self) -> bool:
        """Check if position has matured"""
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