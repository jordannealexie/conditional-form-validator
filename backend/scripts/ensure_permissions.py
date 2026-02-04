
import asyncio
import sys
import os
from pathlib import Path

# Add project root to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.core.casbin_enforcer import casbin_enforcer
from app.db.session import AsyncSessionLocal
from app.models.user import Role
from sqlalchemy import select

async def ensure_permissions():
    print("🚀 Ensuring default permissions are set...")
    
    # Initialize Casbin (using fallback sync method if async fails inside class, but we call it properly)
    await casbin_enforcer.initialize()
    
    # Define standard permissions
    # Format: resource:action
    admin_permissions = [
        # Users
        "users:create",
        "users:read", 
        "users:update",
        "users:delete",
        
        # Forms / Templates
        "templates:create",
        "templates:read",
        "templates:update",
        "templates:delete",
        # Use 'forms' alias if frontend uses it, but backend mostly uses 'templates' as resource name.
        # Frontend utils.js used 'templates' for resource.
        "forms:create",
        "forms:read",
        "forms:update",
        "forms:delete",
        
        # Submissions
        "submissions:create",
        "submissions:read",
        "submissions:viewDetails",
        "submissions:update",
        "submissions:delete",
        "submissions:review",
        
        # Roles
        "roles:create",
        "roles:read",
        "roles:update",
        "roles:delete",
        
        # ABAC Policies
        "policies:create",
        "policies:read",
        "policies:update",
        "policies:delete",
        
    ]
    
    supervisor_permissions = [
        "users:read",
        "templates:read",
        "forms:read",
        "submissions:read",
        "submissions:viewDetails",
        "submissions:review",
        "applications:access",
        "applications:apply",
        "applications:submit"
    ]
    
    fieldman_permissions = [
        "templates:read",
        "forms:read",
        "submissions:create",
        "submissions:read",
        "submissions:update", # own only, enforced by backend logic too
        "submissions:delete",  # own only
        "submissions:viewDetails",  # view own submission details
        "applications:access",  # can open/view fill form page
        "applications:apply",   # can click Apply Now
        "applications:submit"   # can submit completed forms
    ]
    
    async with AsyncSessionLocal() as session:
        # 1. Update Admin Role
        result = await session.execute(select(Role).where(Role.name == "admin"))
        admin_role = result.scalar_one_or_none()
        
        if not admin_role:
            print("⚠️ Admin role not found in DB. Creating...")
            admin_role = Role(name="admin", description="Administrator", permissions=admin_permissions)
            session.add(admin_role)
        else:
            print("✅ Admin role found. Updating permissions...")
            admin_role.permissions = admin_permissions
            
        # 2. Update Supervisor Role
        result = await session.execute(select(Role).where(Role.name == "supervisor"))
        supervisor_role = result.scalar_one_or_none()
        if not supervisor_role:
             supervisor_role = Role(name="supervisor", description="Supervisor", permissions=supervisor_permissions)
             session.add(supervisor_role)
        else:
             supervisor_role.permissions = supervisor_permissions

        # 3. Update Fieldman Role
        result = await session.execute(select(Role).where(Role.name == "fieldman"))
        fieldman_role = result.scalar_one_or_none()
        if not fieldman_role:
             fieldman_role = Role(name="fieldman", description="Fieldman", permissions=fieldman_permissions)
             session.add(fieldman_role)
        else:
             fieldman_role.permissions = fieldman_permissions
        
        # Also check for "user" role (legacy)
        result = await session.execute(select(Role).where(Role.name == "user"))
        user_role = result.scalar_one_or_none()
        if not user_role:
             user_role = Role(name="user", description="Regular User", permissions=fieldman_permissions)
             session.add(user_role)
        else:
             user_role.permissions = fieldman_permissions
             
        await session.commit()
        
        # Sync to Casbin
        print("🔄 Syncing to Casbin...")
        casbin_enforcer.sync_role_permissions("admin", admin_permissions)
        casbin_enforcer.sync_role_permissions("supervisor", supervisor_permissions)
        casbin_enforcer.sync_role_permissions("fieldman", fieldman_permissions)
        casbin_enforcer.sync_role_permissions("user", fieldman_permissions)  # Legacy role
        
        print("✅ Permissions enforced successfully.")

if __name__ == "__main__":
    asyncio.run(ensure_permissions())
