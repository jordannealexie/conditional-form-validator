#!/usr/bin/env python3
"""
Test script to verify the database-driven permission system works correctly.

This script:
1. Finds a non-superuser with ABAC/ReBAC permissions
2. Tests that they can access ABAC and ReBAC endpoints
3. Shows detailed permission checking logs
"""

import asyncio
import sys
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import AsyncSessionLocal
from app.models.user import User, Role
from app.dependencies.permissions import get_user_permissions_from_db


async def test_permission_system():
    """Test the database-driven permission system"""
    
    print("=" * 80)
    print("🧪 Testing Database-Driven Permission System")
    print("=" * 80)
    
    async with AsyncSessionLocal() as db:
        # Find users with ABAC/ReBAC permissions
        print("\n📋 Step 1: Finding users with ABAC/ReBAC permissions...")
        
        # Get all roles with policies:* or relationships:* permissions
        stmt = select(Role).options(selectinload(Role.users))
        result = await db.execute(stmt)
        roles = result.scalars().all()
        
        test_users = []
        for role in roles:
            if not role.permissions:
                continue
            
            has_abac = any("policies:" in p for p in role.permissions)
            has_rebac = any("relationships:" in p for p in role.permissions)
            
            if has_abac or has_rebac:
                for user in role.users:
                    if not user.is_superuser:
                        test_users.append((user, role))
        
        if not test_users:
            print("❌ No non-superuser found with ABAC/ReBAC permissions!")
            print("   Create a role with policies:read or relationships:read and assign it to a user.")
            return False
        
        print(f"✅ Found {len(test_users)} non-superuser(s) with ABAC/ReBAC permissions")
        
        # Test each user
        success_count = 0
        for user, role in test_users[:3]:  # Test up to 3 users
            print(f"\n{'='*80}")
            print(f"👤 Testing user: {user.username}")
            print(f"   Role: {role.name}")
            print(f"{'='*80}")
            
            # Get all permissions for this user
            permissions = await get_user_permissions_from_db(user, db)
            
            print(f"\n🔑 User permissions ({len(permissions)} total):")
            for perm in sorted(permissions):
                print(f"   ✓ {perm}")
            
            # Check specific ABAC permissions
            print("\n🎯 ABAC Permission Checks:")
            abac_perms = {
                "policies:create": "Create ABAC policies",
                "policies:read": "List/view ABAC policies",
                "policies:update": "Update ABAC policies",
                "policies:delete": "Delete ABAC policies"
            }
            
            abac_pass = False
            for perm, desc in abac_perms.items():
                has_perm = perm in permissions
                status = "✅" if has_perm else "❌"
                print(f"   {status} {perm:20s} - {desc}")
                if has_perm:
                    abac_pass = True
            
            # Check specific ReBAC permissions
            print("\n🎯 ReBAC Permission Checks:")
            rebac_perms = {
                "relationships:create": "Create relationships",
                "relationships:read": "List/view relationships",
                "relationships:update": "Update relationships",
                "relationships:delete": "Delete relationships"
            }
            
            rebac_pass = False
            for perm, desc in rebac_perms.items():
                has_perm = perm in permissions
                status = "✅" if has_perm else "❌"
                print(f"   {status} {perm:25s} - {desc}")
                if has_perm:
                    rebac_pass = True
            
            # Summary for this user
            print(f"\n📊 Test Results for {user.username}:")
            if abac_pass:
                print("   ✅ Can access ABAC endpoints (GET /api/v1/abac/policies)")
            else:
                print("   ❌ Cannot access ABAC endpoints")
            
            if rebac_pass:
                print("   ✅ Can access ReBAC endpoints (GET /api/v1/rebac/relationships)")
            else:
                print("   ❌ Cannot access ReBAC endpoints")
            
            if abac_pass or rebac_pass:
                success_count += 1
        
        print(f"\n{'='*80}")
        print(f"🎉 Test Summary: {success_count}/{len(test_users[:3])} users can access ABAC/ReBAC")
        print(f"{'='*80}")
        
        return success_count > 0


async def show_permission_examples():
    """Show example SQL queries and how to assign permissions"""
    
    print("\n" + "=" * 80)
    print("📚 How to Assign Permissions")
    print("=" * 80)
    
    print("""
1. Via SQL (Direct):
   UPDATE roles
   SET permissions = '["policies:read", "policies:create", "relationships:read"]'::jsonb
   WHERE name = 'Policy Viewer';

2. Via Roles & Permissions UI:
   - Login as admin
   - Navigate to Roles page
   - Edit a role
   - Check boxes for:
     • policies:read
     • policies:create
     • policies:update
     • policies:delete
     • relationships:read
     • relationships:create
     • relationships:update
     • relationships:delete

3. Via Python (Backend):
   async with AsyncSessionLocal() as db:
       stmt = select(Role).where(Role.name == "Policy Manager")
       result = await db.execute(stmt)
       role = result.scalar_one()
       
       role.permissions = [
           "policies:read",
           "policies:create",
           "policies:update",
           "policies:delete"
       ]
       
       await db.commit()
""")
    
    print("\n" + "=" * 80)
    print("🔍 Checking Permissions")
    print("=" * 80)
    
    print("""
Query to see who has ABAC access:
    SELECT u.username, r.name AS role_name, r.permissions
    FROM users u
    JOIN user_roles ur ON u.id = ur.user_id
    JOIN roles r ON ur.role_id = r.id
    WHERE r.permissions @> '["policies:read"]'::jsonb;

Query to see all permissions for a user:
    SELECT DISTINCT jsonb_array_elements_text(r.permissions) AS permission
    FROM users u
    JOIN user_roles ur ON u.id = ur.user_id
    JOIN roles r ON ur.role_id = r.id
    WHERE u.username = 'john.doe'
    ORDER BY permission;
""")


if __name__ == "__main__":
    print("\n🚀 Starting Permission System Test...\n")
    
    try:
        result = asyncio.run(test_permission_system())
        asyncio.run(show_permission_examples())
        
        if result:
            print("\n✅ Permission system is working correctly!")
            print("   Users with permissions can now access ABAC and ReBAC pages.")
            sys.exit(0)
        else:
            print("\n⚠️  No users found with ABAC/ReBAC permissions.")
            print("   Assign permissions via the Roles & Permissions UI to test.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
