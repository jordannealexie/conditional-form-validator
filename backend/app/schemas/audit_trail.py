from datetime import datetime
from typing import Optional, Dict, Any, List
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


class AuditLogDetailResponse(BaseModel):
    """Detailed audit log response with field-level information"""
    id: int
    action: str
    activity: str = Field(..., description="Human-readable activity description")
    operator: Optional[str] = Field(None, description="Username of who performed the action")
    operator_id: Optional[int] = Field(None, description="User ID of operator")
    time: datetime = Field(..., description="When the action occurred")
    no_of_fields: int = Field(0, description="Number of fields that were changed", alias="num_fields_changed")
    before_json: Optional[Dict[str, Any]] = Field(None, description="State before change")
    after_json: Optional[Dict[str, Any]] = Field(None, description="State after change")
    edited_fields: Optional[List[str]] = Field(None, description="List of fields that were edited")
    entity_type: str = Field(..., description="Type of entity")
    entity_id: str = Field(..., description="ID of the entity")
    reference_id: Optional[str] = Field(None, description="Reference ID for the audit trail")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
        populate_by_name = True


class AuditTrailPageResponse(BaseModel):
    """Response for audit trail page view"""
    title: str = Field(..., description="Title of the audit trail")
    reference_id: Optional[str] = Field(None, description="Reference ID for this audit trail")
    total: int = Field(..., description="Total number of audit logs")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    showing_from: int = Field(..., description="Showing from entry number")
    showing_to: int = Field(..., description="Showing to entry number")
    logs: List[AuditLogDetailResponse] = Field(..., description="List of audit logs")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True


class UserAuditTrailResponse(BaseModel):
    """Response schema for user audit trail"""
    total: int = Field(..., description="Total number of audit logs")
    logs: list[AuditLogResponse] = Field(..., description="List of audit logs")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
