from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user, get_current_superuser, authorize
from app.repositories.forms import FormTemplateRepository, BankRepository
from app.schemas.forms import FormTemplateResponse, FormTemplateCreate, FormTemplateUpdate
from app.utils.response import create_response
from app.models.user import User
from app.dependencies.audit import get_audit_service
from app.services.audit import AuditService

router = APIRouter()


@router.get("/")
async def list_templates(
    bank_id: Optional[int] = Query(None, description="Filter by bank ID"),
    bank_code: Optional[str] = Query(None, description="Filter by bank code"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List templates. Admin: all or by bank. Others: only their bank."""
    try:
        if bank_code:
            bank = await BankRepository.get_by_code(db, bank_code)
            if not bank:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank not found")
            bank_id = bank.id
        
        # If not admin/superuser, force bank_id filter for supervisor/fieldman
        # This acts as data-level permission (ABAC/ReBAC lite)
        if not getattr(current_user, 'is_superuser', False) and current_user.user_role != "admin" and current_user.bank_id:
            bank_id = current_user.bank_id
        if bank_id:
            templates = await FormTemplateRepository.get_all_by_bank(db, bank_id, active_only=True)
        else:
            templates = await FormTemplateRepository.get_all(db, active_only=True)
        return create_response(data=[FormTemplateResponse.model_validate(t) for t in templates])
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/bank/{bank_id}")
async def read_templates_by_bank(
    bank_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve form templates for a specific bank.
    """
    try:
        bank = await BankRepository.get_by_id(db, bank_id)
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank not found"
            )
            
        templates = await FormTemplateRepository.get_all_by_bank(db, bank_id, active_only=True)
        data = [FormTemplateResponse.model_validate(t) for t in templates]
        return create_response(data=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve templates: {str(e)}"
        )

@router.get("/{template_id}")
async def read_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific Form Template by ID.
    """
    try:
        template = await FormTemplateRepository.get_by_id(db, template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Form template not found"
            )
        return create_response(data=FormTemplateResponse.model_validate(template))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve template: {str(e)}"
        )

@router.post("/")
async def create_template(
    *,
    db: AsyncSession = Depends(get_db),
    template_in: FormTemplateCreate,
    current_user: User = Depends(authorize(resource="forms", action="create")),
    request: Request = None,
    audit_service: AuditService = Depends(get_audit_service)
) -> Any:
    """
    Create a new Form Template.
    Permission: forms:create
    """
    try:
        # Check if bank exists
        bank = await BankRepository.get_by_id(db, template_in.bank_id)
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bank not found"
            )
            
        # Check if version exists
        exists = await FormTemplateRepository.check_version_exists(
            db, template_in.bank_id, template_in.name, template_in.version
        )
        if exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template with this version already exists for the bank"
            )
            
        template = await FormTemplateRepository.create(db, **template_in.model_dump())

        # Best-effort audit log for template creation
        try:
            await audit_service.log(
                action="template_created",
                user_id=current_user.id,
                username=template.name,
                resource_type="template",
                resource_id=str(template.id),
                status="success",
                request=request,
                changes={
                    "action": "created",
                    "after": {
                        "id": template.id,
                        "bank_id": template.bank_id,
                        "name": template.name,
                        "version": template.version,
                        "form_type": template.form_type,
                        "active": template.active,
                        "description": template.description,
                    },
                },
                created_by=current_user.id,
            )
        except Exception as audit_err:
            # Audit failures must not block template creation
            print(f"Error logging template creation in audit trail: {audit_err}")

        # Commit both template and (if successful) its audit log in one transaction
        await db.commit()

        return create_response(data=FormTemplateResponse.model_validate(template))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )


@router.put("/{template_id}")
async def update_template(
    template_id: int,
    template_in: FormTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="forms", action="update")),
    request: Request = None,
    audit_service: AuditService = Depends(get_audit_service)
) -> Any:
    """Update a form template. Permission: forms:update."""
    try:
        template = await FormTemplateRepository.get_by_id(db, template_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form template not found")

        # Snapshot before update
        before_data = {
            "id": template.id,
            "bank_id": template.bank_id,
            "name": template.name,
            "version": template.version,
            "form_type": template.form_type,
            "active": template.active,
            "description": template.description,
        }

        upd = template_in.model_dump(exclude_unset=True)
        if upd:
            updated = await FormTemplateRepository.update(db, template, **upd)

            # Best-effort audit log for template update
            try:
                after_data = {
                    "id": updated.id,
                    "bank_id": updated.bank_id,
                    "name": updated.name,
                    "version": updated.version,
                    "form_type": updated.form_type,
                    "active": updated.active,
                    "description": updated.description,
                }
                await audit_service.log(
                    action="template_updated",
                    user_id=current_user.id,
                    username=updated.name,
                    resource_type="template",
                    resource_id=str(updated.id),
                    status="success",
                    request=request,
                    changes={
                        "action": "updated",
                        "before": before_data,
                        "after": after_data,
                    },
                    updated_by=current_user.id,
                )
                await db.commit()
            except Exception as audit_err:
                print(f"Error logging template update in audit trail: {audit_err}")

            return create_response(data=FormTemplateResponse.model_validate(updated))

        return create_response(data=FormTemplateResponse.model_validate(template))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(authorize(resource="forms", action="delete")),
    request: Request = None,
    audit_service: AuditService = Depends(get_audit_service)
) -> Any:
    """Delete a form template. Permission: forms:delete."""
    try:
        template = await FormTemplateRepository.get_by_id(db, template_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form template not found")

        # Snapshot before delete
        before_data = {
            "id": template.id,
            "bank_id": template.bank_id,
            "name": template.name,
            "version": template.version,
            "form_type": template.form_type,
            "active": template.active,
            "description": template.description,
        }

        await FormTemplateRepository.delete(db, template)

        # Best-effort audit log for template deletion
        try:
            await audit_service.log(
                action="template_deleted",
                user_id=current_user.id,
                username=template.name,
                resource_type="template",
                resource_id=str(template_id),
                status="success",
                request=request,
                changes={
                    "action": "deleted",
                    "before": before_data,
                },
                deleted_by=current_user.id,
            )
            await db.commit()
        except Exception as audit_err:
            print(f"Error logging template deletion in audit trail: {audit_err}")

        return create_response(message="Template deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not delete template. It may have associated submissions. Error: {str(e)}"
        )
