from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password
from app.core.config import settings
from app.dependencies.services import get_user_service
from app.exceptions.http_exceptions import BadRequestError, UnauthorizedError
from app.schemas.auth import UserResponse
from app.models.user import User
from app.db.session import get_db
from app.services.user_service import UserService


from app.core.security import verify_password, decode_access_token


security_bearer = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login", auto_error=False)

async def get_current_user(
    bearer_token: Optional[str] = Depends(security_bearer),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the current authenticated user using JWT.
    """
    user = None
    
    # 1. Try JWT (Bearer)
    if bearer_token:
        # Handle case where user pasted "Bearer " + token into Swagger UI
        if bearer_token.startswith("Bearer "):
            bearer_token = bearer_token.replace("Bearer ", "").strip()
            
        try:
            payload = decode_access_token(bearer_token)
            username = payload.get("sub")
            if username:
                result = await db.execute(
                    select(User).options(selectinload(User.roles)).where(User.username == username)
                )
                user = result.scalar_one_or_none()
        except Exception:
            # Token invalid or expired
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    """
    Get the current active user from the token.
    """
    if not current_user.active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return current_user


async def get_current_superuser(current_user: User = Depends(get_current_active_user)):
    """
    Get the current superuser (admin).
    """
    if not current_user.is_superuser and current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: superuser privileges required"
        )
    
    return current_user


def authorize(resource: Optional[str] = None, action: Optional[str] = None, allowed_roles: Optional[List[str]] = None):
    """
    Dependency for unified access control (RBAC, ABAC, ReBAC).
    Resource and action are used for Casbin enforcement.
    allowed_roles is kept for backward compatibility and simpler role-based checks.
    """
    async def access_checker(current_user: User = Depends(get_current_active_user)):
        # 1. Superuser/Admin bypass
        if current_user.is_superuser or current_user.user_role == "admin":
            return current_user

        # 2. Casbin Unified Enforcement (if resource and action are provided)
        if resource and action:
            from app.core.casbin_enforcer import casbin_enforcer
            has_access = await casbin_enforcer.enforce_unified_async(current_user, resource, action)
            if has_access:
                return current_user

        # 3. Backward Compatibility: Role-based check
        if allowed_roles:
            if current_user.user_role in allowed_roles:
                return current_user
        
        # 4. If nothing grants access, return 403
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: you are not authorized to perform '{action}' on '{resource}'" if action and resource else "Access forbidden: insufficient permissions"
        )

    return access_checker