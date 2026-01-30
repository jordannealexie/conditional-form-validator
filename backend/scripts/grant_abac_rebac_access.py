#!/usr/bin/env python3
"""
Script to grant ABAC and ReBAC permissions to users or roles.
This ensures non-superusers can access ABAC/ReBAC admin pages.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.casbin_enforcer import casbin_enforcer


async def grant_abac_rebac_permissions(username: str = None, role: str = None):
    """
    Grant ABAC and ReBAC permissions to a user or role.
    
    Args:
        username: Username to grant permissions to
        role: Role name to grant permissions to
    """
    if not username and not role:
        print("Error: Must provide either username or role")
        return False
    
    target = username or role
    target_type = "user" if username else "role"
    
    # ABAC permissions
    abac_permissions = [
        (target, "abac", "read"),
        (target, "abac", "write"),
        (target, "abac", "delete"),
    ]
    
    # ReBAC permissions
    rebac_permissions = [
        (target, "rebac", "read"),
        (target, "rebac", "write"),
        (target, "rebac", "delete"),
    ]
    
    all_permissions = abac_permissions + rebac_permissions
    
    print(f"\n🔐 Granting ABAC/ReBAC permissions to {target_type}: {target}")
    print("=" * 60)
    
    for subject, resource, action in all_permissions:
        success = await casbin_enforcer.add_policy_async(subject, resource, action)
        status = "✓" if success else "✗ (already exists)"
        print(f"{status} {subject} -> {action} {resource}")
    
    # If it's a role, show how to assign users to it
    if role:
        print(f"\n📋 To assign users to the '{role}' role, run:")
        print(f"   await casbin_enforcer.add_role_for_user_async('username', '{role}')")
    
    print("\n✅ Permission grant complete!")
    return True


async def assign_user_to_role(username: str, role: str):
    """Assign a user to a role"""
    success = await casbin_enforcer.add_role_for_user_async(username, role)
    if success:
        print(f"✓ Assigned {username} to role: {role}")
    else:
        print(f"✗ Failed to assign {username} to role: {role} (may already exist)")
    return success


async def list_abac_rebac_permissions():
    """List all ABAC and ReBAC permissions"""
    print("\n📋 Current ABAC/ReBAC Permissions:")
    print("=" * 60)
    
    # Get all policies
    policies = await casbin_enforcer.get_policy_async()
    
    abac_policies = [p for p in policies if p[1] == "abac"]
    rebac_policies = [p for p in policies if p[1] == "rebac"]
    
    if abac_policies:
        print("\n🔹 ABAC Permissions:")
        for policy in abac_policies:
            print(f"   {policy[0]} -> {policy[2]} {policy[1]}")
    else:
        print("\n❌ No ABAC permissions found")
    
    if rebac_policies:
        print("\n🔹 ReBAC Permissions:")
        for policy in rebac_policies:
            print(f"   {policy[0]} -> {policy[2]} {policy[1]}")
    else:
        print("\n❌ No ReBAC permissions found")
    
    print()


async def verify_user_permissions(username: str):
    """Verify if a user has ABAC/ReBAC permissions"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return False
    
    print(f"\n🔍 Checking permissions for user: {username}")
    print("=" * 60)
    
    # Check superuser status
    if user.is_superuser:
        print("✓ User is SUPERUSER (has all permissions)")
        return True
    
    # Check ABAC permissions
    abac_read = await casbin_enforcer.check_rbac_permission_async(username, "abac", "read")
    abac_write = await casbin_enforcer.check_rbac_permission_async(username, "abac", "write")
    
    # Check ReBAC permissions
    rebac_read = await casbin_enforcer.check_rbac_permission_async(username, "rebac", "read")
    rebac_write = await casbin_enforcer.check_rbac_permission_async(username, "rebac", "write")
    
    print(f"\nABAC Permissions:")
    print(f"  Read:  {'✓' if abac_read else '✗'}")
    print(f"  Write: {'✓' if abac_write else '✗'}")
    
    print(f"\nReBAC Permissions:")
    print(f"  Read:  {'✓' if rebac_read else '✗'}")
    print(f"  Write: {'✓' if rebac_write else '✗'}")
    
    has_any = abac_read or abac_write or rebac_read or rebac_write
    
    if not has_any:
        print(f"\n❌ User '{username}' has NO ABAC/ReBAC permissions")
        print(f"\n💡 To grant permissions, run:")
        print(f"   python scripts/grant_abac_rebac_access.py grant-user {username}")
    else:
        print(f"\n✅ User has some ABAC/ReBAC permissions")
    
    return has_any


async def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Manage ABAC and ReBAC permissions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Grant permissions to a user
  python scripts/grant_abac_rebac_access.py grant-user john_doe
  
  # Grant permissions to a role
  python scripts/grant_abac_rebac_access.py grant-role abac_admin
  
  # Assign user to a role
  python scripts/grant_abac_rebac_access.py assign john_doe abac_admin
  
  # List all ABAC/ReBAC permissions
  python scripts/grant_abac_rebac_access.py list
  
  # Verify user permissions
  python scripts/grant_abac_rebac_access.py verify john_doe
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Grant user command
    grant_user_parser = subparsers.add_parser("grant-user", help="Grant permissions to a user")
    grant_user_parser.add_argument("username", help="Username to grant permissions to")
    
    # Grant role command
    grant_role_parser = subparsers.add_parser("grant-role", help="Grant permissions to a role")
    grant_role_parser.add_argument("role", help="Role name to grant permissions to")
    
    # Assign user to role command
    assign_parser = subparsers.add_parser("assign", help="Assign user to a role")
    assign_parser.add_argument("username", help="Username to assign")
    assign_parser.add_argument("role", help="Role name")
    
    # List command
    subparsers.add_parser("list", help="List all ABAC/ReBAC permissions")
    
    # Verify command
    verify_parser = subparsers.add_parser("verify", help="Verify user permissions")
    verify_parser.add_argument("username", help="Username to verify")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize Casbin enforcer
    await casbin_enforcer.initialize()
    
    try:
        if args.command == "grant-user":
            await grant_abac_rebac_permissions(username=args.username)
        
        elif args.command == "grant-role":
            await grant_abac_rebac_permissions(role=args.role)
        
        elif args.command == "assign":
            await assign_user_to_role(args.username, args.role)
        
        elif args.command == "list":
            await list_abac_rebac_permissions()
        
        elif args.command == "verify":
            await verify_user_permissions(args.username)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
