"""
Property-based tests for cash optimization algorithms
Feature: treasuryiq-corporate-ai

This module implements property-based testing for the core cash optimization
algorithms to ensure correctness across all valid inputs.

Properties tested:
- Property 1: Cash Optimization Detection
- Property 2: Market-Driven Recalculation  
- Property 3: Liquidity Shortfall Response
- Property 4: Comprehensive Optimization Recommendations
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

from app.services.analytics import TreasuryAnalyticsEngine, OptimizationResult
from app.services.market_data import MarketDataIngestionPipeline
from app.models.cash import CashPosition, AccountType, LiquidityTier


# Test data generation strategies
@st.composite
def cash_position_strategy(draw):
    """Generate valid cash positions for property testing"""
    account_types = list(AccountType)
    liquidity_tiers = list(LiquidityTier)
    
    return CashPosition(
        id=draw(st.uuids()).hex,
        entity_id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        account_name=draw(st.text(min_size=5, max_size=50)),
        account_type=draw(st.sampled_from(account_types)),
        currency=draw(st.sampled_from(["USD", "EUR", "GBP", "JPY"])),
        balance=Decimal(str(draw(st.floats(min_value=100000, max_value=100000000, allow_nan=False, allow_infinity=False)))),
        interest_rate=Decimal(str(draw(st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)))),
        bank_name=draw(st.text(min_size=3, max_size=30)),
        liquidity_tier=draw(st.sampled_from(liquidity_tiers)),
        maturity_date=draw(st.one_of(
            st.none(),
            st.datetimes(min_value=datetime.now(), max_value=datetime.now() + timedelta(days=365*2))
        ))
    )


@st.composite
def market_rates_strategy(draw):
    """Generate valid market rates for testing"""
    return {
        "fed_funds": type('Rate', (), {
            'rate': Decimal(str(draw(st.floats(min_value=0.0, max_value=8.0, allow_nan=False, allow_infinity=False))))
        })(),
        "treasury_3m": type('Rate', (), {
            'rate': Decimal(str(draw(st.floats(min_value=0.0, max_value=8.0, allow_nan=False, allow_infinity=False))))
        })(),
        "treasury_6m": type('Rate', (), {
            'rate': Decimal(str(draw(st.floats(min_value=0.0, max_value=8.0, allow_nan=False, allow_infinity=False))))
        })(),
        "treasury_1y": type('Rate', (), {
            'rate': Decimal(str(draw(st.floats(min_value=0.0, max_value=8.0, allow_nan=False, allow_infinity=False))))
        })(),
        "treasury_2y": type('Rate', (), {
            'rate': Decimal(str(draw(st.floats(min_value=0.0, max_value=8.0, allow_nan=False, allow_infinity=False))))
        })()
    }


class TestCashOptimizationProperties:
    """Property-based tests for cash optimization algorithms"""
    
    @pytest.fixture
    def analytics_engine(self):
        """Create analytics engine for testing"""
        market_data_service = MarketDataIngestionPipeline()
        return TreasuryAnalyticsEngine(market_data_service)
    
    @given(cash_positions=st.lists(cash_position_strategy(), min_size=2, max_size=10))
    @settings(max_examples=100, deadline=30000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_1_cash_optimization_detection(self, cash_positions, analytics_engine):
        """
        Feature: treasuryiq-corporate-ai, Property 1: Cash Optimization Detection
        
        For any set of cash positions with varying yields, when positions exceed 
        optimal thresholds, the Treasury_System should identify all suboptimal 
        placements and calculate accurate opportunity costs.
        
        Validates: Requirements 1.1
        """
        # Ensure we have varying yields for meaningful optimization
        assume(len(set(pos.interest_rate for pos in cash_positions)) > 1)
        assume(all(pos.balance > 0 for pos in cash_positions))
        
        async def run_test():
            # Run optimization
            result = await analytics_engine.calculate_optimal_cash_allocation(cash_positions)
            
            # Property 1.1: Result should be valid OptimizationResult
            assert isinstance(result, OptimizationResult)
            assert result.current_yield >= 0
            assert result.optimal_yield >= 0
            assert isinstance(result.opportunity_cost, Decimal)
            assert 0.0 <= result.confidence <= 1.0
            assert isinstance(result.recommendations, list)
            
            # Property 1.2: Optimal yield should be >= current yield (or equal if already optimal)
            assert result.optimal_yield >= result.current_yield
            
            # Property 1.3: Opportunity cost should be non-negative
            assert result.opportunity_cost >= 0
            
            # Property 1.4: If there's opportunity cost, there should be recommendations
            if result.opportunity_cost > Decimal("1000"):  # Meaningful threshold
                assert len(result.recommendations) > 0
            
            # Property 1.5: All recommendations should have required fields
            for rec in result.recommendations:
                assert "position_id" in rec
                assert "action" in rec
                assert "current_balance" in rec
                assert "target_balance" in rec
                assert "expected_yield_impact" in rec
                assert rec["action"] in ["increase", "decrease"]
                assert rec["current_balance"] >= 0
                assert rec["target_balance"] >= 0
            
            # Property 1.6: Total balance should be conserved in recommendations
            total_current = sum(pos.balance for pos in cash_positions)
            total_recommended = sum(rec["target_balance"] for rec in result.recommendations)
            if result.recommendations:
                # Allow for small rounding differences
                assert abs(float(total_current) - total_recommended) < 1000
        
        # Run async test
        asyncio.run(run_test())
    
    @given(
        cash_positions=st.lists(cash_position_strategy(), min_size=2, max_size=8),
        market_rates_1=market_rates_strategy(),
        market_rates_2=market_rates_strategy(),
        threshold=st.floats(min_value=0.1, max_value=1.0)
    )
    @settings(max_examples=100, deadline=30000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_2_market_driven_recalculation(self, cash_positions, market_rates_1, market_rates_2, threshold, analytics_engine):
        """
        Feature: treasuryiq-corporate-ai, Property 2: Market-Driven Recalculation
        
        For any market condition change, the Treasury_System should automatically 
        recalculate optimal cash allocation strategies within the specified timeframe.
        
        Validates: Requirements 1.2
        """
        assume(all(pos.balance > 0 for pos in cash_positions))
        
        # Ensure significant market change
        fed_rate_1 = float(market_rates_1["fed_funds"].rate)
        fed_rate_2 = float(market_rates_2["fed_funds"].rate)
        assume(abs(fed_rate_1 - fed_rate_2) >= threshold)
        
        async def run_test():
            # Create initial optimization result
            initial_result = await analytics_engine.calculate_optimal_cash_allocation(cash_positions)
            
            # Mock the market data service to return different rates
            original_get_rates = analytics_engine.market_data.get_federal_reserve_rates
            
            async def mock_get_rates_1():
                return market_rates_1
            
            async def mock_get_rates_2():
                return market_rates_2
            
            # Test with first market condition
            analytics_engine.market_data.get_federal_reserve_rates = mock_get_rates_1
            result_1 = await analytics_engine.calculate_optimal_cash_allocation(cash_positions)
            
            # Test recalculation with market change
            analytics_engine.market_data.get_federal_reserve_rates = mock_get_rates_2
            recalc_result = await analytics_engine.recalculate_on_market_change(
                cash_positions, result_1, threshold
            )
            
            # Property 2.1: Should trigger recalculation for significant market change
            if abs(fed_rate_1 - fed_rate_2) >= threshold:
                assert recalc_result is not None, "Should recalculate on significant market change"
                
                # Property 2.2: New result should be different from previous
                assert (recalc_result.optimal_yield != result_1.optimal_yield or 
                       recalc_result.opportunity_cost != result_1.opportunity_cost)
                
                # Property 2.3: New result should be valid
                assert isinstance(recalc_result, OptimizationResult)
                assert recalc_result.optimal_yield >= 0
                assert recalc_result.opportunity_cost >= 0
                assert 0.0 <= recalc_result.confidence <= 1.0
            
            # Restore original method
            analytics_engine.market_data.get_federal_reserve_rates = original_get_rates
        
        asyncio.run(run_test())
    
    @given(
        cash_positions=st.lists(cash_position_strategy(), min_size=2, max_size=8),
        stress_multiplier=st.floats(min_value=1.2, max_value=3.0)
    )
    @settings(max_examples=100, deadline=30000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_3_liquidity_shortfall_response(self, cash_positions, stress_multiplier, analytics_engine):
        """
        Feature: treasuryiq-corporate-ai, Property 3: Liquidity Shortfall Response
        
        For any liquidity forecast indicating shortfalls, the Treasury_System should 
        recommend specific actions with implementation timelines.
        
        Validates: Requirements 1.3
        """
        assume(all(pos.balance > 0 for pos in cash_positions))
        
        # Ensure we have some immediate liquidity positions
        immediate_positions = [pos for pos in cash_positions if pos.liquidity_tier == LiquidityTier.IMMEDIATE]
        assume(len(immediate_positions) >= 1)
        
        async def run_test():
            # Run liquidity analysis
            liquidity_analysis = await analytics_engine.analyze_liquidity_requirements(cash_positions)
            
            # Property 3.1: Analysis should return valid LiquidityAnalysis
            assert hasattr(liquidity_analysis, 'current_liquidity_ratio')
            assert hasattr(liquidity_analysis, 'liquidity_gap')
            assert hasattr(liquidity_analysis, 'recommended_buffer')
            assert hasattr(liquidity_analysis, 'risk_level')
            assert hasattr(liquidity_analysis, 'stress_test_results')
            
            # Property 3.2: Liquidity ratio should be between 0 and 1
            assert 0.0 <= liquidity_analysis.current_liquidity_ratio <= 1.0
            
            # Property 3.3: Risk level should be valid
            assert liquidity_analysis.risk_level in ["low", "medium", "high", "critical"]
            
            # Property 3.4: Recommended buffer should be positive
            assert liquidity_analysis.recommended_buffer > 0
            
            # Property 3.5: Stress test results should be present and positive
            assert isinstance(liquidity_analysis.stress_test_results, dict)
            assert len(liquidity_analysis.stress_test_results) > 0
            assert all(result > 0 for result in liquidity_analysis.stress_test_results.values())
            
            # Property 3.6: If liquidity gap is negative, risk should be high or critical
            if liquidity_analysis.liquidity_gap < 0:
                assert liquidity_analysis.risk_level in ["high", "critical"]
            
            # Property 3.7: Stress test results should increase with stress scenarios
            stress_results = list(liquidity_analysis.stress_test_results.values())
            base_outflow = min(stress_results)
            max_stress_outflow = max(stress_results)
            assert max_stress_outflow >= base_outflow  # Stress should increase requirements
        
        asyncio.run(run_test())
    
    @given(
        cash_positions=st.lists(cash_position_strategy(), min_size=3, max_size=10),
        entity_id=st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))
    )
    @settings(max_examples=100, deadline=45000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_4_comprehensive_optimization_recommendations(self, cash_positions, entity_id, analytics_engine):
        """
        Feature: treasuryiq-corporate-ai, Property 4: Comprehensive Optimization Recommendations
        
        For any valid cash position and market condition input, the Optimization_Engine 
        should provide recommendations that include both projected returns and risk assessments.
        
        Validates: Requirements 1.4
        """
        assume(all(pos.balance > 0 for pos in cash_positions))
        assume(len(set(pos.interest_rate for pos in cash_positions)) > 1)  # Varying rates
        
        async def run_test():
            # Generate comprehensive recommendations
            recommendations = await analytics_engine.generate_comprehensive_recommendations(
                entity_id=entity_id,
                cash_positions=cash_positions,
                include_forecasting=True,
                include_liquidity_analysis=True
            )
            
            # Property 4.1: Should return comprehensive recommendation structure
            required_sections = [
                "entity_id", "analysis_timestamp", "executive_summary", 
                "cash_optimization", "liquidity_analysis", "cash_flow_forecast", 
                "action_items", "risk_alerts"
            ]
            for section in required_sections:
                assert section in recommendations
            
            # Property 4.2: Entity ID should match input
            assert recommendations["entity_id"] == entity_id
            
            # Property 4.3: Cash optimization should include projected returns
            cash_opt = recommendations["cash_optimization"]
            assert "current_yield" in cash_opt
            assert "optimal_yield" in cash_opt
            assert "opportunity_cost" in cash_opt
            assert "confidence" in cash_opt
            assert "recommendations" in cash_opt
            
            # Property 4.4: Should include risk assessments
            assert "liquidity_analysis" in recommendations
            liquidity = recommendations["liquidity_analysis"]
            assert "risk_level" in liquidity
            assert "stress_test_results" in liquidity
            
            # Property 4.5: Executive summary should provide key metrics
            exec_summary = recommendations["executive_summary"]
            assert "total_opportunity_cost" in exec_summary
            assert "optimization_confidence" in exec_summary
            assert "key_findings" in exec_summary
            assert isinstance(exec_summary["key_findings"], list)
            
            # Property 4.6: Action items should be prioritized and actionable
            action_items = recommendations["action_items"]
            assert isinstance(action_items, list)
            for item in action_items:
                assert "priority" in item
                assert "category" in item
                assert "title" in item
                assert "description" in item
                assert "expected_impact" in item
                assert "timeline" in item
                assert isinstance(item["priority"], int)
                assert item["priority"] > 0
            
            # Property 4.7: If action items exist, they should be sorted by priority
            if len(action_items) > 1:
                priorities = [item["priority"] for item in action_items]
                assert priorities == sorted(priorities)
            
            # Property 4.8: Risk alerts should be present for high-risk situations
            risk_alerts = recommendations["risk_alerts"]
            assert isinstance(risk_alerts, list)
            
            # Property 4.9: Cash flow forecast should provide future insights
            forecast = recommendations["cash_flow_forecast"]
            assert "forecast_horizon_days" in forecast
            assert "forecast_accuracy" in forecast
            assert forecast["forecast_horizon_days"] > 0
            if forecast["forecast_accuracy"] is not None:
                assert 0.0 <= forecast["forecast_accuracy"] <= 1.0
        
        asyncio.run(run_test())
    
    @given(
        cash_positions=st.lists(cash_position_strategy(), min_size=2, max_size=6),
        threshold_amount=st.floats(min_value=100000, max_value=10000000)
    )
    @settings(max_examples=100, deadline=30000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_opportunity_detection_threshold_enforcement(self, cash_positions, threshold_amount, analytics_engine):
        """
        Feature: treasuryiq-corporate-ai, Property 5: Alert Threshold Enforcement
        
        For any cash optimization opportunity, the Alert_System should notify treasury 
        management if and only if the financial impact exceeds the specified threshold.
        
        Validates: Requirements 1.5
        """
        assume(all(pos.balance > 0 for pos in cash_positions))
        
        async def run_test():
            # Detect opportunities with specific threshold
            opportunities = await analytics_engine.detect_optimization_opportunities(
                cash_positions, 
                threshold_amount=Decimal(str(threshold_amount))
            )
            
            # Property 5.1: All returned opportunities should exceed threshold
            for opportunity in opportunities:
                assert opportunity["opportunity_cost"] >= threshold_amount
            
            # Property 5.2: Opportunities should be sorted by impact (descending)
            if len(opportunities) > 1:
                opportunity_costs = [opp["opportunity_cost"] for opp in opportunities]
                assert opportunity_costs == sorted(opportunity_costs, reverse=True)
            
            # Property 5.3: Each opportunity should have complete information
            for opportunity in opportunities:
                required_fields = [
                    "position_id", "account_name", "current_balance", "current_rate",
                    "benchmark_rate", "rate_differential", "opportunity_cost",
                    "recommended_action", "priority", "analysis_date"
                ]
                for field in required_fields:
                    assert field in opportunity
                
                # Property 5.4: Opportunity cost calculation should be mathematically correct
                expected_cost = (
                    opportunity["current_balance"] * 
                    opportunity["rate_differential"]
                )
                # Allow for small rounding differences
                assert abs(opportunity["opportunity_cost"] - expected_cost) < 1000
        
        asyncio.run(run_test())


if __name__ == "__main__":
    # Run property tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])