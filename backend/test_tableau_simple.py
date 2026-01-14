#!/usr/bin/env python3
"""
Simple test script for Tableau REST API integration without Redis dependency.
Tests authentication and basic API calls directly.
"""

import asyncio
import httpx
import os
import json

# Tableau configuration
TABLEAU_SERVER_URL = os.getenv("TABLEAU_SERVER_URL", "https://your-tableau-server.com")
TABLEAU_API_KEY = os.getenv("TABLEAU_API_KEY", "your-tableau-api-key-here")
TABLEAU_SITE_ID = os.getenv("TABLEAU_SITE_ID", "")
TABLEAU_API_VERSION = os.getenv("TABLEAU_API_VERSION", "3.21")

# Extract token name and secret
if ":" in TABLEAU_API_KEY:
    TOKEN_NAME, TOKEN_SECRET = TABLEAU_API_KEY.split(":", 1)
else:
    raise ValueError("Invalid Tableau API key format. Expected 'name:secret'")

class SimpleTableauClient:
    """Simple Tableau REST API client for testing."""
    
    def __init__(self):
        self.base_url = f"{TABLEAU_SERVER_URL}/api/{TABLEAU_API_VERSION}"
        self.auth_token = None
        self.site_id = None
        
    async def authenticate(self):
        """Authenticate with Tableau Server using Personal Access Token."""
        auth_payload = {
            "credentials": {
                "personalAccessTokenName": TOKEN_NAME,
                "personalAccessTokenSecret": TOKEN_SECRET,
                "site": {
                    "contentUrl": TABLEAU_SITE_ID
                }
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/auth/signin",
                json=auth_payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code != 200:
                raise Exception(f"Authentication failed: {response.status_code} - {response.text}")
            
            auth_data = response.json()
            self.auth_token = auth_data["credentials"]["token"]
            self.site_id = auth_data["credentials"]["site"]["id"]
            
            return {
                "token": self.auth_token,
                "site_id": self.site_id,
                "user": auth_data["credentials"]["user"],
                "site": auth_data["credentials"]["site"]
            }
    
    async def make_request(self, method: str, endpoint: str, **kwargs):
        """Make authenticated request to Tableau API."""
        if not self.auth_token or not self.site_id:
            await self.authenticate()
        
        headers = kwargs.get("headers", {})
        headers["X-Tableau-Auth"] = self.auth_token
        kwargs["headers"] = headers
        
        url = f"{self.base_url}/sites/{self.site_id}/{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(method, url, **kwargs)
            return response

async def test_tableau_integration():
    """Test Tableau REST API integration."""
    print("🔄 Testing Tableau REST API Integration...")
    print("=" * 50)
    
    client = SimpleTableauClient()
    
    try:
        # Test authentication
        print("1. Testing Authentication...")
        auth_result = await client.authenticate()
        print(f"   ✅ Authentication successful!")
        print(f"   📍 Site ID: {auth_result['site_id']}")
        print(f"   👤 User: {auth_result['user']['name']}")
        print(f"   🏢 Site: {auth_result['site']['name']}")
        
        # Test workbooks
        print("\n2. Testing Workbooks API...")
        response = await client.make_request("GET", "workbooks")
        if response.status_code == 200:
            data = response.json()
            workbooks = data.get("workbooks", {}).get("workbook", [])
            print(f"   ✅ Found {len(workbooks)} workbooks")
            
            if workbooks:
                for i, wb in enumerate(workbooks[:3]):  # Show first 3
                    print(f"   📊 {i+1}. {wb.get('name', 'Unknown')} (ID: {wb.get('id', 'N/A')})")
                    print(f"      Project: {wb.get('project', {}).get('name', 'N/A')}")
                    print(f"      Owner: {wb.get('owner', {}).get('name', 'N/A')}")
                    print(f"      Updated: {wb.get('updatedAt', 'N/A')}")
            else:
                print("   ℹ️  No workbooks found on this site")
        else:
            print(f"   ❌ Failed to fetch workbooks: {response.status_code} - {response.text}")
        
        # Test views
        print("\n3. Testing Views API...")
        response = await client.make_request("GET", "views")
        if response.status_code == 200:
            data = response.json()
            views = data.get("views", {}).get("view", [])
            print(f"   ✅ Found {len(views)} views")
            
            if views:
                for i, view in enumerate(views[:3]):  # Show first 3
                    print(f"   👁️  {i+1}. {view.get('name', 'Unknown')} (ID: {view.get('id', 'N/A')})")
                    print(f"      Workbook: {view.get('workbook', {}).get('name', 'N/A')}")
                    print(f"      Views: {view.get('usage', {}).get('totalViewCount', 0)}")
            else:
                print("   ℹ️  No views found on this site")
        else:
            print(f"   ❌ Failed to fetch views: {response.status_code} - {response.text}")
        
        # Test data sources
        print("\n4. Testing Data Sources API...")
        response = await client.make_request("GET", "datasources")
        if response.status_code == 200:
            data = response.json()
            datasources = data.get("datasources", {}).get("datasource", [])
            print(f"   ✅ Found {len(datasources)} data sources")
            
            if datasources:
                for i, ds in enumerate(datasources[:3]):  # Show first 3
                    print(f"   🗄️  {i+1}. {ds.get('name', 'Unknown')} (Type: {ds.get('type', 'N/A')})")
                    print(f"      Project: {ds.get('project', {}).get('name', 'N/A')}")
                    print(f"      Updated: {ds.get('updatedAt', 'N/A')}")
            else:
                print("   ℹ️  No data sources found on this site")
        else:
            print(f"   ❌ Failed to fetch data sources: {response.status_code} - {response.text}")
        
        # Test projects
        print("\n5. Testing Projects API...")
        response = await client.make_request("GET", "projects")
        if response.status_code == 200:
            data = response.json()
            projects = data.get("projects", {}).get("project", [])
            print(f"   ✅ Found {len(projects)} projects")
            
            if projects:
                for i, project in enumerate(projects[:3]):  # Show first 3
                    print(f"   📁 {i+1}. {project.get('name', 'Unknown')} (ID: {project.get('id', 'N/A')})")
                    print(f"      Description: {project.get('description', 'No description')}")
            else:
                print("   ℹ️  No projects found on this site")
        else:
            print(f"   ❌ Failed to fetch projects: {response.status_code} - {response.text}")
        
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
    print("🚀 TreasuryIQ Tableau Integration Test (Simple)")
    print("=" * 50)
    
    # Check environment variables
    print(f"📍 Tableau Server: {TABLEAU_SERVER_URL}")
    print(f"🔑 API Key: {'*' * 20}:{TOKEN_SECRET[:10]}...")
    print(f"🌐 Site ID: {TABLEAU_SITE_ID or '(default)'}")
    print()
    
    success = await test_tableau_integration()
    
    if success:
        print("\n🎯 Integration test passed! Tableau API is working correctly.")
        print("✨ You can now use the Tableau integration in TreasuryIQ!")
        return 0
    else:
        print("\n💥 Integration test failed! Check the error messages above.")
        print("🔧 Common issues:")
        print("   - Check your Tableau API key is correct")
        print("   - Verify you have access to the Tableau site")
        print("   - Ensure the Tableau Server URL is accessible")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)