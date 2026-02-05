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

        normalized_resource_type = (resource_type or "system").strip().lower()
        normalized_resource_id = str(resource_id) if resource_id is not None else None

        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")

        await self.repository.create(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=normalized_resource_type,
            resource_id=normalized_resource_id,
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
        created_by_username: str,
        created_by_role: str,
        user_data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log user creation with full user data"""
        changes = {
            "action": "created",
            "after": user_data
        }
        details = {
            "performed_by": {
                "user_id": created_by_id,
                "username": created_by_username,
                "role": created_by_role
            },
            "user_username": username
        }
        await self.log(
            action="user_created",
            user_id=created_by_id,
            username=created_by_username,
            resource_type="user",
            resource_id=str(user_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            created_by=created_by_id
        )

    async def log_user_updated(
        self,
        user_id: int,
        username: str,
        updated_by_id: int,
        updated_by_username: str,
        updated_by_role: str,
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
        details = {
            "performed_by": {
                "user_id": updated_by_id,
                "username": updated_by_username,
                "role": updated_by_role
            },
            "user_username": username
        }
        await self.log(
            action="user_updated",
            user_id=updated_by_id,
            username=updated_by_username,
            resource_type="user",
            resource_id=str(user_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            updated_by=updated_by_id
        )

    async def log_user_deleted(
        self,
        user_id: int,
        username: str,
        deleted_by_id: int,
        deleted_by_username: str,
        deleted_by_role: str,
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
        details = {
            "performed_by": {
                "user_id": deleted_by_id,
                "username": deleted_by_username,
                "role": deleted_by_role
            },
            "user_username": username
        }
        await self.log(
            action="user_deleted",
            user_id=None,
            username=deleted_by_username,
            resource_type="user",
            resource_id=str(user_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            deleted_by=deleted_by_id
        )

    async def get_logs(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_all(skip, limit)

    async def get_logs_by_resource_type(
        self,
        resource_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List:
        return await self.repository.get_by_resource_type(
            resource_type=resource_type,
            skip=skip,
            limit=limit
        )
    
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

    # ABAC Policy Audit Methods
    async def log_abac_policy_created(
        self,
        policy_id: int,
        policy_name: str,
        created_by_id: int,
        created_by_username: str,
        created_by_role: str,
        policy_data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log ABAC policy creation with full policy data"""
        changes = {
            "action": "created",
            "after": policy_data
        }
        details = {
            "performed_by": {
                "user_id": created_by_id,
                "username": created_by_username,
                "role": created_by_role
            },
            "policy_name": policy_name
        }
        await self.log(
            action="abac_policy_created",
            user_id=created_by_id,
            username=created_by_username,
            resource_type="abac_policy",
            resource_id=str(policy_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            created_by=created_by_id
        )

    async def log_abac_policy_updated(
        self,
        policy_id: int,
        policy_name: str,
        updated_by_id: int,
        updated_by_username: str,
        updated_by_role: str,
        before_data: Dict[str, Any],
        after_data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log ABAC policy update with before and after values"""
        changes = {
            "action": "updated",
            "before": before_data,
            "after": after_data
        }
        details = {
            "performed_by": {
                "user_id": updated_by_id,
                "username": updated_by_username,
                "role": updated_by_role
            },
            "policy_name": policy_name
        }
        await self.log(
            action="abac_policy_updated",
            user_id=updated_by_id,
            username=updated_by_username,
            resource_type="abac_policy",
            resource_id=str(policy_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            updated_by=updated_by_id
        )

    async def log_abac_policy_deleted(
        self,
        policy_id: int,
        policy_name: str,
        deleted_by_id: int,
        deleted_by_username: str,
        deleted_by_role: str,
        policy_data: Dict[str, Any],
        request: Optional[Request] = None
    ):
        """Log ABAC policy deletion with final policy state"""
        changes = {
            "action": "deleted",
            "before": policy_data
        }
        details = {
            "performed_by": {
                "user_id": deleted_by_id,
                "username": deleted_by_username,
                "role": deleted_by_role
            },
            "policy_name": policy_name
        }
        await self.log(
            action="abac_policy_deleted",
            user_id=deleted_by_id,
            username=deleted_by_username,
            resource_type="abac_policy",
            resource_id=str(policy_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            deleted_by=deleted_by_id
        )

    # User Attribute Audit Methods
    async def log_user_attribute_set(
        self,
        attribute_id: int,
        target_user_id: int,
        attribute_key: str,
        performed_by_id: int,
        performed_by_username: str,
        performed_by_role: str,
        before_value: Optional[str],
        after_value: str,
        request: Optional[Request] = None
    ):
        """Log user attribute creation/update"""
        action_type = "updated" if before_value is not None else "created"
        changes = {
            "action": action_type,
            "attribute_key": attribute_key,
            "before": {"value": before_value} if before_value else None,
            "after": {"value": after_value}
        }
        details = {
            "performed_by": {
                "user_id": performed_by_id,
                "username": performed_by_username,
                "role": performed_by_role
            },
            "target_user_id": target_user_id,
            "attribute_key": attribute_key
        }
        await self.log(
            action=f"user_attribute_{action_type}",
            user_id=performed_by_id,
            username=performed_by_username,
            resource_type="user_attribute",
            resource_id=str(attribute_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            created_by=performed_by_id if action_type == "created" else None,
            updated_by=performed_by_id if action_type == "updated" else None
        )

    async def log_user_attribute_deleted(
        self,
        attribute_id: int,
        target_user_id: int,
        attribute_key: str,
        attribute_value: str,
        deleted_by_id: int,
        deleted_by_username: str,
        deleted_by_role: str,
        request: Optional[Request] = None
    ):
        """Log user attribute deletion"""
        changes = {
            "action": "deleted",
            "attribute_key": attribute_key,
            "before": {"value": attribute_value}
        }
        details = {
            "performed_by": {
                "user_id": deleted_by_id,
                "username": deleted_by_username,
                "role": deleted_by_role
            },
            "target_user_id": target_user_id,
            "attribute_key": attribute_key
        }
        await self.log(
            action="user_attribute_deleted",
            user_id=deleted_by_id,
            username=deleted_by_username,
            resource_type="user_attribute",
            resource_id=str(attribute_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            deleted_by=deleted_by_id
        )

    # Resource Attribute Audit Methods
    async def log_resource_attribute_set(
        self,
        attribute_id: int,
        resource_type_name: str,
        resource_id_value: str,
        attribute_key: str,
        performed_by_id: int,
        performed_by_username: str,
        performed_by_role: str,
        before_value: Optional[str],
        after_value: str,
        request: Optional[Request] = None
    ):
        """Log resource attribute creation/update"""
        action_type = "updated" if before_value is not None else "created"
        changes = {
            "action": action_type,
            "attribute_key": attribute_key,
            "before": {"value": before_value} if before_value else None,
            "after": {"value": after_value}
        }
        details = {
            "performed_by": {
                "user_id": performed_by_id,
                "username": performed_by_username,
                "role": performed_by_role
            },
            "resource_type": resource_type_name,
            "resource_id": resource_id_value,
            "attribute_key": attribute_key
        }
        await self.log(
            action=f"resource_attribute_{action_type}",
            user_id=performed_by_id,
            username=performed_by_username,
            resource_type="resource_attribute",
            resource_id=str(attribute_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            created_by=performed_by_id if action_type == "created" else None,
            updated_by=performed_by_id if action_type == "updated" else None
        )

    async def log_resource_attribute_deleted(
        self,
        attribute_id: int,
        resource_type_name: str,
        resource_id_value: str,
        attribute_key: str,
        attribute_value: str,
        deleted_by_id: int,
        deleted_by_username: str,
        deleted_by_role: str,
        request: Optional[Request] = None
    ):
        """Log resource attribute deletion"""
        changes = {
            "action": "deleted",
            "attribute_key": attribute_key,
            "before": {"value": attribute_value}
        }
        details = {
            "performed_by": {
                "user_id": deleted_by_id,
                "username": deleted_by_username,
                "role": deleted_by_role
            },
            "resource_type": resource_type_name,
            "resource_id": resource_id_value,
            "attribute_key": attribute_key
        }
        await self.log(
            action="resource_attribute_deleted",
            user_id=deleted_by_id,
            username=deleted_by_username,
            resource_type="resource_attribute",
            resource_id=str(attribute_id),
            status="success",
            request=request,
            details=details,
            changes=changes,
            deleted_by=deleted_by_id
        )

    async def get_abac_audit_trail(
        self,
        skip: int = 0,
        limit: int = 100,
        policy_id: Optional[int] = None,
        action_type: Optional[str] = None,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Tuple[List, int]:
        """
        Get audit trail for ABAC policies with filtering options.
        
        Args:
            skip: Pagination offset
            limit: Maximum number of records
            policy_id: Filter by specific policy ID
            action_type: Filter by action (create, update, delete)
            user_id: Filter by user who performed the action
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            Tuple of (logs, total_count)
        """
        return await self.repository.get_abac_audit_logs(
            skip=skip,
            limit=limit,
            policy_id=policy_id,
            action_type=action_type,
            user_id=user_id,
            start_date=start_date,
            end_date=end_date
        )
