from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user, get_current_superuser
from app.repositories.forms import FormTemplateRepository, BankRepository
from app.schemas.forms import FormTemplateResponse, FormTemplateCreate, FormTemplateUpdate
from app.utils.response import create_response
from app.models.user import User

router = APIRouter()


@router.get("/", response_model=List[FormTemplateResponse])
async def list_templates(
    bank_id: Optional[int] = Query(None, description="Filter by bank ID"),
    bank_code: Optional[str] = Query(None, description="Filter by bank code"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """List templates. Admin: all or by bank. Others: only their bank."""
    if bank_code:
        bank = await BankRepository.get_by_code(db, bank_code)
        if not bank:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bank not found")
        bank_id = bank.id
    if current_user.user_role != "admin" and current_user.bank_id:
        bank_id = current_user.bank_id
    if bank_id:
        templates = await FormTemplateRepository.get_all_by_bank(db, bank_id, active_only=True)
    else:
        templates = await FormTemplateRepository.get_all(db, active_only=True)
    return create_response(data=[FormTemplateResponse.model_validate(t) for t in templates])


@router.get("/bank/{bank_id}", response_model=List[FormTemplateResponse])
async def read_templates_by_bank(
    bank_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Retrieve form templates for a specific bank.
    """
    bank = await BankRepository.get_by_id(db, bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bank not found"
        )
        
    templates = await FormTemplateRepository.get_all_by_bank(db, bank_id, active_only=True)
    data = [FormTemplateResponse.model_validate(t) for t in templates]
    return create_response(data=data)

@router.get("/{template_id}", response_model=FormTemplateResponse)
async def read_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific Form Template by ID.
    """
    template = await FormTemplateRepository.get_by_id(db, template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Form template not found"
        )
    return create_response(data=FormTemplateResponse.model_validate(template))

@router.post("/", response_model=FormTemplateResponse)
async def create_template(
    *,
    db: AsyncSession = Depends(get_db),
    template_in: FormTemplateCreate,
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a new Form Template.
    Admin users can create templates.
    """
    # Check if user is admin
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create templates"
        )
    
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
    return create_response(data=FormTemplateResponse.model_validate(template))


@router.put("/{template_id}", response_model=FormTemplateResponse)
async def update_template(
    template_id: int,
    template_in: FormTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Update a form template. Admin only."""
    # Check if user is admin
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update templates"
        )
    
    template = await FormTemplateRepository.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form template not found")
    upd = template_in.model_dump(exclude_unset=True)
    if upd:
        updated = await FormTemplateRepository.update(db, template, **upd)
        return create_response(data=FormTemplateResponse.model_validate(updated))
    return create_response(data=FormTemplateResponse.model_validate(template))


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Delete a form template. Admin only."""
    # Check if user is admin
    if current_user.user_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete templates"
        )
    
    template = await FormTemplateRepository.get_by_id(db, template_id)
    if not template:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Form template not found")
    await FormTemplateRepository.delete(db, template)
    return create_response(message="Template deleted")
