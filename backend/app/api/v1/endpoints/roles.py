"""Roles API: GET /, POST /, DELETE /{id}, GET /{id}/permissions"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field
from datetime import datetime

from app.db.session import get_db
from app.dependencies.auth import authorize
from app.models.user import User, Role
from app.utils.response import create_response
from app.dependencies.audit import get_audit_service
from app.services.audit import AuditService

router = APIRouter()

# use existing user_roles table from models
from app.models.user import user_roles


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    permissions: Optional[List[str]] = Field(default_factory=list)


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = Field(None, description="User ID of creator")
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = Field(None, description="User ID of last updater")

    class Config:
        from_attributes = True


@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="roles", action="read"))
) -> Any:
    """List all roles with permissions. Enabled via rules."""
    result = await db.execute(select(Role).order_by(Role.name))
    roles = result.scalars().all()
    return create_response(data=[RoleResponse.model_validate(r) for r in roles])


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="roles", action="create")),
    request: Request = None,
    audit_service: AuditService = Depends(get_audit_service)
) -> Any:
    """Create a new role. Enabled via rules."""
    try:
        # Check for duplicate role name
        r = await db.execute(select(Role).where(Role.name == body.name))
        if r.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already exists")
        
        # Create role with proper audit fields
        role = Role(
            name=body.name,
            description=body.description,
            permissions=body.permissions or [],
            created_by=current_user.id,
            updated_by=current_user.id  # Set updated_by on creation
        )
        db.add(role)
        await db.commit()
        await db.refresh(role)
        
        # Sync to Casbin
        from app.core.casbin_enforcer import casbin_enforcer
        casbin_enforcer.sync_role_permissions(role.name, role.permissions or [])

        # Best-effort audit log for role creation
        try:
            await audit_service.log(
                action="role_created",
                user_id=current_user.id,
                username=role.name,
                resource_type="role",
                resource_id=str(role.id),
                status="success",
                request=request,
                changes={
                    "action": "created",
                    "after": {
                        "id": role.id,
                        "name": role.name,
                        "description": role.description,
                        "permissions": role.permissions or [],
                        "created_at": role.created_at,
                        "created_by": role.created_by,
                        "updated_at": role.updated_at,
                        "updated_by": role.updated_by,
                    },
                },
                created_by=current_user.id,
            )
            # Commit audit log entry
            await db.commit()
        except Exception as audit_err:
            # Do not fail the main request if audit logging fails
            print(f"Error logging role creation in audit trail: {audit_err}")

        return create_response(data=RoleResponse.model_validate(role), status_code=status.HTTP_201_CREATED)
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log and return proper error instead of 500
        await db.rollback()
        print(f"Error creating role: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create role: {str(e)}"
        )


@router.delete("/{id}")
async def delete_role(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="roles", action="delete")),
    request: Request = None,
    audit_service: AuditService = Depends(get_audit_service)
) -> Any:
    """Delete a role. Enabled via rules. Fails if role is assigned to users."""
    try:
        # Get role
        result = await db.execute(select(Role).where(Role.id == id))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
        # Snapshot role data before delete for audit trail
        role_data = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": role.permissions or [],
            "created_at": role.created_at,
            "created_by": role.created_by,
            "updated_at": role.updated_at,
            "updated_by": role.updated_by,
        }
        role_name = role.name
        
        # Check if any user has this role
        count = await db.execute(select(func.count()).select_from(user_roles).where(user_roles.c.role_id == id))
        n = count.scalar() or 0
        if n > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role is assigned to {n} user(s). Remove assignments first."
            )
        
        # Delete role
        await db.delete(role)
        await db.commit()
        
        # Remove from Casbin
        from app.core.casbin_enforcer import casbin_enforcer
        casbin_enforcer.rbac_enforcer.remove_filtered_policy(0, role_name)
        casbin_enforcer.rbac_enforcer.save_policy()

        # Best-effort audit log for role deletion
        try:
            await audit_service.log(
                action="role_deleted",
                user_id=current_user.id,
                username=role_name,
                resource_type="role",
                resource_id=str(id),
                status="success",
                request=request,
                changes={
                    "action": "deleted",
                    "before": role_data,
                },
                deleted_by=current_user.id,
            )
            await db.commit()
        except Exception as audit_err:
            print(f"Error logging role deletion in audit trail: {audit_err}")
        
        return create_response(message="Role deleted")
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log and return proper error
        await db.rollback()
        print(f"Error deleting role {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete role: {str(e)}"
        )


@router.get("/{id}/permissions")
async def get_role_permissions(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="roles", action="read"))
) -> Any:
    """Get permissions for a role. Enabled via rules."""
    result = await db.execute(select(Role).where(Role.id == id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return create_response(data={"id": role.id, "name": role.name, "permissions": role.permissions or []})


@router.get("/{id}/user-count")
async def get_role_user_count(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="roles", action="read"))
) -> Any:
    """Get user count for a role. Enabled via rules."""
    result = await db.execute(select(Role).where(Role.id == id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    count = await db.execute(select(func.count()).select_from(user_roles).where(user_roles.c.role_id == id))
    user_count = count.scalar() or 0
    return create_response(data={"role_id": id, "user_count": user_count})


@router.put("/{id}")
async def update_role(
    id: int,
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="roles", action="update")),
    request: Request = None,
    audit_service: AuditService = Depends(get_audit_service)
) -> Any:
    """Update a role. Enabled via rules."""
    try:
        # Validate input
        if not body.name or not body.name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Role name is required"
            )
        
        # Get existing role
        result = await db.execute(select(Role).where(Role.id == id))
        role = result.scalar_one_or_none()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        
        # Snapshot before update for audit trail
        before_data = {
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "permissions": role.permissions or [],
            "created_at": role.created_at,
            "created_by": role.created_by,
            "updated_at": role.updated_at,
            "updated_by": role.updated_by,
        }
        
        # Check for duplicate name if changing
        if body.name != role.name:
            r = await db.execute(select(Role).where(Role.name == body.name))
            if r.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already exists")
        
        # Update role fields
        role.name = body.name
        role.description = body.description
        role.permissions = body.permissions or []
        role.updated_by = current_user.id
        
        await db.commit()
        await db.refresh(role)
        
        # Sync to Casbin
        from app.core.casbin_enforcer import casbin_enforcer
        casbin_enforcer.sync_role_permissions(role.name, role.permissions or [])

        # Best-effort audit log for role update
        try:
            after_data = {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "permissions": role.permissions or [],
                "created_at": role.created_at,
                "created_by": role.created_by,
                "updated_at": role.updated_at,
                "updated_by": role.updated_by,
            }
            await audit_service.log(
                action="role_updated",
                user_id=current_user.id,
                username=role.name,
                resource_type="role",
                resource_id=str(role.id),
                status="success",
                request=request,
                changes={
                    "action": "updated",
                    "before": before_data,
                    "after": after_data,
                },
                updated_by=current_user.id,
            )
            await db.commit()
        except Exception as audit_err:
            print(f"Error logging role update in audit trail: {audit_err}")
        
        return create_response(data=RoleResponse.model_validate(role))
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log and return proper error
        await db.rollback()
        print(f"Error updating role {id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update role: {str(e)}"
        )
