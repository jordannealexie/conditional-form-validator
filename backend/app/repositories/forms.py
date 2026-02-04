"""
Repository layer for form system database operations
Follows existing repository pattern with caching and eager loading
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import joinedload, selectinload
from app.models.forms import Bank, FormTemplate, FormSubmission, FormFile, SubmissionStatus
from datetime import datetime, timezone

# Import cache layer
from app.core.cache import template_cache, CacheKeys


class BankRepository:
    """Repository for Bank model CRUD operations"""
    
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> dict:
        """Create a new bank"""
        bank = Bank(**kwargs)
        db.add(bank)
        await db.commit()
        await db.refresh(bank)
        
        # Extract data while in session context
        bank_data = {
            "id": bank.id,
            "name": bank.name,
            "code": bank.code,
            "logo_url": bank.logo_url,
            "primary_color": bank.primary_color,
            "description": bank.description,
            "active": bank.active,
            "created_at": bank.created_at,
            "updated_at": bank.updated_at,
            "deleted_at": bank.deleted_at
        }
        
        # Clear template cache since templates might reference this new bank
        await template_cache.delete_pattern("template:*")
        
        return bank_data
    
    @staticmethod
    async def get_by_id(db: AsyncSession, bank_id: int) -> Optional[dict]:
        """Get bank by ID with fresh data"""
        # Expire all to ensure fresh data
        db.expire_all()
        
        result = await db.execute(
            select(Bank).where(and_(Bank.id == bank_id, Bank.deleted_at.is_(None)))
        )
        bank = result.scalar_one_or_none()
        
        if bank:
            await db.refresh(bank)
            # Extract data while in session context
            bank_data = {
                "id": bank.id,
                "name": bank.name,
                "code": bank.code,
                "logo_url": bank.logo_url,
                "primary_color": bank.primary_color,
                "description": bank.description,
                "active": bank.active,
                "created_at": bank.created_at,
                "updated_at": bank.updated_at,
                "deleted_at": bank.deleted_at
            }
            return bank_data
            
        return None
    
    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Optional[Bank]:
        """Get bank by code"""
        result = await db.execute(
            select(Bank).where(and_(Bank.code == code, Bank.deleted_at.is_(None)))
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(db: AsyncSession, include_deleted: bool = False) -> List[dict]:
        """Get all banks with fresh data"""
        # Expire all cached objects to ensure absolutely fresh data
        db.expire_all()
        
        # Create a completely fresh query
        query = select(Bank)
        if not include_deleted:
            query = query.where(Bank.deleted_at.is_(None))
        
        # Order by updated_at desc, then by name to show recently updated banks first
        result = await db.execute(
            query.order_by(Bank.updated_at.desc().nullslast(), Bank.name)
        )
        banks = list(result.scalars().all())
        
        # Extract data while in session context to avoid greenlet errors
        bank_data_list = []
        for bank in banks:
            await db.refresh(bank)
            bank_data = {
                "id": bank.id,
                "name": bank.name,
                "code": bank.code,
                "logo_url": bank.logo_url,
                "primary_color": bank.primary_color,
                "description": bank.description,
                "active": bank.active,
                "created_at": bank.created_at,
                "updated_at": bank.updated_at,
                "deleted_at": bank.deleted_at
            }
            bank_data_list.append(bank_data)
        
        return bank_data_list
    
    @staticmethod
    async def update(db: AsyncSession, bank: Bank, **kwargs) -> dict:
        """Update bank and return data as dictionary to avoid greenlet issues"""
        from datetime import datetime, timezone
        
        # Ensure we have the latest state first
        await db.refresh(bank)
        
        # Update fields
        for key, value in kwargs.items():
            if value is not None and hasattr(bank, key):
                setattr(bank, key, value)
        
        # Explicitly set updated_at to ensure it's updated
        bank.updated_at = datetime.now(timezone.utc)
        
        # Mark the object as dirty and add to session
        db.add(bank)
        
        # Flush changes to database
        await db.flush()
        
        # Commit the transaction
        await db.commit()
        
        # Refresh the updated object to get latest data from database
        await db.refresh(bank)
        
        # Extract all data while still in session context
        bank_data = {
            "id": bank.id,
            "name": bank.name,
            "code": bank.code,
            "logo_url": bank.logo_url,
            "primary_color": bank.primary_color,
            "description": bank.description,
            "active": bank.active,
            "created_at": bank.created_at,
            "updated_at": bank.updated_at,
            "deleted_at": bank.deleted_at
        }
        
        # Clear session cache to ensure fresh data on next query
        db.expire_all()
        
        # CRITICAL: Invalidate all template cache since templates cache bank data
        await template_cache.delete_pattern("template:*")
        
        return bank_data
    
    @staticmethod
    async def soft_delete(db: AsyncSession, bank: Bank) -> Bank:
        """Soft delete bank"""
        from datetime import datetime, timezone
        
        bank.deleted_at = datetime.now(timezone.utc)
        bank.active = False
        await db.commit()
        await db.refresh(bank)
        return bank


class FormTemplateRepository:
    """Repository for FormTemplate model CRUD operations with caching"""
    
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> FormTemplate:
        """Create a new form template and commit immediately.

        This mirrors the pattern used by other repositories: the
        repository is responsible for persisting and refreshing the
        entity. Callers can perform additional work (such as audit
        logging) afterwards and issue a second commit if needed.
        """
        template = FormTemplate(**kwargs)
        db.add(template)

        # Commit so the template gets a permanent ID and timestamps
        await db.commit()

        # Eager load bank while the session/transaction is active
        await db.refresh(template, attribute_names=["bank"])

        # Cache the new template (best-effort; cache layer is async-safe)
        await FormTemplateRepository._cache_template(template)

        return template
    
    @staticmethod
    async def get_by_id(db: AsyncSession, template_id: int, use_cache: bool = False) -> Optional[FormTemplate]:
        """
        Get template by ID with optional caching (disabled by default for updates)
        
        Performance optimization: Checks cache first, preventing N+1 queries
        """
        # Try cache first
        if use_cache:
            cached = await template_cache.get(CacheKeys.template(template_id))
            if cached:
                # Reconstruct model from cache (simplified - in production use proper deserialization)
                return FormTemplateRepository._from_cache(cached)
        
        # Not in cache - fetch with eager loading (single query)
        result = await db.execute(
            select(FormTemplate)
            .options(joinedload(FormTemplate.bank))  # Eager load bank - NO N+1
            .where(FormTemplate.id == template_id)
        )
        template = result.unique().scalar_one_or_none()
        
        # Cache result
        if template and use_cache:
            await FormTemplateRepository._cache_template(template)
        
        return template
    
    @staticmethod
    async def _cache_template(template: FormTemplate) -> None:
        """Store template in cache"""
        cache_data = {
            "id": template.id,
            "bank_id": template.bank_id,
            "name": template.name,
            "version": template.version,
            "form_type": template.form_type,
            "schema_json": template.schema_json,
            "fields": template.fields,
            "ui_schema": template.ui_schema,
            "description": template.description,
            "active": template.active,
            "created_at": template.created_at.isoformat() if template.created_at else None,
            "updated_at": template.updated_at.isoformat() if template.updated_at else None,
            "created_by": template.created_by,
            "bank": {
                "id": template.bank.id,
                "name": template.bank.name,
                "code": template.bank.code,
                "logo_url": template.bank.logo_url,
                "primary_color": template.bank.primary_color,
                "description": template.bank.description,
                "active": template.bank.active,
                "created_at": template.bank.created_at.isoformat() if template.bank.created_at else None,
                "updated_at": template.bank.updated_at.isoformat() if template.bank.updated_at else None
            } if template.bank else None
        }
        # Use namespaced key so invalidate/delete_pattern work correctly
        await template_cache.set(CacheKeys.template(template.id), cache_data)
    
    @staticmethod
    def _from_cache(cached: dict) -> FormTemplate:
        """
        Reconstruct template from cache
        Note: Returns a detached object - don't use for updates without reattaching
        """
        from datetime import datetime
        from app.models.forms import Bank
        
        template = FormTemplate(
            id=cached["id"],
            bank_id=cached["bank_id"],
            name=cached["name"],
            version=cached["version"],
            form_type=cached["form_type"],
            schema_json=cached["schema_json"],
            fields=cached["fields"],
            ui_schema=cached["ui_schema"],
            description=cached["description"],
            active=cached["active"],
            created_by=cached.get("created_by")
        )
        
        # Set datetime fields
        if cached.get("created_at"):
            template.created_at = datetime.fromisoformat(cached["created_at"])
        if cached.get("updated_at"):
            template.updated_at = datetime.fromisoformat(cached["updated_at"])
        
        # Attach bank data
        if cached.get("bank"):
            bank_data = cached["bank"]
            bank = Bank(
                id=bank_data["id"],
                name=bank_data["name"],
                code=bank_data["code"],
                logo_url=bank_data.get("logo_url"),
                primary_color=bank_data.get("primary_color"),
                description=bank_data.get("description"),
                active=bank_data.get("active", True)
            )
            if bank_data.get("created_at"):
                bank.created_at = datetime.fromisoformat(bank_data["created_at"])
            if bank_data.get("updated_at"):
                bank.updated_at = datetime.fromisoformat(bank_data["updated_at"])
            template.bank = bank
        
        return template
    
    @staticmethod
    async def get_by_bank_and_type(
        db: AsyncSession, 
        bank_id: int, 
        form_type: str, 
        version: Optional[str] = None
    ) -> Optional[FormTemplate]:
        """Get template by bank, form type, and optionally version"""
        query = select(FormTemplate).where(
            and_(
                FormTemplate.bank_id == bank_id,
                FormTemplate.name == form_type
            )
        )
        
        if version:
            query = query.where(FormTemplate.version == version)
        else:
            # Get latest active version
            query = query.where(FormTemplate.active == True).order_by(FormTemplate.created_at.desc())
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_by_bank(
        db: AsyncSession, 
        bank_id: int, 
        active_only: bool = False
    ) -> List[FormTemplate]:
        """
        Get all templates for a bank with eager loading
        
        Performance: Single query with eager loading - NO N+1
        """
        query = (
            select(FormTemplate)
            .options(joinedload(FormTemplate.bank))  # Eager load bank
            .where(FormTemplate.bank_id == bank_id)
        )
        
        if active_only:
            query = query.where(FormTemplate.active == True)
        
        result = await db.execute(query.order_by(FormTemplate.name, FormTemplate.version.desc()))
        return list(result.unique().scalars().all())
    
    @staticmethod
    async def get_all(db: AsyncSession, active_only: bool = False) -> List[FormTemplate]:
        """
        Get all templates with eager loading
        
        Performance: Single query with eager loading - NO N+1
        """
        query = select(FormTemplate).options(joinedload(FormTemplate.bank))  # Eager load
        
        if active_only:
            query = query.where(FormTemplate.active == True)
        
        result = await db.execute(query.order_by(FormTemplate.bank_id, FormTemplate.name))
        return list(result.unique().scalars().all())
    
    @staticmethod
    async def update(db: AsyncSession, template: FormTemplate, **kwargs) -> FormTemplate:
        """Update template and invalidate cache"""
        for key, value in kwargs.items():
            if value is not None and hasattr(template, key):
                setattr(template, key, value)
        await db.commit()
        
        # Invalidate cache on update
        await template_cache.invalidate(template.id)
        
        # Refetch with eager loading to avoid lazy-load issues
        result = await db.execute(
            select(FormTemplate)
            .options(joinedload(FormTemplate.bank))
            .where(FormTemplate.id == template.id)
        )
        updated = result.unique().scalar_one()
        
        # Re-cache updated template
        await FormTemplateRepository._cache_template(updated)
        
        return updated
    
    @staticmethod
    async def delete(db: AsyncSession, template: FormTemplate) -> None:
        """Delete template and invalidate cache"""
        template_id = template.id
        await db.delete(template)
        await db.commit()
        
        # Invalidate cache on delete
        await template_cache.invalidate(template_id)
    
    @staticmethod
    async def check_version_exists(
        db: AsyncSession, 
        bank_id: int, 
        form_type: str, 
        version: str
    ) -> bool:
        """Check if a specific version already exists"""
        result = await db.execute(
            select(func.count(FormTemplate.id)).where(
                and_(
                    FormTemplate.bank_id == bank_id,
                    FormTemplate.name == form_type,
                    FormTemplate.version == version
                )
            )
        )

        count = result.scalar()
        return count > 0

    @staticmethod
    async def delete(db: AsyncSession, template: FormTemplate) -> None:
        """Delete template"""
        await db.delete(template)
        await db.commit()


class FormSubmissionRepository:
    """Repository for FormSubmission model CRUD operations"""
    
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> FormSubmission:
        """Create a new form submission"""
        submission = FormSubmission(**kwargs)
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        return submission
    
    @staticmethod
    async def get_by_id(db: AsyncSession, submission_id: int) -> Optional[FormSubmission]:
        """Get submission by ID"""
        result = await db.execute(
            select(FormSubmission)
            .options(
                joinedload(FormSubmission.template).joinedload(FormTemplate.bank),
                joinedload(FormSubmission.files)
            )
            .where(FormSubmission.id == submission_id)
        )
        return result.unique().scalar_one_or_none()
    
    @staticmethod
    async def get_all(
        db: AsyncSession,
        submitted_by: Optional[str] = None,
        status: Optional[str] = None,
        template_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[FormSubmission]:
        """Get submissions with optional filters"""
        query = select(FormSubmission).options(
            joinedload(FormSubmission.template).joinedload(FormTemplate.bank)
        )
        
        filters = []
        if submitted_by:
            filters.append(FormSubmission.fieldman_id == submitted_by)
        if status:
            filters.append(FormSubmission.status == status)
        if template_id:
            filters.append(FormSubmission.template_id == template_id)
        
        if filters:
            query = query.where(and_(*filters))
        
        query = query.order_by(FormSubmission.created_at.desc()).limit(limit).offset(offset)
        
        result = await db.execute(query)
        return list(result.unique().scalars().all())
    
    @staticmethod
    async def count(
        db: AsyncSession,
        submitted_by: Optional[str] = None,
        status: Optional[str] = None,
        template_id: Optional[int] = None
    ) -> int:
        """Count submissions with optional filters"""
        query = select(func.count(FormSubmission.id))
        
        filters = []
        if submitted_by:
            filters.append(FormSubmission.fieldman_id == submitted_by)
        if status:
            filters.append(FormSubmission.status == status)
        if template_id:
            filters.append(FormSubmission.template_id == template_id)
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await db.execute(query)
        return result.scalar()
    
    @staticmethod
    async def update(db: AsyncSession, submission: FormSubmission, **kwargs) -> FormSubmission:
        """Update submission"""
        for key, value in kwargs.items():
            if hasattr(submission, key):
                setattr(submission, key, value)
        await db.commit()
        await db.refresh(submission)
        return submission
    
    @staticmethod
    async def delete(db: AsyncSession, submission: FormSubmission) -> None:
        """Hard delete submission (only for drafts)"""
        if submission.status != SubmissionStatus.DRAFT:
            raise ValueError("Can only delete draft submissions")
        await db.delete(submission)
        await db.commit()
    
    @staticmethod
    async def submit(db: AsyncSession, submission: FormSubmission) -> FormSubmission:
        """Mark submission as submitted"""
        submission.status = SubmissionStatus.SUBMITTED
        submission.submitted_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(submission)
        return submission


class FormFileRepository:
    """Repository for FormFile model CRUD operations"""
    
    @staticmethod
    async def create(db: AsyncSession, **kwargs) -> FormFile:
        """Create a new form file record"""
        file_record = FormFile(**kwargs)
        db.add(file_record)
        await db.commit()
        await db.refresh(file_record)
        return file_record
    
    @staticmethod
    async def get_by_token(db: AsyncSession, token) -> Optional[FormFile]:
        """Get file by token (str or UUID)."""
        import uuid as _uuid
        tok = _uuid.UUID(str(token)) if not hasattr(token, 'hex') else token
        result = await db.execute(select(FormFile).where(FormFile.token == tok))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_submission(db: AsyncSession, submission_id: int) -> List[FormFile]:
        """Get all files for a submission"""
        result = await db.execute(
            select(FormFile)
            .where(FormFile.submission_id == submission_id)
            .order_by(FormFile.uploaded_at)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def delete(db: AsyncSession, file_record: FormFile) -> None:
        """Delete file record"""
        await db.delete(file_record)
        await db.commit()
