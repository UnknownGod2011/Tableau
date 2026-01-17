"""
Comprehensive Tableau Integration Test
Tests all Tableau API features and functionality
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import json
from datetime import datetime

# Import the Tableau API endpoints
from app.api.v1.endpoints.tableau import (
    tableau_client,
    authenticate_tableau,
    get_workbooks,
    get_views,
    export_workbook_pdf,
    create_treasury_dashboard,
    get_treasury_insights,
    tableau_health_check,
    format_treasury_data_for_tableau,
    generate_treasury_workbook_xml
)


class TestTableauIntegration:
    """Test suite for Tableau integration features"""
    
    def test_tableau_client_initialization(self):
        """Test that Tableau client initializes correctly"""
        assert tableau_client.base_url is not None
        assert "tableau.com" in tableau_client.base_url or "localhost" in tableau_client.base_url
        assert tableau_client.auth_token is None  # Should start unauthenticated
    
    @pytest.mark.asyncio
    async def test_authentication_flow(self):
        """Test Tableau authentication process"""
        # Mock successful authentication response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "credentials": {
                "token": "test_auth_token_12345",
                "site": {"id": "test_site_id"},
                "user": {"id": "test_user_id", "name": "Test User"}
            }
        }
        
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
            
            # Mock Redis client
            with patch.object(tableau_client, 'get_redis') as mock_redis:
                mock_redis_client = AsyncMock()
                mock_redis_client.get.return_value = None  # No cached token
                mock_redis_client.setex = AsyncMock()
                mock_redis.return_value = mock_redis_client
                
                # Test authentication
                result = await tableau_client.authenticate()
                
                assert result["token"] == "test_auth_token_12345"
                assert result["site_id"] == "test_site_id"
                assert tableau_client.auth_token == "test_auth_token_12345"
                assert tableau_client.site_id == "test_site_id"
    
    @pytest.mark.asyncio
    async def test_get_workbooks_endpoint(self):
        """Test fetching workbooks from Tableau"""
        # Mock workbooks response
        mock_workbooks_data = {
            "workbooks": {
                "workbook": [
                    {
                        "id": "workbook_1",
                        "name": "Treasury Dashboard",
                        "description": "Main treasury analytics dashboard",
                        "project": {"id": "project_1", "name": "Treasury"},
                        "owner": {"id": "user_1", "name": "Treasury Manager"},
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-07T00:00:00Z"
                    },
                    {
                        "id": "workbook_2", 
                        "name": "Risk Analysis",
                        "description": "Risk management dashboard",
                        "project": {"id": "project_1", "name": "Treasury"},
                        "owner": {"id": "user_1", "name": "Risk Manager"},
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-07T00:00:00Z"
                    }
                ]
            }
        }
        
        with patch.object(tableau_client, 'make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_workbooks_data
            mock_request.return_value = mock_response
            
            result = await get_workbooks()
            
            assert result["status"] == "success"
            assert result["count"] == 2
            assert len(result["data"]) == 2
            assert result["data"][0]["name"] == "Treasury Dashboard"
            assert result["data"][1]["name"] == "Risk Analysis"
    
    @pytest.mark.asyncio
    async def test_get_views_endpoint(self):
        """Test fetching views from Tableau"""
        mock_views_data = {
            "views": {
                "view": [
                    {
                        "id": "view_1",
                        "name": "Cash Position Overview",
                        "workbook": {"id": "workbook_1", "name": "Treasury Dashboard"},
                        "project": {"id": "project_1", "name": "Treasury"},
                        "owner": {"id": "user_1", "name": "Treasury Manager"}
                    },
                    {
                        "id": "view_2",
                        "name": "FX Risk Analysis", 
                        "workbook": {"id": "workbook_1", "name": "Treasury Dashboard"},
                        "project": {"id": "project_1", "name": "Treasury"},
                        "owner": {"id": "user_1", "name": "Treasury Manager"}
                    }
                ]
            }
        }
        
        with patch.object(tableau_client, 'make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_views_data
            mock_request.return_value = mock_response
            
            result = await get_views()
            
            assert result["status"] == "success"
            assert result["count"] == 2
            assert len(result["data"]) == 2
            assert result["data"][0]["name"] == "Cash Position Overview"
            assert result["data"][1]["name"] == "FX Risk Analysis"
    
    @pytest.mark.asyncio
    async def test_export_workbook_pdf(self):
        """Test PDF export functionality"""
        with patch.object(tableau_client, 'make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"PDF_CONTENT_MOCK"
            mock_request.return_value = mock_response
            
            result = await export_workbook_pdf("workbook_1", {"pageType": "A4"})
            
            # Should return StreamingResponse
            assert hasattr(result, 'media_type')
            assert result.media_type == "application/pdf"
    
    @pytest.mark.asyncio
    async def test_create_treasury_dashboard(self):
        """Test creating treasury-specific dashboards"""
        dashboard_config = {
            "name": "Test Treasury Dashboard",
            "project_id": "project_1",
            "data_sources": ["treasury_data", "market_data"],
            "views": [
                {"name": "Cash Overview", "type": "cash_position"},
                {"name": "Risk Analysis", "type": "fx_risk"}
            ]
        }
        
        mock_response_data = {
            "workbook": {
                "id": "new_workbook_123",
                "name": "Test Treasury Dashboard",
                "project": {"id": "project_1"},
                "webPageUrl": "https://tableau.com/workbooks/new_workbook_123"
            }
        }
        
        with patch.object(tableau_client, 'make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 201
            mock_response.json.return_value = mock_response_data
            mock_request.return_value = mock_response
            
            result = await create_treasury_dashboard(dashboard_config)
            
            assert result["status"] == "success"
            assert result["data"]["workbook_id"] == "new_workbook_123"
            assert result["data"]["workbook_name"] == "Test Treasury Dashboard"
    
    @pytest.mark.asyncio
    async def test_treasury_insights_generation(self):
        """Test AI-powered treasury insights"""
        mock_workbook_data = {
            "workbook": {
                "id": "workbook_1",
                "name": "Treasury Dashboard",
                "viewCount": 150,
                "userCount": 25
            }
        }
        
        with patch.object(tableau_client, 'make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_workbook_data
            mock_request.return_value = mock_response
            
            result = await get_treasury_insights("workbook_1")
            
            assert result["status"] == "success"
            assert "insights" in result["data"]
            insights = result["data"]["insights"]
            
            # Verify insight structure
            assert "summary" in insights
            assert "key_findings" in insights
            assert "recommendations" in insights
            assert "risk_alerts" in insights
            assert "confidence" in insights
            
            # Verify content quality
            assert len(insights["key_findings"]) > 0
            assert len(insights["recommendations"]) > 0
            assert insights["confidence"] > 0.5
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test Tableau health check endpoint"""
        # Mock successful authentication
        with patch.object(tableau_client, 'authenticate') as mock_auth:
            mock_auth.return_value = {"site_id": "test_site"}
            
            # Mock successful API call
            with patch.object(tableau_client, 'make_request') as mock_request:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_request.return_value = mock_response
                
                result = await tableau_health_check()
                
                assert result["status"] == "healthy"
                assert result["authenticated"] == True
                assert result["api_functional"] == True
                assert "features" in result
                
                # Verify all expected features are listed
                features = result["features"]
                expected_features = [
                    "data_publishing", "dashboard_creation", "real_time_filtering",
                    "ai_insights", "usage_analytics", "alert_subscriptions"
                ]
                for feature in expected_features:
                    assert feature in features
                    assert features[feature] == True
    
    def test_treasury_data_formatting(self):
        """Test treasury data formatting for Tableau"""
        test_data = {
            "cash_positions": [
                {
                    "date": "2024-01-07T10:00:00Z",
                    "entity": "US Headquarters",
                    "currency": "USD",
                    "balance": 1000000,
                    "account_type": "Operating"
                }
            ],
            "fx_rates": [
                {
                    "date": "2024-01-07T10:00:00Z",
                    "base_currency": "USD",
                    "target_currency": "EUR",
                    "rate": 0.85
                }
            ],
            "risk_metrics": [
                {
                    "date": "2024-01-07T10:00:00Z",
                    "entity": "US Headquarters",
                    "risk_type": "Market Risk",
                    "value": 50000,
                    "limit": 100000
                }
            ]
        }
        
        formatted_data = format_treasury_data_for_tableau(test_data)
        
        # Should have 3 records (one for each data type)
        assert len(formatted_data) == 3
        
        # Check cash position record
        cash_record = next(r for r in formatted_data if r["Data_Type"] == "Cash Position")
        assert cash_record["Entity"] == "US Headquarters"
        assert cash_record["Currency"] == "USD"
        assert cash_record["Cash_Balance"] == 1000000
        
        # Check FX rate record
        fx_record = next(r for r in formatted_data if r["Data_Type"] == "FX Rate")
        assert fx_record["Base_Currency"] == "USD"
        assert fx_record["Target_Currency"] == "EUR"
        assert fx_record["Exchange_Rate"] == 0.85
        
        # Check risk metric record
        risk_record = next(r for r in formatted_data if r["Data_Type"] == "Risk Metric")
        assert risk_record["Entity"] == "US Headquarters"
        assert risk_record["Risk_Type"] == "Market Risk"
        assert risk_record["Risk_Value"] == 50000
    
    def test_workbook_xml_generation(self):
        """Test treasury workbook XML generation"""
        config = {
            "name": "Test Treasury Workbook",
            "project_id": "project_123",
            "views": [
                {"name": "Cash Overview", "type": "cash_position"},
                {"name": "Risk Dashboard", "type": "fx_risk"}
            ]
        }
        
        xml_content = generate_treasury_workbook_xml(config)
        
        # Verify XML structure
        assert "<?xml version='1.0' encoding='UTF-8'?>" in xml_content
        assert "<tsRequest>" in xml_content
        assert "Test Treasury Workbook" in xml_content
        assert "project_123" in xml_content
        assert "Cash Position Overview" in xml_content
        assert "FX Risk Analysis" in xml_content
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in Tableau API calls"""
        # Test authentication failure
        with patch.object(tableau_client, 'make_request') as mock_request:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_request.return_value = mock_response
            
            with pytest.raises(Exception):  # Should raise HTTPException
                await get_workbooks()
    
    def test_advanced_features_availability(self):
        """Test that all advanced Tableau features are implemented"""
        # Check that all expected methods exist on tableau_client
        expected_methods = [
            'authenticate', 'make_request', 'ensure_authenticated'
        ]
        
        for method in expected_methods:
            assert hasattr(tableau_client, method), f"Missing method: {method}"
        
        # Check that all advanced endpoints are available
        from app.api.v1.endpoints.tableau import router
        
        # Get all route paths
        route_paths = [route.path for route in router.routes]
        
        expected_endpoints = [
            "/auth", "/workbooks", "/views", "/datasources",
            "/analytics/treasury-insights/{workbook_id}",
            "/workbooks/create-treasury-dashboard",
            "/health"
        ]
        
        for endpoint in expected_endpoints:
            # Check if endpoint pattern exists (allowing for path parameters)
            endpoint_exists = any(
                endpoint.replace("{workbook_id}", "").replace("{view_id}", "").replace("{datasource_id}", "") in path
                for path in route_paths
            )
            assert endpoint_exists, f"Missing endpoint: {endpoint}"


class TestTableauIntegrationPerformance:
    """Performance and reliability tests for Tableau integration"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling multiple concurrent Tableau requests"""
        async def mock_workbook_request():
            with patch.object(tableau_client, 'make_request') as mock_request:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"workbooks": {"workbook": []}}
                mock_request.return_value = mock_response
                
                return await get_workbooks()
        
        # Run 5 concurrent requests
        tasks = [mock_workbook_request() for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        for result in results:
            assert result["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_authentication_caching(self):
        """Test that authentication tokens are properly cached"""
        with patch.object(tableau_client, 'get_redis') as mock_redis:
            mock_redis_client = AsyncMock()
            
            # First call - no cached token
            mock_redis_client.get.return_value = None
            mock_redis_client.setex = AsyncMock()
            mock_redis.return_value = mock_redis_client
            
            with patch('httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "credentials": {
                        "token": "cached_token_123",
                        "site": {"id": "site_123"},
                        "user": {"id": "user_123"}
                    }
                }
                mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
                
                # First authentication
                result1 = await tableau_client.authenticate()
                assert not result1.get("cached", True)  # Should not be cached
                
                # Mock cached token for second call
                mock_redis_client.get.side_effect = [
                    b"cached_token_123",  # auth token
                    b"site_123"          # site id
                ]
                
                # Second authentication should use cache
                result2 = await tableau_client.authenticate()
                assert result2.get("cached", False)  # Should be cached


if __name__ == "__main__":
    print("Running Comprehensive Tableau Integration Tests")
    
    # Run the tests
    import sys
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))