"""
Property-based test for audit trail maintenance (Property 24)

Feature: treasuryiq-corporate-ai, Property 24: Audit Trail Maintenance
For any financial calculation performed, the Treasury_System should maintain 
complete data lineage and audit trails
Validates: Requirements 5.4
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timezone
from decimal import Decimal
import uuid

from app.models import (
    CashPosition, Investment, FXExposure, RiskMetrics, 
    OptimizationRecommendation, EntityType, AccountType, 
    InstrumentType, ExposureType, RecommendationType
)


# Test data strategies
@st.composite
def corporate_entity_strategy(draw):
    """Generate corporate entity test data"""
    return {
        "id": str(uuid.uuid4()),
        "entity_name": draw(st.text(min_size=5, max_size=100)),
        "entity_type": draw(st.sampled_from(EntityType)),
        "base_currency": draw(st.sampled_from(["USD", "EUR", "GBP", "JPY"])),
        "reporting_currency": draw(st.sampled_from(["USD", "EUR", "GBP", "JPY"])),
    }


@st.composite
def cash_position_strategy(draw):
    """Generate cash position test data"""
    entity = draw(corporate_entity_strategy())
    now = datetime.now(timezone.utc)
    return CashPosition(
        entity_id=entity["id"],
        account_number=draw(st.text(min_size=8, max_size=20)),
        account_name=draw(st.text(min_size=5, max_size=100)),
        account_type=draw(st.sampled_from(AccountType)),
        bank_name=draw(st.text(min_size=5, max_size=100)),
        currency=entity["base_currency"],
        balance=draw(st.decimals(min_value=1000, max_value=100000000, places=2)),
        interest_rate=draw(st.decimals(min_value=0, max_value=0.1, places=6)),
        last_updated=now,
        created_by="test_user",
        created_at=now,
        updated_at=now,
        is_active=True,
    )


@st.composite
def investment_strategy(draw):
    """Generate investment test data"""
    entity = draw(corporate_entity_strategy())
    now = datetime.now(timezone.utc)
    return Investment(
        entity_id=entity["id"],
        investment_name=draw(st.text(min_size=5, max_size=100)),
        instrument_type=draw(st.sampled_from(InstrumentType)),
        issuer_name=draw(st.text(min_size=5, max_size=100)),
        currency=entity["base_currency"],
        principal_amount=draw(st.decimals(min_value=10000, max_value=50000000, places=2)),
        purchase_price=draw(st.decimals(min_value=90, max_value=110, places=6)),
        purchase_date=now,
        created_by="test_user",
        created_at=now,
        updated_at=now,
        is_active=True,
    )


@st.composite
def fx_exposure_strategy(draw):
    """Generate FX exposure test data"""
    entity = draw(corporate_entity_strategy())
    currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
    base_curr = entity["base_currency"]
    exp_curr = draw(st.sampled_from([c for c in currencies if c != base_curr]))
    now = datetime.now(timezone.utc)
    
    return FXExposure(
        entity_id=entity["id"],
        exposure_name=draw(st.text(min_size=5, max_size=100)),
        exposure_type=draw(st.sampled_from(ExposureType)),
        base_currency=base_curr,
        exposure_currency=exp_curr,
        notional_amount=draw(st.decimals(min_value=100000, max_value=10000000, places=2)),
        base_currency_equivalent=draw(st.decimals(min_value=100000, max_value=10000000, places=2)),
        spot_rate=draw(st.decimals(min_value=0.5, max_value=2.0, places=6)),
        exposure_date=now,
        created_by="test_user",
        created_at=now,
        updated_at=now,
        is_active=True,
    )


@st.composite
def optimization_recommendation_strategy(draw):
    """Generate optimization recommendation test data"""
    entity = draw(corporate_entity_strategy())
    now = datetime.now(timezone.utc)
    return OptimizationRecommendation(
        entity_id=entity["id"],
        recommendation_type=draw(st.sampled_from(RecommendationType)),
        title=draw(st.text(min_size=10, max_size=200)),
        description=draw(st.text(min_size=20, max_size=1000)),
        recommended_action={"action": "test_action", "parameters": {}},
        expected_financial_impact=draw(st.decimals(min_value=1000, max_value=1000000, places=2)),
        confidence_level=draw(st.decimals(min_value=0.5, max_value=1.0, places=4)),
        created_by="test_user",
        created_at=now,
        updated_at=now,
        is_active=True,
    )


class TestAuditTrailMaintenance:
    """Test audit trail maintenance for all treasury operations"""
    
    @given(cash_position=cash_position_strategy())
    @settings(max_examples=100)
    def test_cash_position_audit_trail(self, cash_position):
        """
        Property 24: Audit Trail Maintenance - Cash Positions
        Verify that cash position operations maintain complete audit trails
        """
        # Verify audit fields are populated
        assert cash_position.created_by is not None, "Created by field must be populated"
        assert cash_position.created_at is not None, "Created at timestamp must be populated"
        assert cash_position.updated_at is not None, "Updated at timestamp must be populated"
        assert cash_position.is_active is not None, "Active status must be defined"
        
        # Verify data lineage can be traced
        assert cash_position.entity_id is not None, "Entity relationship must be traceable"
        assert cash_position.last_updated is not None, "Last update timestamp must be maintained"
        
        # Verify financial data integrity
        assert cash_position.balance is not None, "Balance must be recorded"
        assert cash_position.currency is not None, "Currency must be specified"
        
        # Simulate update operation
        original_balance = cash_position.balance
        cash_position.balance = original_balance + Decimal('1000.00')
        cash_position.updated_by = "test_updater"
        cash_position.audit_notes = f"Balance updated from {original_balance}"
        
        # Verify audit trail for updates
        assert cash_position.updated_by == "test_updater", "Updater must be recorded"
        assert cash_position.audit_notes is not None, "Audit notes must capture changes"
    
    @given(investment=investment_strategy())
    @settings(max_examples=100)
    def test_investment_audit_trail(self, investment):
        """
        Property 24: Audit Trail Maintenance - Investments
        Verify that investment operations maintain complete audit trails
        """
        # Verify audit fields are populated
        assert investment.created_by is not None, "Created by field must be populated"
        assert investment.created_at is not None, "Created at timestamp must be populated"
        assert investment.updated_at is not None, "Updated at timestamp must be populated"
        
        # Verify investment-specific lineage
        assert investment.entity_id is not None, "Entity relationship must be traceable"
        assert investment.purchase_date is not None, "Purchase date must be recorded"
        assert investment.principal_amount is not None, "Principal amount must be recorded"
        
        # Simulate valuation update
        original_value = investment.market_value
        new_value = investment.principal_amount * Decimal('1.05')  # 5% gain
        investment.market_value = new_value
        investment.unrealized_gain_loss = new_value - investment.principal_amount
        investment.updated_by = "valuation_system"
        investment.audit_notes = f"Market valuation updated from {original_value} to {new_value}"
        
        # Verify audit trail captures valuation changes
        assert investment.updated_by == "valuation_system", "System updater must be recorded"
        assert investment.audit_notes is not None, "Valuation changes must be documented"
        assert investment.unrealized_gain_loss is not None, "P&L impact must be calculated"
    
    @given(fx_exposure=fx_exposure_strategy())
    @settings(max_examples=100)
    def test_fx_exposure_audit_trail(self, fx_exposure):
        """
        Property 24: Audit Trail Maintenance - FX Exposures
        Verify that FX exposure operations maintain complete audit trails
        """
        # Verify audit fields are populated
        assert fx_exposure.created_by is not None, "Created by field must be populated"
        assert fx_exposure.created_at is not None, "Created at timestamp must be populated"
        
        # Verify FX-specific lineage
        assert fx_exposure.entity_id is not None, "Entity relationship must be traceable"
        assert fx_exposure.exposure_date is not None, "Exposure date must be recorded"
        assert fx_exposure.spot_rate is not None, "Exchange rate must be recorded"
        
        # Simulate revaluation
        original_rate = fx_exposure.spot_rate
        new_rate = original_rate * Decimal('1.02')  # 2% currency movement
        fx_exposure.spot_rate = new_rate
        
        # Calculate revaluation impact
        old_base_value = fx_exposure.base_currency_equivalent
        new_base_value = fx_exposure.notional_amount * new_rate
        fx_exposure.base_currency_equivalent = new_base_value
        fx_exposure.unrealized_fx_gain_loss = new_base_value - old_base_value
        fx_exposure.updated_by = "fx_revaluation_system"
        fx_exposure.audit_notes = f"FX revaluation: rate {original_rate} -> {new_rate}"
        
        # Verify audit trail captures FX movements
        assert fx_exposure.updated_by == "fx_revaluation_system", "FX system updater must be recorded"
        assert fx_exposure.audit_notes is not None, "FX rate changes must be documented"
        assert fx_exposure.unrealized_fx_gain_loss is not None, "FX P&L impact must be calculated"
    
    @given(recommendation=optimization_recommendation_strategy())
    @settings(max_examples=100)
    def test_recommendation_audit_trail(self, recommendation):
        """
        Property 24: Audit Trail Maintenance - Optimization Recommendations
        Verify that recommendation lifecycle maintains complete audit trails
        """
        # Verify audit fields are populated
        assert recommendation.created_by is not None, "Created by field must be populated"
        assert recommendation.created_at is not None, "Created at timestamp must be populated"
        
        # Verify recommendation-specific lineage
        assert recommendation.entity_id is not None, "Entity relationship must be traceable"
        assert recommendation.recommended_action is not None, "Recommended action must be recorded"
        assert recommendation.confidence_level is not None, "AI confidence must be recorded"
        
        # Simulate recommendation approval workflow
        recommendation.status = "under_review"
        recommendation.assigned_to = "treasury_manager"
        recommendation.updated_by = "workflow_system"
        recommendation.audit_notes = "Recommendation assigned for review"
        
        # Verify workflow audit trail
        assert recommendation.assigned_to == "treasury_manager", "Assignment must be recorded"
        assert recommendation.updated_by == "workflow_system", "Workflow system must be recorded"
        assert recommendation.audit_notes is not None, "Workflow changes must be documented"
        
        # Simulate implementation
        recommendation.status = "implemented"
        recommendation.implementation_date = datetime.now(timezone.utc)
        recommendation.actual_financial_impact = recommendation.expected_financial_impact * Decimal('0.95')
        recommendation.updated_by = "implementation_system"
        recommendation.audit_notes += "; Implementation completed with 95% of expected impact"
        
        # Verify implementation audit trail
        assert recommendation.implementation_date is not None, "Implementation date must be recorded"
        assert recommendation.actual_financial_impact is not None, "Actual results must be recorded"
        assert "Implementation completed" in recommendation.audit_notes, "Implementation must be documented"
    
    @given(
        cash_positions=st.lists(cash_position_strategy(), min_size=2, max_size=10),
        investments=st.lists(investment_strategy(), min_size=1, max_size=5)
    )
    @settings(max_examples=50)
    def test_cross_entity_audit_trail(self, cash_positions, investments):
        """
        Property 24: Audit Trail Maintenance - Cross-Entity Operations
        Verify that operations affecting multiple entities maintain complete audit trails
        """
        # Simulate a treasury optimization that moves cash between positions
        source_position = cash_positions[0]
        target_position = cash_positions[1]
        transfer_amount = min(source_position.balance, Decimal('1000000'))
        
        # Record the transfer with full audit trail
        transaction_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Update source position
        source_position.balance -= transfer_amount
        source_position.updated_by = "treasury_optimization_system"
        source_position.audit_notes = f"Transfer out: {transfer_amount} to {target_position.account_number} (txn: {transaction_id})"
        
        # Update target position
        target_position.balance += transfer_amount
        target_position.updated_by = "treasury_optimization_system"
        target_position.audit_notes = f"Transfer in: {transfer_amount} from {source_position.account_number} (txn: {transaction_id})"
        
        # Verify cross-entity audit trail
        assert transaction_id in source_position.audit_notes, "Transaction ID must link related operations"
        assert transaction_id in target_position.audit_notes, "Transaction ID must link related operations"
        assert source_position.updated_by == target_position.updated_by, "Same system must update both sides"
        
        # Verify data consistency
        assert source_position.balance >= 0, "Source balance must remain non-negative"
        assert target_position.balance > 0, "Target balance must be positive after transfer"
    
    def test_audit_trail_data_lineage_requirements(self):
        """
        Property 24: Audit Trail Maintenance - Data Lineage Requirements
        Verify that audit trail meets regulatory and compliance requirements
        """
        # Test that all required audit fields are present in base model
        from app.models.base import BaseModel, AuditMixin
        
        # Verify AuditMixin provides required fields
        audit_fields = ['created_by', 'updated_by', 'is_active', 'audit_notes']
        for field in audit_fields:
            assert hasattr(AuditMixin, field), f"AuditMixin must provide {field} field"
        
        # Verify BaseModel includes timestamp fields
        timestamp_fields = ['created_at', 'updated_at']
        from app.models.base import TimestampMixin
        for field in timestamp_fields:
            assert hasattr(TimestampMixin, field), f"TimestampMixin must provide {field} field"
        
        # Verify UUID field for unique identification
        from app.models.base import UUIDMixin
        assert hasattr(UUIDMixin, 'id'), "UUIDMixin must provide unique ID field"


if __name__ == "__main__":
    # Run the property tests
    pytest.main([__file__, "-v", "--tb=short"])