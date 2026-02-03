from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.dependencies.audit import get_audit_service
from app.dependencies.auth import authorize
from app.services.audit import AuditService
from app.schemas.audit_trail import AuditLogResponse, UserAuditTrailResponse
from app.dtos.custom_response_dto import CustomResponse
from app.utils.response import create_response
from app.models.user import User

router = APIRouter()


@router.get(
    "/users",
    response_model=CustomResponse[list[AuditLogResponse]],
    summary="Get audit trail for all user entity logs",
    description="Get audit trail logs scoped strictly to user entities"
)
async def get_users_audit_trail(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    audit_service: AuditService = Depends(get_audit_service),
    current_user: User = Depends(authorize(resource="users", action="read"))
):
    logs = await audit_service.get_logs_by_resource_type("user", skip, limit)

    if not logs:
        return create_response(data=[])

    return create_response(
        data=[AuditLogResponse.model_validate(log) for log in logs]
    )


@router.get(
    "/users/{user_id}",
    response_model=CustomResponse[UserAuditTrailResponse],
    summary="Get audit trail for a user",
    description="Get audit trail logs for a specific user including all changes, creations, updates, and deletions"
)
async def get_user_audit_trail(
    user_id: int,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    audit_service: AuditService = Depends(get_audit_service),
    current_user: User = Depends(authorize(resource="users", action="read"))
):
    """
    Get audit trail for a specific user.
    
    Returns all audit logs related to the user including:
    - Created by and Created at
    - Updated by and Updated at
    - Deleted by and Deleted at
    - What was changed (before and after values in JSON format)
    """
    logs, total = await audit_service.get_user_audit_trail(user_id, skip, limit)
    
    if not logs:
        return create_response(
            data=UserAuditTrailResponse(total=0, logs=[])
        )
    
    return create_response(
        data=UserAuditTrailResponse(
            total=total,
            logs=[AuditLogResponse.model_validate(log) for log in logs]
        )
    )


@router.get(
    "/",
    response_model=CustomResponse[list[AuditLogResponse]],
    summary="Get all audit logs",
    description="Get all audit logs with pagination"
)
async def get_all_audit_logs(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    resource_type: Optional[str] = Query(None, description="Filter by resource type (e.g., user, role, template)"),
    audit_service: AuditService = Depends(get_audit_service),
    current_user: User = Depends(authorize(resource="users", action="read"))
):
    """Get all audit logs with pagination"""
    if resource_type:
        logs = await audit_service.get_logs_by_resource_type(resource_type.strip().lower(), skip, limit)
    else:
        logs = await audit_service.get_logs(skip, limit)
    
    if not logs:
        return create_response(data=[])
    
    return create_response(
        data=[AuditLogResponse.model_validate(log) for log in logs]
    )
