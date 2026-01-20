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




# Usage example:

# @router.get("/admin")
# async def read_admin_data(current_user: UserResponse = Depends(authorize(allowed_roles=["admin"]))):
#     return {"message": "Welcome, admin!"}
#

# @router.get("/user")
# async def read_user_data(current_user: UserResponse = Depends(authorize(allowed_roles=["user"]))):
#     return {"message": "Welcome, user!"}

#multiple roles
# @router.get("/admin_or_user")
# async def read_admin_or_user_data(current_user: UserResponse = Depends(authorize(allowed_roles=["admin", "user"]))):
#     return {"message": "Welcome, admin or user!"}

# @router.get("/any")
# async def read_any_data(current_user: UserResponse = Depends(authorize())):
#     return {"message": "Welcome, any authenticated user!"}

# This allows you to specify which roles are allowed to access certain endpoints.
# You can also create a route that is accessible to any authenticated user by not passing any roles to the authorize function.
def authorize(allowed_roles: Optional[List[str]] = None):
    """
    Dependency for role-based access control.
    If no roles are provided, any authenticated active user is allowed.
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if allowed_roles:
            # Check if current user has one of the allowed roles
            if not current_user.is_superuser and current_user.user_role not in allowed_roles and current_user.user_role != "admin":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access forbidden: insufficient role"
                )
            
        return current_user

    return role_checker