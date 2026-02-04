from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.dependencies.audit import get_audit_service, get_bulk_audit_service
from app.dependencies.auth import authorize
from app.services.audit import AuditService
from app.services.bulk_audit import BulkAuditService
from app.schemas.audit_trail import (
    AuditLogResponse, 
    AuditLogDetailResponse,
    AuditTrailPageResponse,
    UserAuditTrailResponse
)
from app.dtos.custom_response_dto import CustomResponse
from app.utils.response import create_response
from app.models.user import User

router = APIRouter()


def _convert_to_detail_response(log, reference_id: Optional[str] = None) -> AuditLogDetailResponse:
    """Convert AuditLog model to AuditLogDetailResponse"""
    changes = log.changes or {}
    before_json = changes.get("before")
    after_json = changes.get("after")
    edited_fields = changes.get("edited_fields", [])
    
    # Calculate number of fields changed
    num_fields = len(edited_fields) if edited_fields else 0
    if not num_fields and before_json and after_json:
        # Calculate from before/after diff if edited_fields not provided
        changed_keys = [k for k in set(before_json.keys()) | set(after_json.keys()) 
                       if before_json.get(k) != after_json.get(k)]
        num_fields = len(changed_keys)
    
    # Generate detailed activity description
    # Format: "entity_type > action (field1, field2, field3)"
    entity_display = log.resource_type.replace("_", " ").title()
    action_display = log.action.replace("_", " ").title()
    
    if edited_fields and len(edited_fields) > 0:
        # Show edited fields in the activity
        fields_display = ", ".join([f.replace("_", " ").title() for f in edited_fields[:5]])
        if len(edited_fields) > 5:
            fields_display += f", +{len(edited_fields) - 5} more"
        activity = f"{entity_display} > {action_display} ({fields_display})"
    else:
        activity = f"{entity_display} > {action_display}"
    
    return AuditLogDetailResponse(
        id=log.id,
        action=log.action,
        activity=activity,
        operator=log.username or "System",
        operator_id=log.user_id,
        time=log.created_at,
        num_fields_changed=num_fields,
        before_json=before_json,
        after_json=after_json,
        edited_fields=edited_fields,
        entity_type=log.resource_type,
        entity_id=log.resource_id or "",
        reference_id=reference_id
    )


@router.get(
    "/page/{entity_type}",
    response_model=CustomResponse[AuditTrailPageResponse],
    summary="Get audit trail for a specific page (entity type)",
    description="Get all audit logs scoped to a specific entity type (page). Logs are ordered by created_at DESC before pagination."
)
async def get_page_audit_trail(
    entity_type: str,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=1000, description="Number of items per page"),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="read"))
):
    """
    Get audit trail for a specific page (entity type).
    
    Examples:
    - /page/user - All user-related audit logs
    - /page/role - All role-related audit logs
    - /page/form_template - All form template-related audit logs
    
    Logs are ordered by created_at DESC before pagination.
    """
    skip = (page - 1) * page_size
    logs, total = await bulk_audit_service.get_logs_by_page(
        entity_type=entity_type,
        skip=skip,
        limit=page_size
    )
    
    detail_logs = [_convert_to_detail_response(log) for log in logs]
    
    # Calculate showing range
    showing_from = skip + 1 if total > 0 else 0
    showing_to = min(skip + page_size, total)
    
    # Generate title
    entity_display = entity_type.replace("_", " ").title()
    title = f"Activity Log - Complete audit trail for {entity_display}"
    
    return create_response(
        data=AuditTrailPageResponse(
            title=title,
            reference_id=None,
            total=total,
            page=page,
            page_size=page_size,
            showing_from=showing_from,
            showing_to=showing_to,
            logs=detail_logs
        )
    )


@router.get(
    "/row/{entity_type}/{entity_id}",
    response_model=CustomResponse[AuditTrailPageResponse],
    summary="Get audit trail for a specific row (entity instance)",
    description="Get audit logs for a specific entity instance. Shows only logs for this specific row."
)
async def get_row_audit_trail(
    entity_type: str,
    entity_id: int,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=1000, description="Number of items per page"),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="read"))
):
    """
    Get audit trail for a specific row (entity instance).
    
    Examples:
    - /row/user/123 - All audit logs for user with ID 123
    - /row/role/5 - All audit logs for role with ID 5
    """
    skip = (page - 1) * page_size
    
    logs, total = await bulk_audit_service.get_logs_by_row(
        entity_type=entity_type,
        entity_id=entity_id,
        skip=skip,
        limit=page_size
    )
    
    # Generate reference ID for this specific entity
    reference_id = f"{entity_type.upper()}{entity_id}"
    
    detail_logs = [_convert_to_detail_response(log, reference_id) for log in logs]
    
    # Calculate showing range
    showing_from = skip + 1 if total > 0 else 0
    showing_to = min(skip + page_size, total)
    
    # Generate title
    entity_display = entity_type.replace("_", " ").title()
    title = f"Activity Log - Complete audit trail for {reference_id}"
    
    return create_response(
        data=AuditTrailPageResponse(
            title=title,
            reference_id=reference_id,
            total=total,
            page=page,
            page_size=page_size,
            showing_from=showing_from,
            showing_to=showing_to,
            logs=detail_logs
        )
    )


@router.get(
    "/entity/{entity_type}",
    response_model=CustomResponse[AuditTrailPageResponse],
    summary="Get audit logs by entity type with optional filters",
    description="Get audit logs filtered by entity type, with optional entity_id and actor_user_id filters"
)
async def get_entity_audit_logs(
    entity_type: str,
    entity_id: Optional[int] = Query(None, description="Filter by specific entity ID"),
    actor_user_id: Optional[int] = Query(None, description="Filter by user who performed the action"),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=1000, description="Number of items per page"),
    bulk_audit_service: BulkAuditService = Depends(get_bulk_audit_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="read"))
):
    """
    Get audit logs with flexible filtering.
    
    Supports:
    - Filtering by entity_type (required)
    - Filtering by entity_id (optional)
    - Filtering by actor_user_id (optional)
    - Pagination with page and page_size
    """
    skip = (page - 1) * page_size
    
    logs, total = await bulk_audit_service.get_logs_by_entity(
        entity_type=entity_type,
        entity_id=entity_id,
        actor_user_id=actor_user_id,
        skip=skip,
        limit=page_size
    )
    
    # Generate reference ID if entity_id is provided
    reference_id = f"{entity_type.upper()}{entity_id}" if entity_id else None
    
    detail_logs = [_convert_to_detail_response(log, reference_id) for log in logs]
    
    # Calculate showing range
    showing_from = skip + 1 if total > 0 else 0
    showing_to = min(skip + page_size, total)
    
    # Generate title
    entity_display = entity_type.replace("_", " ").title()
    if reference_id:
        title = f"Activity Log - Complete audit trail for {reference_id}"
    else:
        title = f"Activity Log - Complete audit trail for {entity_display}"
    
    return create_response(
        data=AuditTrailPageResponse(
            title=title,
            reference_id=reference_id,
            total=total,
            page=page,
            page_size=page_size,
            showing_from=showing_from,
            showing_to=showing_to,
            logs=detail_logs
        )
    )


# Legacy endpoints (kept for backward compatibility)
@router.get(
    "/users",
    response_model=CustomResponse[list[AuditLogResponse]],
    summary="Get audit trail for all user entity logs (Legacy)",
    description="Get audit trail logs scoped strictly to user entities. Use /page/user instead."
)
async def get_users_audit_trail(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    audit_service: AuditService = Depends(get_audit_service),
    current_user: User = Depends(authorize(resource="users", action="read"))
):
    logs = await audit_service.get_logs_by_resource_type("user", skip, limit)
    logs = [log for log in logs if (log.action or "").lower() != "update_profile"]

    if not logs:
        return create_response(data=[])

    return create_response(
        data=[AuditLogResponse.model_validate(log) for log in logs]
    )


@router.get(
    "/users/{user_id}",
    response_model=CustomResponse[UserAuditTrailResponse],
    summary="Get audit trail for a user (Legacy)",
    description="Get audit trail logs for a specific user. Use /row/user/{user_id} instead."
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
    summary="Get all audit logs (Legacy)",
    description="Get all audit logs with pagination. Use /entity/{entity_type} for filtered results."
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
