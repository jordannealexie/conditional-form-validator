import asyncio
import sys
from pathlib import Path

# Add project root to path
backend_path = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_path))

from app.db.session import AsyncSessionLocal
from app.models.forms import Bank, FormTemplate, FormSubmission
from app.models.user import User, Role
from sqlalchemy import select

async def audit_data():
    async with AsyncSessionLocal() as session:
        # 1. Banks
        result = await session.execute(select(Bank))
        banks = result.scalars().all()
        print(f"--- Banks ({len(banks)}) ---")
        for b in banks:
            print(f"- {b.name} ({b.code})")
        
        # 2. Roles
        result = await session.execute(select(Role))
        roles = result.scalars().all()
        print(f"\n--- Roles ({len(roles)}) ---")
        for r in roles:
            print(f"- {r.name}")
        
        # 3. Users
        result = await session.execute(select(User))
        users = result.scalars().all()
        print(f"\n--- Users ({len(users)}) ---")
        for u in users:
            print(f"- {u.username} (Superuser: {u.is_superuser})")
            
        # 4. Templates
        result = await session.execute(select(FormTemplate))
        templates = result.scalars().all()
        print(f"\n--- Templates ({len(templates)}) ---")
        for t in templates:
            print(f"- {t.title} (Bank ID: {t.bank_id}, Version: {t.version})")

if __name__ == "__main__":
    asyncio.run(audit_data())
