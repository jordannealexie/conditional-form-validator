from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.audit import AuditRepository
from app.services.audit import AuditService

async def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    repository = AuditRepository(db)
    return AuditService(repository)
