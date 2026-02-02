from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.audit import AuditLog
from typing import List, Optional, Tuple

class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> AuditLog:
        audit_log = AuditLog(**kwargs)
        self.db.add(audit_log)
        await self.db.flush()  # Use flush instead of commit to stay in transaction
        await self.db.refresh(audit_log)
        return audit_log

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        query = select(AuditLog).offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_user(self, username: str, limit: int = 50) -> List[AuditLog]:
        query = select(AuditLog).where(AuditLog.username == username).limit(limit).order_by(AuditLog.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_resource(
        self, 
        resource_type: str, 
        resource_id: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> Tuple[List[AuditLog], int]:
        """
        Get audit logs for a specific resource with pagination
        Returns tuple of (logs, total_count)
        """
        # Query for logs
        query = (
            select(AuditLog)
            .where(AuditLog.resource_type == resource_type)
            .where(AuditLog.resource_id == resource_id)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        # Query for total count
        count_query = (
            select(func.count())
            .select_from(AuditLog)
            .where(AuditLog.resource_type == resource_type)
            .where(AuditLog.resource_id == resource_id)
        )
        count_result = await self.db.execute(count_query)
        total = count_result.scalar()
        
        return logs, total
