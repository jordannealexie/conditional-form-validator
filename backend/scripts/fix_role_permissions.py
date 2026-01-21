
import asyncio
import sys
import json
from pathlib import Path
from sqlalchemy import select

# Add project root to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.db.session import AsyncSessionLocal
from app.models.user import Role

async def fix_role_permissions():
    print("🚀 Starting role permissions fix...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Role))
        roles = result.scalars().all()
        
        fixed_count = 0
        for role in roles:
            perms = role.permissions
            if isinstance(perms, dict):
                print(f"🔧 Fixing role '{role.name}' with dict permissions: {perms}")
                new_perms = []
                for resource, actions in perms.items():
                    if isinstance(actions, list):
                        for action in actions:
                            new_perms.append(f"{resource}:{action}")
                    elif isinstance(actions, str):
                        new_perms.append(f"{resource}:{actions}")
                
                print(f"   -> Converted to: {new_perms}")
                role.permissions = new_perms
                fixed_count += 1
            elif perms is None:
                 role.permissions = []
        
        if fixed_count > 0:
            await session.commit()
            print(f"✅ Successfully fixed {fixed_count} roles.")
        else:
            print("✨ No roles needed fixing.")

if __name__ == "__main__":
    asyncio.run(fix_role_permissions())
