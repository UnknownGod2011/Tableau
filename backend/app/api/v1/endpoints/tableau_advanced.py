"""
Advanced Tableau REST API features for TreasuryIQ.
Implements additional Tableau capabilities: Metadata API, Webhooks, Users, Groups, Permissions, etc.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from typing import List, Dict, Any, Optional
import httpx
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Import the main tableau client
from .tableau import tableau_client

# ============================================================================
# USERS & GROUPS MANAGEMENT
# ============================================================================

@router.get("/users")
async def get_users(page_size: int = 100, page_number: int = 1):
    """Get all users on the site."""
    try:
        response = await tableau_client.make_request(
            "GET", 
            f"users?pageSize={page_size}&pageNumber={page_number}"
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch users: {response.text}"
            )
        
        data = response.json()
        users = data.get("users", {}).get("user", [])
        
        return {
            "status": "success",
            "data": users,
            "count": len(users),
            "pagination": {
                "page_size": page_size,
                "page_number": page_number
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch users")

@router.get("/groups")
async def get_groups():
    """Get all groups on the site."""
    try:
        response = await tableau_client.make_request("GET", "groups")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch groups: {response.text}"
            )
        
        data = response.json()
        groups = data.get("groups", {}).get("group", [])
        
        return {
            "status": "success",
            "data": groups,
            "count": len(groups)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching groups: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch groups")

@router.post("/users")
async def create_user(user_data: Dict[str, Any]):
    """Create a new user on the site."""
    try:
        payload = {
            "user": {
                "name": user_data.get("name"),
                "siteRole": user_data.get("siteRole", "Viewer"),
                "authSetting": user_data.get("authSetting", "ServerDefault")
            }
        }
        
        response = await tableau_client.make_request(
            "POST",
            "users",
            json=payload
        )
        
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create user: {response.text}"
            )
        
        data = response.json()
        return {
            "status": "success",
            "message": "User created successfully",
            "data": data.get("user", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user")

# ============================================================================
# PERMISSIONS MANAGEMENT
# ============================================================================

@router.get("/workbooks/{workbook_id}/permissions")
async def get_workbook_permissions(workbook_id: str):
    """Get permissions for a workbook."""
    try:
        response = await tableau_client.make_request(
            "GET",
            f"workbooks/{workbook_id}/permissions"
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch permissions: {response.text}"
            )
        
        data = response.json()
        return {
            "status": "success",
            "data": data.get("permissions", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching workbook permissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch permissions")

@router.put("/workbooks/{workbook_id}/permissions")
async def update_workbook_permissions(workbook_id: str, permissions: Dict[str, Any]):
    """Update permissions for a workbook."""
    try:
        payload = build_permissions_payload(permissions)
        
        response = await tableau_client.make_request(
            "PUT",
            f"workbooks/{workbook_id}/permissions",
            json=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to update permissions: {response.text}"
            )
        
        return {
            "status": "success",
            "message": "Permissions updated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating permissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to update permissions")

# ============================================================================
# SCHEDULES & TASKS
# ============================================================================

@router.get("/schedules")
async def get_schedules():
    """Get all schedules on the site."""
    try:
        response = await tableau_client.make_request("GET", "schedules")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch schedules: {response.text}"
            )
        
        data = response.json()
        schedules = data.get("schedules", {}).get("schedule", [])
        
        return {
            "status": "success",
            "data": schedules,
            "count": len(schedules)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching schedules: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch schedules")

@router.post("/schedules")
async def create_schedule(schedule_data: Dict[str, Any]):
    """Create a new schedule for automated tasks."""
    try:
        payload = {
            "schedule": {
                "name": schedule_data.get("name"),
                "priority": schedule_data.get("priority", 50),
                "type": schedule_data.get("type", "Extract"),
                "frequency": schedule_data.get("frequency", "Daily"),
                "frequencyDetails": schedule_data.get("frequencyDetails", {})
            }
        }
        
        response = await tableau_client.make_request(
            "POST",
            "schedules",
            json=payload
        )
        
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create schedule: {response.text}"
            )
        
        data = response.json()
        return {
            "status": "success",
            "message": "Schedule created successfully",
            "data": data.get("schedule", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating schedule: {e}")
        raise HTTPException(status_code=500, detail="Failed to create schedule")

# ============================================================================
# METADATA API
# ============================================================================

@router.post("/metadata/graphql")
async def query_metadata(query: Dict[str, Any]):
    """Query Tableau Metadata API using GraphQL."""
    try:
        await tableau_client.ensure_authenticated()
        
        # Metadata API uses different endpoint
        metadata_url = f"{tableau_client.base_url.replace('/api/', '/api/metadata/')}/graphql"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                metadata_url,
                json={"query": query.get("query"), "variables": query.get("variables", {})},
                headers={
                    "X-Tableau-Auth": tableau_client.auth_token,
                    "Content-Type": "application/json"
                }
            )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Metadata query failed: {response.text}"
            )
        
        return {
            "status": "success",
            "data": response.json()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying metadata: {e}")
        raise HTTPException(status_code=500, detail="Metadata query failed")

@router.get("/metadata/workbook-lineage/{workbook_id}")
async def get_workbook_lineage(workbook_id: str):
    """Get data lineage for a workbook using Metadata API."""
    try:
        graphql_query = """
        query WorkbookLineage($workbookId: ID!) {
            workbook(id: $workbookId) {
                id
                name
                upstreamDatasources {
                    id
                    name
                    upstreamTables {
                        id
                        name
                        database {
                            name
                        }
                    }
                }
                downstreamSheets {
                    id
                    name
                }
            }
        }
        """
        
        result = await query_metadata({
            "query": graphql_query,
            "variables": {"workbookId": workbook_id}
        })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching workbook lineage: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch lineage")

# ============================================================================
# WEBHOOKS & NOTIFICATIONS
# ============================================================================

@router.post("/webhooks")
async def create_webhook(webhook_config: Dict[str, Any]):
    """Create a webhook for Tableau events."""
    try:
        payload = {
            "webhook": {
                "name": webhook_config.get("name"),
                "event": webhook_config.get("event"),  # e.g., "workbook-refresh-succeeded"
                "url": webhook_config.get("url")
            }
        }
        
        response = await tableau_client.make_request(
            "POST",
            "webhooks",
            json=payload
        )
        
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to create webhook: {response.text}"
            )
        
        data = response.json()
        return {
            "status": "success",
            "message": "Webhook created successfully",
            "data": data.get("webhook", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to create webhook")

@router.get("/webhooks")
async def list_webhooks():
    """List all webhooks on the site."""
    try:
        response = await tableau_client.make_request("GET", "webhooks")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch webhooks: {response.text}"
            )
        
        data = response.json()
        webhooks = data.get("webhooks", {}).get("webhook", [])
        
        return {
            "status": "success",
            "data": webhooks,
            "count": len(webhooks)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching webhooks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch webhooks")

@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str):
    """Delete a webhook."""
    try:
        response = await tableau_client.make_request(
            "DELETE",
            f"webhooks/{webhook_id}"
        )
        
        if response.status_code != 204:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to delete webhook: {response.text}"
            )
        
        return {
            "status": "success",
            "message": "Webhook deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting webhook: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete webhook")

# ============================================================================
# FAVORITES & RECOMMENDATIONS
# ============================================================================

@router.get("/favorites")
async def get_favorites():
    """Get user's favorite content."""
    try:
        response = await tableau_client.make_request("GET", "favorites")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch favorites: {response.text}"
            )
        
        data = response.json()
        return {
            "status": "success",
            "data": data.get("favorites", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching favorites: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch favorites")

@router.post("/favorites/workbook/{workbook_id}")
async def add_workbook_to_favorites(workbook_id: str):
    """Add a workbook to favorites."""
    try:
        payload = {
            "favorite": {
                "label": "workbook",
                "workbook": {"id": workbook_id}
            }
        }
        
        response = await tableau_client.make_request(
            "POST",
            "favorites",
            json=payload
        )
        
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to add favorite: {response.text}"
            )
        
        return {
            "status": "success",
            "message": "Workbook added to favorites"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding favorite: {e}")
        raise HTTPException(status_code=500, detail="Failed to add favorite")

# ============================================================================
# TAGS & LABELS
# ============================================================================

@router.post("/workbooks/{workbook_id}/tags")
async def add_tags_to_workbook(workbook_id: str, tags: List[str]):
    """Add tags to a workbook."""
    try:
        for tag in tags:
            payload = {"tags": {"tag": [{"label": tag}]}}
            
            response = await tableau_client.make_request(
                "PUT",
                f"workbooks/{workbook_id}/tags",
                json=payload
            )
            
            if response.status_code != 200:
                logger.warning(f"Failed to add tag '{tag}': {response.text}")
        
        return {
            "status": "success",
            "message": f"Added {len(tags)} tags to workbook",
            "tags": tags
        }
    except Exception as e:
        logger.error(f"Error adding tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to add tags")

@router.get("/workbooks/{workbook_id}/tags")
async def get_workbook_tags(workbook_id: str):
    """Get tags for a workbook."""
    try:
        response = await tableau_client.make_request(
            "GET",
            f"workbooks/{workbook_id}/tags"
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch tags: {response.text}"
            )
        
        data = response.json()
        tags = data.get("tags", {}).get("tag", [])
        
        return {
            "status": "success",
            "data": [tag.get("label") for tag in tags]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tags: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tags")

# ============================================================================
# EXTRACT REFRESH TASKS
# ============================================================================

@router.post("/datasources/{datasource_id}/refresh-schedule")
async def schedule_datasource_refresh(datasource_id: str, schedule_config: Dict[str, Any]):
    """Schedule automatic refresh for a data source."""
    try:
        payload = {
            "task": {
                "extractRefresh": {
                    "datasource": {"id": datasource_id},
                    "schedule": {"id": schedule_config.get("schedule_id")}
                }
            }
        }
        
        response = await tableau_client.make_request(
            "POST",
            "tasks/extractRefreshes",
            json=payload
        )
        
        if response.status_code not in [200, 201]:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to schedule refresh: {response.text}"
            )
        
        data = response.json()
        return {
            "status": "success",
            "message": "Data source refresh scheduled",
            "data": data.get("task", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling refresh: {e}")
        raise HTTPException(status_code=500, detail="Failed to schedule refresh")

@router.get("/tasks/extractRefreshes")
async def get_extract_refresh_tasks():
    """Get all extract refresh tasks."""
    try:
        response = await tableau_client.make_request("GET", "tasks/extractRefreshes")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch tasks: {response.text}"
            )
        
        data = response.json()
        tasks = data.get("tasks", {}).get("task", [])
        
        return {
            "status": "success",
            "data": tasks,
            "count": len(tasks)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch tasks")

# ============================================================================
# CONNECTED APPS (OAuth)
# ============================================================================

@router.get("/connected-apps")
async def get_connected_apps():
    """Get all connected apps configured on the site."""
    try:
        response = await tableau_client.make_request("GET", "connected-apps")
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Failed to fetch connected apps: {response.text}"
            )
        
        data = response.json()
        return {
            "status": "success",
            "data": data.get("connectedApps", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching connected apps: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch connected apps")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def build_permissions_payload(permissions: Dict[str, Any]) -> Dict[str, Any]:
    """Build permissions payload for Tableau API."""
    capabilities = []
    
    for capability, mode in permissions.get("capabilities", {}).items():
        capabilities.append({
            "name": capability,
            "mode": mode
        })
    
    return {
        "permissions": {
            "granteeCapabilities": [{
                "user": {"id": permissions.get("user_id")} if "user_id" in permissions else None,
                "group": {"id": permissions.get("group_id")} if "group_id" in permissions else None,
                "capabilities": {"capability": capabilities}
            }]
        }
    }
