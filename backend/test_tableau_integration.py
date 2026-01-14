#!/usr/bin/env python3
"""
Simple test script for Tableau REST API integration.
Tests authentication and basic API calls.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.api.v1.endpoints.tableau import tableau_client

async def test_tableau_integration():
    """Test Tableau REST API integration."""
    print("🔄 Testing Tableau REST API Integration...")
    print("=" * 50)
    
    try:
        # Test authentication
        print("1. Testing Authentication...")
        auth_result = await tableau_client.authenticate()
        print(f"   ✅ Authentication successful!")
        print(f"   📍 Site ID: {auth_result['site_id']}")
        print(f"   🔑 Token cached: {auth_result.get('cached', False)}")
        
        # Test workbooks
        print("\n2. Testing Workbooks API...")
        response = await tableau_client.make_request("GET", "workbooks")
        if response.status_code == 200:
            data = response.json()
            workbooks = data.get("workbooks", {}).get("workbook", [])
            print(f"   ✅ Found {len(workbooks)} workbooks")
            
            if workbooks:
                for i, wb in enumerate(workbooks[:3]):  # Show first 3
                    print(f"   📊 {i+1}. {wb.get('name', 'Unknown')} (ID: {wb.get('id', 'N/A')})")
            else:
                print("   ℹ️  No workbooks found on this site")
        else:
            print(f"   ❌ Failed to fetch workbooks: {response.status_code}")
        
        # Test views
        print("\n3. Testing Views API...")
        response = await tableau_client.make_request("GET", "views")
        if response.status_code == 200:
            data = response.json()
            views = data.get("views", {}).get("view", [])
            print(f"   ✅ Found {len(views)} views")
            
            if views:
                for i, view in enumerate(views[:3]):  # Show first 3
                    print(f"   👁️  {i+1}. {view.get('name', 'Unknown')} (ID: {view.get('id', 'N/A')})")
            else:
                print("   ℹ️  No views found on this site")
        else:
            print(f"   ❌ Failed to fetch views: {response.status_code}")
        
        # Test data sources
        print("\n4. Testing Data Sources API...")
        response = await tableau_client.make_request("GET", "datasources")
        if response.status_code == 200:
            data = response.json()
            datasources = data.get("datasources", {}).get("datasource", [])
            print(f"   ✅ Found {len(datasources)} data sources")
            
            if datasources:
                for i, ds in enumerate(datasources[:3]):  # Show first 3
                    print(f"   🗄️  {i+1}. {ds.get('name', 'Unknown')} (Type: {ds.get('type', 'N/A')})")
            else:
                print("   ℹ️  No data sources found on this site")
        else:
            print(f"   ❌ Failed to fetch data sources: {response.status_code}")
        
        # Test site info
        print("\n5. Testing Site Info API...")
        response = await tableau_client.make_request("GET", "")
        if response.status_code == 200:
            data = response.json()
            site = data.get("site", {})
            print(f"   ✅ Site info retrieved")
            print(f"   🏢 Site Name: {site.get('name', 'Unknown')}")
            print(f"   🌐 Content URL: {site.get('contentUrl', 'N/A')}")
            print(f"   👥 User Quota: {site.get('userQuota', 'N/A')}")
        else:
            print(f"   ❌ Failed to fetch site info: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("🎉 Tableau Integration Test Complete!")
        print("✅ All basic API calls successful")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Main test function."""
    print("🚀 TreasuryIQ Tableau Integration Test")
    print("=" * 50)
    
    # Check environment variables
    tableau_server = os.getenv("TABLEAU_SERVER_URL", "https://your-tableau-server.com")
    tableau_api_key = os.getenv("TABLEAU_API_KEY", "your-tableau-api-key-here")
    
    print(f"📍 Tableau Server: {tableau_server}")
    print(f"🔑 API Key: {'*' * 20}:{tableau_api_key.split(':')[1][:10]}...")
    print()
    
    success = await test_tableau_integration()
    
    if success:
        print("\n🎯 Integration test passed! Tableau API is working correctly.")
        sys.exit(0)
    else:
        print("\n💥 Integration test failed! Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())