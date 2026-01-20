from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.audit import AuditLog
from typing import List, Optional

class AuditRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> AuditLog:
        audit_log = AuditLog(**kwargs)
        self.db.add(audit_log)
        await self.db.commit()
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
