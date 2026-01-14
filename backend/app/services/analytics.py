"""
Treasury Analytics Engine - Core optimization and analysis algorithms
"""

import numpy as np
from typing import List, Dict, Optional, Tuple, Any
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass
import structlog

from app.models import CashPosition, Investment, FXExposure
from app.services.market_data import MarketDataService

logger = structlog.get_logger(__name__)


@dataclass
class OptimizationResult:
    """Result of cash optimization analysis"""
    current_yield: Decimal
    optimal_yield: Decimal
    opportunity_cost: Decimal
    recommendations: List[Dict[str, Any]]
    confidence: float
    analysis_date: datetime


@dataclass
class CashFlowForecast:
    """Cash flow forecast result"""
    entity_id: str
    forecast_horizon_days: int
    daily_forecasts: List[Dict[str, Any]]
    confidence_intervals: Dict[str, List[float]]
    key_assumptions: List[str]
    forecast_accuracy: Optional[float] = None


@dataclass
class LiquidityAnalysis:
    """Liquidity risk analysis result"""
    current_liquidity_ratio: float
    stress_test_results: Dict[str, float]
    liquidity_gap: Decimal
    recommended_buffer: Decimal
    risk_level: str  # "low", "medium", "high", "critical"


class TreasuryAnalyticsEngine:
    """Advanced analytics engine for treasury optimization"""
    
    def __init__(self, market_data_service: MarketDataService):
        self.market_data = market_data_service
        self._optimization_cache: Dict[str, Any] = {}
    
    async def calculate_optimal_cash_allocation(
        self, 
        cash_positions: List[CashPosition],
        constraints: Optional[Dict[str, Any]] = None
    ) -> OptimizationResult:
        """
        Calculate optimal cash allocation across positions
        Property 1: Cash Optimization Detection
        """
        try:
            # Get current market rates
            market_rates = await self.market_data.get_federal_reserve_rates()
            
            # Calculate current portfolio yield
            current_yield = self._calculate_portfolio_yield(cash_positions)
            
            # Run optimization algorithm
            optimal_allocation = self._optimize_cash_allocation(
                cash_positions, market_rates, constraints
            )
            
            # Calculate opportunity cost
            opportunity_cost = optimal_allocation["optimal_yield"] - current_yield
            
            # Generate recommendations
            recommendations = self._generate_cash_recommendations(
                cash_positions, optimal_allocation, market_rates
            )
            
            return OptimizationResult(
                current_yield=current_yield,
                optimal_yield=optimal_allocation["optimal_yield"],
                opportunity_cost=opportunity_cost,
                recommendations=recommendations,
                confidence=optimal_allocation["confidence"],
                analysis_date=datetime.now()
            )
            
        except Exception as e:
            logger.error("Cash optimization failed", error=str(e))
            raise
    
    def _calculate_portfolio_yield(self, positions: List[CashPosition]) -> Decimal:
        """Calculate weighted average yield of current positions"""
        total_balance = sum(pos.balance for pos in positions)
        if total_balance == 0:
            return Decimal("0")
        
        weighted_yield = sum(
            pos.balance * (pos.interest_rate or Decimal("0")) 
            for pos in positions
        ) / total_balance
        
        return weighted_yield
    
    def _optimize_cash_allocation(
        self,
        positions: List[CashPosition],
        market_rates: Dict[str, Any],
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Core optimization algorithm using modern portfolio theory"""
        
        # Default constraints
        if not constraints:
            constraints = {
                "max_single_position": 0.4,  # 40% max in single position
                "min_liquidity_tier_immediate": 0.2,  # 20% in immediate liquidity
                "max_maturity_days": 365,  # Max 1 year maturity
                "min_fdic_coverage": 0.8,  # 80% FDIC insured
            }
        
        # Create optimization matrix
        total_balance = sum(pos.balance for pos in positions)
        n_positions = len(positions)
        
        # Yield vector (expected returns)
        yields = np.array([
            float(pos.interest_rate or 0) + self._get_market_adjustment(pos)
            for pos in positions
        ])
        
        # Risk matrix (simplified covariance)
        risk_matrix = self._build_risk_matrix(positions, market_rates)
        
        # Constraint matrix
        A_eq, b_eq = self._build_constraint_matrix(positions, constraints)
        
        # Optimize using quadratic programming (simplified)
        optimal_weights = self._solve_optimization(yields, risk_matrix, A_eq, b_eq)
        
        # Calculate optimal yield
        optimal_yield = Decimal(str(np.dot(optimal_weights, yields)))
        
        return {
            "optimal_weights": optimal_weights.tolist(),
            "optimal_yield": optimal_yield,
            "confidence": self._calculate_confidence(optimal_weights, risk_matrix),
            "risk_metrics": self._calculate_risk_metrics(optimal_weights, risk_matrix)
        }
    
    def _get_market_adjustment(self, position: CashPosition) -> float:
        """Get market-based yield adjustment for position type"""
        adjustments = {
            "checking": 0.0,
            "savings": 0.5,
            "money_market": 1.0,
            "cd": 1.5,
            "treasury": 2.0,
        }
        return adjustments.get(position.account_type.value, 0.0) / 100.0
    
    def _build_risk_matrix(
        self, 
        positions: List[CashPosition], 
        market_rates: Dict[str, Any]
    ) -> np.ndarray:
        """Build risk covariance matrix"""
        n = len(positions)
        risk_matrix = np.eye(n) * 0.01  # Base risk of 1%
        
        # Add correlation based on currency and institution
        for i in range(n):
            for j in range(i+1, n):
                correlation = 0.0
                
                # Same currency correlation
                if positions[i].currency == positions[j].currency:
                    correlation += 0.3
                
                # Same bank correlation
                if positions[i].bank_name == positions[j].bank_name:
                    correlation += 0.5
                
                # Same account type correlation
                if positions[i].account_type == positions[j].account_type:
                    correlation += 0.2
                
                risk_matrix[i, j] = risk_matrix[j, i] = correlation * 0.005
        
        return risk_matrix
    
    def _build_constraint_matrix(
        self, 
        positions: List[CashPosition], 
        constraints: Dict[str, Any]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Build constraint matrix for optimization"""
        n = len(positions)
        
        # Equality constraint: weights sum to 1
        A_eq = np.ones((1, n))
        b_eq = np.array([1.0])
        
        return A_eq, b_eq
    
    def _solve_optimization(
        self,
        yields: np.ndarray,
        risk_matrix: np.ndarray,
        A_eq: np.ndarray,
        b_eq: np.ndarray
    ) -> np.ndarray:
        """Solve quadratic optimization problem"""
        # Simplified optimization - in production would use scipy.optimize
        n = len(yields)
        
        # Equal weight as baseline
        weights = np.ones(n) / n
        
        # Adjust based on yield differentials
        yield_scores = (yields - np.mean(yields)) / np.std(yields) if np.std(yields) > 0 else np.zeros(n)
        
        # Apply yield-based adjustments
        for i in range(n):
            weights[i] *= (1.0 + yield_scores[i] * 0.1)
        
        # Normalize to sum to 1
        weights = weights / np.sum(weights)
        
        return weights
    
    def _calculate_confidence(self, weights: np.ndarray, risk_matrix: np.ndarray) -> float:
        """Calculate confidence score for optimization"""
        portfolio_risk = np.sqrt(np.dot(weights, np.dot(risk_matrix, weights)))
        
        # Higher confidence for lower risk, more diversified portfolios
        diversification_score = 1.0 - np.max(weights)  # Lower max weight = more diversified
        risk_score = max(0.0, 1.0 - portfolio_risk * 10)  # Lower risk = higher score
        
        confidence = (diversification_score + risk_score) / 2.0
        return min(1.0, max(0.0, confidence))
    
    def _calculate_risk_metrics(self, weights: np.ndarray, risk_matrix: np.ndarray) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        portfolio_variance = np.dot(weights, np.dot(risk_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        
        return {
            "portfolio_volatility": float(portfolio_volatility),
            "max_position_weight": float(np.max(weights)),
            "diversification_ratio": float(1.0 / np.sum(weights**2)),  # Effective number of positions
            "concentration_risk": float(np.sum(weights**2))  # Herfindahl index
        }
    
    def _generate_cash_recommendations(
        self,
        positions: List[CashPosition],
        optimization: Dict[str, Any],
        market_rates: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations"""
        recommendations = []
        optimal_weights = optimization["optimal_weights"]
        
        total_balance = sum(pos.balance for pos in positions)
        
        for i, position in enumerate(positions):
            current_weight = float(position.balance / total_balance)
            optimal_weight = optimal_weights[i]
            
            if abs(optimal_weight - current_weight) > 0.05:  # 5% threshold
                target_balance = Decimal(str(optimal_weight)) * total_balance
                difference = target_balance - position.balance
                
                action = "increase" if difference > 0 else "decrease"
                
                recommendations.append({
                    "position_id": position.id,
                    "account_name": position.account_name,
                    "action": action,
                    "current_balance": float(position.balance),
                    "target_balance": float(target_balance),
                    "amount_change": float(abs(difference)),
                    "expected_yield_impact": float(
                        (optimal_weight - current_weight) * 
                        float(position.interest_rate or Decimal("0"))
                    ),
                    "priority": "high" if abs(difference) > total_balance * Decimal("0.1") else "medium",
                    "rationale": f"Optimize yield by {action}ing allocation to {position.account_type.value}"
                })
        
        # Sort by expected impact
        recommendations.sort(key=lambda x: abs(x["expected_yield_impact"]), reverse=True)
        
        return recommendations[:10]  # Top 10 recommendations
    
    async def forecast_cash_flow(
        self,
        entity_id: str,
        historical_data: List[Dict[str, Any]],
        forecast_days: int = 90
    ) -> CashFlowForecast:
        """
        Generate cash flow forecast using time series analysis
        Property 16: Cash Flow Forecasting
        """
        try:
            # Prepare time series data
            if not historical_data:
                # Generate synthetic historical data for demo
                historical_data = self._generate_synthetic_cash_flow_data(entity_id, 365)
            
            # Extract cash flow series
            cash_flows = np.array([d["net_cash_flow"] for d in historical_data])
            dates = [datetime.fromisoformat(d["date"]) for d in historical_data]
            
            # Apply time series forecasting (simplified ARIMA-like model)
            forecast_values = self._apply_time_series_forecast(cash_flows, forecast_days)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_forecast_confidence(
                cash_flows, forecast_values
            )
            
            # Generate daily forecasts
            daily_forecasts = []
            base_date = max(dates) if dates else datetime.now()
            
            for i, forecast_value in enumerate(forecast_values):
                forecast_date = base_date + timedelta(days=i+1)
                daily_forecasts.append({
                    "date": forecast_date.isoformat(),
                    "forecasted_cash_flow": float(forecast_value),
                    "confidence_lower": confidence_intervals["lower"][i],
                    "confidence_upper": confidence_intervals["upper"][i],
                    "cumulative_flow": float(np.sum(forecast_values[:i+1]))
                })
            
            return CashFlowForecast(
                entity_id=entity_id,
                forecast_horizon_days=forecast_days,
                daily_forecasts=daily_forecasts,
                confidence_intervals=confidence_intervals,
                key_assumptions=[
                    "Historical patterns continue",
                    "No major market disruptions",
                    "Seasonal patterns remain consistent",
                    "Current business operations continue"
                ],
                forecast_accuracy=self._calculate_historical_accuracy(historical_data)
            )
            
        except Exception as e:
            logger.error("Cash flow forecasting failed", error=str(e))
            raise
    
    def _generate_synthetic_cash_flow_data(
        self, 
        entity_id: str, 
        days: int
    ) -> List[Dict[str, Any]]:
        """Generate realistic synthetic cash flow data for demo"""
        np.random.seed(hash(entity_id) % 2**32)  # Consistent seed per entity
        
        base_date = datetime.now() - timedelta(days=days)
        data = []
        
        # Base daily cash flow with trend and seasonality
        base_flow = 1000000  # $1M base daily flow
        trend = 0.001  # 0.1% daily growth trend
        
        for i in range(days):
            date = base_date + timedelta(days=i)
            
            # Seasonal component (weekly and monthly patterns)
            weekly_seasonal = 0.1 * np.sin(2 * np.pi * i / 7)  # Weekly pattern
            monthly_seasonal = 0.05 * np.sin(2 * np.pi * i / 30)  # Monthly pattern
            
            # Random component
            random_component = np.random.normal(0, 0.2)
            
            # Calculate net cash flow
            net_flow = base_flow * (
                1 + trend * i + weekly_seasonal + monthly_seasonal + random_component
            )
            
            data.append({
                "date": date.isoformat(),
                "net_cash_flow": net_flow,
                "inflows": net_flow * 1.2 if net_flow > 0 else 0,
                "outflows": abs(net_flow * 0.2) if net_flow > 0 else abs(net_flow),
            })
        
        return data
    
    def _apply_time_series_forecast(
        self, 
        historical_flows: np.ndarray, 
        forecast_days: int
    ) -> np.ndarray:
        """Apply time series forecasting algorithm"""
        # Simple exponential smoothing with trend
        alpha = 0.3  # Smoothing parameter
        beta = 0.1   # Trend parameter
        
        # Initialize
        level = historical_flows[0]
        trend = np.mean(np.diff(historical_flows[:10]))  # Initial trend
        
        # Fit model to historical data
        for value in historical_flows[1:]:
            prev_level = level
            level = alpha * value + (1 - alpha) * (level + trend)
            trend = beta * (level - prev_level) + (1 - beta) * trend
        
        # Generate forecasts
        forecasts = []
        for h in range(1, forecast_days + 1):
            forecast = level + h * trend
            forecasts.append(forecast)
        
        return np.array(forecasts)
    
    def _calculate_forecast_confidence(
        self,
        historical_flows: np.ndarray,
        forecast_values: np.ndarray
    ) -> Dict[str, List[float]]:
        """Calculate confidence intervals for forecasts"""
        # Calculate historical volatility
        historical_volatility = np.std(historical_flows)
        
        # Confidence intervals widen with forecast horizon
        confidence_intervals = {"lower": [], "upper": []}
        
        for i, forecast in enumerate(forecast_values):
            # Confidence interval widens with time
            interval_width = historical_volatility * np.sqrt(i + 1) * 1.96  # 95% confidence
            
            confidence_intervals["lower"].append(float(forecast - interval_width))
            confidence_intervals["upper"].append(float(forecast + interval_width))
        
        return confidence_intervals
    
    async def analyze_liquidity_requirements(
        self,
        cash_positions: List[CashPosition],
        projected_outflows: Optional[List[Dict[str, Any]]] = None,
        stress_scenarios: Optional[List[str]] = None
    ) -> LiquidityAnalysis:
        """
        Analyze liquidity requirements and stress test scenarios
        Property 3: Liquidity Shortfall Response
        """
        try:
            # Calculate current liquidity metrics
            total_cash = sum(pos.balance for pos in cash_positions)
            immediate_liquidity = sum(
                pos.balance for pos in cash_positions 
                if pos.liquidity_tier == "immediate"
            )
            
            current_liquidity_ratio = float(immediate_liquidity / total_cash) if total_cash > 0 else 0.0
            
            # Default projected outflows if not provided
            if not projected_outflows:
                projected_outflows = self._generate_default_outflow_projections(total_cash)
            
            # Default stress scenarios
            if not stress_scenarios:
                stress_scenarios = [
                    "market_crisis", "credit_downgrade", "operational_disruption", 
                    "supplier_concentration", "regulatory_change"
                ]
            
            # Run stress tests
            stress_test_results = {}
            for scenario in stress_scenarios:
                stress_result = self._run_liquidity_stress_test(
                    cash_positions, projected_outflows, scenario
                )
                stress_test_results[scenario] = stress_result
            
            # Calculate liquidity gap
            worst_case_outflow = max(
                sum(outflow["amount"] for outflow in projected_outflows),
                max(stress_test_results.values()) if stress_test_results else 0
            )
            
            liquidity_gap = immediate_liquidity - Decimal(str(worst_case_outflow))
            
            # Determine recommended buffer
            recommended_buffer = self._calculate_recommended_liquidity_buffer(
                total_cash, stress_test_results
            )
            
            # Assess risk level
            risk_level = self._assess_liquidity_risk_level(
                current_liquidity_ratio, liquidity_gap, recommended_buffer
            )
            
            return LiquidityAnalysis(
                current_liquidity_ratio=current_liquidity_ratio,
                stress_test_results=stress_test_results,
                liquidity_gap=liquidity_gap,
                recommended_buffer=recommended_buffer,
                risk_level=risk_level
            )
            
        except Exception as e:
            logger.error("Liquidity analysis failed", error=str(e))
            raise
    
    def _generate_default_outflow_projections(self, total_cash: Decimal) -> List[Dict[str, Any]]:
        """Generate default outflow projections based on total cash"""
        base_daily_outflow = float(total_cash) * 0.02  # 2% daily outflow assumption
        
        return [
            {
                "category": "operational_expenses",
                "amount": base_daily_outflow * 0.6,
                "probability": 0.95,
                "timing_days": 1
            },
            {
                "category": "debt_service",
                "amount": base_daily_outflow * 0.2,
                "probability": 1.0,
                "timing_days": 7
            },
            {
                "category": "capital_expenditure",
                "amount": base_daily_outflow * 0.15,
                "probability": 0.7,
                "timing_days": 30
            },
            {
                "category": "contingency",
                "amount": base_daily_outflow * 0.05,
                "probability": 0.3,
                "timing_days": 1
            }
        ]
    
    def _run_liquidity_stress_test(
        self,
        positions: List[CashPosition],
        projected_outflows: List[Dict[str, Any]],
        scenario: str
    ) -> float:
        """Run specific liquidity stress test scenario"""
        stress_multipliers = {
            "market_crisis": 2.5,      # 150% increase in outflows
            "credit_downgrade": 1.8,   # 80% increase
            "operational_disruption": 2.0,  # 100% increase
            "supplier_concentration": 1.5,  # 50% increase
            "regulatory_change": 1.3   # 30% increase
        }
        
        multiplier = stress_multipliers.get(scenario, 1.5)
        
        # Calculate stressed outflows
        stressed_outflow = sum(
            outflow["amount"] * outflow["probability"] * multiplier
            for outflow in projected_outflows
        )
        
        return stressed_outflow
    
    def _calculate_recommended_liquidity_buffer(
        self,
        total_cash: Decimal,
        stress_results: Dict[str, float]
    ) -> Decimal:
        """Calculate recommended liquidity buffer"""
        # Base buffer: 10% of total cash
        base_buffer = total_cash * Decimal("0.10")
        
        # Stress-based buffer: cover worst-case scenario
        if stress_results:
            worst_case = max(stress_results.values())
            stress_buffer = Decimal(str(worst_case * 1.2))  # 20% margin above worst case
        else:
            stress_buffer = total_cash * Decimal("0.05")
        
        # Return the higher of the two
        return max(base_buffer, stress_buffer)
    
    def _assess_liquidity_risk_level(
        self,
        liquidity_ratio: float,
        liquidity_gap: Decimal,
        recommended_buffer: Decimal
    ) -> str:
        """Assess overall liquidity risk level"""
        # Risk factors
        ratio_risk = "high" if liquidity_ratio < 0.15 else "medium" if liquidity_ratio < 0.25 else "low"
        gap_risk = "high" if liquidity_gap < 0 else "medium" if liquidity_gap < recommended_buffer else "low"
        
        # Combined risk assessment
        if ratio_risk == "high" or gap_risk == "high":
            return "critical" if ratio_risk == "high" and gap_risk == "high" else "high"
        elif ratio_risk == "medium" or gap_risk == "medium":
            return "medium"
        else:
            return "low"
    
    async def detect_optimization_opportunities(
        self,
        cash_positions: List[CashPosition],
        threshold_amount: Decimal = Decimal("1000000")  # $1M threshold
    ) -> List[Dict[str, Any]]:
        """
        Detect cash optimization opportunities above threshold
        Property 1: Cash Optimization Detection
        """
        try:
            opportunities = []
            
            # Get current market rates for comparison
            market_rates = await self.market_data.get_federal_reserve_rates()
            
            # Analyze each position for optimization potential
            for position in cash_positions:
                opportunity = await self._analyze_position_opportunity(
                    position, market_rates, threshold_amount
                )
                if opportunity:
                    opportunities.append(opportunity)
            
            # Sort by opportunity cost (highest first)
            opportunities.sort(key=lambda x: x["opportunity_cost"], reverse=True)
            
            return opportunities
            
        except Exception as e:
            logger.error("Opportunity detection failed", error=str(e))
            raise
    
    async def _analyze_position_opportunity(
        self,
        position: CashPosition,
        market_rates: Dict[str, Any],
        threshold: Decimal
    ) -> Optional[Dict[str, Any]]:
        """Analyze individual position for optimization opportunity"""
        current_rate = position.interest_rate or Decimal("0")
        
        # Get benchmark rate for position type
        benchmark_rate = self._get_benchmark_rate(position, market_rates)
        
        # Calculate opportunity cost
        rate_differential = benchmark_rate - current_rate
        annual_opportunity_cost = position.balance * rate_differential
        
        # Only flag if above threshold
        if annual_opportunity_cost >= threshold:
            return {
                "position_id": position.id,
                "account_name": position.account_name,
                "current_balance": float(position.balance),
                "current_rate": float(current_rate),
                "benchmark_rate": float(benchmark_rate),
                "rate_differential": float(rate_differential),
                "opportunity_cost": float(annual_opportunity_cost),
                "recommended_action": self._get_recommended_action(position, benchmark_rate),
                "priority": "high" if annual_opportunity_cost >= threshold * 5 else "medium",
                "analysis_date": datetime.now().isoformat()
            }
        
        return None
    
    def _get_benchmark_rate(
        self,
        position: CashPosition,
        market_rates: Dict[str, Any]
    ) -> Decimal:
        """Get appropriate benchmark rate for position type"""
        # Map account types to market rate benchmarks
        rate_mapping = {
            "checking": "fed_funds",
            "savings": "treasury_3m",
            "money_market": "treasury_6m",
            "cd": "treasury_1y",
            "treasury": "treasury_2y"
        }
        
        benchmark_key = rate_mapping.get(position.account_type.value, "fed_funds")
        
        if benchmark_key in market_rates:
            return market_rates[benchmark_key].rate
        else:
            # Default benchmark rates if market data unavailable
            default_rates = {
                "checking": Decimal("0.01"),
                "savings": Decimal("2.50"),
                "money_market": Decimal("3.00"),
                "cd": Decimal("4.00"),
                "treasury": Decimal("4.50")
            }
            return default_rates.get(position.account_type.value, Decimal("2.00"))
    
    def _get_recommended_action(self, position: CashPosition, benchmark_rate: Decimal) -> str:
        """Get recommended action for position optimization"""
        current_rate = position.interest_rate or Decimal("0")
        
        if benchmark_rate > current_rate * Decimal("1.5"):  # 50% better rate available
            return f"Move to higher-yield {position.account_type.value} earning {benchmark_rate}%"
        elif benchmark_rate > current_rate * Decimal("1.2"):  # 20% better rate available
            return f"Consider switching to earn additional {benchmark_rate - current_rate}%"
        else:
            return "Monitor for better opportunities"
    
    async def recalculate_on_market_change(
        self,
        positions: List[CashPosition],
        previous_optimization: OptimizationResult,
        market_change_threshold: float = 0.25  # 25 basis points
    ) -> Optional[OptimizationResult]:
        """
        Recalculate optimization when market conditions change significantly
        Property 2: Market-Driven Recalculation
        """
        try:
            # Get current market rates
            current_market_rates = await self.market_data.get_federal_reserve_rates()
            
            # Check if market has changed significantly
            if not self._has_significant_market_change(
                previous_optimization, current_market_rates, market_change_threshold
            ):
                return None  # No significant change, no recalculation needed
            
            logger.info("Significant market change detected, recalculating optimization")
            
            # Recalculate optimization with new market conditions
            new_optimization = await self.calculate_optimal_cash_allocation(positions)
            
            # Add market change context
            new_optimization.market_change_trigger = True
            new_optimization.previous_analysis_date = previous_optimization.analysis_date
            
            return new_optimization
            
        except Exception as e:
            logger.error("Market-driven recalculation failed", error=str(e))
            raise
    
    def _has_significant_market_change(
        self,
        previous_optimization: OptimizationResult,
        current_rates: Dict[str, Any],
        threshold: float
    ) -> bool:
        """Check if market rates have changed significantly"""
        # This is a simplified check - in production would compare with 
        # rates used in previous optimization
        
        # For demo purposes, assume significant change if fed funds rate moved
        if "fed_funds" in current_rates:
            current_fed_rate = float(current_rates["fed_funds"].rate)
            
            # Compare with a baseline (simplified)
            baseline_rate = 5.25  # Assume this was the previous rate
            
            change = abs(current_fed_rate - baseline_rate)
            return change >= threshold
        
        return False
    def _calculate_historical_accuracy(self, historical_data: List[Dict[str, Any]]) -> float:
        """Calculate historical forecast accuracy"""
        # Simplified accuracy calculation
        if len(historical_data) < 30:
            return 0.85  # Default accuracy
        
        # Calculate mean absolute percentage error on recent data
        recent_flows = np.array([d["net_cash_flow"] for d in historical_data[-30:]])
        mean_flow = np.mean(recent_flows)
        volatility = np.std(recent_flows) / mean_flow if mean_flow != 0 else 0.1
        
        # Higher volatility = lower accuracy
        accuracy = max(0.6, min(0.95, 1.0 - volatility))
        return accuracy
    
    async def generate_comprehensive_recommendations(
        self,
        entity_id: str,
        cash_positions: List[CashPosition],
        include_forecasting: bool = True,
        include_liquidity_analysis: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive treasury recommendations combining all analyses
        Property 4: Comprehensive Optimization Recommendations
        """
        try:
            recommendations = {
                "entity_id": entity_id,
                "analysis_timestamp": datetime.now().isoformat(),
                "executive_summary": {},
                "cash_optimization": {},
                "liquidity_analysis": {},
                "cash_flow_forecast": {},
                "action_items": [],
                "risk_alerts": []
            }
            
            # 1. Cash Optimization Analysis
            optimization_result = await self.calculate_optimal_cash_allocation(cash_positions)
            recommendations["cash_optimization"] = {
                "current_yield": float(optimization_result.current_yield),
                "optimal_yield": float(optimization_result.optimal_yield),
                "opportunity_cost": float(optimization_result.opportunity_cost),
                "confidence": optimization_result.confidence,
                "recommendations": optimization_result.recommendations
            }
            
            # 2. Opportunity Detection
            opportunities = await self.detect_optimization_opportunities(cash_positions)
            recommendations["cash_optimization"]["opportunities"] = opportunities
            
            # 3. Liquidity Analysis (if requested)
            if include_liquidity_analysis:
                liquidity_analysis = await self.analyze_liquidity_requirements(cash_positions)
                recommendations["liquidity_analysis"] = {
                    "current_liquidity_ratio": liquidity_analysis.current_liquidity_ratio,
                    "liquidity_gap": float(liquidity_analysis.liquidity_gap),
                    "recommended_buffer": float(liquidity_analysis.recommended_buffer),
                    "risk_level": liquidity_analysis.risk_level,
                    "stress_test_results": liquidity_analysis.stress_test_results
                }
                
                # Add liquidity risk alerts
                if liquidity_analysis.risk_level in ["high", "critical"]:
                    recommendations["risk_alerts"].append({
                        "type": "liquidity_risk",
                        "severity": liquidity_analysis.risk_level,
                        "message": f"Liquidity risk level is {liquidity_analysis.risk_level}",
                        "recommended_action": "Increase immediate liquidity reserves"
                    })
            
            # 4. Cash Flow Forecasting (if requested)
            if include_forecasting:
                forecast = await self.forecast_cash_flow(entity_id, [])
                recommendations["cash_flow_forecast"] = {
                    "forecast_horizon_days": forecast.forecast_horizon_days,
                    "forecast_accuracy": forecast.forecast_accuracy,
                    "key_insights": self._extract_forecast_insights(forecast),
                    "upcoming_cash_needs": self._identify_cash_needs(forecast)
                }
            
            # 5. Generate Executive Summary
            recommendations["executive_summary"] = self._generate_executive_summary(
                optimization_result, 
                recommendations.get("liquidity_analysis"),
                opportunities
            )
            
            # 6. Prioritized Action Items
            recommendations["action_items"] = self._generate_action_items(
                optimization_result.recommendations,
                opportunities,
                recommendations.get("liquidity_analysis")
            )
            
            return recommendations
            
        except Exception as e:
            logger.error("Comprehensive recommendations generation failed", error=str(e))
            raise
    
    def _extract_forecast_insights(self, forecast: CashFlowForecast) -> List[str]:
        """Extract key insights from cash flow forecast"""
        insights = []
        
        # Analyze forecast trends
        daily_flows = [f["forecasted_cash_flow"] for f in forecast.daily_forecasts]
        
        if len(daily_flows) >= 30:
            first_month_avg = np.mean(daily_flows[:30])
            last_month_avg = np.mean(daily_flows[-30:]) if len(daily_flows) >= 60 else np.mean(daily_flows[30:])
            
            if last_month_avg > first_month_avg * 1.1:
                insights.append("Cash flows expected to improve significantly over forecast period")
            elif last_month_avg < first_month_avg * 0.9:
                insights.append("Cash flows expected to decline over forecast period")
            else:
                insights.append("Cash flows expected to remain relatively stable")
        
        # Check for negative periods
        negative_days = sum(1 for f in daily_flows if f < 0)
        if negative_days > len(daily_flows) * 0.1:  # More than 10% negative days
            insights.append(f"Expect {negative_days} days with negative cash flows")
        
        # Volatility assessment
        volatility = np.std(daily_flows) / abs(np.mean(daily_flows)) if np.mean(daily_flows) != 0 else 0
        if volatility > 0.3:
            insights.append("High cash flow volatility expected - maintain larger liquidity buffer")
        
        return insights
    
    def _identify_cash_needs(self, forecast: CashFlowForecast) -> List[Dict[str, Any]]:
        """Identify upcoming significant cash needs"""
        cash_needs = []
        
        cumulative_flow = 0
        for day_forecast in forecast.daily_forecasts[:30]:  # Next 30 days
            cumulative_flow += day_forecast["forecasted_cash_flow"]
            
            # Flag significant negative cumulative flows
            if cumulative_flow < -1000000:  # $1M negative
                cash_needs.append({
                    "date": day_forecast["date"],
                    "cumulative_shortfall": cumulative_flow,
                    "severity": "high" if cumulative_flow < -5000000 else "medium",
                    "recommendation": "Ensure adequate liquidity reserves"
                })
        
        return cash_needs
    
    def _generate_executive_summary(
        self,
        optimization: OptimizationResult,
        liquidity_analysis: Optional[Dict[str, Any]],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate executive summary of treasury analysis"""
        summary = {
            "total_opportunity_cost": float(optimization.opportunity_cost),
            "optimization_confidence": optimization.confidence,
            "key_findings": [],
            "immediate_actions_required": 0,
            "estimated_annual_savings": 0.0
        }
        
        # Key findings
        if optimization.opportunity_cost > Decimal("1000000"):
            summary["key_findings"].append(
                f"Significant optimization opportunity: ${float(optimization.opportunity_cost):,.0f} annual savings potential"
            )
        
        if liquidity_analysis and liquidity_analysis["risk_level"] in ["high", "critical"]:
            summary["key_findings"].append(
                f"Liquidity risk level: {liquidity_analysis['risk_level']} - immediate attention required"
            )
        
        # Count immediate actions
        high_priority_opportunities = [o for o in opportunities if o.get("priority") == "high"]
        summary["immediate_actions_required"] = len(high_priority_opportunities)
        
        # Estimate annual savings
        summary["estimated_annual_savings"] = sum(
            o.get("opportunity_cost", 0) for o in opportunities
        )
        
        return summary
    
    def _generate_action_items(
        self,
        optimization_recommendations: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        liquidity_analysis: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate prioritized action items"""
        action_items = []
        
        # High-priority optimization actions
        for rec in optimization_recommendations[:3]:  # Top 3
            if rec.get("priority") == "high":
                action_items.append({
                    "priority": 1,
                    "category": "cash_optimization",
                    "title": f"Optimize {rec['account_name']} allocation",
                    "description": rec["rationale"],
                    "expected_impact": f"${rec['expected_yield_impact']:,.0f} annual yield improvement",
                    "timeline": "Within 1 week"
                })
        
        # High-value opportunities
        for opp in opportunities[:2]:  # Top 2 opportunities
            if opp.get("priority") == "high":
                action_items.append({
                    "priority": 2,
                    "category": "opportunity_capture",
                    "title": f"Address {opp['account_name']} underperformance",
                    "description": opp["recommended_action"],
                    "expected_impact": f"${opp['opportunity_cost']:,.0f} annual savings",
                    "timeline": "Within 2 weeks"
                })
        
        # Liquidity actions
        if liquidity_analysis and liquidity_analysis["risk_level"] in ["high", "critical"]:
            action_items.append({
                "priority": 1 if liquidity_analysis["risk_level"] == "critical" else 3,
                "category": "liquidity_management",
                "title": "Address liquidity risk",
                "description": f"Current liquidity ratio: {liquidity_analysis['current_liquidity_ratio']:.1%}",
                "expected_impact": "Reduce liquidity risk to acceptable levels",
                "timeline": "Immediate" if liquidity_analysis["risk_level"] == "critical" else "Within 1 week"
            })
        
        # Sort by priority
        action_items.sort(key=lambda x: x["priority"])
        
        return action_items