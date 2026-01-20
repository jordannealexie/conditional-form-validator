"""
Simple database initialization script
Alternative simpler version that uses SQLAlchemy directly
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, insert
from app.core.config import settings
from app.db.base_class import Base
from app.models.user import User, Role, ResourceRelationship, user_roles
from app.core.security import get_password_hash
from app.core.casbin_enforcer import casbin_enforcer


async def init_db():
    """Initialize database with tables and seed data"""
    # Create engine
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    
    # Create tables
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables created")
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create roles
        print("Creating roles...")
        roles_to_create = [
            {"name": "admin", "description": "Administrator"},
            {"name": "manager", "description": "Manager"},
            {"name": "user", "description": "Regular User"},
            {"name": "moderator", "description": "Moderator"},
        ]
        
        for role_data in roles_to_create:
            result = await session.execute(
                select(Role).where(Role.name == role_data["name"])
            )
            if not result.scalar_one_or_none():
                role = Role(**role_data)
                session.add(role)
        
        await session.commit()
        print("✅ Roles created")
        
        # Create users
        print("Creating users...")
        users_to_create = [
            {
                "email": "admin@example.com",
                "username": "admin",
                "password": "Admin123!",
                "full_name": "Admin User",
                "active": True,
                "department": "IT",
                "level": 10,
                "location": "HQ",
                "role_names": ["admin"]
            },
            {
                "email": "manager@example.com",
                "username": "manager",
                "password": "Manager123!",
                "full_name": "Manager User",
                "active": True,
                "department": "Engineering",
                "level": 7,
                "location": "US",
                "role_names": ["manager"]
            },
            {
                "email": "user@example.com",
                "username": "user",
                "password": "User123!",
                "full_name": "Regular User",
                "active": True,
                "department": "Engineering",
                "level": 5,
                "location": "US",
                "role_names": ["user"]
            },
        ]
        
        for user_data in users_to_create:
            role_names = user_data.pop("role_names", [])
            password = user_data.pop("password")
            
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            if not result.scalar_one_or_none():
                user = User(
                    **user_data,
                    password_hash=get_password_hash(password)
                )
                session.add(user)
                await session.flush()
                
                # Assign roles
                if role_names:
                    result = await session.execute(
                        select(Role).where(Role.name.in_(role_names))
                    )
                    roles = result.scalars().all()
                    for role in roles:
                        await session.execute(insert(user_roles).values(user_id=user.id, role_id=role.id))
                    await session.flush()
                await session.commit()
        
        await session.commit()
        print("✅ Users created")
    
    # Initialize Casbin and create policies
    print("Initializing Casbin...")
    await casbin_enforcer.initialize()
    
    print("Creating Casbin policies...")
    # RBAC Policies
    policies = [
        # Admin permissions
        ("admin", "users", "read"),
        ("admin", "users", "write"),
        ("admin", "users", "delete"),
        ("admin", "roles", "read"),
        ("admin", "roles", "assign"),
        ("admin", "roles", "revoke"),
        ("admin", "permissions", "read"),
        ("admin", "permissions", "assign"),
        # Manager permissions
        ("manager", "users", "read"),
        ("manager", "users", "write"),
        ("manager", "roles", "read"),
        # User permissions
        ("user", "profile", "read"),
        ("user", "profile", "write"),
    ]
    
    for role, resource, action in policies:
        casbin_enforcer.add_permission_for_role(role, resource, action)
    
    # Assign roles to users
    casbin_enforcer.add_role_for_user("admin", "admin")
    casbin_enforcer.add_role_for_user("manager", "manager")
    casbin_enforcer.add_role_for_user("user", "user")
    
    await casbin_enforcer.save_policy()
    print("✅ Casbin policies created")
    
    await engine.dispose()
    
    print("\n" + "="*60)
    print("✅ Database initialization complete!")
    print("="*60)
    print("\n📋 Test Users:")
    print("  Admin:    admin@example.com / admin (Password: Admin123!)")
    print("  Manager:  manager@example.com / manager (Password: Manager123!)")
    print("  User:     user@example.com / user (Password: User123!)")
    print("\n💡 Use these credentials to test the API!")


if __name__ == "__main__":
    asyncio.run(init_db())
