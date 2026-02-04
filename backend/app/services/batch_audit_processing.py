"""Service for batch audit processing operations"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from celery.result import AsyncResult
from sqlalchemy import select, func
from app.repositories.audit import AuditRepository
from app.tasks.audit_tasks import (
    bulk_create_audit_logs,
    batch_delete_audit_logs,
    batch_export_audit_logs,
    batch_archive_audit_logs,
    get_audit_statistics,
    process_audit_batch_with_validation,
)
from app.schemas.batch_audit import (
    AuditBatchItem,
    BatchStatus,
)
from app.core.celery_app import celery_app
from app.models.audit import AuditLog
import logging

logger = logging.getLogger(__name__)


class BatchAuditProcessingService:
    """Service for handling batch audit processing operations"""

    def __init__(self, repository: AuditRepository):
        """Initialize with audit repository"""
        self.repository = repository

    def _convert_batch_item_to_dict(self, item: AuditBatchItem) -> Dict[str, Any]:
        """Convert a batch item schema to dictionary format for task processing"""
        entry = {
            "action": item.action,
            "entity_type": item.entity_type.lower(),
            "entity_id": item.entity_id,
            "actor_user_id": item.actor_user_id,
            "actor_username": item.actor_username,
            "status": item.status,
            "ip_address": item.ip_address,
            "user_agent": item.user_agent,
        }
        
        if item.before_json:
            entry["before_json"] = item.before_json
        if item.after_json:
            entry["after_json"] = item.after_json
        if item.edited_fields:
            entry["edited_fields"] = item.edited_fields
            
        return entry

    async def submit_batch_audit(
        self,
        entries: List[AuditBatchItem],
        use_validation: bool = True
    ) -> Tuple[str, int]:
        """
        Submit a batch of audit entries for processing.
        
        Args:
            entries: List of AuditBatchItem to process
            use_validation: Whether to use the validation task
            
        Returns:
            Tuple of (task_id, entries_count)
        """
        # Convert entries to dict format
        entry_dicts = [self._convert_batch_item_to_dict(item) for item in entries]
        
        # Submit to Celery
        if use_validation:
            task = process_audit_batch_with_validation.delay(entry_dicts, validate_entities=False)
        else:
            task = bulk_create_audit_logs.delay(entry_dicts)
        
        logger.info(f"Submitted batch audit task {task.id} with {len(entries)} entries")
        
        return task.id, len(entries)

    async def submit_batch_delete(
        self,
        entity_type: Optional[str] = None,
        entity_ids: Optional[List[int]] = None,
        older_than_days: Optional[int] = None,
        actor_user_id: Optional[int] = None
    ) -> str:
        """
        Submit a batch delete request for processing.
        
        Args:
            entity_type: Delete logs for specific entity type
            entity_ids: Delete logs for specific entity IDs
            older_than_days: Delete logs older than specified days
            actor_user_id: Delete logs by specific actor
            
        Returns:
            Task ID
        """
        task = batch_delete_audit_logs.delay(
            entity_type=entity_type,
            entity_ids=entity_ids,
            older_than_days=older_than_days,
            actor_user_id=actor_user_id
        )
        
        logger.info(f"Submitted batch delete task {task.id}")
        
        return task.id

    async def submit_batch_export(
        self,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        actor_user_id: Optional[int] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        export_format: str = "json"
    ) -> str:
        """
        Submit a batch export request for processing.
        
        Args:
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            actor_user_id: Filter by actor user ID
            from_date: Export logs from this date
            to_date: Export logs until this date
            export_format: Export format (json or csv)
            
        Returns:
            Task ID
        """
        task = batch_export_audit_logs.delay(
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            from_date=from_date.isoformat() if from_date else None,
            to_date=to_date.isoformat() if to_date else None,
            export_format=export_format
        )
        
        logger.info(f"Submitted batch export task {task.id}")
        
        return task.id

    async def submit_batch_archive(
        self,
        older_than_days: int,
        entity_type: Optional[str] = None
    ) -> str:
        """
        Submit a batch archive request for processing.
        
        Args:
            older_than_days: Archive logs older than specified days
            entity_type: Optionally filter by entity type
            
        Returns:
            Task ID
        """
        task = batch_archive_audit_logs.delay(
            older_than_days=older_than_days,
            entity_type=entity_type
        )
        
        logger.info(f"Submitted batch archive task {task.id}")
        
        return task.id

    async def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get the status of a batch processing task.
        
        Args:
            task_id: The Celery task ID
            
        Returns:
            Dict containing task status information
        """
        task_result = AsyncResult(task_id, app=celery_app)
        
        status = task_result.status
        result = None
        error = None
        
        if status == "SUCCESS":
            result = task_result.result
        elif status == "FAILURE":
            error = str(task_result.result) if task_result.result else "Unknown error"
        
        # Get task info if available
        started_at = None
        completed_at = None
        
        if hasattr(task_result, 'date_done') and task_result.date_done:
            completed_at = task_result.date_done
        
        return {
            "task_id": task_id,
            "status": BatchStatus(status) if status in BatchStatus.__members__ else BatchStatus.PENDING,
            "result": result,
            "error": error,
            "started_at": started_at,
            "completed_at": completed_at,
        }

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get audit log statistics.
        
        Can be called synchronously (waits for result) or returns cached stats.
        
        Returns:
            Dict containing audit statistics
        """
        # Try Celery task first (fast path if worker is available)
        try:
            task = get_audit_statistics.delay()
            result = task.get(timeout=10)
            if result and result.get("success"):
                return result
        except Exception as e:
            logger.warning(f"Celery stats unavailable, falling back to DB: {str(e)}")

        # Fallback to direct DB aggregation to avoid timeouts
        return await self._get_statistics_from_db()

    async def _get_statistics_from_db(self) -> Dict[str, Any]:
        """Compute audit statistics directly from the database."""
        now = datetime.utcnow()

        total_query = select(func.count()).select_from(AuditLog)
        total_result = await self.repository.db.execute(total_query)
        total = total_result.scalar() or 0

        entity_query = select(
            AuditLog.resource_type,
            func.count().label("count")
        ).group_by(AuditLog.resource_type)
        entity_result = await self.repository.db.execute(entity_query)
        logs_by_entity = {row.resource_type or "unknown": row.count for row in entity_result}

        action_query = select(
            AuditLog.action,
            func.count().label("count")
        ).group_by(AuditLog.action)
        action_result = await self.repository.db.execute(action_query)
        logs_by_action = {row.action or "unknown": row.count for row in action_result}

        last_24h = now - timedelta(hours=24)
        count_24h_query = select(func.count()).select_from(AuditLog).where(
            AuditLog.created_at >= last_24h
        )
        count_24h_result = await self.repository.db.execute(count_24h_query)
        logs_last_24h = count_24h_result.scalar() or 0

        last_7d = now - timedelta(days=7)
        count_7d_query = select(func.count()).select_from(AuditLog).where(
            AuditLog.created_at >= last_7d
        )
        count_7d_result = await self.repository.db.execute(count_7d_query)
        logs_last_7d = count_7d_result.scalar() or 0

        last_30d = now - timedelta(days=30)
        count_30d_query = select(func.count()).select_from(AuditLog).where(
            AuditLog.created_at >= last_30d
        )
        count_30d_result = await self.repository.db.execute(count_30d_query)
        logs_last_30d = count_30d_result.scalar() or 0

        return {
            "success": True,
            "total_logs": total,
            "logs_by_entity_type": logs_by_entity,
            "logs_by_action": logs_by_action,
            "logs_last_24h": logs_last_24h,
            "logs_last_7d": logs_last_7d,
            "logs_last_30d": logs_last_30d,
            "generated_at": now.isoformat()
        }

    async def get_pending_tasks_count(self) -> int:
        """
        Get the count of pending batch processing tasks.
        
        Returns:
            Number of pending tasks
        """
        try:
            # Get celery inspect
            inspect = celery_app.control.inspect()
            
            # Get active and scheduled tasks
            active = inspect.active() or {}
            scheduled = inspect.scheduled() or {}
            reserved = inspect.reserved() or {}
            
            total_pending = 0
            for worker_tasks in [active.values(), scheduled.values(), reserved.values()]:
                for tasks in worker_tasks:
                    # Filter only audit-related tasks
                    audit_tasks = [t for t in tasks if 'audit' in t.get('name', '').lower()]
                    total_pending += len(audit_tasks)
            
            return total_pending
        except Exception as e:
            logger.error(f"Error getting pending tasks count: {str(e)}")
            return 0

    async def revoke_task(self, task_id: str, terminate: bool = False) -> bool:
        """
        Revoke a pending or running task.
        
        Args:
            task_id: The task ID to revoke
            terminate: If True, also terminate if currently executing
            
        Returns:
            True if revoke command was sent successfully
        """
        try:
            celery_app.control.revoke(task_id, terminate=terminate)
            logger.info(f"Revoked task {task_id} (terminate={terminate})")
            return True
        except Exception as e:
            logger.error(f"Error revoking task {task_id}: {str(e)}")
            return False

    async def get_task_result(self, task_id: str, timeout: int = 60) -> Dict[str, Any]:
        """
        Get the result of a completed task, waiting if necessary.
        
        Args:
            task_id: The task ID
            timeout: Maximum seconds to wait for result
            
        Returns:
            Task result or error information
        """
        task_result = AsyncResult(task_id, app=celery_app)
        
        try:
            if task_result.ready():
                return {
                    "success": True,
                    "status": task_result.status,
                    "result": task_result.result
                }
            
            # Wait for result
            result = task_result.get(timeout=timeout)
            return {
                "success": True,
                "status": "SUCCESS",
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "status": task_result.status,
                "error": str(e)
            }

