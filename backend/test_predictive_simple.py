"""
Simple test for predictive analytics service
"""

import asyncio
from app.services.predictive_analytics import PredictiveAnalyticsService
from app.services.market_data import MarketDataService


async def test_predictive_analytics():
    """Test predictive analytics service functionality"""
    
    print("🧪 Testing Predictive Analytics Service")
    print("=" * 50)
    
    # Initialize services
    market_data_service = MarketDataService()
    predictive_service = PredictiveAnalyticsService(market_data_service)
    
    print("✅ Services initialized successfully")
    
    # Test 1: Cash Flow Forecasting
    print("\n📈 Testing Cash Flow Forecasting")
    try:
        forecast = await predictive_service.forecast_cash_flows(
            entity_id="demo_entity",
            forecast_horizon_days=30,
            confidence_level=0.95
        )
        
        print(f"✅ Generated {len(forecast.daily_forecasts)} daily forecasts")
        print(f"✅ Forecast accuracy: {forecast.forecast_accuracy:.1%}")
        print(f"✅ Key assumptions: {len(forecast.key_assumptions)} items")
        
        # Show sample forecast
        sample_day = forecast.daily_forecasts[0]
        print(f"✅ Sample forecast: ${sample_day['predicted_flow']:,.0f} on {sample_day['date'][:10]}")
        
    except Exception as e:
        print(f"❌ Cash flow forecasting failed: {e}")
        return False
    
    # Test 2: Market Volatility Prediction
    print("\n📊 Testing Market Volatility Prediction")
    try:
        volatility_forecast = await predictive_service.predict_market_volatility(
            asset_class="fixed_income",
            forecast_horizon_days=30
        )
        
        print(f"✅ Predicted volatility: {volatility_forecast.predicted_volatility:.1%}")
        print(f"✅ Volatility regime: {volatility_forecast.volatility_regime}")
        print(f"✅ Key drivers: {len(volatility_forecast.key_drivers)} identified")
        print(f"✅ Model accuracy: {volatility_forecast.model_accuracy:.1%}")
        
    except Exception as e:
        print(f"❌ Volatility prediction failed: {e}")
        return False
    
    # Test 3: Default Probability Calculation
    print("\n🏦 Testing Default Probability Calculation")
    try:
        financial_data = {
            "revenue": 50000000,
            "total_debt": 15000000,
            "current_assets": 20000000,
            "current_liabilities": 8000000,
            "ebitda": 8000000,
            "interest_expense": 500000,
            "years_in_business": 12,
            "industry_risk_score": 4
        }
        
        default_prob = await predictive_service.calculate_default_probability(
            supplier_id="supplier_123",
            financial_data=financial_data
        )
        
        print(f"✅ 1-year default probability: {default_prob.probability_1y:.2%}")
        print(f"✅ Risk grade: {default_prob.risk_grade}")
        print(f"✅ Key risk factors: {len(default_prob.key_risk_factors)} identified")
        print(f"✅ Model confidence: {default_prob.model_confidence:.1%}")
        
    except Exception as e:
        print(f"❌ Default probability calculation failed: {e}")
        return False
    
    # Test 4: Scenario Analysis
    print("\n🎯 Testing Scenario Analysis")
    try:
        scenarios = [
            {
                "name": "Economic Recession",
                "type": "recession",
                "probability": 0.15,
                "duration_months": 18
            },
            {
                "name": "Market Crisis",
                "type": "crisis",
                "probability": 0.05,
                "duration_months": 6
            }
        ]
        
        scenario_analysis = await predictive_service.generate_scenario_analysis(
            entity_id="demo_entity",
            scenarios=scenarios
        )
        
        print(f"✅ Analyzed {len(scenario_analysis['scenarios'])} scenarios")
        print(f"✅ Base case included with {len(scenario_analysis['base_case'].daily_forecasts)} forecasts")
        
        for scenario_name, results in scenario_analysis['scenarios'].items():
            print(f"✅ {scenario_name}: {results['cash_flow_impact']:+.1%} cash flow impact")
        
    except Exception as e:
        print(f"❌ Scenario analysis failed: {e}")
        return False
    
    # Test 5: Model Performance
    print("\n⚙️ Testing Model Performance Tracking")
    try:
        performance = predictive_service.model_performance
        
        for model_name, metrics in performance.items():
            print(f"✅ {model_name.title()} model accuracy: {metrics['accuracy']:.1%}")
        
    except Exception as e:
        print(f"❌ Model performance check failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All Predictive Analytics tests passed!")
    return True


if __name__ == "__main__":
    result = asyncio.run(test_predictive_analytics())
    exit(0 if result else 1)