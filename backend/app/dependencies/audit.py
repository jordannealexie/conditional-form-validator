from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.audit import AuditRepository
from app.services.audit import AuditService
from app.services.bulk_audit import BulkAuditService
from app.services.batch_audit_processing import BatchAuditProcessingService

async def get_audit_service(db: AsyncSession = Depends(get_db)) -> AuditService:
    repository = AuditRepository(db)
    return AuditService(repository)

async def get_bulk_audit_service(db: AsyncSession = Depends(get_db)) -> BulkAuditService:
    """Dependency for bulk audit service"""
    repository = AuditRepository(db)
    return BulkAuditService(repository)

async def get_batch_audit_processing_service(
    db: AsyncSession = Depends(get_db)
) -> BatchAuditProcessingService:
    """Dependency for batch audit processing service"""
    repository = AuditRepository(db)
    return BatchAuditProcessingService(repository)
