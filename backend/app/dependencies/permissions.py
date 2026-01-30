"""
Dependencies for RBAC, ABAC, and ReBAC authorization
"""
from typing import Optional, List, Set
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.core.casbin_enforcer import casbin_enforcer
from app.db.session import get_db


# ============================================================================
# DATABASE-DRIVEN PERMISSION SYSTEM
# ============================================================================
# This system reads permissions directly from the database (roles.permissions JSON)
# and does NOT rely on Casbin policies or hardcoded superuser checks.
# 
# Permission format in database: ["resource:action", "policies:read", "relationships:create"]
# ============================================================================

async def get_user_permissions_from_db(user: User, db: AsyncSession) -> Set[str]:
    """
    Fetch all permissions for a user from database role assignments.
    
    This function:
    1. Queries all roles assigned to the user
    2. Extracts the permissions JSON from each role
    3. Returns a set of all unique permissions (e.g., {"policies:read", "relationships:write"})
    
    Args:
        user: The authenticated user
        db: Database session
        
    Returns:
        Set of permission strings (e.g., {"policies:read", "policies:write"})
    """
    try:
        # Fetch user with eagerly loaded roles
        stmt = select(User).where(User.id == user.id).options(selectinload(User.roles))
        result = await db.execute(stmt)
        user_with_roles = result.scalar_one_or_none()
        
        if not user_with_roles:
            return set()
        
        # Collect all permissions from all assigned roles
        all_permissions = set()
        for role in user_with_roles.roles:
            if role.permissions and isinstance(role.permissions, list):
                all_permissions.update(role.permissions)
        
        return all_permissions
    except Exception as e:
        print(f"❌ Error fetching user permissions from DB: {e}")
        import traceback
        traceback.print_exc()
        return set()


def require_permission(required_permission: str):
    """
    Database-driven permission dependency factory.
    
    Checks permissions stored in roles.permissions JSON column.
    Does NOT use Casbin or hardcoded superuser checks.
    
    Args:
        required_permission: Permission string in format "resource:action" 
                           (e.g., "policies:read", "relationships:create")
    
    Usage:
        @router.get("/abac/policies")
        async def list_policies(
            user: User = Depends(require_permission("policies:read"))
        ):
            ...
    
    Returns:
        Dependency function that validates permission and returns user
    """
    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        # Check if user is active
        if not current_user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Optional: Allow superusers to bypass (uncomment if needed)
        # if current_user.is_superuser:
        #     print(f"✅ Superuser bypass: {current_user.username} -> {required_permission}")
        #     return current_user
        
        # Fetch permissions from database
        user_permissions = await get_user_permissions_from_db(current_user, db)
        
        # Check if user has the required permission
        if required_permission not in user_permissions:
            print(f"❌ Permission denied: User '{current_user.username}' lacks '{required_permission}'")
            print(f"   User has: {sorted(user_permissions)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission: {required_permission}"
            )
        
        print(f"✅ Permission granted: {current_user.username} has '{required_permission}'")
        return current_user
    
    return check_permission


def require_any_permission(*required_permissions: str):
    """
    Database-driven permission dependency that allows access if user has ANY of the listed permissions.
    
    Args:
        *required_permissions: Variable number of permission strings
                              (e.g., "policies:read", "policies:write")
    
    Usage:
        @router.get("/abac/metadata")
        async def get_metadata(
            user: User = Depends(require_any_permission("policies:read", "policies:write"))
        ):
            ...
    """
    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
    ) -> User:
        if not current_user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Fetch permissions from database
        user_permissions = await get_user_permissions_from_db(current_user, db)
        
        # Check if user has any of the required permissions
        has_permission = any(perm in user_permissions for perm in required_permissions)
        
        if not has_permission:
            print(f"❌ Permission denied: User '{current_user.username}' lacks any of {required_permissions}")
            print(f"   User has: {sorted(user_permissions)}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required permission. Need one of: {', '.join(required_permissions)}"
            )
        
        print(f"✅ Permission granted: {current_user.username} has one of {required_permissions}")
        return current_user
    
    return check_permission


# ============================================================================
# LEGACY PERMISSION SYSTEM (Casbin-based)
# ============================================================================
# The functions below use Casbin and are kept for backward compatibility.
# For new code, use require_permission() or require_any_permission() instead.
# ============================================================================


def require_rbac(resource: str, action: str):
    """
    Dependency factory for RBAC permission checking.
    
    Usage:
        @router.get("/resource")
        async def get_resource(
            user: User = Depends(require_rbac("resource", "read"))
        ):
            ...
    """
    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Superuser bypass
        if current_user.is_superuser:
            return current_user
        
        # Check RBAC permission
        has_permission = await casbin_enforcer.check_rbac_permission_async(
            current_user.username,
            resource,
            action
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions: cannot {action} {resource}"
            )
        
        return current_user
    
    return check_permission


def require_abac(resource: str, action: str):
    """
    Dependency factory for ABAC permission checking.
    
    Usage:
        @router.get("/resource")
        async def get_resource(
            user: User = Depends(require_abac("resource", "read"))
        ):
            ...
    """
    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Superuser bypass
        if current_user.is_superuser:
            return current_user
        
        # Build attributes from user
        attributes = {
            "department": current_user.department or "",
            "level": current_user.level or 1,
            "location": current_user.location or "",
            "is_superuser": current_user.is_superuser
        }
        
        # Check ABAC permission
        has_permission = await casbin_enforcer.check_abac_permission_async(
            attributes,
            resource,
            action
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions based on attributes: cannot {action} {resource}"
            )
        
        return current_user
    
    return check_permission


def require_rebac(resource: str, action: str):
    """
    Dependency factory for ReBAC permission checking.
    
    Usage:
        @router.get("/resource/{resource_id}")
        async def get_resource(
            resource_id: str,
            user: User = Depends(require_rebac("resource", "read"))
        ):
            ...
    """
    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Superuser bypass
        if current_user.is_superuser:
            return current_user
        
        # Check ReBAC permission
        has_permission = await casbin_enforcer.check_rebac_permission_async(
            current_user.username,
            resource,
            action
        )
        
        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions based on relationships: cannot {action} {resource}"
            )
        
        return current_user
    
    return check_permission


def require_superuser(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require superuser privileges.
    
    Usage:
        @router.delete("/admin/resource")
        async def delete_resource(
            user: User = Depends(require_superuser)
        ):
            ...
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Superuser privileges required"
        )
    
    return current_user


def require_admin_or_permission(resource: str, action: str):
    """
    Dependency factory for admin-level operations that also checks explicit permissions.
    Allows both superusers AND users with specific RBAC/ABAC permissions.
    
    Usage:
        @router.get("/abac/policies")
        async def list_policies(
            user: User = Depends(require_admin_or_permission("abac", "read"))
        ):
            ...
    """
    async def check_permission(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user"
            )
        
        # Superuser bypass
        if current_user.is_superuser:
            print(f"✅ Superuser access granted for {current_user.username} on {resource}:{action}")
            return current_user
        
        # Check RBAC permission through Casbin
        try:
            # Check if enforcer is initialized
            if not casbin_enforcer.rbac_enforcer:
                print(f"⚠️ RBAC enforcer not initialized - granting access to superusers only")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Permission system is initializing. Please try again in a moment."
                )
            
            has_permission = await casbin_enforcer.check_rbac_permission_async(
                current_user.username,
                resource,
                action
            )
            
            if not has_permission:
                print(f"❌ Permission denied: User '{current_user.username}' lacks permission '{action}' on resource '{resource}'")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions: requires superuser or explicit permission to {action} {resource}"
                )
            
            print(f"✅ Permission granted: User '{current_user.username}' has permission '{action}' on resource '{resource}'")
        except HTTPException:
            # Re-raise HTTP exceptions as-is
            raise
        except Exception as e:
            # If permission check fails due to system error, log and deny
            print(f"⚠️ Error checking permission for {current_user.username} on {resource}:{action} - {e}")
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Permission check failed: {str(e)}"
            )
        
        return current_user
    
    return check_permission
