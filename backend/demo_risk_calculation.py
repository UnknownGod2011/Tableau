#!/usr/bin/env python3
"""
Risk Calculation Engine Demo
Feature: treasuryiq-corporate-ai

This script demonstrates the comprehensive risk calculation capabilities including:
- Value at Risk (VaR) calculations using Monte Carlo simulation
- Currency risk assessment and hedging recommendations
- Credit risk scoring and analysis
- Stress testing and scenario analysis
"""

import asyncio
import sys
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np

# Import models and services
from app.models import CashPosition, Investment, FXExposure
from app.models.cash import AccountType, LiquidityTier
from app.models.investments import InstrumentType, CreditRating
from app.services.risk import RiskCalculationService
from app.services.market_data import MarketDataService


def create_demo_portfolio() -> tuple[List[CashPosition], List[Investment], List[FXExposure]]:
    """Create a comprehensive demo portfolio for GlobalTech Industries"""
    
    # Cash positions across multiple currencies and account types
    cash_positions = [
        CashPosition(
            id="cash_001",
            entity_id="globaltech_us",
            account_name="Primary USD Operating Account",
            account_type=AccountType.CHECKING,
            currency="USD",
            balance=Decimal("15000000"),
            interest_rate=Decimal("0.75"),
            bank_name="JPMorgan Chase",
            liquidity_tier=LiquidityTier.IMMEDIATE
        ),
        CashPosition(
            id="cash_002",
            entity_id="globaltech_us",
            account_name="USD High-Yield Savings",
            account_type=AccountType.SAVINGS,
            currency="USD",
            balance=Decimal("35000000"),
            interest_rate=Decimal("4.25"),
            bank_name="Goldman Sachs",
            liquidity_tier=LiquidityTier.SHORT_TERM
        ),
        CashPosition(
            id="cash_003",
            entity_id="globaltech_eu",
            account_name="EUR Operating Account",
            account_type=AccountType.CHECKING,
            currency="EUR",
            balance=Decimal("8000000"),
            interest_rate=Decimal("2.15"),
            bank_name="Deutsche Bank",
            liquidity_tier=LiquidityTier.IMMEDIATE
        ),
        CashPosition(
            id="cash_004",
            entity_id="globaltech_uk",
            account_name="GBP Money Market",
            account_type=AccountType.MONEY_MARKET,
            currency="GBP",
            balance=Decimal("12000000"),
            interest_rate=Decimal("3.85"),
            bank_name="Barclays",
            liquidity_tier=LiquidityTier.SHORT_TERM
        )
    ]
    
    # Investment portfolio with various instruments and credit ratings
    investments = [
        Investment(
            id="inv_001",
            entity_id="globaltech_us",
            instrument_name="US Treasury 2Y Note",
            instrument_type=InstrumentType.TREASURY_NOTE,
            currency="USD",
            principal_amount=Decimal("25000000"),
            market_value=Decimal("24850000"),
            purchase_date=datetime.now() - timedelta(days=180),
            maturity_date=datetime.now() + timedelta(days=550),
            coupon_rate=Decimal("4.75"),
            yield_to_maturity=Decimal("4.95"),
            credit_rating=CreditRating.AAA,
            duration=Decimal("1.85")
        ),
        Investment(
            id="inv_002",
            entity_id="globaltech_us",
            instrument_name="Apple Inc Corporate Bond",
            instrument_type=InstrumentType.CORPORATE_BOND,
            currency="USD",
            principal_amount=Decimal("10000000"),
            market_value=Decimal("9950000"),
            purchase_date=datetime.now() - timedelta(days=90),
            maturity_date=datetime.now() + timedelta(days=1095),
            coupon_rate=Decimal("3.25"),
            yield_to_maturity=Decimal("3.45"),
            credit_rating=CreditRating.AA_PLUS,
            duration=Decimal("2.75")
        ),
        Investment(
            id="inv_003",
            entity_id="globaltech_us",
            instrument_name="Money Market Fund - Prime",
            instrument_type=InstrumentType.MONEY_MARKET_FUND,
            currency="USD",
            principal_amount=Decimal("20000000"),
            market_value=Decimal("20000000"),
            purchase_date=datetime.now() - timedelta(days=30),
            maturity_date=None,  # Open-ended
            coupon_rate=Decimal("5.15"),
            yield_to_maturity=Decimal("5.15"),
            credit_rating=CreditRating.AAA,
            duration=Decimal("0.08")
        ),
        Investment(
            id="inv_004",
            entity_id="globaltech_eu",
            instrument_name="German Government Bond",
            instrument_type=InstrumentType.TREASURY_BOND,
            currency="EUR",
            principal_amount=Decimal("15000000"),
            market_value=Decimal("14925000"),
            purchase_date=datetime.now() - timedelta(days=120),
            maturity_date=datetime.now() + timedelta(days=1825),
            coupon_rate=Decimal("2.50"),
            yield_to_maturity=Decimal("2.65"),
            credit_rating=CreditRating.AAA,
            duration=Decimal("4.25")
        )
    ]
    
    # FX exposures with varying hedge ratios
    fx_exposures = [
        FXExposure(
            id="fx_001",
            entity_id="globaltech_us",
            base_currency="USD",
            exposure_currency="EUR",
            notional_amount=Decimal("25000000"),
            spot_rate=Decimal("0.92"),
            forward_rate=Decimal("0.918"),
            hedge_ratio=Decimal("0.75"),
            maturity_date=datetime.now() + timedelta(days=90),
            hedge_instrument="Forward Contract"
        ),
        FXExposure(
            id="fx_002",
            entity_id="globaltech_us",
            base_currency="USD",
            exposure_currency="GBP",
            notional_amount=Decimal("18000000"),
            spot_rate=Decimal("0.79"),
            forward_rate=Decimal("0.785"),
            hedge_ratio=Decimal("0.60"),
            maturity_date=datetime.now() + timedelta(days=180),
            hedge_instrument="Currency Option"
        ),
        FXExposure(
            id="fx_003",
            entity_id="globaltech_us",
            base_currency="USD",
            exposure_currency="JPY",
            notional_amount=Decimal("30000000"),
            spot_rate=Decimal("150.25"),
            forward_rate=Decimal("149.80"),
            hedge_ratio=Decimal("0.40"),
            maturity_date=datetime.now() + timedelta(days=270),
            hedge_instrument="Cross-Currency Swap"
        ),
        FXExposure(
            id="fx_004",
            entity_id="globaltech_us",
            base_currency="USD",
            exposure_currency="CAD",
            notional_amount=Decimal("12000000"),
            spot_rate=Decimal("1.35"),
            forward_rate=Decimal("1.348"),
            hedge_ratio=Decimal("0.85"),
            maturity_date=datetime.now() + timedelta(days=60),
            hedge_instrument="Forward Contract"
        )
    ]
    
    return cash_positions, investments, fx_exposures


async def demo_var_calculation():
    """Demonstrate Value at Risk calculation"""
    print("\n" + "="*80)
    print("VALUE AT RISK (VaR) CALCULATION DEMONSTRATION")
    print("="*80)
    
    # Create portfolio
    cash_positions, investments, fx_exposures = create_demo_portfolio()
    
    # Calculate portfolio totals
    total_cash = sum(pos.balance for pos in cash_positions)
    total_investments = sum(inv.market_value for inv in investments)
    total_fx_notional = sum(fx.notional_amount for fx in fx_exposures)
    
    print(f"\n📊 PORTFOLIO COMPOSITION:")
    print(f"Total Cash Positions: ${total_cash:,.2f}")
    print(f"Total Investments: ${total_investments:,.2f}")
    print(f"Total FX Notional: ${total_fx_notional:,.2f}")
    print(f"Total Portfolio Value: ${total_cash + total_investments:,.2f}")
    
    print(f"\n💰 CASH POSITIONS ({len(cash_positions)}):")
    for pos in cash_positions:
        print(f"  • {pos.currency} {pos.account_name}: ${pos.balance:,.2f} @ {pos.interest_rate}%")
    
    print(f"\n📈 INVESTMENTS ({len(investments)}):")
    for inv in investments:
        print(f"  • {inv.instrument_name}: ${inv.market_value:,.2f} ({inv.credit_rating.value if inv.credit_rating else 'NR'})")
    
    print(f"\n💱 FX EXPOSURES ({len(fx_exposures)}):")
    for fx in fx_exposures:
        hedge_pct = float(fx.hedge_ratio) * 100
        print(f"  • {fx.base_currency}/{fx.exposure_currency}: ${fx.notional_amount:,.2f} ({hedge_pct:.0f}% hedged)")
    
    # Initialize services
    market_data_service = MarketDataService()
    risk_service = RiskCalculationService(market_data_service)
    
    # Calculate VaR at different confidence levels
    confidence_levels = [0.95, 0.99]
    
    for confidence in confidence_levels:
        print(f"\n🎯 CALCULATING VaR AT {confidence:.0%} CONFIDENCE LEVEL...")
        
        var_result = await risk_service.calculate_portfolio_var(
            cash_positions=cash_positions,
            investments=investments,
            fx_exposures=fx_exposures,
            confidence_level=confidence,
            time_horizon=1
        )
        
        print(f"\n📊 VaR RESULTS ({confidence:.0%} confidence):")
        print(f"1-Day VaR: ${var_result.portfolio_var_1d:,.2f}")
        print(f"10-Day VaR: ${var_result.portfolio_var_10d:,.2f}")
        print(f"Expected Shortfall: ${var_result.expected_shortfall:,.2f}")
        print(f"Calculation Method: {var_result.calculation_method}")
        
        # VaR as percentage of portfolio
        portfolio_value = total_cash + total_investments
        var_percentage = float(var_result.portfolio_var_1d) / float(portfolio_value) * 100
        print(f"VaR as % of Portfolio: {var_percentage:.2f}%")
        
        print(f"\n🔍 COMPONENT VaR BREAKDOWN:")
        for component, var_amount in var_result.component_vars.items():
            component_pct = float(var_amount) / float(var_result.portfolio_var_1d) * 100 if var_result.portfolio_var_1d > 0 else 0
            print(f"  • {component.replace('_', ' ').title()}: ${var_amount:,.2f} ({component_pct:.1f}%)")
        
        print(f"\n🧪 STRESS TEST RESULTS:")
        for scenario, loss in var_result.stress_test_results.items():
            scenario_name = scenario.replace('_', ' ').title()
            loss_pct = float(loss) / float(portfolio_value) * 100
            print(f"  • {scenario_name}: ${loss:,.2f} ({loss_pct:.2f}% of portfolio)")
    
    print("✅ VaR Calculation Demonstration - COMPLETED")
    return var_result


async def demo_currency_risk_assessment():
    """Demonstrate currency risk assessment"""
    print("\n" + "="*80)
    print("CURRENCY RISK ASSESSMENT DEMONSTRATION")
    print("="*80)
    
    # Get FX exposures
    _, _, fx_exposures = create_demo_portfolio()
    
    # Initialize services
    market_data_service = MarketDataService()
    risk_service = RiskCalculationService(market_data_service)
    
    print(f"\n💱 ANALYZING {len(fx_exposures)} FX EXPOSURES...")
    
    # Assess currency risk
    currency_risk = await risk_service.assess_currency_risk(fx_exposures)
    
    print(f"\n📊 CURRENCY RISK SUMMARY:")
    print(f"Total FX Exposure: ${currency_risk.total_exposure:,.2f}")
    print(f"Hedged Exposure: ${currency_risk.hedged_exposure:,.2f}")
    print(f"Unhedged Exposure: ${currency_risk.unhedged_exposure:,.2f}")
    print(f"Overall Hedge Ratio: {currency_risk.hedge_ratio:.1%}")
    
    # Risk assessment
    unhedged_ratio = float(currency_risk.unhedged_exposure) / float(currency_risk.total_exposure) if currency_risk.total_exposure > 0 else 0
    if unhedged_ratio > 0.5:
        risk_level = "HIGH"
    elif unhedged_ratio > 0.3:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    print(f"Currency Risk Level: {risk_level}")
    
    print(f"\n💰 CURRENCY-SPECIFIC VaR:")
    total_currency_var = sum(float(var) for var in currency_risk.currency_vars.values())
    for currency_pair, var_amount in currency_risk.currency_vars.items():
        var_pct = float(var_amount) / total_currency_var * 100 if total_currency_var > 0 else 0
        print(f"  • {currency_pair}: ${var_amount:,.2f} ({var_pct:.1f}% of total currency VaR)")
    
    print(f"\n🔗 CURRENCY CORRELATION MATRIX:")
    currencies = list(currency_risk.correlation_matrix.keys())
    if currencies:
        print("     ", end="")
        for curr in currencies:
            print(f"{curr:>8}", end="")
        print()
        
        for curr1 in currencies:
            print(f"{curr1:>4} ", end="")
            for curr2 in currencies:
                correlation = currency_risk.correlation_matrix[curr1][curr2]
                print(f"{correlation:>8.2f}", end="")
            print()
    
    print(f"\n💡 HEDGING RECOMMENDATIONS ({len(currency_risk.hedging_recommendations)}):")
    if currency_risk.hedging_recommendations:
        for i, rec in enumerate(currency_risk.hedging_recommendations, 1):
            print(f"\n{i}. {rec['currency_pair']} Exposure")
            print(f"   Current Hedge Ratio: {rec['current_hedge_ratio']:.1%}")
            print(f"   Recommended Hedge Ratio: {rec['recommended_hedge_ratio']:.1%}")
            print(f"   Additional Hedge Amount: ${rec['additional_hedge_amount']:,.2f}")
            print(f"   Expected VaR Reduction: ${rec['expected_var_reduction']:,.2f}")
            print(f"   Priority: {rec['priority'].upper()}")
            print(f"   Recommended Instruments: {', '.join(rec['recommended_instruments'])}")
    else:
        print("   No additional hedging recommendations at this time.")
        print("   Current hedge ratios appear adequate for risk tolerance.")
    
    print("✅ Currency Risk Assessment Demonstration - COMPLETED")
    return currency_risk


async def demo_stress_testing():
    """Demonstrate comprehensive stress testing"""
    print("\n" + "="*80)
    print("COMPREHENSIVE STRESS TESTING DEMONSTRATION")
    print("="*80)
    
    # Create portfolio
    cash_positions, investments, fx_exposures = create_demo_portfolio()
    
    # Initialize services
    market_data_service = MarketDataService()
    risk_service = RiskCalculationService(market_data_service)
    
    print(f"\n🧪 RUNNING COMPREHENSIVE STRESS TESTS...")
    
    # Calculate VaR to get stress test results
    var_result = await risk_service.calculate_portfolio_var(
        cash_positions=cash_positions,
        investments=investments,
        fx_exposures=fx_exposures,
        confidence_level=0.95,
        time_horizon=1
    )
    
    # Portfolio value for context
    portfolio_value = sum(pos.balance for pos in cash_positions) + sum(inv.market_value for inv in investments)
    
    print(f"\n📊 STRESS TEST SCENARIO ANALYSIS:")
    print(f"Base Portfolio Value: ${portfolio_value:,.2f}")
    
    # Sort stress test results by impact
    sorted_scenarios = sorted(
        var_result.stress_test_results.items(),
        key=lambda x: float(x[1]),
        reverse=True
    )
    
    for i, (scenario, loss) in enumerate(sorted_scenarios, 1):
        scenario_name = scenario.replace('_', ' ').title()
        loss_pct = float(loss) / float(portfolio_value) * 100
        
        # Determine severity
        if loss_pct > 10:
            severity = "🔴 CRITICAL"
        elif loss_pct > 5:
            severity = "🟠 HIGH"
        elif loss_pct > 2:
            severity = "🟡 MEDIUM"
        else:
            severity = "🟢 LOW"
        
        print(f"\n{i}. {scenario_name}")
        print(f"   Potential Loss: ${loss:,.2f}")
        print(f"   Impact: {loss_pct:.2f}% of portfolio")
        print(f"   Severity: {severity}")
        
        # Scenario-specific insights
        if "interest_rate" in scenario:
            print(f"   Impact Driver: Duration risk from bond portfolio")
            print(f"   Mitigation: Consider duration hedging or shorter-term instruments")
        elif "fx_crisis" in scenario:
            print(f"   Impact Driver: Unhedged foreign exchange exposures")
            print(f"   Mitigation: Increase FX hedge ratios or use options for downside protection")
        elif "credit_crisis" in scenario:
            print(f"   Impact Driver: Credit spread widening on corporate bonds")
            print(f"   Mitigation: Diversify credit exposure or use credit default swaps")
        elif "liquidity_crisis" in scenario:
            print(f"   Impact Driver: Liquidity premium and forced asset sales")
            print(f"   Mitigation: Maintain higher cash buffers and committed credit lines")
    
    # Risk concentration analysis
    print(f"\n🎯 RISK CONCENTRATION ANALYSIS:")
    
    # Currency concentration
    currency_exposure = {}
    for pos in cash_positions:
        currency_exposure[pos.currency] = currency_exposure.get(pos.currency, 0) + float(pos.balance)
    for inv in investments:
        currency_exposure[inv.currency] = currency_exposure.get(inv.currency, 0) + float(inv.market_value)
    
    total_exposure = sum(currency_exposure.values())
    print(f"\nCurrency Concentration:")
    for currency, exposure in sorted(currency_exposure.items(), key=lambda x: x[1], reverse=True):
        concentration_pct = exposure / total_exposure * 100
        print(f"  • {currency}: ${exposure:,.2f} ({concentration_pct:.1f}%)")
    
    # Credit rating concentration
    credit_exposure = {}
    for inv in investments:
        rating = inv.credit_rating.value if inv.credit_rating else "NR"
        credit_exposure[rating] = credit_exposure.get(rating, 0) + float(inv.market_value)
    
    if credit_exposure:
        print(f"\nCredit Rating Concentration:")
        for rating, exposure in sorted(credit_exposure.items(), key=lambda x: x[1], reverse=True):
            concentration_pct = exposure / sum(credit_exposure.values()) * 100
            print(f"  • {rating}: ${exposure:,.2f} ({concentration_pct:.1f}%)")
    
    print("✅ Comprehensive Stress Testing Demonstration - COMPLETED")
    return var_result.stress_test_results


async def demo_risk_monitoring_alerts():
    """Demonstrate risk monitoring and alert generation"""
    print("\n" + "="*80)
    print("RISK MONITORING & ALERT SYSTEM DEMONSTRATION")
    print("="*80)
    
    # Create portfolio
    cash_positions, investments, fx_exposures = create_demo_portfolio()
    
    # Initialize services
    market_data_service = MarketDataService()
    risk_service = RiskCalculationService(market_data_service)
    
    print(f"\n🚨 RISK MONITORING SYSTEM ACTIVE...")
    
    # Calculate current risk metrics
    var_result = await risk_service.calculate_portfolio_var(
        cash_positions=cash_positions,
        investments=investments,
        fx_exposures=fx_exposures,
        confidence_level=0.95,
        time_horizon=1
    )
    
    currency_risk = await risk_service.assess_currency_risk(fx_exposures)
    
    # Portfolio value
    portfolio_value = sum(pos.balance for pos in cash_positions) + sum(inv.market_value for inv in investments)
    
    # Define risk thresholds
    risk_thresholds = {
        "var_limit": float(portfolio_value) * 0.05,  # 5% of portfolio
        "fx_hedge_ratio_min": 0.70,  # Minimum 70% hedge ratio
        "concentration_limit": 0.40,  # Maximum 40% in single currency
        "credit_rating_min": "BBB",  # Minimum investment grade
        "liquidity_ratio_min": 0.15  # Minimum 15% immediate liquidity
    }
    
    print(f"\n📊 RISK THRESHOLD MONITORING:")
    print(f"Portfolio Value: ${portfolio_value:,.2f}")
    print(f"VaR Limit: ${risk_thresholds['var_limit']:,.2f} (5% of portfolio)")
    
    # Generate alerts based on thresholds
    alerts = []
    
    # VaR threshold check
    current_var = float(var_result.portfolio_var_1d)
    if current_var > risk_thresholds["var_limit"]:
        breach_pct = (current_var / risk_thresholds["var_limit"] - 1) * 100
        alerts.append({
            "type": "var_breach",
            "severity": "high" if breach_pct > 50 else "medium",
            "title": "VaR Limit Exceeded",
            "description": f"Portfolio VaR (${current_var:,.2f}) exceeds limit (${risk_thresholds['var_limit']:,.2f})",
            "breach_percentage": breach_pct,
            "recommended_actions": [
                "Review portfolio composition for risk concentration",
                "Consider reducing high-risk positions",
                "Implement additional hedging strategies"
            ]
        })
    
    # FX hedge ratio check
    if currency_risk.hedge_ratio < risk_thresholds["fx_hedge_ratio_min"]:
        breach_pct = (risk_thresholds["fx_hedge_ratio_min"] - currency_risk.hedge_ratio) * 100
        alerts.append({
            "type": "hedge_ratio_low",
            "severity": "medium",
            "title": "FX Hedge Ratio Below Minimum",
            "description": f"Overall hedge ratio ({currency_risk.hedge_ratio:.1%}) below minimum ({risk_thresholds['fx_hedge_ratio_min']:.1%})",
            "breach_percentage": breach_pct,
            "recommended_actions": [
                "Increase FX hedging across major exposures",
                "Consider using currency options for asymmetric protection",
                "Review hedge accounting implications"
            ]
        })
    
    # Currency concentration check
    currency_exposure = {}
    for pos in cash_positions:
        currency_exposure[pos.currency] = currency_exposure.get(pos.currency, 0) + float(pos.balance)
    for inv in investments:
        currency_exposure[inv.currency] = currency_exposure.get(inv.currency, 0) + float(inv.market_value)
    
    total_exposure = sum(currency_exposure.values())
    for currency, exposure in currency_exposure.items():
        concentration = exposure / total_exposure
        if concentration > risk_thresholds["concentration_limit"]:
            breach_pct = (concentration / risk_thresholds["concentration_limit"] - 1) * 100
            alerts.append({
                "type": "concentration_risk",
                "severity": "medium",
                "title": f"{currency} Concentration Risk",
                "description": f"{currency} exposure ({concentration:.1%}) exceeds limit ({risk_thresholds['concentration_limit']:.1%})",
                "breach_percentage": breach_pct,
                "recommended_actions": [
                    f"Diversify {currency} exposure across other currencies",
                    "Consider natural hedging through operational adjustments",
                    "Implement currency overlay strategy"
                ]
            })
    
    # Liquidity ratio check
    immediate_liquidity = sum(
        float(pos.balance) for pos in cash_positions 
        if pos.liquidity_tier == LiquidityTier.IMMEDIATE
    )
    liquidity_ratio = immediate_liquidity / float(portfolio_value)
    
    if liquidity_ratio < risk_thresholds["liquidity_ratio_min"]:
        breach_pct = (risk_thresholds["liquidity_ratio_min"] - liquidity_ratio) * 100
        alerts.append({
            "type": "liquidity_risk",
            "severity": "high",
            "title": "Insufficient Liquidity Buffer",
            "description": f"Immediate liquidity ({liquidity_ratio:.1%}) below minimum ({risk_thresholds['liquidity_ratio_min']:.1%})",
            "breach_percentage": breach_pct,
            "recommended_actions": [
                "Increase cash reserves in immediate access accounts",
                "Establish committed credit facilities",
                "Review investment maturity profile"
            ]
        })
    
    # Display alerts
    print(f"\n🚨 ACTIVE RISK ALERTS ({len(alerts)}):")
    
    if alerts:
        # Sort by severity
        severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 0), reverse=True)
        
        for i, alert in enumerate(alerts, 1):
            severity_icon = {
                "critical": "🔴",
                "high": "🟠", 
                "medium": "🟡",
                "low": "🟢"
            }.get(alert["severity"], "⚪")
            
            print(f"\n{i}. {severity_icon} {alert['title']} ({alert['severity'].upper()})")
            print(f"   {alert['description']}")
            print(f"   Breach: {alert['breach_percentage']:.1f}%")
            print(f"   Recommended Actions:")
            for action in alert['recommended_actions']:
                print(f"     • {action}")
    else:
        print("   ✅ No active risk alerts - all metrics within acceptable thresholds")
    
    # Risk dashboard summary
    print(f"\n📈 RISK DASHBOARD SUMMARY:")
    print(f"Portfolio VaR (1-day, 95%): ${current_var:,.2f} ({current_var/float(portfolio_value)*100:.2f}% of portfolio)")
    print(f"FX Hedge Ratio: {currency_risk.hedge_ratio:.1%}")
    print(f"Liquidity Ratio: {liquidity_ratio:.1%}")
    print(f"Active Alerts: {len(alerts)}")
    print(f"Risk Score: {'HIGH' if len([a for a in alerts if a['severity'] in ['critical', 'high']]) > 0 else 'MEDIUM' if len(alerts) > 0 else 'LOW'}")
    
    print("✅ Risk Monitoring & Alert System Demonstration - COMPLETED")
    return alerts


async def run_comprehensive_risk_demo():
    """Run comprehensive risk calculation engine demonstration"""
    print("🚀 STARTING COMPREHENSIVE RISK CALCULATION ENGINE DEMONSTRATION")
    print("=" * 80)
    print("This demo showcases the complete risk management capabilities:")
    print("1. Value at Risk (VaR) Calculation using Monte Carlo simulation")
    print("2. Currency Risk Assessment with hedging recommendations")
    print("3. Comprehensive Stress Testing across multiple scenarios")
    print("4. Risk Monitoring & Alert System with threshold management")
    print("=" * 80)
    
    try:
        # Run all demonstrations
        var_result = await demo_var_calculation()
        currency_risk = await demo_currency_risk_assessment()
        stress_results = await demo_stress_testing()
        alerts = await demo_risk_monitoring_alerts()
        
        # Final summary
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE RISK CALCULATION ENGINE DEMONSTRATION COMPLETED")
        print("="*80)
        print("✅ Value at Risk (VaR) Calculation")
        print("✅ Currency Risk Assessment")
        print("✅ Comprehensive Stress Testing")
        print("✅ Risk Monitoring & Alert System")
        
        # Key metrics summary
        portfolio_value = 118500000  # Approximate from demo data
        print(f"\n📊 KEY RISK METRICS SUMMARY:")
        print(f"Portfolio Value: ${portfolio_value:,.2f}")
        print(f"1-Day VaR (95%): ${var_result.portfolio_var_1d:,.2f}")
        print(f"VaR as % of Portfolio: {float(var_result.portfolio_var_1d)/portfolio_value*100:.2f}%")
        print(f"FX Hedge Ratio: {currency_risk.hedge_ratio:.1%}")
        print(f"Active Risk Alerts: {len(alerts)}")
        
        worst_case_loss = max(float(loss) for loss in stress_results.values())
        print(f"Worst-Case Stress Loss: ${worst_case_loss:,.2f}")
        
        print(f"\n🏆 The risk calculation engine successfully demonstrates:")
        print(f"• Advanced Monte Carlo VaR modeling with component attribution")
        print(f"• Multi-currency risk assessment with correlation analysis")
        print(f"• Comprehensive stress testing across 5 economic scenarios")
        print(f"• Real-time risk monitoring with automated alert generation")
        print(f"• Enterprise-grade risk management for $100M+ portfolios")
        
        return True
        
    except Exception as e:
        print(f"\n❌ RISK CALCULATION DEMONSTRATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run the comprehensive demonstration
    success = asyncio.run(run_comprehensive_risk_demo())
    sys.exit(0 if success else 1)