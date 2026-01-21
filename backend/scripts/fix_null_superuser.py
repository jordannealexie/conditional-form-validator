
import asyncio
import os
import sys

# Add backend directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select, update
from app.db.session import AsyncSessionLocal
from app.models.user import User

async def fix_null_superuser():
    print("🚀 Starting fix for NULL is_superuser values...")
    async with AsyncSessionLocal() as db:
        # Find users with NULL is_superuser
        stmt = select(User).where(User.is_superuser == None)
        result = await db.execute(stmt)
        users = result.scalars().all()
        
        print(f"Found {len(users)} users with NULL is_superuser")
        
        if not users:
            print("✅ No users to fix.")
            return

        # Update all to False first
        await db.execute(
            update(User)
            .where(User.is_superuser == None)
            .values(is_superuser=False)
        )
        
        # Update admin to True
        await db.execute(
            update(User)
            .where(User.username == "admin")
            .values(is_superuser=True)
        )
        
        await db.commit()
        print(f"✅ Successfully updated {len(users)} users.")
        print("✅ Admin user set to is_superuser=True")

if __name__ == "__main__":
    asyncio.run(fix_null_superuser())
