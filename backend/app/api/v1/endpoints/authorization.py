"""
Unified Authorization API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.authorization import (
    UnifiedAuthorizationRequest,
    UnifiedAuthorizationResponse
)
from app.services.authorization_service import AuthorizationService

router = APIRouter()


@router.post("/check", response_model=UnifiedAuthorizationResponse)
async def check_unified_authorization(
    check_request: UnifiedAuthorizationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check permission across RBAC and ABAC
    Returns detailed information about which models granted access
    """
    # Get the user to check
    result = await db.execute(
        select(User).where(User.username == check_request.username)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check permissions across all models
    service = AuthorizationService(db)
    has_permission, granted_by, results = await service.check_permission(
        user=user,
        resource=check_request.resource,
        action=check_request.action,
        resource_type=check_request.resource_type,
        resource_id=check_request.resource_id
    )
    
    return UnifiedAuthorizationResponse(
        username=check_request.username,
        resource=check_request.resource,
        action=check_request.action,
        has_permission=has_permission,
        granted_by=granted_by,
        results=results
    )


@router.get("/permissions")
async def get_user_permissions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all effective permissions for the current user.
    Uses RBAC roles and ABAC policies.
    """
    # For now, return a list of permissions based on RBAC roles
    # In a full implementation, this might query all Casbin policies
    # relevant to the user's roles and attributes.
    from app.core.casbin_enforcer import casbin_enforcer
    
    # Get roles from Casbin (which might be more up-to-date than the database field)
    roles = casbin_enforcer.get_roles_for_user(current_user.username)
    if not roles and current_user.user_role:
        roles = [current_user.user_role]
    
    # Get permissions for these roles
    permissions = []
    for role in roles:
        role_perms = casbin_enforcer.get_permissions_for_role(role)
        for perm in role_perms:
            # Casbin permissions are typically [role, resource, action]
            if len(perm) >= 3:
                permissions.append({
                    "resource": perm[1],
                    "action": perm[2]
                })
    
    return {
        "username": current_user.username,
        "roles": roles,
        "permissions": permissions,
        "is_admin": current_user.is_superuser or current_user.user_role == "admin",
        "attributes": {
            "department": current_user.department,
            "level": current_user.level,
            "location": current_user.location
        }
    }
