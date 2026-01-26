#!/usr/bin/env python3
"""
Test the /authorization/permissions endpoint to verify it returns correct permissions
"""
import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.casbin_enforcer import casbin_enforcer
from sqlalchemy import select

async def test_permissions_endpoint():
    await casbin_enforcer.initialize()
    
    print("🧪 Testing Permission Endpoint Response")
    print("=" * 70)
    
    async with AsyncSessionLocal() as session:
        # Test different user types
        test_users = ["bdo_fieldman_1", "bdo_supervisor_1", "harrypotter"]
        
        for username in test_users:
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                print(f"❌ User {username} not found")
                continue
            
            print(f"\n👤 User: {user.username}")
            print(f"   Role: {user.user_role}")
            
            # Get roles from Casbin
            roles = casbin_enforcer.get_roles_for_user(user.username)
            if not roles and user.user_role:
                roles = [user.user_role]
            
            print(f"   Casbin Roles: {roles}")
            
            # Get permissions for these roles (simulating the endpoint)
            permissions = []
            for role in roles:
                role_perms = casbin_enforcer.get_permissions_for_role(role)
                for perm in role_perms:
                    if len(perm) >= 3:
                        permissions.append({
                            "resource": perm[1],
                            "action": perm[2]
                        })
            
            print(f"   Permissions returned: {len(permissions)}")
            
            # Check specific permissions
            has_submissions_create = any(
                p["resource"] == "submissions" and p["action"] == "create" 
                for p in permissions
            )
            has_templates_read = any(
                p["resource"] == "templates" and p["action"] == "read" 
                for p in permissions
            )
            
            print(f"   ✓ submissions:create = {has_submissions_create}")
            print(f"   ✓ templates:read = {has_templates_read}")
            
            if user.user_role == "fieldman":
                if not has_submissions_create:
                    print(f"   ⚠️  WARNING: Fieldman should have submissions:create!")
            elif user.user_role == "supervisor":
                if has_submissions_create:
                    print(f"   ⚠️  WARNING: Supervisor should NOT have submissions:create!")
        
        print("\n" + "=" * 70)
        print("✅ Test complete - check results above")

if __name__ == "__main__":
    asyncio.run(test_permissions_endpoint())
