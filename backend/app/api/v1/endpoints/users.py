from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.dependencies.services import get_user_service
from app.dependencies.auth import get_current_active_user, authorize, get_current_superuser
from app.core.casbin_enforcer import casbin_enforcer
from app.models.user import User
from app.dtos.custom_response_dto import CustomResponse
from app.schemas.user import UserUpdate
from app.schemas.auth import UserResponse, UserCreate, UserAdminUpdate
from app.services.user_service import UserService
from app.utils.response import create_response
from app.dependencies.audit import get_audit_service
from app.services.audit import AuditService
from app.core.security import get_password_hash, verify_password
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

router = APIRouter()

@router.get(
    "/",
    response_model=CustomResponse[List[UserResponse]],
    summary="Get all users",
    description="Get a list of users"
)
async def get_users(
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> CustomResponse[List[UserResponse]]:
    users = await user_service.get_all_users()
    if not users:
        return create_response(data=None)
    return create_response(data=[UserResponse.model_validate(u) for u in users])

@router.get(
    "/by-email",
    response_model=CustomResponse[UserResponse],
    summary="Get user by email",
    description="Get a user by their email address"
)
async def get_user_by_email(
    email: str,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
) -> CustomResponse[UserResponse]:
    user = await user_service.get_by_email(email)
    if not user:
        return create_response(data=None)
    return create_response(data=UserResponse.model_validate(user))

@router.get(
    "/me",
    response_model=CustomResponse[UserResponse],
    summary="Get current user",
    description="Get current authenticated user"
)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> CustomResponse[UserResponse]:
    return create_response(data=UserResponse.model_validate(current_user))

@router.patch(
    "/me",
    response_model=CustomResponse[UserResponse],
    summary="Update current user profile"
)
async def update_user_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    audit: AuditService = Depends(get_audit_service)
) -> CustomResponse[UserResponse]:
    """Update current user profile"""
    upd = user_in.model_dump(exclude_unset=True) if hasattr(user_in, "model_dump") else user_in.dict(exclude_unset=True)
    if "is_active" in upd:
        upd["active"] = upd.pop("is_active")
    updated_user = await user_service.update(current_user.id, upd)
    await audit.log("update_profile", user_id=current_user.id, username=current_user.username, details="User updated their profile")
    return create_response(data=UserResponse.model_validate(updated_user))

@router.post(
    "/me/password",
    summary="Change current user password"
)
async def change_password_me(
    pwd_in: PasswordChangeRequest,
    current_user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service),
    audit: AuditService = Depends(get_audit_service)
):
    """Change current user password"""
    # Ensure we compare against the stored password hash
    if not current_user.password_hash:
        await audit.log("change_password", user_id=current_user.id, username=current_user.username, status="failure", details="Missing password hash on user")
        raise HTTPException(status_code=500, detail="Password data unavailable")

    if not verify_password(pwd_in.current_password, current_user.password_hash):
        await audit.log("change_password", user_id=current_user.id, username=current_user.username, status="failure", details="Incorrect current password")
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    await user_service.update(current_user.id, {"password": pwd_in.new_password})
    await audit.log("change_password", user_id=current_user.id, username=current_user.username, details="User changed their password")
    return create_response(message="Password updated successfully")

@router.get(
    "/me/activity",
    summary="Get current user activity logs"
)
async def get_user_activity(
    current_user: User = Depends(get_current_active_user),
    audit: AuditService = Depends(get_audit_service)
):
    """Get activity logs for the current user"""
    try:
        logs = await audit.repository.get_by_user(current_user.username)
        # Return proper format
        return {"data": logs}
    except Exception as e:
        # Return empty list on error instead of 500
        print(f"Error loading activity logs for {current_user.username}: {str(e)}")
        return {"data": []}

@router.post(
    "/",
    response_model=CustomResponse[UserResponse],
    summary="Create user (admin only)",
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    user_in: UserCreate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(authorize(allowed_roles=["admin"])),
    db: AsyncSession = Depends(get_db)
):
    """Create a new user. Admin only."""
    if await user_service.get_by_email(user_in.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    r = await db.execute(select(User).where(User.username == user_in.username))
    if r.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    user = await user_service.create_admin_user(user_in)
    return create_response(data=UserResponse.model_validate(user), status_code=status.HTTP_201_CREATED)


@router.get(
    "/{id}",
    response_model=CustomResponse[UserResponse],
    summary="Get user by ID",
    description="Get a user by their ID"
)
async def get_user_by_id(
    id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_active_user)
) -> CustomResponse[UserResponse]:
    user = await user_service.get(id)
    if not user:
        return create_response(data=None)
    return create_response(data=UserResponse.model_validate(user))


@router.put(
    "/{id}",
    response_model=CustomResponse[UserResponse],
    summary="Update user (admin only)"
)
async def update_user(
    id: int,
    user_in: UserAdminUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> CustomResponse[UserResponse]:
    """Edit user: email, role, bank, active. Admin only."""
    user = await user_service.get(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    upd = user_in.model_dump(exclude_unset=True)
    updated = await user_service.update(id, upd)
    return create_response(data=UserResponse.model_validate(updated))


@router.put(
    "/{id}/role",
    response_model=CustomResponse[UserResponse],
    summary="Change user role (admin only)"
)
async def update_user_role(
    id: int,
    body: Dict[str, str],
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> CustomResponse[UserResponse]:
    role = body.get("role") or body.get("user_role")
    if not role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="role is required")
    user = await user_service.get(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated = await user_service.update(id, {"user_role": role})
    return create_response(data=UserResponse.model_validate(updated))


@router.put(
    "/{id}/bank",
    response_model=CustomResponse[UserResponse],
    summary="Assign user to bank (admin only)"
)
async def update_user_bank(
    id: int,
    body: Dict[str, Optional[int]],
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(authorize(allowed_roles=["admin"]))
) -> CustomResponse[UserResponse]:
    bank_id = body.get("bank_id")
    user = await user_service.get(id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated = await user_service.update(id, {"bank_id": bank_id})
    return create_response(data=UserResponse.model_validate(updated))


@router.delete(
    "/{id}",
    summary="Delete user (admin only)",
    description="Delete a user account. Admin only."
)
async def delete_user(
    id: int,
    soft_delete: bool = Query(False, description="Perform soft delete (deactivate) instead of hard delete"),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(authorize(allowed_roles=["admin"])),
    db: AsyncSession = Depends(get_db)
):
    target_user = await user_service.get(id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if soft_delete:
        deleted_user = await user_service.deactivate_user(id)
        return create_response(data=UserResponse.model_validate(deleted_user), message="User deactivated successfully")
    else:
        # Hard delete - permanently remove from database
        username = target_user.username
        await db.delete(target_user)
        await db.commit()
        return create_response(data=None, message=f"User {username} permanently deleted")
