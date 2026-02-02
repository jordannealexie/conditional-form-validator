from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class AuditLogBase(BaseModel):
    """Base Audit Log Schema"""
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    status: Optional[str] = "success"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    # Allow any JSON-serializable structure (dict, list, str, etc.)
    payload: Optional[Any] = None
    details: Optional[Any] = None
    changes: Optional[Dict[str, Any]] = Field(None, description="Before and after values in JSON format")
    created_by: Optional[int] = Field(None, description="User ID who created this record")
    updated_by: Optional[int] = Field(None, description="User ID who updated this record")
    deleted_by: Optional[int] = Field(None, description="User ID who deleted this record")


class AuditLogCreate(AuditLogBase):
    """Schema for creating audit log"""
    pass


class AuditLogResponse(AuditLogBase):
    """Schema for audit log response"""
    id: int
    created_at: datetime

    class Config:
        """Pydantic configuration"""
        from_attributes = True
        orm_mode = True


class UserAuditTrailResponse(BaseModel):
    """Response schema for user audit trail"""
    total: int = Field(..., description="Total number of audit logs")
    logs: list[AuditLogResponse] = Field(..., description="List of audit logs")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
