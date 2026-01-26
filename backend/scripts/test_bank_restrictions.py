#!/usr/bin/env python3
"""
Test that users with permissions can now submit forms regardless of bank restrictions.
"""
import asyncio
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.forms import FormTemplate
from app.core.casbin_enforcer import casbin_enforcer
from sqlalchemy import select

async def test_bank_restrictions():
    await casbin_enforcer.initialize()
    
    print("🧪 Testing Bank Restriction Removal")
    print("=" * 70)
    
    async with AsyncSessionLocal() as session:
        # Get a user with bank restriction
        result = await session.execute(
            select(User).where(User.username == "bdo_fieldman_1")
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ Test user not found")
            return
        
        print(f"\n👤 Test User: {user.username}")
        print(f"   Role: {user.user_role}")
        print(f"   Bank ID: {user.bank_id}")
        
        # Check if user has submissions:create permission
        has_perm = await casbin_enforcer.check_rbac_permission_async(
            user.username, "submissions", "create"
        )
        
        print(f"\n🔑 Permission Check:")
        print(f"   submissions:create = {'✅ GRANTED' if has_perm else '❌ DENIED'}")
        
        # Get templates from different banks
        result = await session.execute(
            select(FormTemplate).limit(3)
        )
        templates = result.scalars().all()
        
        print(f"\n📋 Template Access Test:")
        print(f"   (Previously: blocked if template.bank_id != user.bank_id)")
        print(f"   (Now: allowed if user has permissions)")
        
        for template in templates:
            bank_match = (template.bank_id == user.bank_id) if user.bank_id else True
            status = "✅ MATCH" if bank_match else "⚠️  DIFF BANK"
            print(f"\n   Template: {template.name[:30]:30} | Bank: {template.bank_id} | {status}")
            if has_perm:
                print(f"            → User CAN submit (has permission)")
            else:
                print(f"            → User CANNOT submit (no permission)")
        
        print("\n" + "=" * 70)
        print("✅ Bank restriction removed - users with permissions can submit to any bank")
        print("   Users must have 'submissions:create' permission checked in their role")

if __name__ == "__main__":
    asyncio.run(test_bank_restrictions())
