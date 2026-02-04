"""Batch audit processing endpoints for bulk operations"""

from typing import Optional
from fastapi import APIRouter, Depends, Query, status, HTTPException

from app.dependencies.audit import get_batch_audit_processing_service
from app.dependencies.auth import authorize
from app.services.batch_audit_processing import BatchAuditProcessingService
from app.schemas.batch_audit import (
    BatchAuditRequest,
    BatchAuditResponse,
    BatchTaskStatusResponse,
    BatchDeleteRequest,
    BatchDeleteResponse,
    BatchExportRequest,
    BatchExportResponse,
    BatchArchiveRequest,
    BatchArchiveResponse,
    BatchStatisticsResponse,
    BatchStatus,
)
from app.dtos.custom_response_dto import CustomResponse
from app.utils.response import create_response
from app.models.user import User

router = APIRouter()


@router.post(
    "/process-batch",
    response_model=CustomResponse[BatchAuditResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit batch audit entries for processing",
    description="Submit multiple audit log entries for asynchronous bulk processing via Celery"
)
async def process_batch_audit(
    batch_request: BatchAuditRequest,
    batch_service: BatchAuditProcessingService = Depends(get_batch_audit_processing_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="create"))
):
    """
    Submit a batch of audit log entries for asynchronous processing.
    
    This endpoint:
    - Accepts up to 1000 audit entries per request
    - Processes entries asynchronously using Celery
    - Returns a task ID for tracking the batch job status
    
    Example payload:
    ```json
    {
        "entries": [
            {
                "action": "created",
                "entity_type": "user",
                "entity_id": 1,
                "actor_user_id": 1,
                "actor_username": "admin",
                "after_json": {"username": "newuser"},
                "status": "success"
            }
        ]
    }
    ```
    """
    task_id, entries_count = await batch_service.submit_batch_audit(
        entries=batch_request.entries,
        use_validation=True
    )
    
    return create_response(
        data=BatchAuditResponse(
            task_id=task_id,
            entries_count=entries_count,
            message=f"Batch audit processing started with {entries_count} entries"
        ),
        status_code=status.HTTP_202_ACCEPTED
    )


@router.get(
    "/task-status/{task_id}",
    response_model=CustomResponse[BatchTaskStatusResponse],
    summary="Get batch task status",
    description="Check the status of a batch processing task"
)
async def get_task_status(
    task_id: str,
    batch_service: BatchAuditProcessingService = Depends(get_batch_audit_processing_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="read"))
):
    """
    Get the current status of a batch processing task.
    
    Status values:
    - PENDING: Task is waiting to be processed
    - STARTED: Task has started processing
    - SUCCESS: Task completed successfully
    - FAILURE: Task failed
    - RETRY: Task is being retried
    - REVOKED: Task was cancelled
    """
    status_info = await batch_service.get_task_status(task_id)
    
    return create_response(
        data=BatchTaskStatusResponse(
            task_id=status_info["task_id"],
            status=status_info["status"],
            result=status_info.get("result"),
            error=status_info.get("error"),
            started_at=status_info.get("started_at"),
            completed_at=status_info.get("completed_at")
        )
    )


@router.get(
    "/task-result/{task_id}",
    response_model=CustomResponse,
    summary="Get batch task result",
    description="Get the result of a completed batch task, optionally waiting for completion"
)
async def get_task_result(
    task_id: str,
    timeout: int = Query(30, ge=1, le=120, description="Seconds to wait for result"),
    batch_service: BatchAuditProcessingService = Depends(get_batch_audit_processing_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="read"))
):
    """
    Get the result of a batch processing task.
    
    If the task is not yet complete, this endpoint will wait up to the specified
    timeout (default 30 seconds) for the task to finish.
    """
    result = await batch_service.get_task_result(task_id, timeout=timeout)
    
    if not result.get("success"):
        return create_response(
            success=False,
            data=result,
            message=result.get("error", "Task failed or timed out")
        )
    
    return create_response(data=result)


@router.post(
    "/batch-delete",
    response_model=CustomResponse[BatchDeleteResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit batch delete request",
    description="Delete audit logs in bulk based on specified criteria"
)
async def batch_delete_audit_logs(
    delete_request: BatchDeleteRequest,
    batch_service: BatchAuditProcessingService = Depends(get_batch_audit_processing_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="delete"))
):
    """
    Submit a batch delete request for audit logs.
    
    At least one filter criteria must be provided:
    - entity_type: Delete logs for specific entity type
    - entity_ids: Delete logs for specific entity IDs
    - older_than_days: Delete logs older than specified days
    - actor_user_id: Delete logs by specific actor
    
    **Warning**: This operation is irreversible. Use with caution.
    """
    # Validate that at least one filter is provided
    if not any([
        delete_request.entity_type,
        delete_request.entity_ids,
        delete_request.older_than_days,
        delete_request.actor_user_id
    ]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one filter criteria must be provided"
        )
    
    task_id = await batch_service.submit_batch_delete(
        entity_type=delete_request.entity_type,
        entity_ids=delete_request.entity_ids,
        older_than_days=delete_request.older_than_days,
        actor_user_id=delete_request.actor_user_id
    )
    
    return create_response(
        data=BatchDeleteResponse(
            task_id=task_id,
            message="Batch deletion started"
        ),
        status_code=status.HTTP_202_ACCEPTED
    )


@router.post(
    "/batch-export",
    response_model=CustomResponse[BatchExportResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit batch export request",
    description="Export audit logs in bulk to JSON or CSV format"
)
async def batch_export_audit_logs(
    export_request: BatchExportRequest,
    batch_service: BatchAuditProcessingService = Depends(get_batch_audit_processing_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="read"))
):
    """
    Submit a batch export request for audit logs.
    
    Filters (all optional):
    - entity_type: Filter by entity type
    - entity_id: Filter by specific entity ID
    - actor_user_id: Filter by user who performed actions
    - from_date: Export logs from this date
    - to_date: Export logs until this date
    
    Export formats:
    - json (default): Returns data as JSON array
    - csv: Returns data as CSV string
    
    Use GET /task-result/{task_id} to retrieve the exported data.
    """
    task_id = await batch_service.submit_batch_export(
        entity_type=export_request.entity_type,
        entity_id=export_request.entity_id,
        actor_user_id=export_request.actor_user_id,
        from_date=export_request.from_date,
        to_date=export_request.to_date,
        export_format=export_request.format
    )
    
    return create_response(
        data=BatchExportResponse(
            task_id=task_id,
            message=f"Batch export started (format: {export_request.format})"
        ),
        status_code=status.HTTP_202_ACCEPTED
    )


@router.post(
    "/batch-archive",
    response_model=CustomResponse[BatchArchiveResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit batch archive request",
    description="Archive and remove old audit logs"
)
async def batch_archive_audit_logs(
    archive_request: BatchArchiveRequest,
    batch_service: BatchAuditProcessingService = Depends(get_batch_audit_processing_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="delete"))
):
    """
    Submit a batch archive request for audit logs.
    
    This operation:
    1. Exports matching logs to JSON format
    2. Deletes the exported logs from the database
    3. Returns the archived data in the task result
    
    Parameters:
    - older_than_days: Archive logs older than this (minimum 30 days)
    - entity_type: Optionally filter by entity type
    
    Use GET /task-result/{task_id} to retrieve the archived data.
    """
    task_id = await batch_service.submit_batch_archive(
        older_than_days=archive_request.older_than_days,
        entity_type=archive_request.entity_type
    )
    
    return create_response(
        data=BatchArchiveResponse(
            task_id=task_id,
            message=f"Batch archive started for logs older than {archive_request.older_than_days} days"
        ),
        status_code=status.HTTP_202_ACCEPTED
    )


@router.get(
    "/statistics",
    response_model=CustomResponse[BatchStatisticsResponse],
    summary="Get audit log statistics",
    description="Get statistics about audit logs including counts by type and time periods"
)
async def get_audit_statistics(
    batch_service: BatchAuditProcessingService = Depends(get_batch_audit_processing_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="read"))
):
    """
    Get comprehensive statistics about audit logs.
    
    Returns:
    - Total number of audit logs
    - Count by entity type
    - Count by action type
    - Logs created in last 24 hours, 7 days, 30 days
    - Number of pending batch tasks
    """
    stats = await batch_service.get_statistics()
    
    if not stats.get("success"):
        return create_response(
            success=False,
            data=None,
            message=stats.get("error", "Failed to retrieve statistics")
        )
    
    pending_tasks = await batch_service.get_pending_tasks_count()
    
    return create_response(
        data=BatchStatisticsResponse(
            total_logs=stats.get("total_logs", 0),
            logs_by_entity_type=stats.get("logs_by_entity_type", {}),
            logs_by_action=stats.get("logs_by_action", {}),
            logs_last_24h=stats.get("logs_last_24h", 0),
            logs_last_7d=stats.get("logs_last_7d", 0),
            logs_last_30d=stats.get("logs_last_30d", 0),
            pending_tasks=pending_tasks
        )
    )


@router.post(
    "/revoke-task/{task_id}",
    response_model=CustomResponse,
    summary="Revoke a batch task",
    description="Cancel a pending or running batch processing task"
)
async def revoke_batch_task(
    task_id: str,
    terminate: bool = Query(False, description="Terminate if currently executing"),
    batch_service: BatchAuditProcessingService = Depends(get_batch_audit_processing_service),
    current_user: User = Depends(authorize(resource="audit_logs", action="delete"))
):
    """
    Revoke (cancel) a batch processing task.
    
    Parameters:
    - task_id: The task ID to revoke
    - terminate: If True, also terminate if the task is currently executing
    
    Note: Revoked tasks cannot be restarted. You'll need to submit a new batch request.
    """
    success = await batch_service.revoke_task(task_id, terminate=terminate)
    
    if success:
        return create_response(
            data={"task_id": task_id, "revoked": True},
            message=f"Task {task_id} has been revoked"
        )
    
    return create_response(
        success=False,
        data={"task_id": task_id, "revoked": False},
        message="Failed to revoke task"
    )

