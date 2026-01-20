from datetime import datetime
from typing import Optional, Any, Dict
from app.repositories.audit import AuditRepository
from fastapi import Request

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
        details: Optional[str] = None
    ):
        """
        Record an audit log entry
        """
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
            payload=payload,
            details=details
        )

    async def get_logs(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_all(skip, limit)
