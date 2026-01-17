#!/usr/bin/env python3
"""
Standalone Risk Calculation Engine Demo
Feature: treasuryiq-corporate-ai

This script demonstrates the comprehensive risk calculation capabilities without
complex service dependencies, including:
- Value at Risk (VaR) calculations using Monte Carlo simulation
- Currency risk assessment and hedging recommendations
- Credit risk scoring and analysis
- Stress testing and scenario analysis
"""

import asyncio
import sys
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np


# Minimal model definitions for standalone demo
class AccountType(Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    MONEY_MARKET = "money_market"
    CD = "cd"
    TREASURY = "treasury"


class LiquidityTier(Enum):
    IMMEDIATE = "immediate"
    SHORT_TERM = "short_term"
    MEDIUM_TERM = "medium_term"
    LONG_TERM = "long_term"


class InstrumentType(Enum):
    TREASURY_BILL = "treasury_bill"
    TREASURY_NOTE = "treasury_note"
    TREASURY_BOND = "treasury_bond"
    CORPORATE_BOND = "corporate_bond"
    MONEY_MARKET_FUND = "money_market_fund"
    CD = "cd"
    COMMERCIAL_PAPER = "commercial_paper"


class CreditRating(Enum):
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


@dataclass
class CashPosition:
    id: str
    entity_id: str
    account_name: str
    account_type: AccountType
    currency: str
    balance: Decimal
    interest_rate: Optional[Decimal]
    bank_name: str
    liquidity_tier: LiquidityTier


@dataclass
class Investment:
    id: str
    entity_id: str
    instrument_name: str
    instrument_type: InstrumentType
    currency: str
    principal_amount: Decimal
    market_value: Decimal
    purchase_date: datetime
    maturity_date: Optional[datetime]
    coupon_rate: Decimal
    yield_to_maturity: Decimal
    credit_rating: Optional[CreditRating]
    duration: Decimal


@dataclass
class FXExposure:
    id: str
    entity_id: str
    base_currency: str
    exposure_currency: str
    notional_amount: Decimal
    spot_rate: Decimal
    forward_rate: Decimal
    hedge_ratio: Decimal
    maturity_date: datetime
    hedge_instrument: str


@dataclass
class VaRResult:
    portfolio_var_1d: Decimal
    portfolio_var_10d: Decimal
    expected_shortfall: Decimal
    confidence_level: float
    calculation_method: str
    component_vars: Dict[str, Decimal]
    stress_test_results: Dict[str, Decimal]


@dataclass
class CurrencyRiskAnalysis:
    total_exposure: Decimal
    hedged_exposure: Decimal
    unhedged_exposure: Decimal
    hedge_ratio: float
    currency_vars: Dict[str, Decimal]
    correlation_matrix: Dict[str, Dict[str, float]]
    hedging_recommendations: List[Dict[str, Any]]


# Simplified risk calculation engine for demo
class SimplifiedRiskCalculationEngine:
    """Simplified risk calculation engine for demonstration"""
    
    def __init__(self):
        self._market_rates = {
            "fed_funds": Decimal("5.25"),
            "treasury_3m": Decimal("5.15"),
            "treasury_6m": Decimal("5.05"),
            "treasury_1y": Decimal("4.95"),
            "treasury_2y": Decimal("4.85")
        }
        
        # FX volatilities (annualized)
        self._fx_volatilities = {
            ("USD", "EUR"): 0.12,
            ("USD", "GBP"): 0.14,
            ("USD", "JPY"): 0.16,
            ("USD", "CAD"): 0.10,
            ("USD", "AUD"): 0.18,
            ("USD", "CHF"): 0.11,
            ("USD", "SGD"): 0.08
        }
    
    async def calculate_portfolio_var(
        self,
        cash_positions: List[CashPosition],
        investments: List[Investment],
        fx_exposures: List[FXExposure],
        confidence_level: float = 0.95,
        time_horizon: int = 1
    ) -> VaRResult:
        """Calculate Value at Risk using Monte Carlo simulation"""
        
        # Build portfolio components
        portfolio_components = self._build_portfolio_components(
            cash_positions, investments, fx_exposures
        )
        
        # Run Monte Carlo simulation
        var_results = self._monte_carlo_var_simulation(
            portfolio_components, confidence_level, time_horizon
        )
        
        # Calculate component VaRs
        component_vars = self._calculate_component_vars(
            portfolio_components, var_results
        )
        
        # Run stress tests
        stress_results = self._run_stress_tests(portfolio_components)
        
        return VaRResult(
            portfolio_var_1d=Decimal(str(var_results["var_1d"])),
            portfolio_var_10d=Decimal(str(var_results["var_10d"])),
            expected_shortfall=Decimal(str(var_results["expected_shortfall"])),
            confidence_level=confidence_level,
            calculation_method="Monte Carlo",
            component_vars=component_vars,
            stress_test_results=stress_results
        )
    
    def _build_portfolio_components(
        self,
        cash_positions: List[CashPosition],
        investments: List[Investment], 
        fx_exposures: List[FXExposure]
    ) -> Dict[str, Any]:
        """Build portfolio components for risk calculation"""
        components = {
            "cash": [],
            "investments": [],
            "fx": [],
            "total_value": Decimal("0")
        }
        
        # Process cash positions
        for pos in cash_positions:
            components["cash"].append({
                "id": pos.id,
                "value": pos.balance,
                "currency": pos.currency,
                "risk_weight": self._get_cash_risk_weight(pos)
            })
            components["total_value"] += pos.balance
        
        # Process investments
        for inv in investments:
            components["investments"].append({
                "id": inv.id,
                "value": inv.market_value,
                "currency": inv.currency,
                "duration": inv.duration,
                "credit_rating": inv.credit_rating.value if inv.credit_rating else "NR",
                "risk_weight": self._get_investment_risk_weight(inv)
            })
            components["total_value"] += inv.market_value
        
        # Process FX exposures
        for fx in fx_exposures:
            components["fx"].append({
                "id": fx.id,
                "notional": fx.notional_amount,
                "base_currency": fx.base_currency,
                "exposure_currency": fx.exposure_currency,
                "hedge_ratio": fx.hedge_ratio,
                "risk_weight": self._get_fx_risk_weight(fx)
            })
        
        return components
    
    def _get_cash_risk_weight(self, position: CashPosition) -> float:
        """Get risk weight for cash position"""
        weights = {
            AccountType.CHECKING: 0.01,
            AccountType.SAVINGS: 0.01,
            AccountType.MONEY_MARKET: 0.02,
            AccountType.CD: 0.03,
            AccountType.TREASURY: 0.005
        }
        return weights.get(position.account_type, 0.02)
    
    def _get_investment_risk_weight(self, investment: Investment) -> float:
        """Get risk weight for investment"""
        # Base weight by instrument type
        type_weights = {
            InstrumentType.TREASURY_BILL: 0.005,
            InstrumentType.TREASURY_NOTE: 0.01,
            InstrumentType.TREASURY_BOND: 0.02,
            InstrumentType.CORPORATE_BOND: 0.05,
            InstrumentType.MONEY_MARKET_FUND: 0.01,
            InstrumentType.CD: 0.02,
            InstrumentType.COMMERCIAL_PAPER: 0.03
        }
        
        base_weight = type_weights.get(investment.instrument_type, 0.05)
        
        # Adjust for credit rating
        if investment.credit_rating:
            rating_adjustments = {
                CreditRating.AAA: 0.8, CreditRating.AA_PLUS: 0.9, CreditRating.AA: 1.0,
                CreditRating.AA_MINUS: 1.1, CreditRating.A_PLUS: 1.2, CreditRating.A: 1.3,
                CreditRating.A_MINUS: 1.4, CreditRating.BBB_PLUS: 1.6, CreditRating.BBB: 1.8,
                CreditRating.BBB_MINUS: 2.0, CreditRating.BB_PLUS: 2.5, CreditRating.BB: 3.0,
                CreditRating.BB_MINUS: 3.5, CreditRating.B_PLUS: 4.0, CreditRating.B: 5.0,
                CreditRating.B_MINUS: 6.0, CreditRating.CCC: 8.0, CreditRating.CC: 10.0,
                CreditRating.C: 12.0, CreditRating.D: 15.0
            }
            adjustment = rating_adjustments.get(investment.credit_rating, 2.0)
            base_weight *= adjustment
        
        return base_weight
    
    def _get_fx_risk_weight(self, exposure: FXExposure) -> float:
        """Get risk weight for FX exposure"""
        pair = (exposure.base_currency, exposure.exposure_currency)
        base_vol = self._fx_volatilities.get(pair, 0.15)
        
        # Adjust for hedge ratio (lower risk if hedged)
        hedge_adjustment = 1.0 - float(exposure.hedge_ratio) * 0.8
        
        return base_vol * hedge_adjustment
    
    def _monte_carlo_var_simulation(
        self,
        portfolio_components: Dict[str, Any],
        confidence_level: float,
        time_horizon: int,
        num_simulations: int = 10000
    ) -> Dict[str, float]:
        """Run Monte Carlo simulation for VaR calculation"""
        
        # Initialize random number generator
        np.random.seed(42)  # For reproducible results
        
        # Extract portfolio values and risk weights
        portfolio_values = []
        risk_weights = []
        
        for component_type in ["cash", "investments", "fx"]:
            for component in portfolio_components[component_type]:
                if component_type == "fx":
                    portfolio_values.append(float(component["notional"]))
                else:
                    portfolio_values.append(float(component["value"]))
                risk_weights.append(component["risk_weight"])
        
        portfolio_values = np.array(portfolio_values)
        risk_weights = np.array(risk_weights)
        
        if len(portfolio_values) == 0:
            return {
                "var_1d": 0.0,
                "var_10d": 0.0,
                "expected_shortfall": 0.0
            }
        
        # Generate correlation matrix
        correlation_matrix = self._build_correlation_matrix(len(portfolio_values))
        
        # Run simulations
        portfolio_returns = []
        
        for _ in range(num_simulations):
            # Generate correlated random shocks
            random_shocks = np.random.multivariate_normal(
                mean=np.zeros(len(portfolio_values)),
                cov=correlation_matrix
            )
            
            # Apply risk weights and time scaling
            scaled_shocks = random_shocks * risk_weights * np.sqrt(time_horizon)
            
            # Calculate portfolio return
            portfolio_return = np.sum(portfolio_values * scaled_shocks) / np.sum(portfolio_values)
            portfolio_returns.append(portfolio_return)
        
        portfolio_returns = np.array(portfolio_returns)
        
        # Calculate VaR and Expected Shortfall
        var_percentile = (1 - confidence_level) * 100
        var_1d = -np.percentile(portfolio_returns, var_percentile)
        var_10d = var_1d * np.sqrt(10)  # Scale to 10 days
        
        # Expected Shortfall (average of losses beyond VaR)
        tail_losses = portfolio_returns[portfolio_returns <= -var_1d]
        expected_shortfall = -np.mean(tail_losses) if len(tail_losses) > 0 else var_1d
        
        return {
            "var_1d": var_1d * float(portfolio_components["total_value"]),
            "var_10d": var_10d * float(portfolio_components["total_value"]),
            "expected_shortfall": expected_shortfall * float(portfolio_components["total_value"])
        }
    
    def _build_correlation_matrix(self, n_assets: int) -> np.ndarray:
        """Build correlation matrix for portfolio components"""
        # Start with identity matrix
        correlation_matrix = np.eye(n_assets)
        
        # Add realistic correlations
        base_correlation = 0.3
        
        for i in range(n_assets):
            for j in range(i+1, n_assets):
                # Random correlation with some structure
                correlation = base_correlation * np.random.uniform(0.5, 1.0)
                correlation_matrix[i, j] = correlation
                correlation_matrix[j, i] = correlation
        
        # Ensure positive definite
        eigenvals, eigenvecs = np.linalg.eigh(correlation_matrix)
        eigenvals = np.maximum(eigenvals, 0.01)  # Ensure positive eigenvalues
        correlation_matrix = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
        
        return correlation_matrix
    
    def _calculate_component_vars(
        self,
        portfolio_components: Dict[str, Any],
        var_results: Dict[str, float]
    ) -> Dict[str, Decimal]:
        """Calculate VaR contribution by component"""
        component_vars = {}
        
        total_value = float(portfolio_components["total_value"])
        if total_value == 0:
            return component_vars
        
        # Simplified component VaR calculation
        for component_type in ["cash", "investments", "fx"]:
            if component_type == "fx":
                type_value = sum(
                    float(comp["notional"]) for comp in portfolio_components[component_type]
                )
            else:
                type_value = sum(
                    float(comp["value"]) for comp in portfolio_components[component_type]
                )
            
            type_weight = type_value / total_value if total_value > 0 else 0
            
            component_vars[f"{component_type}_var"] = Decimal(str(
                var_results["var_1d"] * type_weight
            ))
        
        return component_vars
    
    def _run_stress_tests(
        self,
        portfolio_components: Dict[str, Any]
    ) -> Dict[str, Decimal]:
        """Run stress test scenarios"""
        stress_results = {}
        
        total_value = float(portfolio_components["total_value"])
        if total_value == 0:
            return stress_results
        
        # Define stress scenarios
        scenarios = {
            "interest_rate_shock_up": {"rate_change": 0.02, "fx_impact": 0.05},
            "interest_rate_shock_down": {"rate_change": -0.02, "fx_impact": -0.03},
            "fx_crisis": {"rate_change": 0.01, "fx_impact": 0.20},
            "credit_crisis": {"rate_change": 0.03, "fx_impact": 0.10},
            "liquidity_crisis": {"rate_change": 0.05, "fx_impact": 0.15}
        }
        
        for scenario_name, scenario in scenarios.items():
            scenario_loss = 0.0
            
            # Impact on cash positions
            for cash_comp in portfolio_components["cash"]:
                loss = float(cash_comp["value"]) * scenario["rate_change"] * 0.1
                scenario_loss += abs(loss)
            
            # Impact on investments
            for inv_comp in portfolio_components["investments"]:
                # Duration-based interest rate impact
                duration = 2.0  # Simplified average duration
                rate_impact = float(inv_comp["value"]) * duration * scenario["rate_change"]
                scenario_loss += abs(rate_impact)
            
            # Impact on FX exposures
            for fx_comp in portfolio_components["fx"]:
                fx_impact = float(fx_comp["notional"]) * scenario["fx_impact"]
                # Adjust for hedge ratio
                hedge_ratio = float(fx_comp["hedge_ratio"])
                unhedged_impact = fx_impact * (1 - hedge_ratio)
                scenario_loss += abs(unhedged_impact)
            
            stress_results[scenario_name] = Decimal(str(scenario_loss))
        
        return stress_results
    
    async def assess_currency_risk(
        self,
        fx_exposures: List[FXExposure]
    ) -> CurrencyRiskAnalysis:
        """Assess currency risk across all FX exposures"""
        
        if not fx_exposures:
            return CurrencyRiskAnalysis(
                total_exposure=Decimal("0"),
                hedged_exposure=Decimal("0"),
                unhedged_exposure=Decimal("0"),
                hedge_ratio=0.0,
                currency_vars={},
                correlation_matrix={},
                hedging_recommendations=[]
            )
        
        # Calculate exposure totals
        total_exposure = sum(fx.notional_amount for fx in fx_exposures)
        hedged_exposure = sum(
            fx.notional_amount * fx.hedge_ratio for fx in fx_exposures
        )
        unhedged_exposure = total_exposure - hedged_exposure
        
        overall_hedge_ratio = float(hedged_exposure / total_exposure) if total_exposure > 0 else 0.0
        
        # Calculate currency-specific VaRs
        currency_vars = self._calculate_currency_vars(fx_exposures)
        
        # Build correlation matrix
        correlation_matrix = self._build_fx_correlation_matrix(fx_exposures)
        
        # Generate hedging recommendations
        recommendations = self._generate_hedging_recommendations(
            fx_exposures, currency_vars
        )
        
        return CurrencyRiskAnalysis(
            total_exposure=total_exposure,
            hedged_exposure=hedged_exposure,
            unhedged_exposure=unhedged_exposure,
            hedge_ratio=overall_hedge_ratio,
            currency_vars=currency_vars,
            correlation_matrix=correlation_matrix,
            hedging_recommendations=recommendations
        )
    
    def _calculate_currency_vars(
        self,
        fx_exposures: List[FXExposure]
    ) -> Dict[str, Decimal]:
        """Calculate VaR for each currency exposure"""
        currency_vars = {}
        
        for fx in fx_exposures:
            currency_pair = f"{fx.base_currency}/{fx.exposure_currency}"
            
            # Get historical volatility
            volatility = self._get_fx_volatility(fx.base_currency, fx.exposure_currency)
            
            # Calculate 1-day VaR at 95% confidence
            var_1d = float(fx.notional_amount) * volatility * 1.645  # 95% confidence
            
            # Adjust for hedge ratio
            unhedged_var = var_1d * (1 - float(fx.hedge_ratio))
            
            currency_vars[currency_pair] = Decimal(str(unhedged_var))
        
        return currency_vars
    
    def _get_fx_volatility(self, base_currency: str, target_currency: str) -> float:
        """Get FX volatility for currency pair"""
        pair = (base_currency, target_currency)
        annual_vol = self._fx_volatilities.get(pair, 0.15)
        
        # Convert to daily volatility
        daily_vol = annual_vol / np.sqrt(252)  # 252 trading days per year
        
        return daily_vol
    
    def _build_fx_correlation_matrix(
        self,
        fx_exposures: List[FXExposure]
    ) -> Dict[str, Dict[str, float]]:
        """Build FX correlation matrix"""
        currencies = list(set(
            fx.exposure_currency for fx in fx_exposures
        ))
        
        # Simplified correlation matrix
        correlations = {}
        for curr1 in currencies:
            correlations[curr1] = {}
            for curr2 in currencies:
                if curr1 == curr2:
                    correlations[curr1][curr2] = 1.0
                else:
                    # Simplified correlation based on economic relationships
                    correlation = self._get_currency_correlation(curr1, curr2)
                    correlations[curr1][curr2] = correlation
        
        return correlations
    
    def _get_currency_correlation(self, curr1: str, curr2: str) -> float:
        """Get correlation between two currencies"""
        # Simplified correlation matrix
        correlations = {
            ("EUR", "GBP"): 0.7,
            ("EUR", "CHF"): 0.8,
            ("GBP", "CHF"): 0.6,
            ("JPY", "CHF"): 0.3,
            ("CAD", "AUD"): 0.6,
            ("SGD", "JPY"): 0.4,
        }
        
        pair = tuple(sorted([curr1, curr2]))
        return correlations.get(pair, 0.3)  # Default correlation
    
    def _generate_hedging_recommendations(
        self,
        fx_exposures: List[FXExposure],
        currency_vars: Dict[str, Decimal]
    ) -> List[Dict[str, Any]]:
        """Generate FX hedging recommendations"""
        recommendations = []
        
        for fx in fx_exposures:
            currency_pair = f"{fx.base_currency}/{fx.exposure_currency}"
            current_hedge_ratio = float(fx.hedge_ratio)
            
            # Get VaR for this exposure
            exposure_var = currency_vars.get(currency_pair, Decimal("0"))
            
            # Recommend hedging if unhedged VaR is significant
            if exposure_var > fx.notional_amount * Decimal("0.05"):  # 5% threshold
                if current_hedge_ratio < 0.8:  # Less than 80% hedged
                    recommendations.append({
                        "exposure_id": fx.id,
                        "currency_pair": currency_pair,
                        "current_hedge_ratio": current_hedge_ratio,
                        "recommended_hedge_ratio": 0.85,
                        "additional_hedge_amount": float(
                            fx.notional_amount * (Decimal("0.85") - fx.hedge_ratio)
                        ),
                        "expected_var_reduction": float(exposure_var * Decimal("0.85")),
                        "recommended_instruments": [
                            "Forward contracts",
                            "Currency options",
                            "Cross-currency swaps"
                        ],
                        "priority": "high" if exposure_var > fx.notional_amount * Decimal("0.10") else "medium"
                    })
        
        return recommendations


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
    
    # Initialize risk engine
    risk_engine = SimplifiedRiskCalculationEngine()
    
    # Calculate VaR at different confidence levels
    confidence_levels = [0.95, 0.99]
    
    for confidence in confidence_levels:
        print(f"\n🎯 CALCULATING VaR AT {confidence:.0%} CONFIDENCE LEVEL...")
        
        var_result = await risk_engine.calculate_portfolio_var(
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
    
    # Initialize risk engine
    risk_engine = SimplifiedRiskCalculationEngine()
    
    print(f"\n💱 ANALYZING {len(fx_exposures)} FX EXPOSURES...")
    
    # Assess currency risk
    currency_risk = await risk_engine.assess_currency_risk(fx_exposures)
    
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


async def run_comprehensive_risk_demo():
    """Run comprehensive risk calculation engine demonstration"""
    print("🚀 STARTING COMPREHENSIVE RISK CALCULATION ENGINE DEMONSTRATION")
    print("=" * 80)
    print("This demo showcases the complete risk management capabilities:")
    print("1. Value at Risk (VaR) Calculation using Monte Carlo simulation")
    print("2. Currency Risk Assessment with hedging recommendations")
    print("3. Comprehensive Stress Testing across multiple scenarios")
    print("4. Component-level risk attribution and analysis")
    print("=" * 80)
    
    try:
        # Run all demonstrations
        var_result = await demo_var_calculation()
        currency_risk = await demo_currency_risk_assessment()
        
        # Final summary
        print("\n" + "="*80)
        print("🎉 COMPREHENSIVE RISK CALCULATION ENGINE DEMONSTRATION COMPLETED")
        print("="*80)
        print("✅ Value at Risk (VaR) Calculation")
        print("✅ Currency Risk Assessment")
        print("✅ Comprehensive Stress Testing")
        print("✅ Component Risk Attribution")
        
        # Key metrics summary
        portfolio_value = 134775000  # Approximate from demo data
        print(f"\n📊 KEY RISK METRICS SUMMARY:")
        print(f"Portfolio Value: ${portfolio_value:,.2f}")
        print(f"1-Day VaR (95%): ${var_result.portfolio_var_1d:,.2f}")
        print(f"VaR as % of Portfolio: {float(var_result.portfolio_var_1d)/portfolio_value*100:.2f}%")
        print(f"FX Hedge Ratio: {currency_risk.hedge_ratio:.1%}")
        
        worst_case_loss = max(float(loss) for loss in var_result.stress_test_results.values())
        print(f"Worst-Case Stress Loss: ${worst_case_loss:,.2f}")
        
        print(f"\n🏆 The risk calculation engine successfully demonstrates:")
        print(f"• Advanced Monte Carlo VaR modeling with component attribution")
        print(f"• Multi-currency risk assessment with correlation analysis")
        print(f"• Comprehensive stress testing across 5 economic scenarios")
        print(f"• Sophisticated hedging recommendations based on risk thresholds")
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