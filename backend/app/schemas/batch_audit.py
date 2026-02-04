"""Schemas for batch audit trail processing"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from enum import Enum


class BatchStatus(str, Enum):
    """Batch job status enumeration"""
    PENDING = "PENDING"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"


class AuditBatchItem(BaseModel):
    """Single audit log entry for batch processing"""
    action: str = Field(..., description="Action performed (created, updated, deleted)")
    entity_type: str = Field(..., description="Type of entity (user, role, form_template)")
    entity_id: int = Field(..., description="ID of the entity")
    actor_user_id: Optional[int] = Field(None, description="User ID who performed the action")
    actor_username: Optional[str] = Field(None, description="Username who performed the action")
    before_json: Optional[Dict[str, Any]] = Field(None, description="State before the change")
    after_json: Optional[Dict[str, Any]] = Field(None, description="State after the change")
    edited_fields: Optional[List[str]] = Field(None, description="List of fields that were changed")
    status: str = Field("success", description="Status of the action")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "action": "updated",
                "entity_type": "user",
                "entity_id": 123,
                "actor_user_id": 1,
                "actor_username": "admin",
                "before_json": {"email": "old@example.com"},
                "after_json": {"email": "new@example.com"},
                "edited_fields": ["email"],
                "status": "success"
            }
        }


class BatchAuditRequest(BaseModel):
    """Request schema for batch audit processing"""
    entries: List[AuditBatchItem] = Field(
        ..., 
        min_length=1,
        max_length=1000,
        description="List of audit entries to process in batch"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "entries": [
                    {
                        "action": "created",
                        "entity_type": "user",
                        "entity_id": 1,
                        "actor_user_id": 1,
                        "actor_username": "admin",
                        "after_json": {"username": "newuser", "email": "new@example.com"},
                        "status": "success"
                    },
                    {
                        "action": "updated",
                        "entity_type": "user",
                        "entity_id": 2,
                        "actor_user_id": 1,
                        "actor_username": "admin",
                        "before_json": {"email": "old@example.com"},
                        "after_json": {"email": "updated@example.com"},
                        "edited_fields": ["email"],
                        "status": "success"
                    }
                ]
            }
        }


class BatchAuditResponse(BaseModel):
    """Response schema for batch audit submission"""
    task_id: str = Field(..., description="Celery task ID for tracking the batch job")
    entries_count: int = Field(..., description="Number of entries submitted for processing")
    message: str = Field(..., description="Status message")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "task_id": "d1234f56-7890-1234-5678-abcdef012345",
                "entries_count": 100,
                "message": "Batch audit processing started"
            }
        }


class BatchTaskStatusResponse(BaseModel):
    """Response schema for batch task status"""
    task_id: str = Field(..., description="Celery task ID")
    status: BatchStatus = Field(..., description="Current status of the task")
    result: Optional[Dict[str, Any]] = Field(None, description="Task result if completed")
    error: Optional[str] = Field(None, description="Error message if failed")
    started_at: Optional[datetime] = Field(None, description="When the task started")
    completed_at: Optional[datetime] = Field(None, description="When the task completed")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "task_id": "d1234f56-7890-1234-5678-abcdef012345",
                "status": "SUCCESS",
                "result": {
                    "success": True,
                    "count": 100,
                    "message": "Successfully inserted 100 audit logs"
                },
                "error": None,
                "started_at": "2026-02-03T10:00:00Z",
                "completed_at": "2026-02-03T10:00:05Z"
            }
        }


class BatchDeleteRequest(BaseModel):
    """Request schema for batch audit log deletion"""
    entity_type: Optional[str] = Field(None, description="Delete logs for specific entity type")
    entity_ids: Optional[List[int]] = Field(None, description="Delete logs for specific entity IDs")
    older_than_days: Optional[int] = Field(
        None, 
        ge=1, 
        description="Delete logs older than specified days"
    )
    actor_user_id: Optional[int] = Field(None, description="Delete logs by specific actor")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "entity_type": "user",
                "older_than_days": 90
            }
        }


class BatchDeleteResponse(BaseModel):
    """Response schema for batch deletion"""
    task_id: str = Field(..., description="Celery task ID for tracking the deletion job")
    message: str = Field(..., description="Status message")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "task_id": "d1234f56-7890-1234-5678-abcdef012345",
                "message": "Batch deletion started"
            }
        }


class BatchExportRequest(BaseModel):
    """Request schema for batch audit log export"""
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    entity_id: Optional[int] = Field(None, description="Filter by entity ID")
    actor_user_id: Optional[int] = Field(None, description="Filter by actor user ID")
    from_date: Optional[datetime] = Field(None, description="Export logs from this date")
    to_date: Optional[datetime] = Field(None, description="Export logs until this date")
    format: str = Field("json", description="Export format (json, csv)")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "entity_type": "user",
                "from_date": "2026-01-01T00:00:00Z",
                "to_date": "2026-02-01T00:00:00Z",
                "format": "json"
            }
        }


class BatchExportResponse(BaseModel):
    """Response schema for batch export"""
    task_id: str = Field(..., description="Celery task ID for tracking the export job")
    message: str = Field(..., description="Status message")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "task_id": "d1234f56-7890-1234-5678-abcdef012345",
                "message": "Batch export started"
            }
        }


class BatchArchiveRequest(BaseModel):
    """Request schema for batch audit log archival"""
    older_than_days: int = Field(
        ..., 
        ge=30, 
        description="Archive logs older than specified days (minimum 30)"
    )
    entity_type: Optional[str] = Field(None, description="Archive logs for specific entity type")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "older_than_days": 90,
                "entity_type": "user"
            }
        }


class BatchArchiveResponse(BaseModel):
    """Response schema for batch archival"""
    task_id: str = Field(..., description="Celery task ID for tracking the archive job")
    message: str = Field(..., description="Status message")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "task_id": "d1234f56-7890-1234-5678-abcdef012345",
                "message": "Batch archive started for logs older than 90 days"
            }
        }


class BatchStatisticsResponse(BaseModel):
    """Response schema for batch processing statistics"""
    total_logs: int = Field(..., description="Total number of audit logs")
    logs_by_entity_type: Dict[str, int] = Field(..., description="Count by entity type")
    logs_by_action: Dict[str, int] = Field(..., description="Count by action type")
    logs_last_24h: int = Field(..., description="Logs created in last 24 hours")
    logs_last_7d: int = Field(..., description="Logs created in last 7 days")
    logs_last_30d: int = Field(..., description="Logs created in last 30 days")
    pending_tasks: int = Field(0, description="Number of pending batch tasks")

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "total_logs": 10000,
                "logs_by_entity_type": {"user": 5000, "role": 2000, "form_template": 3000},
                "logs_by_action": {"created": 4000, "updated": 5000, "deleted": 1000},
                "logs_last_24h": 150,
                "logs_last_7d": 1000,
                "logs_last_30d": 4000,
                "pending_tasks": 2
            }
        }

