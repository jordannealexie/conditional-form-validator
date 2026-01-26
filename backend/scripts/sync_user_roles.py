"""
Script to sync all users' roles to Casbin.
This ensures that all users have their role mappings in Casbin.
"""
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.core.casbin_enforcer import casbin_enforcer
from app.db.session import AsyncSessionLocal
from app.models.user import User, Role
from sqlalchemy import select
from sqlalchemy.orm import selectinload

async def sync_all_user_roles():
    """Sync all users' roles to Casbin"""
    print("🚀 Starting user role synchronization to Casbin...")
    
    # Initialize Casbin
    await casbin_enforcer.initialize()
    
    async with AsyncSessionLocal() as session:
        # Get all users with their roles
        result = await session.execute(
            select(User).options(selectinload(User.roles))
        )
        users = result.scalars().all()
        
        print(f"📊 Found {len(users)} users to sync")
        
        synced_count = 0
        for user in users:
            if user.user_role:
                print(f"  Syncing user: {user.username} -> role: {user.user_role}")
                casbin_enforcer.sync_user_roles(user.username, [user.user_role])
                synced_count += 1
            else:
                print(f"  ⚠️ User {user.username} has no role assigned")
        
        print(f"\n✅ Successfully synced {synced_count} users to Casbin")
        
        # Verify sync by checking a few users
        print("\n🔍 Verifying sync (sampling a few users):")
        for user in users[:5]:  # Check first 5 users
            roles = casbin_enforcer.get_roles_for_user(user.username)
            print(f"  User {user.username}: Casbin roles = {roles}")

if __name__ == "__main__":
    asyncio.run(sync_all_user_roles())
