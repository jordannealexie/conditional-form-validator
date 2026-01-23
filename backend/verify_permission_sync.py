import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000/api/v1"

async def login(username, password):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            data={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"Login failed for {username}: {response.status_code} - {response.text}")
            return None

async def get_permissions(token):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/authorization/permissions",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            # Check if wrapped in create_response
            resp_json = response.json()
            if "data" in resp_json:
                return resp_json["data"]["permissions"]
            return resp_json["permissions"]
        else:
            print(f"Failed to get permissions: {response.text}")
            return []

async def get_role(token, role_name):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/roles",
            headers={"Authorization": f"Bearer {token}"}
        )
        resp_json = response.json()
        print(f"Roles response: {resp_json}")
        roles = resp_json.get("data", []) if isinstance(resp_json, dict) else resp_json
        if not isinstance(roles, list):
            print(f"Error: expected list of roles, got {type(roles)}")
            return None
        for role in roles:
            if role["name"] == role_name:
                return role
        return None

async def update_role_permissions(token, role_id, role_name, permissions):
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.put(
            f"{BASE_URL}/roles/{role_id}",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"name": role_name, "permissions": permissions}
        )
        return response.status_code == 200

async def verify_sync():
    print("🚀 Starting verification script...")
    
    # 1. Login as admin
    print("🔑 Logging in as admin...")
    admin_token = await login("harrypotter", "harrypotter")
    if not admin_token: return
    
    # 2. Login as fieldman
    print("👤 Logging in as fieldman...")
    fieldman_token = await login("bdo_fieldman_1", "password123")
    if not fieldman_token: return
    
    # 3. Check current permissions for fieldman
    fieldman_perms = await get_permissions(fieldman_token)
    print(f"Initial fieldman permissions: {fieldman_perms}")
    
    # 4. Add 'users:read' to fieldman role
    fieldman_role = await get_role(admin_token, "fieldman")
    if not fieldman_role:
        print("Fieldman role not found!")
        return
    
    new_perms = fieldman_role.get("permissions", []) + ["users:read"]
    print(f"🔄 Adding 'users:read' to fieldman role...")
    success = await update_role_permissions(admin_token, fieldman_role["id"], "fieldman", new_perms)
    if not success:
        print("Failed to update role!")
        return
    
    # 5. Check permissions for fieldman again (should be immediate)
    fieldman_perms_updated = await get_permissions(fieldman_token)
    print(f"Updated fieldman permissions: {fieldman_perms_updated}")
    
    # Extract permission strings for comparison
    updated_actions = [f"{p['resource']}:{p['action']}" for p in fieldman_perms_updated]
    
    if "users:read" in updated_actions:
        print("✅ SUCCESS: Role permission update synced immediately!")
    else:
        print("❌ FAILURE: Role permission update did NOT sync immediately!")

    # 6. Revert change
    print("🔄 Reverting changes...")
    await update_role_permissions(admin_token, fieldman_role["id"], "fieldman", [p for p in new_perms if p != "users:read"])
    
    # 7. Final check
    final_perms = await get_permissions(fieldman_token)
    final_actions = [f"{p['resource']}:{p['action']}" for p in final_perms]
    print(f"Final fieldman permissions: {final_actions}")
    if "users:read" not in final_actions:
        print("✅ SUCCESS: Role permission removal synced immediately!")
    else:
        print("❌ FAILURE: Role permission removal did NOT sync immediately!")

if __name__ == "__main__":
    asyncio.run(verify_sync())
