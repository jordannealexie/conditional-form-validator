import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import AsyncSessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_admin():
    async with AsyncSessionLocal() as session:
        # Check if admin exists
        result = await session.execute(
            select(User).where(User.username == "admin")
        )
        existing = result.scalar_one_or_none()

        if not existing:
            admin = User(
                email="admin@example.com",
                username="admin",
                password_hash=get_password_hash("AdminPass123!"),
                first_name="System",
                last_name="Administrator",
                full_name="System Administrator",
                department="IT",
                level=5,
                location="Makati",
                user_role="admin",
                active=True
            )
            
            # Check for admin role
            result = await session.execute(select(Role).where(Role.name == "admin"))
            admin_role = result.scalar_one_or_none()
            if not admin_role:
                admin_role = Role(name="admin", description="Administrator")
                session.add(admin_role)
            
            admin.roles = [admin_role]
            
            session.add(admin)
            await session.commit()
            print("Admin user created")
        else:
            print("Admin user already exists")
            admin = existing
            
        # Ensure admin role functionality
        try:
            # Check for admin role
            result = await session.execute(select(Role).where(Role.name == "admin"))
            admin_role = result.scalar_one_or_none()
            if not admin_role:
                admin_role = Role(name="admin", description="Administrator")
                session.add(admin_role)
                await session.flush() # ensure id
            
            # Check if user has role
            # We need to load roles first if not loaded
            # But simpler to just reset if needed or check
            # Since User.roles is lazy, we can't easily check without loading
            # Let's just reset/ensure
            from sqlalchemy.orm import selectinload
            result = await session.execute(
                 select(User).options(selectinload(User.roles)).where(User.id == admin.id)
            )
            admin = result.scalar_one()
            
            has_role = any(r.name == "admin" for r in admin.roles)
            if not has_role:
                 print("Assigning admin role to existing user")
                 admin.roles.append(admin_role)
                 session.add(admin)
                 await session.commit()
                 
        except Exception as e:
            print(f"Error ensuring admin role: {e}")

if __name__ == "__main__":
    asyncio.run(create_admin())