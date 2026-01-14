"""
Risk Calculation Service - VaR, Credit Risk, and Market Risk Analysis
"""

import numpy as np
from typing import List, Dict, Optional, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass
import structlog

from app.models import CashPosition, Investment, FXExposure, RiskMetrics
from app.services.market_data import MarketDataService

logger = structlog.get_logger(__name__)


@dataclass
class VaRResult:
    """Value at Risk calculation result"""
    portfolio_var_1d: Decimal
    portfolio_var_10d: Decimal
    expected_shortfall: Decimal
    confidence_level: float
    calculation_method: str
    component_vars: Dict[str, Decimal]
    stress_test_results: Dict[str, Decimal]


@dataclass
class CurrencyRiskAnalysis:
    """Currency risk analysis result"""
    total_exposure: Decimal
    hedged_exposure: Decimal
    unhedged_exposure: Decimal
    hedge_ratio: float
    currency_vars: Dict[str, Decimal]
    correlation_matrix: Dict[str, Dict[str, float]]
    hedging_recommendations: List[Dict[str, Any]]


@dataclass
class CreditRiskScore:
    """Credit risk assessment result"""
    overall_score: int  # 1-1000 scale
    probability_of_default: float
    expected_loss: Decimal
    risk_grade: str  # AAA, AA, A, BBB, BB, B, CCC, CC, C, D
    key_factors: List[Dict[str, Any]]
    recommendations: List[str]


class RiskCalculationService:
    """Advanced risk calculation and monitoring service"""
    
    def __init__(self, market_data_service: MarketDataService):
        self.market_data = market_data_service
        self._risk_cache: Dict[str, Any] = {}
    
    async def calculate_portfolio_var(
        self,
        cash_positions: List[CashPosition],
        investments: List[Investment],
        fx_exposures: List[FXExposure],
        confidence_level: float = 0.95,
        time_horizon: int = 1
    ) -> VaRResult:
        """
        Calculate Value at Risk using Monte Carlo simulation
        Property 9: Continuous VaR Monitoring
        """
        try:
            # Get market data for risk calculations
            market_data = await self.market_data.get_market_summary()
            
            # Build portfolio components
            portfolio_components = self._build_portfolio_components(
                cash_positions, investments, fx_exposures
            )
            
            # Run Monte Carlo simulation
            var_results = self._monte_carlo_var_simulation(
                portfolio_components, market_data, confidence_level, time_horizon
            )
            
            # Calculate component VaRs
            component_vars = self._calculate_component_vars(
                portfolio_components, var_results
            )
            
            # Run stress tests
            stress_results = self._run_stress_tests(
                portfolio_components, market_data
            )
            
            return VaRResult(
                portfolio_var_1d=Decimal(str(var_results["var_1d"])),
                portfolio_var_10d=Decimal(str(var_results["var_10d"])),
                expected_shortfall=Decimal(str(var_results["expected_shortfall"])),
                confidence_level=confidence_level,
                calculation_method="Monte Carlo",
                component_vars=component_vars,
                stress_test_results=stress_results
            )
            
        except Exception as e:
            logger.error("VaR calculation failed", error=str(e))
            raise
    
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
                "interest_rate": pos.interest_rate or Decimal("0"),
                "liquidity_tier": pos.liquidity_tier.value,
                "risk_weight": self._get_cash_risk_weight(pos)
            })
            components["total_value"] += pos.balance
        
        # Process investments
        for inv in investments:
            market_value = inv.market_value or inv.principal_amount
            components["investments"].append({
                "id": inv.id,
                "value": market_value,
                "currency": inv.currency,
                "instrument_type": inv.instrument_type.value,
                "credit_rating": inv.credit_rating.value if inv.credit_rating else "NR",
                "duration": inv.duration or Decimal("0"),
                "yield_to_maturity": inv.yield_to_maturity or Decimal("0"),
                "risk_weight": self._get_investment_risk_weight(inv)
            })
            components["total_value"] += market_value
        
        # Process FX exposures
        for fx in fx_exposures:
            components["fx"].append({
                "id": fx.id,
                "notional": fx.notional_amount,
                "base_currency": fx.base_currency,
                "exposure_currency": fx.exposure_currency,
                "hedge_ratio": fx.hedge_ratio,
                "spot_rate": fx.spot_rate,
                "risk_weight": self._get_fx_risk_weight(fx)
            })
        
        return components
    
    def _get_cash_risk_weight(self, position: CashPosition) -> float:
        """Get risk weight for cash position"""
        weights = {
            "checking": 0.01,
            "savings": 0.01,
            "money_market": 0.02,
            "cd": 0.03,
            "treasury": 0.005
        }
        return weights.get(position.account_type.value, 0.02)
    
    def _get_investment_risk_weight(self, investment: Investment) -> float:
        """Get risk weight for investment"""
        # Base weight by instrument type
        type_weights = {
            "treasury_bill": 0.005,
            "treasury_note": 0.01,
            "treasury_bond": 0.02,
            "corporate_bond": 0.05,
            "money_market_fund": 0.01,
            "cd": 0.02,
            "commercial_paper": 0.03
        }
        
        base_weight = type_weights.get(investment.instrument_type.value, 0.05)
        
        # Adjust for credit rating
        if investment.credit_rating:
            rating_adjustments = {
                "AAA": 0.8, "AA+": 0.9, "AA": 1.0, "AA-": 1.1,
                "A+": 1.2, "A": 1.3, "A-": 1.4,
                "BBB+": 1.6, "BBB": 1.8, "BBB-": 2.0,
                "BB+": 2.5, "BB": 3.0, "BB-": 3.5,
                "B+": 4.0, "B": 5.0, "B-": 6.0,
                "CCC": 8.0, "CC": 10.0, "C": 12.0, "D": 15.0
            }
            adjustment = rating_adjustments.get(investment.credit_rating.value, 2.0)
            base_weight *= adjustment
        
        return base_weight
    
    def _get_fx_risk_weight(self, exposure: FXExposure) -> float:
        """Get risk weight for FX exposure"""
        # Base FX volatility by currency pair
        volatilities = {
            ("USD", "EUR"): 0.12,
            ("USD", "GBP"): 0.14,
            ("USD", "JPY"): 0.16,
            ("USD", "CAD"): 0.10,
            ("USD", "AUD"): 0.18,
            ("USD", "CHF"): 0.11,
            ("USD", "SGD"): 0.08
        }
        
        pair = (exposure.base_currency, exposure.exposure_currency)
        base_vol = volatilities.get(pair, 0.15)
        
        # Adjust for hedge ratio (lower risk if hedged)
        hedge_adjustment = 1.0 - float(exposure.hedge_ratio) * 0.8
        
        return base_vol * hedge_adjustment
    
    def _monte_carlo_var_simulation(
        self,
        portfolio_components: Dict[str, Any],
        market_data: Dict[str, Any],
        confidence_level: float,
        time_horizon: int,
        num_simulations: int = 10000
    ) -> Dict[str, float]:
        """Run Monte Carlo simulation for VaR calculation"""
        
        # Initialize random number generator
        np.random.seed(42)  # For reproducible results
        
        # Extract portfolio values
        portfolio_values = []
        risk_weights = []
        
        for component_type in ["cash", "investments", "fx"]:
            for component in portfolio_components[component_type]:
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
        
        # Generate correlated random shocks
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
        
        # Add some realistic correlations
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
        portfolio_components: Dict[str, Any],
        market_data: Dict[str, Any]
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
                # Interest rate impact on cash is minimal
                loss = float(cash_comp["value"]) * scenario["rate_change"] * 0.1
                scenario_loss += loss
            
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
        """
        Assess currency risk across all FX exposures
        Property 6: Risk Threshold Response
        """
        try:
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
            currency_vars = await self._calculate_currency_vars(fx_exposures)
            
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
            
        except Exception as e:
            logger.error("Currency risk assessment failed", error=str(e))
            raise
    
    async def _calculate_currency_vars(
        self,
        fx_exposures: List[FXExposure]
    ) -> Dict[str, Decimal]:
        """Calculate VaR for each currency exposure"""
        currency_vars = {}
        
        # Get current exchange rates for volatility calculation
        exchange_rates = await self.market_data.get_exchange_rates()
        
        for fx in fx_exposures:
            currency_pair = f"{fx.base_currency}/{fx.exposure_currency}"
            
            # Get historical volatility (simplified)
            volatility = self._get_fx_volatility(fx.base_currency, fx.exposure_currency)
            
            # Calculate 1-day VaR at 95% confidence
            var_1d = float(fx.notional_amount) * volatility * 1.645  # 95% confidence
            
            # Adjust for hedge ratio
            unhedged_var = var_1d * (1 - float(fx.hedge_ratio))
            
            currency_vars[currency_pair] = Decimal(str(unhedged_var))
        
        return currency_vars
    
    def _get_fx_volatility(self, base_currency: str, target_currency: str) -> float:
        """Get FX volatility for currency pair"""
        # Historical volatilities (annualized)
        volatilities = {
            ("USD", "EUR"): 0.12,
            ("USD", "GBP"): 0.14,
            ("USD", "JPY"): 0.16,
            ("USD", "CAD"): 0.10,
            ("USD", "AUD"): 0.18,
            ("USD", "CHF"): 0.11,
            ("USD", "SGD"): 0.08
        }
        
        pair = (base_currency, target_currency)
        annual_vol = volatilities.get(pair, 0.15)
        
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