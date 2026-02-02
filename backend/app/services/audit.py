from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Any, Dict, Tuple, List
from app.repositories.audit import AuditRepository
from fastapi import Request


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


class AuditService:
    def __init__(self, repository: AuditRepository):
        self.repository = repository

    async def log(
        self,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        status: str = "success",
        request: Optional[Request] = None,
        payload: Optional[Dict[str, Any]] = None,
        details: Optional[Any] = None,
        changes: Optional[Dict[str, Any]] = None,
        created_by: Optional[int] = None,
        updated_by: Optional[int] = None,
        deleted_by: Optional[int] = None
    ):
        """Record an audit log entry with JSON-safe payloads."""
        ip_address = None
        user_agent = None

        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        await self.repository.create(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent,
            payload=_to_jsonable(payload) if payload is not None else None,
            details=_to_jsonable(details) if details is not None else None,
            changes=_to_jsonable(changes) if changes is not None else None,
            created_by=created_by,
            updated_by=updated_by,
            deleted_by=deleted_by
        )

    async def log_user_created(
        self,
        user_id: int,
        username: str,
        created_by_id: int,
        user_data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log user creation with full user data"""
        changes = {
            "action": "created",
            "after": user_data
        }
        await self.log(
            action="user_created",
            user_id=user_id,
            username=username,
            resource_type="user",
            resource_id=str(user_id),
            status="success",
            request=request,
            changes=changes,
            created_by=created_by_id
        )

    async def log_user_updated(
        self,
        user_id: int,
        username: str,
        updated_by_id: int,
        before_data: Dict[str, Any],
        after_data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log user update with before and after values"""
        changes = {
            "action": "updated",
            "before": before_data,
            "after": after_data
        }
        await self.log(
            action="user_updated",
            user_id=user_id,
            username=username,
            resource_type="user",
            resource_id=str(user_id),
            status="success",
            request=request,
            changes=changes,
            updated_by=updated_by_id
        )

    async def log_user_deleted(
        self,
        user_id: int,
        username: str,
        deleted_by_id: int,
        user_data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log user deletion with final user data.

        For hard deletes we must not keep a strong FK from audit_logs.user_id
        to the deleted user record, otherwise the delete would violate the
        foreign key constraint. We instead record the logical user identifier
        in resource_id and username, and leave user_id as NULL.
        """
        changes = {
            "action": "deleted",
            "before": user_data
        }
        await self.log(
            action="user_deleted",
            user_id=None,
            username=username,
            resource_type="user",
            resource_id=str(user_id),
            status="success",
            request=request,
            changes=changes,
            deleted_by=deleted_by_id
        )

    async def get_logs(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_all(skip, limit)
    
    async def get_user_audit_trail(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List, int]:
        """
        Get audit trail for a specific user
        Returns tuple of (logs, total_count)
        """
        return await self.repository.get_by_resource(
            resource_type="user",
            resource_id=str(user_id),
            skip=skip,
            limit=limit
        )
