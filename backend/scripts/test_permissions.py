#!/usr/bin/env python3
"""
Test script to verify that non-admin users can access templates and submit forms.
"""
import asyncio
import sys
from pathlib import Path

# Add project root to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.core.casbin_enforcer import casbin_enforcer
from app.db.session import AsyncSessionLocal
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def test_user_permissions():
    """Test that non-admin users have proper access"""
    print("🧪 Testing user permissions...")
    print("=" * 70)
    
    # Initialize Casbin
    await casbin_enforcer.initialize()
    
    async with AsyncSessionLocal() as session:
        # Test a supervisor user
        result = await session.execute(
            select(User).where(User.username == "bdo_supervisor_1")
        )
        supervisor = result.scalar_one_or_none()
        
        if not supervisor:
            print("❌ Supervisor test user not found")
            return
        
        print(f"\n👤 Testing User: {supervisor.username} (role: {supervisor.user_role})")
        print("-" * 70)
        
        # Test cases for supervisor
        supervisor_tests = [
            ("templates", "read", True, "View templates"),
            ("forms", "read", True, "View forms"),
            ("submissions", "read", True, "View submissions"),
            ("submissions", "review", True, "Review submissions"),
            ("submissions", "create", False, "Create submissions (should fail)"),
            ("users", "create", False, "Create users (should fail)"),
        ]
        
        print("\n📋 Supervisor Permission Tests:")
        for resource, action, expected, description in supervisor_tests:
            result = await casbin_enforcer.enforce_unified_async(
                supervisor, resource, action
            )
            status = "✅ PASS" if result == expected else "❌ FAIL"
            expected_str = "allowed" if expected else "denied"
            actual_str = "allowed" if result else "denied"
            print(f"  {status} {description:40} - Expected: {expected_str:7}, Got: {actual_str:7}")
        
        # Test a fieldman user
        result = await session.execute(
            select(User).where(User.username == "bdo_fieldman_1")
        )
        fieldman = result.scalar_one_or_none()
        
        if not fieldman:
            print("\n❌ Fieldman test user not found")
            return
        
        print(f"\n\n👤 Testing User: {fieldman.username} (role: {fieldman.user_role})")
        print("-" * 70)
        
        # Test cases for fieldman
        fieldman_tests = [
            ("templates", "read", True, "View templates"),
            ("forms", "read", True, "View forms"),
            ("submissions", "create", True, "Create submissions"),
            ("submissions", "read", True, "View submissions"),
            ("submissions", "update", True, "Update submissions"),
            ("submissions", "delete", True, "Delete submissions"),
            ("submissions", "review", False, "Review submissions (should fail)"),
            ("users", "read", False, "View users (should fail)"),
        ]
        
        print("\n📋 Fieldman Permission Tests:")
        for resource, action, expected, description in fieldman_tests:
            result = await casbin_enforcer.enforce_unified_async(
                fieldman, resource, action
            )
            status = "✅ PASS" if result == expected else "❌ FAIL"
            expected_str = "allowed" if expected else "denied"
            actual_str = "allowed" if result else "denied"
            print(f"  {status} {description:40} - Expected: {expected_str:7}, Got: {actual_str:7}")
        
        print("\n" + "=" * 70)
        print("✅ Permission testing complete!")

if __name__ == "__main__":
    asyncio.run(test_user_permissions())
