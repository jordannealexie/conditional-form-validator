from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Callable
from functools import wraps
from app.core.casbin_enforcer import casbin_enforcer
from app.services.abac_service import ABACService
from app.db.session import get_db
from app.core.security import decode_access_token

security = HTTPBearer()

class AuthorizationMiddleware:
    """Middleware for handling authorization checks"""
    
    @staticmethod
    async def verify_token(credentials: HTTPAuthorizationCredentials) -> dict:
        """Verify JWT token and extract user information"""
        try:
            token = credentials.credentials
            payload = decode_access_token(token)
            return payload
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    @staticmethod
    async def check_rbac_permission(user: dict, resource: str, action: str) -> bool:
        """Check RBAC permission for user"""
        username = user.get("sub")
        return casbin_enforcer.check_rbac_permission(username, resource, action)
    
    @staticmethod
    async def check_abac_permission(user: dict, resource: str, action: str) -> bool:
        """Check ABAC permission based on user attributes"""
        async for db in get_db():
            service = ABACService(db)
            # Minimal user object stub
            class SimpleUser:
                pass
            su = SimpleUser()
            su.id = user.get("user_id")
            su.department = user.get("department")
            su.active = user.get("account_status") != "inactive"
            su.roles = []
            return (await service.evaluate_policy(su, resource, action))[0]


def require_rbac_permission(resource: str, action: str):
    """Decorator to require RBAC permission"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request') or args[0]
            
            # Get authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header"
                )
            
            # Extract and verify token
            token = auth_header.split(' ')[1]
            try:
                payload = decode_access_token(token)
                username = payload.get("sub")
                
                # Check RBAC permission
                has_permission = casbin_enforcer.check_rbac_permission(
                    username, resource, action
                )
                
                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )
                
                # Add user info to request state
                request.state.user = payload
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_abac_permission(resource: str, action: str):
    """Decorator to require ABAC permission"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = kwargs.get('request') or args[0]
            
            # Get authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Missing or invalid authorization header"
                )
            
            # Extract and verify token
            token = auth_header.split(' ')[1]
            try:
                payload = decode_access_token(token)
                
                # Build attributes
                attributes = {
                    "department": payload.get("department"),
                    "level": payload.get("level"),
                    "location": payload.get("location"),
                }
                
                # Check ABAC permission
                has_permission = casbin_enforcer.check_abac_permission(
                    attributes, resource, action
                )
                
                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions based on attributes"
                    )
                
                # Add user info to request state
                request.state.user = payload
                
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

