"""Bulk Audit Service for efficient audit log collection and persistence"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any, Dict, List, Tuple
from fastapi import Request
from app.repositories.audit import AuditRepository
from app.tasks.audit_tasks import bulk_create_audit_logs
from app.core.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


def _to_jsonable(value: Any) -> Any:
    """Recursively convert values to JSON-serializable forms."""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {k: _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_to_jsonable(v) for v in value]
    return value


class BulkAuditCollector:
    """
    Context manager for collecting audit entries in memory for bulk insertion.
    
    Usage:
        async with BulkAuditCollector() as collector:
            collector.add_entry(...)
            collector.add_entry(...)
            # On __aexit__, all entries are dispatched to Celery for bulk insert
    """
    
    def __init__(self, async_mode: bool = True):
        """
        Initialize the collector.
        
        Args:
            async_mode: If True, dispatch to Celery. If False, insert directly (for testing)
        """
        self.entries: List[Dict[str, Any]] = []
        self.async_mode = async_mode
        self._repository: Optional[AuditRepository] = None
    
    def set_repository(self, repository: AuditRepository):
        """Set repository for synchronous mode"""
        self._repository = repository
    
    def add_entry(
        self,
        action: str,
        entity_type: str,
        entity_id: int,
        actor_user_id: Optional[int] = None,
        actor_username: Optional[str] = None,
        target_username: Optional[str] = None,
        before_json: Optional[Dict[str, Any]] = None,
        after_json: Optional[Dict[str, Any]] = None,
        edited_fields: Optional[List[str]] = None,
        status: str = "success",
        request: Optional[Request] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """
        Add an audit entry to the collection.
        
        Args:
            action: Action performed (created, updated, deleted)
            entity_type: Type of entity (user, role, form_template, etc.)
            entity_id: ID of the entity
            actor_user_id: User ID who performed the action
            actor_username: Username who performed the action
            before_json: State before the change (for updates/deletes)
            after_json: State after the change (for creates/updates)
            edited_fields: List of fields that were changed
            status: Status of the action (success, failure)
            request: FastAPI Request object for extracting IP and user agent
            ip_address: Override IP address
            user_agent: Override user agent
        """
        # Extract request details if provided
        if request and not ip_address:
            ip_address = request.client.host if request.client else None
        if request and not user_agent:
            user_agent = request.headers.get("user-agent")
        
        # Build changes dict
        changes = {}
        if before_json is not None:
            changes["before"] = _to_jsonable(before_json)
        if after_json is not None:
            changes["after"] = _to_jsonable(after_json)
        if edited_fields:
            changes["edited_fields"] = edited_fields
        
        entry = {
            "action": action,
            "resource_type": entity_type.lower(),
            "resource_id": str(entity_id),
            "user_id": actor_user_id,
            "username": target_username or actor_username,
            "status": status,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "changes": changes if changes else None,
            "created_by": None,
            "updated_by": None,
            "deleted_by": None,
        }

        action_lower = action.lower()
        if "created" in action_lower:
            entry["created_by"] = actor_user_id
        elif "updated" in action_lower:
            entry["updated_by"] = actor_user_id
        elif "deleted" in action_lower:
            entry["deleted_by"] = actor_user_id
        
        self.entries.append(entry)
        logger.debug(f"Added audit entry: {action} on {entity_type}:{entity_id}")
    
    async def __aenter__(self):
        """Enter context manager"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager and persist entries"""
        if exc_type is not None:
            # Exception occurred, don't persist
            logger.warning(f"Exception in audit collector context: {exc_type.__name__}")
            return False
        
        if not self.entries:
            logger.debug("No audit entries to persist")
            return False
        
        try:
            if self.async_mode:
                # Dispatch to Celery for async processing
                logger.info(f"Dispatching {len(self.entries)} audit entries to Celery")
                bulk_create_audit_logs.delay(self.entries)
            else:
                # Synchronous mode for testing
                if self._repository:
                    logger.info(f"Bulk inserting {len(self.entries)} audit entries directly")
                    await self._repository.bulk_create(self.entries)
                else:
                    logger.error("No repository set for synchronous bulk insert")
        except Exception as e:
            logger.error(f"Error persisting audit entries: {str(e)}", exc_info=True)
            # Don't raise - audit failure shouldn't break business logic
        
        return False


class BulkAuditService:
    """Service for bulk audit operations"""
    
    def __init__(self, repository: AuditRepository):
        self.repository = repository

    def _has_active_workers(self) -> bool:
        """Check if any Celery workers are available."""
        try:
            inspector = celery_app.control.inspect(timeout=0.5)
            ping = inspector.ping() or {}
            return bool(ping)
        except Exception as exc:
            logger.warning(f"Celery worker check failed: {exc}")
            return False
    
    def create_collector(self, async_mode: Optional[bool] = None) -> BulkAuditCollector:
        """
        Create a new bulk audit collector.
        
        Args:
            async_mode: If True, use Celery. If False, insert directly. If None, auto-detect.
            
        Returns:
            BulkAuditCollector instance
        """
        if async_mode is None:
            async_mode = self._has_active_workers()
        elif async_mode and not self._has_active_workers():
            logger.warning("No Celery workers detected. Falling back to synchronous bulk insert.")
            async_mode = False

        collector = BulkAuditCollector(async_mode=async_mode)
        if not async_mode:
            collector.set_repository(self.repository)
        return collector
    
    async def get_logs_by_entity(
        self,
        entity_type: str,
        entity_id: Optional[int] = None,
        actor_user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List, int]:
        """
        Get audit logs filtered by entity type and optionally by entity ID.
        
        Args:
            entity_type: Type of entity (user, role, form_template, etc.)
            entity_id: Optional ID for row-specific logs
            actor_user_id: Optional user ID who performed actions
            skip: Pagination offset
            limit: Maximum number of records
            
        Returns:
            Tuple of (logs, total_count)
        """
        return await self.repository.get_by_entity_type_and_id(
            entity_type=entity_type,
            entity_id=entity_id,
            actor_user_id=actor_user_id,
            skip=skip,
            limit=limit
        )
    
    async def get_logs_by_page(
        self,
        entity_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List, int]:
        """
        Get all audit logs for a specific page (entity type).
        
        Args:
            entity_type: Type of entity (user, role, form_template, etc.)
            skip: Pagination offset
            limit: Maximum number of records
            
        Returns:
            Tuple of (logs, total_count)
        """
        return await self.repository.get_by_entity_type_and_id(
            entity_type=entity_type,
            entity_id=None,
            skip=skip,
            limit=limit
        )
    
    async def get_logs_by_row(
        self,
        entity_type: str,
        entity_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List, int]:
        """
        Get audit logs for a specific row (entity instance).
        
        Args:
            entity_type: Type of entity (user, role, form_template, etc.)
            entity_id: ID of the specific entity instance
            skip: Pagination offset
            limit: Maximum number of records
            
        Returns:
            Tuple of (logs, total_count)
        """
        return await self.repository.get_by_entity_type_and_id(
            entity_type=entity_type,
            entity_id=entity_id,
            skip=skip,
            limit=limit
        )
