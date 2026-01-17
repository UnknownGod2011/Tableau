"""
Test FastAPI application startup without database connections
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_app_creation():
    """Test that FastAPI app can be created"""
    try:
        # Mock the database and redis connections to avoid connection errors
        import unittest.mock
        
        with unittest.mock.patch('app.core.database.engine'), \
             unittest.mock.patch('app.core.redis.redis_client'):
            
            from app.main import app
            
            # Test that app is created
            assert app is not None, "FastAPI app should be created"
            assert app.title == "TreasuryIQ API", "App should have correct title"
            
            # Test that routes are included
            routes = [route.path for route in app.routes]
            expected_routes = ["/health", "/", "/api/v1/entities/", "/api/v1/cash/"]
            
            for expected_route in expected_routes:
                found = any(expected_route in route for route in routes)
                assert found, f"Route {expected_route} should be included"
            
            print("✓ FastAPI application created successfully")
            print(f"✓ Found {len(routes)} routes")
            
    except Exception as e:
        print(f"✗ App creation failed: {e}")
        raise


def test_demo_data_generation():
    """Test demo data generation"""
    try:
        from app.demo.globaltech_data import create_globaltech_demo_data
        
        demo_data = create_globaltech_demo_data()
        
        # Verify data structure
        assert "entities" in demo_data, "Demo data should include entities"
        assert "cash_positions" in demo_data, "Demo data should include cash positions"
        assert "investments" in demo_data, "Demo data should include investments"
        assert "fx_exposures" in demo_data, "Demo data should include FX exposures"
        
        # Verify data counts
        assert len(demo_data["entities"]) == 5, "Should have 5 entities"
        assert len(demo_data["cash_positions"]) > 0, "Should have cash positions"
        assert len(demo_data["investments"]) > 0, "Should have investments"
        assert len(demo_data["fx_exposures"]) > 0, "Should have FX exposures"
        
        # Calculate totals
        total_cash = sum(pos.balance for pos in demo_data["cash_positions"])
        total_investments = sum(inv.market_value or inv.principal_amount for inv in demo_data["investments"])
        
        print(f"✓ Demo data generated successfully")
        print(f"  - Entities: {len(demo_data['entities'])}")
        print(f"  - Cash Positions: {len(demo_data['cash_positions'])}")
        print(f"  - Investments: {len(demo_data['investments'])}")
        print(f"  - FX Exposures: {len(demo_data['fx_exposures'])}")
        print(f"  - Total Cash: ${total_cash:,.2f}")
        print(f"  - Total Investments: ${total_investments:,.2f}")
        print(f"  - Total Portfolio: ${total_cash + total_investments:,.2f}")
        
        # Verify we're close to $500M target
        total_portfolio = total_cash + total_investments
        assert 400_000_000 <= total_portfolio <= 600_000_000, f"Portfolio should be ~$500M, got ${total_portfolio:,.2f}"
        
    except Exception as e:
        print(f"✗ Demo data generation failed: {e}")
        raise


if __name__ == "__main__":
    test_app_creation()
    test_demo_data_generation()
    print("\n✅ All application tests passed!")