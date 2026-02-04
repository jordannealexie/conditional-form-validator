from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, insert
from app.models.audit import AuditLog
from typing import List, Optional, Tuple, Dict, Any

class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> AuditLog:
        audit_log = AuditLog(**kwargs)
        self.db.add(audit_log)
        await self.db.flush()  # Use flush instead of commit to stay in transaction
        await self.db.refresh(audit_log)
        return audit_log
    
    async def bulk_create(self, audit_entries: List[Dict[str, Any]]) -> int:
        """
        Bulk insert audit log entries using a single INSERT statement.
        
        Args:
            audit_entries: List of dictionaries containing audit log data
            
        Returns:
            Number of rows inserted
        """
        if not audit_entries:
            return 0
        
        # Use SQLAlchemy Core insert for bulk operations
        stmt = insert(AuditLog).values(audit_entries)
        result = await self.db.execute(stmt)
        await self.db.flush()
        
        return result.rowcount if result.rowcount else len(audit_entries)

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        query = select(AuditLog).offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_resource_type(
        self,
        resource_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        query = (
            select(AuditLog)
            .where(func.lower(AuditLog.resource_type) == resource_type)
            .order_by(AuditLog.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
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
    
    async def get_by_entity_type_and_id(
        self,
        entity_type: str,
        entity_id: Optional[int] = None,
        actor_user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[AuditLog], int]:
        """
        Get audit logs filtered by entity_type, optionally by entity_id and actor.
        Always orders by created_at DESC before pagination.
        
        Args:
            entity_type: The type of entity (user, role, form_template, etc.)
            entity_id: Optional entity ID for row-specific logs
            actor_user_id: Optional user ID who performed the action
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (logs, total_count)
        """
        # Build base query
        query = select(AuditLog).where(
            func.lower(AuditLog.resource_type) == entity_type.lower()
        )
        
        # Add entity_id filter if provided
        if entity_id is not None:
            query = query.where(AuditLog.resource_id == str(entity_id))
        
        # Add actor filter if provided
        if actor_user_id is not None:
            query = query.where(AuditLog.user_id == actor_user_id)
        
        # Order by created_at DESC BEFORE pagination
        query = query.order_by(AuditLog.created_at.desc())
        
        # Count query
        count_query = select(func.count()).select_from(AuditLog).where(
            func.lower(AuditLog.resource_type) == entity_type.lower()
        )
        if entity_id is not None:
            count_query = count_query.where(AuditLog.resource_id == str(entity_id))
        if actor_user_id is not None:
            count_query = count_query.where(AuditLog.user_id == actor_user_id)
        
        # Execute count
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # Add pagination
        query = query.offset(skip).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        logs = result.scalars().all()
        
        return logs, total
