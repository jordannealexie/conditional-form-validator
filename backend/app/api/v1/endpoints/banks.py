"""
Bank API endpoints for form system
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

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
from app.repositories.forms import BankRepository
from app.utils.response import create_response


router = APIRouter()


@router.get("/", response_model=CustomResponse[List[BankResponse]], summary="List all banks")
async def list_banks(
    include_deleted: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve all banks.
    Requires authentication.
    """
    banks = await BankRepository.get_all(db, include_deleted=include_deleted)
    # banks is now a list of dictionaries, use directly
    return create_response(data=banks)


@router.post("/", response_model=CustomResponse[BankResponse], status_code=status.HTTP_201_CREATED, summary="Create a new bank")
async def create_bank(
    bank_data: BankCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only admins can create banks
):
    """
    Create a new bank.
    Requires superuser authentication.
    """
    # Check if bank code already exists
    existing_bank = await BankRepository.get_by_code(db, bank_data.code)
    if existing_bank:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Bank with code '{bank_data.code}' already exists"
        )
    
    bank = await BankRepository.create(db, **bank_data.model_dump())
    
    # bank is now a dictionary, use it directly
    return create_response(data=bank)


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
    bank = await BankRepository.get_by_id(db, bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank with ID {bank_id} not found"
        )
    
    # bank is now a dictionary, use it directly
    return create_response(data=bank)


@router.put("/{bank_id}", response_model=CustomResponse[BankResponse], summary="Update bank")
async def update_bank(
    bank_id: int,
    bank_data: BankUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only admins can update banks
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
    
    updated_bank = await BankRepository.update(
        db, 
        bank, 
        **bank_data.model_dump(exclude_unset=True)
    )
    
    # updated_bank is now a dictionary, use it directly
    return create_response(data=updated_bank)


@router.delete("/{bank_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete bank")
async def delete_bank(
    bank_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)  # Only admins can delete banks
):
    """
    Soft delete a bank.
    Requires superuser authentication.
    """
    bank = await BankRepository.get_by_id(db, bank_id)
    if not bank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank with ID {bank_id} not found"
        )
    
    await BankRepository.soft_delete(db, bank)
    return None
