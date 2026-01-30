"""
Lookup Tables API endpoints
Provides endpoints for managing departments, locations, and other lookup values
used in ABAC policy builder and user management
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.dependencies.permissions import require_permission
from app.models.user import User
from app.models.lookup import Department, Location
from app.schemas.abac import (
    DepartmentCreate, DepartmentResponse,
    LocationCreate, LocationResponse
)
from app.utils.response import create_response

router = APIRouter()


# ============ Department Endpoints ============

@router.get("/departments", response_model=List[DepartmentResponse], summary="Get all departments")
async def list_departments(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all departments for dropdown population.
    This endpoint is accessible to any authenticated user.
    """
    query = select(Department).order_by(Department.display_order, Department.name)
    if active_only:
        query = query.where(Department.is_active == True)
    
    result = await db.execute(query)
    departments = result.scalars().all()
    return create_response(data=[DepartmentResponse.model_validate(d) for d in departments])


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("settings:create"))
):
    """Create a new department - requires settings:create permission"""
    # Check for duplicate
    existing = await db.execute(select(Department).where(Department.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Department '{data.name}' already exists"
        )
    
    department = Department(**data.model_dump())
    db.add(department)
    await db.commit()
    await db.refresh(department)
    return create_response(data=DepartmentResponse.model_validate(department), status_code=status.HTTP_201_CREATED)


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(
    department_id: int,
    data: DepartmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("settings:update"))
):
    """Update a department - requires settings:update permission"""
    result = await db.execute(select(Department).where(Department.id == department_id))
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    for key, value in data.model_dump().items():
        setattr(department, key, value)
    
    await db.commit()
    await db.refresh(department)
    return create_response(data=DepartmentResponse.model_validate(department))


@router.delete("/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_department(
    department_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("settings:delete"))
):
    """Delete a department - requires settings:delete permission"""
    result = await db.execute(select(Department).where(Department.id == department_id))
    department = result.scalar_one_or_none()
    
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    
    await db.delete(department)
    await db.commit()
    return None


# ============ Location Endpoints ============

@router.get("/locations", response_model=List[LocationResponse], summary="Get all locations")
async def list_locations(
    active_only: bool = True,
    region: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all locations for dropdown population.
    This endpoint is accessible to any authenticated user.
    Optionally filter by region.
    """
    query = select(Location).order_by(Location.display_order, Location.name)
    if active_only:
        query = query.where(Location.is_active == True)
    if region:
        query = query.where(Location.region == region)
    
    result = await db.execute(query)
    locations = result.scalars().all()
    return create_response(data=[LocationResponse.model_validate(loc) for loc in locations])


@router.post("/locations", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
async def create_location(
    data: LocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("settings:create"))
):
    """Create a new location - requires settings:create permission"""
    # Check for duplicate
    existing = await db.execute(select(Location).where(Location.name == data.name))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Location '{data.name}' already exists"
        )
    
    location = Location(**data.model_dump())
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return create_response(data=LocationResponse.model_validate(location), status_code=status.HTTP_201_CREATED)


@router.put("/locations/{location_id}", response_model=LocationResponse)
async def update_location(
    location_id: int,
    data: LocationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("settings:update"))
):
    """Update a location - requires settings:update permission"""
    result = await db.execute(select(Location).where(Location.id == location_id))
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    for key, value in data.model_dump().items():
        setattr(location, key, value)
    
    await db.commit()
    await db.refresh(location)
    return create_response(data=LocationResponse.model_validate(location))


@router.delete("/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_location(
    location_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_permission("settings:delete"))
):
    """Delete a location - requires settings:delete permission"""
    result = await db.execute(select(Location).where(Location.id == location_id))
    location = result.scalar_one_or_none()
    
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    
    await db.delete(location)
    await db.commit()
    return None
