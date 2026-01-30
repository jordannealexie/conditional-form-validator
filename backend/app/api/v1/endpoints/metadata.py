"""
Form Metadata API Endpoints
Provides centralized dropdown data for all forms across the application.
This is the SINGLE SOURCE OF TRUTH for dropdown values.

All dropdown values come from the database - NO HARDCODING.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from app.db.session import get_db
from app.models.user import Role
from app.models.lookup import Department, Location
from app.utils.response import create_response

router = APIRouter()


# ============ Response Schemas ============

class DropdownOption(BaseModel):
    """Standard dropdown option format"""
    value: str = Field(..., description="The value to submit")
    label: str = Field(..., description="The display label")
    description: Optional[str] = Field(None, description="Optional description/tooltip")


class LevelOption(BaseModel):
    """Level dropdown option with numeric value"""
    value: int = Field(..., description="The numeric level value (1-3)")
    label: str = Field(..., description="User-friendly label")
    description: Optional[str] = Field(None, description="Level description")


class FormMetadataResponse(BaseModel):
    """Complete form metadata for all dropdowns"""
    roles: List[DropdownOption] = Field(default_factory=list)
    departments: List[DropdownOption] = Field(default_factory=list)
    locations: List[DropdownOption] = Field(default_factory=list)
    levels: List[LevelOption] = Field(default_factory=list)


# ============ Constants ============

# Valid levels - EXACTLY 3 levels as specified
LEVEL_OPTIONS = [
    LevelOption(value=1, label="Level 1 (Basic)", description="Basic access level"),
    LevelOption(value=2, label="Level 2 (Standard)", description="Standard access level"),
    LevelOption(value=3, label="Level 3 (Advanced)", description="Advanced access level"),
]


# ============ Endpoints ============

@router.get(
    "/form-dropdowns",
    response_model=FormMetadataResponse,
    summary="Get all form dropdown data",
    description="Returns all dropdown values for forms. This is the SINGLE SOURCE OF TRUTH for dropdowns."
)
async def get_form_dropdowns(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all dropdown data for forms in a single request.
    This endpoint is PUBLIC (no auth required) to support registration.
    
    Returns:
    - roles: All active roles from the database
    - departments: All active departments from the database
    - locations: All active locations from the database (EXACTLY 17 cities)
    - levels: Static level options (1-3 only)
    """
    # Fetch roles from database
    roles_result = await db.execute(
        select(Role).order_by(Role.name)
    )
    roles = roles_result.scalars().all()
    role_options = [
        DropdownOption(
            value=r.name,
            label=r.name.replace('_', ' ').title(),
            description=r.description
        ) for r in roles
    ]
    
    # Fetch departments from database
    dept_result = await db.execute(
        select(Department)
        .where(Department.is_active == True)
        .order_by(Department.display_order, Department.name)
    )
    departments = dept_result.scalars().all()
    dept_options = [
        DropdownOption(
            value=d.name,
            label=d.name,
            description=d.description
        ) for d in departments
    ]
    
    # Fetch locations from database
    loc_result = await db.execute(
        select(Location)
        .where(Location.is_active == True)
        .order_by(Location.display_order, Location.name)
    )
    locations = loc_result.scalars().all()
    loc_options = [
        DropdownOption(
            value=loc.name,
            label=loc.name,
            description=f"{loc.region}" if loc.region else None
        ) for loc in locations
    ]
    
    metadata = FormMetadataResponse(
        roles=role_options,
        departments=dept_options,
        locations=loc_options,
        levels=LEVEL_OPTIONS
    )
    
    return create_response(data=metadata.model_dump())


@router.get(
    "/roles",
    response_model=List[DropdownOption],
    summary="Get roles for dropdown"
)
async def get_roles_metadata(
    db: AsyncSession = Depends(get_db)
):
    """Get all roles for dropdown - no auth required for registration support"""
    result = await db.execute(select(Role).order_by(Role.name))
    roles = result.scalars().all()
    options = [
        DropdownOption(
            value=r.name,
            label=r.name.replace('_', ' ').title(),
            description=r.description
        ) for r in roles
    ]
    return create_response(data=[o.model_dump() for o in options])


@router.get(
    "/departments",
    response_model=List[DropdownOption],
    summary="Get departments for dropdown"
)
async def get_departments_metadata(
    db: AsyncSession = Depends(get_db)
):
    """Get all active departments for dropdown"""
    result = await db.execute(
        select(Department)
        .where(Department.is_active == True)
        .order_by(Department.display_order, Department.name)
    )
    departments = result.scalars().all()
    options = [
        DropdownOption(
            value=d.name,
            label=d.name,
            description=d.description
        ) for d in departments
    ]
    return create_response(data=[o.model_dump() for o in options])


@router.get(
    "/locations",
    response_model=List[DropdownOption],
    summary="Get locations for dropdown"
)
async def get_locations_metadata(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all active locations for dropdown.
    Locations are restricted to EXACTLY 17 cities from the database.
    """
    result = await db.execute(
        select(Location)
        .where(Location.is_active == True)
        .order_by(Location.display_order, Location.name)
    )
    locations = result.scalars().all()
    options = [
        DropdownOption(
            value=loc.name,
            label=loc.name,
            description=f"{loc.region}" if loc.region else None
        ) for loc in locations
    ]
    return create_response(data=[o.model_dump() for o in options])


@router.get(
    "/levels",
    response_model=List[LevelOption],
    summary="Get levels for dropdown"
)
async def get_levels_metadata():
    """
    Get level options for dropdown.
    Levels are restricted to EXACTLY 1, 2, 3.
    """
    return create_response(data=[l.model_dump() for l in LEVEL_OPTIONS])
