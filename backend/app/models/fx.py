"""
Foreign exchange exposure models
"""

from sqlalchemy import Column, String, Enum, Numeric, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class ExposureType(str, enum.Enum):
    """FX exposure types"""
    TRANSACTION = "transaction"      # Known future cash flows
    TRANSLATION = "translation"      # Net investment in foreign operations
    ECONOMIC = "economic"           # Long-term competitive position
    CONTINGENT = "contingent"       # Potential future exposures


class HedgeInstrumentType(str, enum.Enum):
    """Hedge instrument types"""
    FORWARD_CONTRACT = "forward_contract"
    FUTURES_CONTRACT = "futures_contract"
    CURRENCY_SWAP = "currency_swap"
    CURRENCY_OPTION = "currency_option"
    CROSS_CURRENCY_SWAP = "cross_currency_swap"
    NATURAL_HEDGE = "natural_hedge"


class FXExposure(BaseModel):
    """Foreign exchange exposure model"""
    
    __tablename__ = "fx_exposures"
    
    # Foreign keys
    entity_id = Column(String(36), ForeignKey("corporate_entities.id"), nullable=False, index=True)
    entity = relationship("CorporateEntity", backref="fx_exposures")
    
    # Exposure identification
    exposure_name = Column(String(200), nullable=False)
    exposure_type = Column(Enum(ExposureType), nullable=False)
    
    # Currency details
    base_currency = Column(String(3), nullable=False)      # Reporting currency
    exposure_currency = Column(String(3), nullable=False)   # Foreign currency
    
    # Exposure amounts
    notional_amount = Column(Numeric(20, 2), nullable=False)  # In exposure currency
    base_currency_equivalent = Column(Numeric(20, 2), nullable=False)  # In base currency
    
    # Exchange rates
    spot_rate = Column(Numeric(12, 6), nullable=False)
    forward_rate = Column(Numeric(12, 6), nullable=True)
    hedge_rate = Column(Numeric(12, 6), nullable=True)
    
    # Hedging details
    hedge_ratio = Column(Numeric(5, 4), nullable=False, default=0.0)  # 0.0 to 1.0
    hedged_amount = Column(Numeric(20, 2), nullable=True, default=0)
    unhedged_amount = Column(Numeric(20, 2), nullable=True)
    
    # Dates
    exposure_date = Column(DateTime(timezone=True), nullable=False)
    maturity_date = Column(DateTime(timezone=True), nullable=True)
    last_revaluation_date = Column(DateTime(timezone=True), nullable=True)
    
    # Risk metrics
    value_at_risk_1d = Column(Numeric(20, 2), nullable=True)
    value_at_risk_10d = Column(Numeric(20, 2), nullable=True)
    sensitivity_1pct = Column(Numeric(20, 2), nullable=True)  # P&L impact of 1% FX move
    
    # Performance tracking
    unrealized_fx_gain_loss = Column(Numeric(20, 2), nullable=True, default=0)
    realized_fx_gain_loss = Column(Numeric(20, 2), nullable=True, default=0)
    hedge_effectiveness = Column(Numeric(5, 4), nullable=True)  # Hedge accounting effectiveness
    
    # Additional metadata
    business_purpose = Column(String(200), nullable=True)
    counterparty = Column(String(200), nullable=True)
    hedge_designation = Column(String(100), nullable=True)  # Fair value, cash flow, net investment
    
    __table_args__ = (
        Index('ix_fx_exposures_entity_currencies', 'entity_id', 'base_currency', 'exposure_currency'),
        Index('ix_fx_exposures_maturity', 'maturity_date'),
        Index('ix_fx_exposures_type', 'exposure_type'),
    )
    
    def __repr__(self):
        return f"<FXExposure(name='{self.exposure_name}', amount={self.notional_amount} {self.exposure_currency})>"
    
    @property
    def is_mature(self) -> bool:
        """Check if exposure has matured"""
        if not self.maturity_date:
            return False
        from datetime import datetime, timezone
        return datetime.now(timezone.utc) >= self.maturity_date
    
    @property
    def hedge_percentage(self) -> float:
        """Calculate hedge percentage"""
        return float(self.hedge_ratio) * 100
    
    @property
    def net_exposure(self) -> float:
        """Calculate net unhedged exposure"""
        return float(self.notional_amount) * (1 - float(self.hedge_ratio))


class HedgeInstrument(BaseModel):
    """Hedge instrument model"""
    
    __tablename__ = "hedge_instruments"
    
    # Foreign keys
    fx_exposure_id = Column(String(36), ForeignKey("fx_exposures.id"), nullable=False, index=True)
    fx_exposure = relationship("FXExposure", backref="hedge_instruments")
    
    # Instrument details
    instrument_type = Column(Enum(HedgeInstrumentType), nullable=False)
    instrument_name = Column(String(200), nullable=False)
    counterparty = Column(String(200), nullable=False)
    
    # Financial details
    notional_amount = Column(Numeric(20, 2), nullable=False)
    strike_rate = Column(Numeric(12, 6), nullable=True)  # For options
    premium_paid = Column(Numeric(20, 2), nullable=True, default=0)
    
    # Dates
    trade_date = Column(DateTime(timezone=True), nullable=False)
    settlement_date = Column(DateTime(timezone=True), nullable=False)
    maturity_date = Column(DateTime(timezone=True), nullable=False)
    
    # Performance
    mark_to_market_value = Column(Numeric(20, 2), nullable=True, default=0)
    unrealized_gain_loss = Column(Numeric(20, 2), nullable=True, default=0)
    
    __table_args__ = (
        Index('ix_hedge_instruments_exposure_type', 'fx_exposure_id', 'instrument_type'),
        Index('ix_hedge_instruments_maturity', 'maturity_date'),
    )
    
    def __repr__(self):
        return f"<HedgeInstrument(type='{self.instrument_type}', notional={self.notional_amount})>"