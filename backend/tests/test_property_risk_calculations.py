"""
Property-based tests for risk calculation algorithms
Feature: treasuryiq-corporate-ai

This module implements property-based testing for the core risk calculation
algorithms including VaR, currency risk, and credit risk assessments.

Properties tested:
- Property 6: Risk Threshold Response
- Property 7: Volatility Impact Assessment
- Property 8: Credit Risk Monitoring
- Property 9: Continuous VaR Monitoring
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import numpy as np


# Minimal model definitions for testing
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
    A = "A"
    BBB = "BBB"
    BB = "BB"
    B = "B"
    CCC = "CCC"
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


@dataclass
class CreditRiskScore:
    overall_score: int  # 1-1000 scale
    probability_of_default: float
    expected_loss: Decimal
    risk_grade: str
    key_factors: List[Dict[str, Any]]
    recommendations: List[str]

# Simplified risk calculation engine for testing
class RiskCalculationTestEngine:
    """Simplified risk calculation engine for property testing"""
    
    def __init__(self):
        self._market_rates = {
            "fed_funds": Decimal("5.25"),
            "treasury_3m": Decimal("5.15"),
            "treasury_6m": Decimal("5.05"),
            "treasury_1y": Decimal("4.95"),
            "treasury_2y": Decimal("4.85")
        }
        
        # Risk thresholds for testing
        self._risk_thresholds = {
            "var_limit_pct": 0.05,  # 5% of portfolio
            "fx_hedge_ratio_min": 0.70,  # Minimum 70% hedge ratio
            "concentration_limit": 0.40,  # Maximum 40% in single currency
            "credit_rating_min": "BBB",  # Minimum investment grade
            "liquidity_ratio_min": 0.15  # Minimum 15% immediate liquidity
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
        
        # Run simplified Monte Carlo simulation
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
                CreditRating.A: 1.3, CreditRating.BBB: 1.8, CreditRating.BB: 3.0,
                CreditRating.B: 5.0, CreditRating.CCC: 8.0, CreditRating.D: 15.0
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
        num_simulations: int = 1000  # Reduced for testing speed
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
    
    async def assess_credit_risk(
        self,
        investments: List[Investment]
    ) -> CreditRiskScore:
        """Assess credit risk for investment portfolio"""
        
        if not investments:
            return CreditRiskScore(
                overall_score=1000,  # Perfect score for no investments
                probability_of_default=0.0,
                expected_loss=Decimal("0"),
                risk_grade="AAA",
                key_factors=[],
                recommendations=[]
            )
        
        # Calculate weighted average credit score
        total_value = sum(inv.market_value for inv in investments)
        weighted_score = 0
        
        # Credit rating to score mapping
        rating_scores = {
            CreditRating.AAA: 950, CreditRating.AA_PLUS: 900, CreditRating.AA: 850,
            CreditRating.A: 750, CreditRating.BBB: 650, CreditRating.BB: 500,
            CreditRating.B: 350, CreditRating.CCC: 200, CreditRating.D: 50
        }
        
        for inv in investments:
            if inv.credit_rating:
                score = rating_scores.get(inv.credit_rating, 500)
            else:
                # Default score for unrated investments (assume BBB equivalent)
                score = 650
            weight = float(inv.market_value / total_value)
            weighted_score += score * weight
        
        # Calculate probability of default based on score
        if weighted_score >= 900:
            prob_default = 0.001  # 0.1%
            risk_grade = "AAA"
        elif weighted_score >= 800:
            prob_default = 0.005  # 0.5%
            risk_grade = "AA"
        elif weighted_score >= 700:
            prob_default = 0.02   # 2%
            risk_grade = "A"
        elif weighted_score >= 600:
            prob_default = 0.05   # 5%
            risk_grade = "BBB"
        elif weighted_score >= 400:
            prob_default = 0.15   # 15%
            risk_grade = "BB"
        else:
            prob_default = 0.30   # 30%
            risk_grade = "B"
        
        # Calculate expected loss
        expected_loss = total_value * Decimal(str(prob_default)) * Decimal("0.6")  # 60% loss given default
        
        # Generate key factors and recommendations
        key_factors = []
        recommendations = []
        
        # Analyze concentration risk
        rating_concentration = {}
        for inv in investments:
            if inv.credit_rating:
                rating = inv.credit_rating.value
                rating_concentration[rating] = rating_concentration.get(rating, 0) + float(inv.market_value)
        
        for rating, value in rating_concentration.items():
            concentration_pct = value / float(total_value) * 100
            if concentration_pct > 40:  # More than 40% in single rating
                key_factors.append({
                    "factor": "concentration_risk",
                    "description": f"High concentration in {rating} rated securities ({concentration_pct:.1f}%)",
                    "impact": "high" if concentration_pct > 60 else "medium"
                })
                recommendations.append(f"Diversify credit exposure across different rating categories")
        
        return CreditRiskScore(
            overall_score=int(weighted_score),
            probability_of_default=prob_default,
            expected_loss=expected_loss,
            risk_grade=risk_grade,
            key_factors=key_factors,
            recommendations=recommendations
        )
    
    async def check_risk_thresholds(
        self,
        cash_positions: List[CashPosition],
        investments: List[Investment],
        fx_exposures: List[FXExposure]
    ) -> List[Dict[str, Any]]:
        """Check if portfolio breaches risk thresholds"""
        
        alerts = []
        
        # Calculate portfolio value
        portfolio_value = sum(pos.balance for pos in cash_positions) + sum(inv.market_value for inv in investments)
        
        if portfolio_value == 0:
            return alerts
        
        # Calculate VaR
        var_result = await self.calculate_portfolio_var(cash_positions, investments, fx_exposures)
        
        # VaR threshold check
        var_limit = float(portfolio_value) * self._risk_thresholds["var_limit_pct"]
        current_var = float(var_result.portfolio_var_1d)
        
        if current_var > var_limit:
            breach_pct = (current_var / var_limit - 1) * 100
            alerts.append({
                "type": "var_breach",
                "severity": "high" if breach_pct > 50 else "medium",
                "current_value": current_var,
                "threshold_value": var_limit,
                "breach_percentage": breach_pct,
                "description": f"Portfolio VaR exceeds {self._risk_thresholds['var_limit_pct']:.1%} limit"
            })
        
        # FX hedge ratio check
        if fx_exposures:
            currency_risk = await self.assess_currency_risk(fx_exposures)
            if currency_risk.hedge_ratio < self._risk_thresholds["fx_hedge_ratio_min"]:
                breach_pct = (self._risk_thresholds["fx_hedge_ratio_min"] - currency_risk.hedge_ratio) * 100
                alerts.append({
                    "type": "hedge_ratio_low",
                    "severity": "medium",
                    "current_value": currency_risk.hedge_ratio,
                    "threshold_value": self._risk_thresholds["fx_hedge_ratio_min"],
                    "breach_percentage": breach_pct,
                    "description": f"FX hedge ratio below {self._risk_thresholds['fx_hedge_ratio_min']:.1%} minimum"
                })
        
        return alerts

# Test data generation strategies
@st.composite
def cash_position_strategy(draw):
    """Generate valid cash positions for property testing"""
    account_types = list(AccountType)
    liquidity_tiers = list(LiquidityTier)
    
    # Use fixed base date to avoid flaky tests
    base_date = datetime(2024, 1, 1)
    
    return CashPosition(
        id=draw(st.uuids()).hex,
        entity_id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        account_name=draw(st.text(min_size=5, max_size=50)),
        account_type=draw(st.sampled_from(account_types)),
        currency=draw(st.sampled_from(["USD", "EUR", "GBP", "JPY"])),
        balance=Decimal(str(draw(st.floats(min_value=1000000, max_value=100000000, allow_nan=False, allow_infinity=False)))),
        interest_rate=Decimal(str(draw(st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)))),
        bank_name=draw(st.text(min_size=3, max_size=30)),
        liquidity_tier=draw(st.sampled_from(liquidity_tiers))
    )


@st.composite
def investment_strategy(draw):
    """Generate valid investments for property testing"""
    instrument_types = list(InstrumentType)
    credit_ratings = list(CreditRating)
    
    # Use fixed base date to avoid flaky tests
    base_date = datetime(2024, 1, 1)
    
    principal = Decimal(str(draw(st.floats(min_value=1000000, max_value=50000000, allow_nan=False, allow_infinity=False))))
    market_value = principal * Decimal(str(draw(st.floats(min_value=0.95, max_value=1.05, allow_nan=False, allow_infinity=False))))
    
    return Investment(
        id=draw(st.uuids()).hex,
        entity_id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        instrument_name=draw(st.text(min_size=5, max_size=50)),
        instrument_type=draw(st.sampled_from(instrument_types)),
        currency=draw(st.sampled_from(["USD", "EUR", "GBP", "JPY"])),
        principal_amount=principal,
        market_value=market_value,
        purchase_date=base_date,
        maturity_date=draw(st.one_of(
            st.none(),
            st.datetimes(min_value=base_date, max_value=base_date + timedelta(days=365*5))
        )),
        coupon_rate=Decimal(str(draw(st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)))),
        yield_to_maturity=Decimal(str(draw(st.floats(min_value=0.0, max_value=10.0, allow_nan=False, allow_infinity=False)))),
        credit_rating=draw(st.one_of(st.none(), st.sampled_from(credit_ratings))),
        duration=Decimal(str(draw(st.floats(min_value=0.1, max_value=10.0, allow_nan=False, allow_infinity=False))))
    )


@st.composite
def fx_exposure_strategy(draw):
    """Generate valid FX exposures for property testing"""
    # Use fixed base date to avoid flaky tests
    base_date = datetime(2024, 1, 1)
    
    return FXExposure(
        id=draw(st.uuids()).hex,
        entity_id=draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        base_currency="USD",  # Fixed base currency for simplicity
        exposure_currency=draw(st.sampled_from(["EUR", "GBP", "JPY", "CAD"])),
        notional_amount=Decimal(str(draw(st.floats(min_value=5000000, max_value=50000000, allow_nan=False, allow_infinity=False)))),
        spot_rate=Decimal(str(draw(st.floats(min_value=0.5, max_value=2.0, allow_nan=False, allow_infinity=False)))),
        forward_rate=Decimal(str(draw(st.floats(min_value=0.5, max_value=2.0, allow_nan=False, allow_infinity=False)))),
        hedge_ratio=Decimal(str(draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)))),
        maturity_date=base_date + timedelta(days=draw(st.integers(min_value=30, max_value=365))),
        hedge_instrument=draw(st.sampled_from(["Forward Contract", "Currency Option", "Cross-Currency Swap"]))
    )


class TestRiskCalculationProperties:
    """Property-based tests for risk calculation algorithms"""
    
    def get_risk_engine(self):
        """Create risk calculation engine for testing"""
        return RiskCalculationTestEngine()
    
    @given(
        cash_positions=st.lists(cash_position_strategy(), min_size=1, max_size=5),
        investments=st.lists(investment_strategy(), min_size=1, max_size=5),
        fx_exposures=st.lists(fx_exposure_strategy(), min_size=1, max_size=3),
        confidence_level=st.floats(min_value=0.90, max_value=0.99)
    )
    @settings(max_examples=30, deadline=20000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_6_risk_threshold_response(self, cash_positions, investments, fx_exposures, confidence_level):
        """
        Feature: treasuryiq-corporate-ai, Property 6: Risk Threshold Response
        
        For any portfolio exceeding risk thresholds, the Risk_System should 
        generate appropriate alerts with accurate breach calculations.
        
        Validates: Requirements 2.1
        """
        assume(all(pos.balance > 0 for pos in cash_positions))
        assume(all(inv.market_value > 0 for inv in investments))
        assume(all(fx.notional_amount > 0 for fx in fx_exposures))
        
        risk_engine = self.get_risk_engine()
        
        async def run_test():
            # Check risk thresholds
            alerts = await risk_engine.check_risk_thresholds(
                cash_positions, investments, fx_exposures
            )
            
            # Property 6.1: All alerts should have required fields
            for alert in alerts:
                assert "type" in alert
                assert "severity" in alert
                assert "current_value" in alert
                assert "threshold_value" in alert
                assert "breach_percentage" in alert
                assert "description" in alert
                
                # Property 6.2: Breach percentage should be positive
                assert alert["breach_percentage"] > 0
                
                # Property 6.3: Current value should exceed threshold for VaR breaches
                if alert["type"] == "var_breach":
                    assert alert["current_value"] > alert["threshold_value"]
                elif alert["type"] == "hedge_ratio_low":
                    # For hedge ratio, current value should be below threshold
                    assert alert["current_value"] < alert["threshold_value"]
                
                # Property 6.4: Severity should be valid
                assert alert["severity"] in ["low", "medium", "high", "critical"]
        
        asyncio.run(run_test())
    
    @given(
        cash_positions=st.lists(cash_position_strategy(), min_size=1, max_size=4),
        investments=st.lists(investment_strategy(), min_size=1, max_size=4),
        fx_exposures=st.lists(fx_exposure_strategy(), min_size=1, max_size=3),
        volatility_multiplier=st.floats(min_value=1.0, max_value=3.0)
    )
    @settings(max_examples=30, deadline=20000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_7_volatility_impact_assessment(self, cash_positions, investments, fx_exposures, volatility_multiplier):
        """
        Feature: treasuryiq-corporate-ai, Property 7: Volatility Impact Assessment
        
        For any increase in market volatility, the Risk_System should 
        proportionally increase VaR calculations and risk assessments.
        
        Validates: Requirements 2.2
        """
        assume(all(pos.balance > 0 for pos in cash_positions))
        assume(all(inv.market_value > 0 for inv in investments))
        assume(all(fx.notional_amount > 0 for fx in fx_exposures))
        
        risk_engine = self.get_risk_engine()
        
        async def run_test():
            # Calculate baseline VaR
            baseline_var = await risk_engine.calculate_portfolio_var(
                cash_positions, investments, fx_exposures, confidence_level=0.95
            )
            
            # Simulate higher volatility by increasing risk weights
            # This is a simplified approach for testing
            original_fx_vols = risk_engine._fx_volatilities.copy()
            
            # Increase FX volatilities
            for pair in risk_engine._fx_volatilities:
                risk_engine._fx_volatilities[pair] *= volatility_multiplier
            
            # Calculate VaR with higher volatility
            high_vol_var = await risk_engine.calculate_portfolio_var(
                cash_positions, investments, fx_exposures, confidence_level=0.95
            )
            
            # Restore original volatilities
            risk_engine._fx_volatilities = original_fx_vols
            
            # Property 7.1: Higher volatility should increase VaR
            assert high_vol_var.portfolio_var_1d >= baseline_var.portfolio_var_1d
            
            # Property 7.2: VaR should scale reasonably with volatility
            if baseline_var.portfolio_var_1d > 0:
                var_ratio = float(high_vol_var.portfolio_var_1d) / float(baseline_var.portfolio_var_1d)
                # VaR should increase but not unreasonably (within 5x)
                assert 1.0 <= var_ratio <= 5.0
            
            # Property 7.3: Expected shortfall should also increase
            assert high_vol_var.expected_shortfall >= baseline_var.expected_shortfall
            
            # Property 7.4: Stress test results should be consistent
            assert len(high_vol_var.stress_test_results) == len(baseline_var.stress_test_results)
            for scenario in baseline_var.stress_test_results:
                assert scenario in high_vol_var.stress_test_results
        
        asyncio.run(run_test())
    
    @given(
        investments=st.lists(investment_strategy(), min_size=2, max_size=6)
    )
    @settings(max_examples=30, deadline=15000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_8_credit_risk_monitoring(self, investments):
        """
        Feature: treasuryiq-corporate-ai, Property 8: Credit Risk Monitoring
        
        For any investment portfolio, the Risk_System should accurately 
        assess credit risk based on ratings and concentration.
        
        Validates: Requirements 2.3
        """
        assume(all(inv.market_value > 0 for inv in investments))
        
        risk_engine = self.get_risk_engine()
        
        async def run_test():
            # Assess credit risk
            credit_risk = await risk_engine.assess_credit_risk(investments)
            
            # Property 8.1: Credit risk score should be valid
            assert isinstance(credit_risk.overall_score, int)
            assert 1 <= credit_risk.overall_score <= 1000
            
            # Property 8.2: Probability of default should be reasonable
            assert 0.0 <= credit_risk.probability_of_default <= 1.0
            
            # Property 8.3: Expected loss should be non-negative
            assert credit_risk.expected_loss >= 0
            
            # Property 8.4: Risk grade should be valid
            valid_grades = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC", "CC", "C", "D"]
            assert credit_risk.risk_grade in valid_grades
            
            # Property 8.5: Higher credit scores should have lower default probability
            if credit_risk.overall_score >= 800:
                assert credit_risk.probability_of_default <= 0.05  # 5% max for high grades
            elif credit_risk.overall_score <= 400:
                assert credit_risk.probability_of_default >= 0.10  # 10% min for low grades
            
            # Property 8.6: Key factors should be structured properly
            for factor in credit_risk.key_factors:
                assert "factor" in factor
                assert "description" in factor
                assert "impact" in factor
                assert factor["impact"] in ["low", "medium", "high"]
        
        asyncio.run(run_test())
    
    @given(
        cash_positions=st.lists(cash_position_strategy(), min_size=1, max_size=4),
        investments=st.lists(investment_strategy(), min_size=1, max_size=4),
        fx_exposures=st.lists(fx_exposure_strategy(), min_size=0, max_size=3),
        confidence_level=st.floats(min_value=0.90, max_value=0.99)
    )
    @settings(max_examples=30, deadline=20000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_9_continuous_var_monitoring(self, cash_positions, investments, fx_exposures, confidence_level):
        """
        Feature: treasuryiq-corporate-ai, Property 9: Continuous VaR Monitoring
        
        For any portfolio composition, the Risk_System should calculate 
        consistent and mathematically sound VaR metrics.
        
        Validates: Requirements 2.4
        """
        assume(all(pos.balance > 0 for pos in cash_positions))
        assume(all(inv.market_value > 0 for inv in investments))
        assume(all(fx.notional_amount > 0 for fx in fx_exposures))
        
        risk_engine = self.get_risk_engine()
        
        async def run_test():
            # Calculate VaR
            var_result = await risk_engine.calculate_portfolio_var(
                cash_positions, investments, fx_exposures, confidence_level
            )
            
            # Property 9.1: VaR result should be valid
            assert isinstance(var_result, VaRResult)
            assert var_result.portfolio_var_1d >= 0
            assert var_result.portfolio_var_10d >= 0
            assert var_result.expected_shortfall >= 0
            
            # Property 9.2: 10-day VaR should be >= 1-day VaR
            assert var_result.portfolio_var_10d >= var_result.portfolio_var_1d
            
            # Property 9.3: Expected shortfall should be >= VaR
            assert var_result.expected_shortfall >= var_result.portfolio_var_1d
            
            # Property 9.4: Confidence level should match input
            assert abs(var_result.confidence_level - confidence_level) < 0.001
            
            # Property 9.5: Component VaRs should sum reasonably to total
            component_sum = sum(float(var) for var in var_result.component_vars.values())
            total_var = float(var_result.portfolio_var_1d)
            
            if total_var > 0:
                # Due to correlation effects, component sum may not equal total exactly
                # but should be in reasonable range (allow for diversification benefits)
                ratio = component_sum / total_var
                assert 0.1 <= ratio <= 10.0  # Allow for significant correlation effects
            
            # Property 9.6: Stress test results should be present
            assert len(var_result.stress_test_results) > 0
            for scenario, loss in var_result.stress_test_results.items():
                assert isinstance(scenario, str)
                assert loss >= 0
        
        asyncio.run(run_test())


if __name__ == "__main__":
    # Run property tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])