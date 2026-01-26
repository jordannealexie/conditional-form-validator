#!/usr/bin/env python3
"""
Quick script to check if a specific user has a permission.
Usage: python3 check_user_access.py <username> <resource> <action>
Example: python3 check_user_access.py fieldman1 submissions create
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

async def check_access(username: str, resource: str, action: str):
    """Check if user has access to resource/action"""
    await casbin_enforcer.initialize()
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ User '{username}' not found")
            return
        
        print(f"👤 User: {username}")
        print(f"🎭 Role: {user.user_role}")
        print(f"🔑 Checking: {resource}:{action}")
        print("-" * 50)
        
        # Check access
        has_access = await casbin_enforcer.enforce_unified_async(
            user, resource, action
        )
        
        if has_access:
            print(f"✅ GRANTED - User can {action} {resource}")
        else:
            print(f"❌ DENIED - User cannot {action} {resource}")
            
            # Show what roles they have
            roles = casbin_enforcer.get_roles_for_user(username)
            print(f"\n📋 User has roles: {roles}")
            
            # Show what permissions those roles have
            for role in roles:
                perms = casbin_enforcer.get_permissions_for_role(role)
                print(f"\n   Role '{role}' permissions:")
                for p in perms:
                    if len(p) >= 3:
                        print(f"     - {p[1]}:{p[2]}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 check_user_access.py <username> <resource> <action>")
        print("Example: python3 check_user_access.py fieldman1 submissions create")
        sys.exit(1)
    
    username = sys.argv[1]
    resource = sys.argv[2]
    action = sys.argv[3]
    
    asyncio.run(check_access(username, resource, action))
