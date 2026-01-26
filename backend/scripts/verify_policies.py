"""
Script to verify Casbin policies are correctly set.
This helps debug permission issues.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.core.casbin_enforcer import casbin_enforcer

async def verify_policies():
    """Verify Casbin policies"""
    print("🔍 Verifying Casbin policies...")
    
    # Initialize Casbin
    await casbin_enforcer.initialize()
    
    # Test roles
    test_roles = ["admin", "supervisor", "fieldman"]
    test_resources = ["submissions", "templates", "forms"]
    test_actions = ["create", "read", "update", "delete"]
    
    print("\n📊 Role Permissions in Casbin:")
    print("=" * 70)
    
    for role in test_roles:
        print(f"\n🔹 Role: {role}")
        perms = casbin_enforcer.get_permissions_for_role(role)
        if perms:
            for perm in perms:
                if len(perm) >= 3:
                    print(f"  ✓ {perm[1]}:{perm[2]}")
        else:
            print(f"  ⚠️ No permissions found for role {role}")
    
    print("\n\n👥 Sample User Role Assignments:")
    print("=" * 70)
    
    test_users = ["harrypotter", "fieldman1", "bdo_supervisor_1", "bdo_fieldman_1"]
    for username in test_users:
        roles = casbin_enforcer.get_roles_for_user(username)
        print(f"  User: {username:20} -> Roles: {roles}")
    
    print("\n\n🧪 Permission Test Cases:")
    print("=" * 70)
    
    test_cases = [
        ("fieldman1", "submissions", "create", True),
        ("fieldman1", "submissions", "read", True),
        ("fieldman1", "forms", "read", True),
        ("fieldman1", "users", "create", False),
        ("bdo_supervisor_1", "submissions", "read", True),
        ("bdo_supervisor_1", "submissions", "review", True),
        ("bdo_supervisor_1", "submissions", "create", False),
        ("harrypotter", "users", "create", True),
    ]
    
    for username, resource, action, expected in test_cases:
        result = await casbin_enforcer.check_rbac_permission_async(username, resource, action)
        status = "✅" if result == expected else "❌"
        expected_str = "should pass" if expected else "should fail"
        actual_str = "passed" if result else "failed"
        print(f"  {status} {username:20} {resource:15} {action:10} ({expected_str:15}) -> {actual_str}")

if __name__ == "__main__":
    asyncio.run(verify_policies())
