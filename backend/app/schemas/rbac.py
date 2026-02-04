from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RoleAssignment(BaseModel):
    username: str
    role: str


class PermissionAssignment(BaseModel):
    role: str
    resource: str
    action: str


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


class PermissionResponse(BaseModel):
    id: int
    role_id: int
    resource: str
    action: str
    
    class Config:
        from_attributes = True


class RBACCheckRequest(BaseModel):
    """Schema for checking RBAC permission"""
    username: str
    resource: str
    action: str


class RBACCheckResponse(BaseModel):
    """Schema for RBAC permission check response"""
    username: str
    resource: str
    action: str
    has_permission: bool