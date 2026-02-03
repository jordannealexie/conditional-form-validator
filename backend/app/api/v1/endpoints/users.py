from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.dependencies.auth import get_current_active_user, authorize, get_current_superuser
from app.dependencies.services import get_user_service
from app.repositories.user import UserRepository
from app.repositories.audit import AuditRepository
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
    current_user: User = Depends(authorize(resource="users", action="read"))
):
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
    if "email" in upd and upd["email"] is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email cannot be null")
    if "is_active" in upd:
        upd["active"] = upd.pop("is_active")
    updated_user = await user_service.update(current_user.id, upd)
    await audit.log("update_profile", user_id=current_user.id, username=current_user.username, details="User updated their profile")
    await user_service.db.commit()
    await user_service.db.refresh(updated_user)
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
    current_user: User = Depends(authorize(resource="users", action="create")),
    db: AsyncSession = Depends(get_db),
    request: Request = None
):
    """Create a new user. Admin only."""
    try:
        # Use the same DB session for service and audit repository
        user_service = UserService(db, UserRepository(db))
        audit = AuditService(AuditRepository(db))

        # Validate input
        if not user_in.username or not user_in.username.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username is required"
            )
        if not user_in.email or not user_in.email.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )
        if not user_in.password or len(user_in.password) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters"
            )
        
        # Check for existing email
        if await user_service.get_by_email(user_in.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check for existing username
        r = await db.execute(select(User).where(User.username == user_in.username))
        if r.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create user
        user = await user_service.create_admin_user(user_in)

        # Capture user data immediately after creation
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_role": user.user_role,
            "department": user.department,
            "location": user.location,
            "level": user.level,
            "active": user.active,
            "role": user.user_role,
            "is_active": user.active,
            "roles": [user.user_role] if user.user_role else []
        }

        # Log user creation in audit trail (best-effort; don't block on failures)
        try:
            await audit.log_user_created(
                user_id=user_data["id"],
                username=user_data["username"],
                created_by_id=current_user.id,
                user_data=user_data,
                request=request
            )
        except Exception as audit_err:
            print(f"Audit logging failed for user create {user_data['id']}: {audit_err}")

        # Commit the transaction after both creation and audit logging
        await db.commit()

        return create_response(
            data=UserResponse.model_validate(user_data),
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log and return proper error
        print(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )


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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="users", action="update")),
    request: Request = None
) -> CustomResponse[UserResponse]:
    """Edit user: email, role, bank, active. Admin only."""
    try:
        stage = "init"
        # Use the same DB session for service and audit repository
        user_service = UserService(db, UserRepository(db))
        audit = AuditService(AuditRepository(db))

        # Get existing user
        stage = "get_user"
        user = await user_service.get(id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Immediately convert to dict to avoid lazy loading issues
        stage = "build_before_data"
        # Access all column attributes at once before any other async operations
        before_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "user_role": user.user_role,
            "department": user.department,
            "location": user.location,
            "level": user.level,
            "active": user.active,
            "bank_id": user.bank_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
        # Store username for audit log
        username_for_audit = before_data["username"]
        
        # Get update data
        stage = "prepare_update_data"
        upd = user_in.model_dump(exclude_unset=True)
        
        # Validate if there's anything to update
        if not upd:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        # Set audit field
        upd['updated_by'] = current_user.id
        
        # Capture after state - create from before_data + updates
        after_data = before_data.copy()
        after_data.update({k: v for k, v in upd.items() if k in before_data})
        
        # Update user
        stage = "update_user_service"
        updated = await user_service.update(id, upd)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        
        # Log update in audit trail (after update succeeds) - best-effort
        stage = "log_audit"
        try:
            await audit.log_user_updated(
                user_id=id,
                username=username_for_audit,
                updated_by_id=current_user.id,
                before_data=before_data,
                after_data=after_data,
                request=request
            )
        except Exception as audit_err:
            print(f"Audit logging failed for user update {id}: {audit_err}")
        
        # Commit the transaction after both update and audit logging
        stage = "commit"
        await db.commit()
        
        # Build response data from after_data to avoid accessing the model after commit
        stage = "build_response"
        response_data = {
            "id": id,
            "username": username_for_audit,
            "email": after_data.get('email'),
            "role": after_data.get('user_role'),
            "user_role": after_data.get('user_role'),
            "department": after_data.get('department'),
            "location": after_data.get('location'),
            "level": after_data.get('level'),
            "active": after_data.get('active'),
            "is_active": after_data.get('active'),
            "bank_id": after_data.get('bank_id'),
            "first_name": after_data.get('first_name'),
            "last_name": after_data.get('last_name'),
            "full_name": after_data.get('full_name'),
            "is_superuser": after_data.get('is_superuser', False),
            "created_at": after_data.get('created_at'),
            "updated_at": after_data.get('updated_at'),
            "roles": [after_data.get('user_role')] if after_data.get('user_role') else [],
            "updated_by": current_user.id
        }
        
        stage = "done"
        return create_response(data=UserResponse.model_validate(response_data))
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log and return proper error, including stage info to locate source
        import traceback
        print(f"Error updating user {id} at stage '{stage}': {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"[stage={stage}] Failed to update user: {str(e)}"
        )


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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="users", action="delete")),
    request: Request = None
):
    """
    Delete a user account.
    - Soft delete: Deactivates user, removes permissions.
    - Hard delete: Removes user from DB (if possible).
    """
    # 1. Prevent canceling self
    if current_user.id == id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="You cannot delete your own account."
        )

    # Use the same DB session for service and audit repository
    user_service = UserService(db, UserRepository(db))
    audit = AuditService(AuditRepository(db))

    target_user = await user_service.get(id)
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    # Immediately convert to dict to avoid lazy loading issues
    # Access all attributes at once before any other operations
    user_data = {
        "id": target_user.id,
        "username": target_user.username,
        "email": target_user.email,
        "user_role": target_user.user_role,
        "department": target_user.department,
        "location": target_user.location,
        "level": target_user.level,
        "active": target_user.active,
        "bank_id": target_user.bank_id,
        "first_name": target_user.first_name,
        "last_name": target_user.last_name,
        "full_name": target_user.full_name,
        "is_superuser": target_user.is_superuser,
        "created_at": target_user.created_at,
        "updated_at": target_user.updated_at,
        "roles": [target_user.user_role] if target_user.user_role else []
    }
    
    # Store username for audit
    username_for_audit = user_data["username"]
    
    # 2. Prevent deleting superuser or special users (optional logic, can be ABAC'd but good safety net)
    if user_data["is_superuser"]:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot delete a superuser."
        )

    if soft_delete:
        deleted_user = await user_service.deactivate_user(id)
        if not deleted_user:
             raise HTTPException(status_code=500, detail="Failed to deactivate user")
        
        # Log soft delete in audit trail (best-effort)
        try:
            await audit.log_user_deleted(
                user_id=id,
                username=username_for_audit,
                deleted_by_id=current_user.id,
                user_data=user_data,
                request=request
            )
        except Exception as audit_err:
            print(f"Audit logging failed for user soft delete {id}: {audit_err}")
        
        # Commit the transaction after both deactivation and audit logging
        await db.commit()
        
        # Build response from user_data (updated with active=False)
        response_data = user_data.copy()
        response_data["active"] = False
        response_data["is_active"] = False
        response_data["role"] = response_data.get("user_role")
        return create_response(data=UserResponse.model_validate(response_data), message="User deactivated successfully")
    else:
        # Hard delete uses the service logic with error checking
        result = await user_service.delete(id)
        
        if not result["success"]:
            # Return 400 for logic/integrity errors, avoiding 500s
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["error"]
            )
        
        # Log hard delete in audit trail (best-effort)
        try:
            await audit.log_user_deleted(
                user_id=id,
                username=username_for_audit,
                deleted_by_id=current_user.id,
                user_data=user_data,
                request=request
            )
        except Exception as audit_err:
            print(f"Audit logging failed for user hard delete {id}: {audit_err}")
        
        # Commit the transaction after both deletion and audit logging
        await db.commit()
            
        return create_response(data=None, message=f"User {username_for_audit} permanently deleted")
