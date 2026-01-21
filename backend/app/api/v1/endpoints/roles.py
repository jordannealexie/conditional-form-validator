"""Roles API: GET /, POST /, DELETE /{id}, GET /{id}/permissions"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.dependencies.auth import authorize
from app.models.user import User, Role
from app.utils.response import create_response

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

    class Config:
        from_attributes = True


@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> Any:
    """List all roles with permissions. Admin only."""
    result = await db.execute(select(Role).order_by(Role.name))
    roles = result.scalars().all()
    return create_response(data=[RoleResponse.model_validate(r) for r in roles])


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    body: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> Any:
    """Create a new role. Admin only."""
    r = await db.execute(select(Role).where(Role.name == body.name))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already exists")
    role = Role(name=body.name, description=body.description, permissions=body.permissions or [])
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return create_response(data=RoleResponse.model_validate(role), status_code=status.HTTP_201_CREATED)


@router.delete("/{id}")
async def delete_role(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> Any:
    """Delete a role. Admin only. Fails if role is assigned to users."""
    result = await db.execute(select(Role).where(Role.id == id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    # Check if any user has this role
    count = await db.execute(select(func.count()).select_from(user_roles).where(user_roles.c.role_id == id))
    n = count.scalar() or 0
    if n > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role is assigned to {n} user(s). Remove assignments first.")
    await db.delete(role)
    await db.commit()
    return create_response(message="Role deleted")


@router.get("/{id}/permissions")
async def get_role_permissions(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> Any:
    """Get permissions for a role. Admin only."""
    result = await db.execute(select(Role).where(Role.id == id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    return create_response(data={"id": role.id, "name": role.name, "permissions": role.permissions or []})


@router.get("/{id}/user-count")
async def get_role_user_count(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> Any:
    """Get user count for a role. Admin only."""
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
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> Any:
    """Update a role. Admin only."""
    result = await db.execute(select(Role).where(Role.id == id))
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    # Check for duplicate name if changing
    if body.name != role.name:
        r = await db.execute(select(Role).where(Role.name == body.name))
        if r.scalar_one_or_none():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role name already exists")
    
    role.name = body.name
    role.description = body.description
    role.permissions = body.permissions or []
    
    await db.commit()
    await db.refresh(role)
    return create_response(data=RoleResponse.model_validate(role))
