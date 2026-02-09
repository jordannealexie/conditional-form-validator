"""
Bank API endpoints for form system
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update

from app.db.session import get_db
from app.models.user import User
from app.models.forms import Bank
from app.dependencies.auth import get_current_user, get_current_superuser
from app.dtos.custom_response_dto import CustomResponse
from app.schemas.forms import (
    BankCreate,
    BankUpdate,
    BankResponse,
    BankListResponse
)
from app.dependencies.audit import get_audit_service
from app.services.audit import AuditService
from app.repositories.forms import BankRepository
from app.utils.response import create_response


router = APIRouter()


@router.get("/", response_model=CustomResponse[BankListResponse], summary="List all banks")
async def list_banks(
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db),
    # current_user: User = Depends(get_current_user)
):
    """
    Retrieve all banks.
    Requires authentication.
    """
    query = select(Bank)
    if not include_deleted:
        query = query.where(Bank.deleted_at.is_(None))
    query = query.order_by(Bank.updated_at.desc().nullslast(), Bank.name)
    result = await db.execute(query)
    banks_db = result.scalars().all()
    
    banks_response = [BankResponse.model_validate(b) for b in banks_db]
    return create_response(data=BankListResponse(total=len(banks_response), data=banks_response))


@router.post("/", response_model=CustomResponse[BankResponse], status_code=status.HTTP_201_CREATED, summary="Create a new bank")
async def create_bank(
    bank_data: BankCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit: AuditService = Depends(get_audit_service)
):
    """
    Create a new bank.
    Requires superuser authentication.
    """
    # Check if bank code already exists
    existing_result = await db.execute(
        select(Bank).where(and_(Bank.code == bank_data.code, Bank.deleted_at.is_(None)))
    )
    existing_bank = existing_result.scalar_one_or_none()
    if existing_bank:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bank with code '{bank_data.code}' already exists"
        )
    
    # Create new bank directly
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    
    new_bank = Bank(
        name=bank_data.name,
        code=bank_data.code,
        description=bank_data.description,
        logo_url=bank_data.logo_url,
        primary_color=bank_data.primary_color,
        active=bank_data.active,
        created_at=now,
        updated_at=now
    )
    
    db.add(new_bank)
    await db.commit()
    await db.refresh(new_bank)
    
    # Extract data
    bank = {
        "id": new_bank.id,
        "name": new_bank.name,
        "code": new_bank.code,
        "logo_url": new_bank.logo_url,
        "primary_color": new_bank.primary_color,
        "description": new_bank.description,
        "active": new_bank.active,
        "created_at": new_bank.created_at,
        "updated_at": new_bank.updated_at,
        "deleted_at": new_bank.deleted_at
    }
    
    # Log the bank creation
    await audit.log(
        action="created",
        user_id=current_user.id,
        username=current_user.username,
        resource_type="banks",
        resource_id=str(bank["id"]),
        changes={
            "action": "created",
            "after": bank
        },
        details={
            "bank_name": bank["name"],
            "bank_code": bank["code"]
        }
    )
    
    # bank is now a dictionary, use it directly
    return create_response(data=BankResponse.model_validate(bank))


@router.get("/{bank_id}", response_model=CustomResponse[BankResponse], summary="Get bank by ID")
async def get_bank(
    bank_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific bank by ID.
    Requires authentication.
    """
    try:
        # Use the same query as list_banks but filter by ID
        result = await db.execute(
            select(Bank).where(and_(Bank.id == bank_id, Bank.deleted_at.is_(None)))
        )
        bank = result.scalar_one_or_none()
        
        if not bank:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Bank with ID {bank_id} not found"
            )
        
        # Convert to dict like the list endpoint
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
        
        return create_response(data=bank_data)
    except Exception as e:
        # Debug: log the error
        print(f"Error in get_bank: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get bank: {str(e)}"
        )


@router.put("/{bank_id}", response_model=CustomResponse[BankResponse], summary="Update bank")
async def update_bank(
    bank_id: int,
    bank_data: BankUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit: AuditService = Depends(get_audit_service)
):
    """
    Update a bank.
    Requires superuser authentication.
    """
    # Get bank object for update (need actual object)
    bank_result = await db.execute(
        select(Bank).where(and_(Bank.id == bank_id, Bank.deleted_at.is_(None)))
    )
    bank = bank_result.scalar_one_or_none()
    
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank with ID {bank_id} not found"
        )
    
    # Capture before state
    before_data = {
        "id": bank.id,
        "name": bank.name,
        "code": bank.code,
        "description": bank.description,
        "logo_url": bank.logo_url,
        "primary_color": bank.primary_color,
        "active": bank.active
    }
    
    # If updating code, check if new code already exists
    if bank_data.code and bank_data.code != bank.code:
        existing_result = await db.execute(
            select(Bank).where(and_(Bank.code == bank_data.code, Bank.deleted_at.is_(None)))
        )
        existing_bank = existing_result.scalar_one_or_none()
        if existing_bank:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Bank with code '{bank_data.code}' already exists"
            )
    
    # Update bank directly
    from datetime import datetime, timezone
    update_data = bank_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    # Build update query
    update_stmt = (
        update(Bank)
        .where(and_(Bank.id == bank_id, Bank.deleted_at.is_(None)))
        .values(**update_data)
    )
    
    await db.execute(update_stmt)
    await db.commit()
    
    # Get updated bank data
    result = await db.execute(
        select(Bank).where(and_(Bank.id == bank_id, Bank.deleted_at.is_(None)))
    )
    updated_bank_obj = result.scalar_one()
    
    updated_bank = {
        "id": updated_bank_obj.id,
        "name": updated_bank_obj.name,
        "code": updated_bank_obj.code,
        "logo_url": updated_bank_obj.logo_url,
        "primary_color": updated_bank_obj.primary_color,
        "description": updated_bank_obj.description,
        "active": updated_bank_obj.active,
        "created_at": updated_bank_obj.created_at,
        "updated_at": updated_bank_obj.updated_at,
        "deleted_at": updated_bank_obj.deleted_at
    }
    
    # Log the bank update
    edited_fields = list(bank_data.model_dump(exclude_unset=True).keys())
    await audit.log(
        action="updated",
        user_id=current_user.id,
        username=current_user.username,
        resource_type="banks",
        resource_id=str(bank_id),
        changes={
            "action": "updated",
            "before": before_data,
            "after": updated_bank,
            "edited_fields": edited_fields
        },
        details={
            "bank_name": updated_bank["name"],
            "bank_code": updated_bank["code"]
        }
    )
    
    # updated_bank is now a dictionary, use it directly
    return create_response(data=BankResponse.model_validate(updated_bank))


@router.delete("/{bank_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete bank")
async def delete_bank(
    bank_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audit: AuditService = Depends(get_audit_service)
):
    """
    Permanently delete a bank and all associated data.
    Requires superuser authentication.
    """
    bank = await BankRepository.get_bank_object_by_id(db, bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank with ID {bank_id} not found"
        )
    
    # Capture before state for audit log
    before_data = {
        "id": bank.id,
        "name": bank.name,
        "code": bank.code,
        "description": bank.description,
        "logo_url": bank.logo_url,
        "primary_color": bank.primary_color,
        "active": bank.active
    }
    
    # Log the bank deletion before actually deleting
    await audit.log(
        action="deleted",
        user_id=current_user.id,
        username=current_user.username,
        resource_type="banks",
        resource_id=str(bank_id),
        changes={
            "action": "deleted",
            "before": before_data
        },
        details={
            "bank_name": bank.name,
            "bank_code": bank.code
        }
    )
    
    await BankRepository.hard_delete(db, bank)
    return None
