"""
API endpoints for enum definitions
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import authorize
from app.models.user import UserRole
from app.models.field_types import DataSourceType
from app.schemas.field_types import (
    EnumDefinitionResponse,
    EnumDefinitionCreate,
    EnumDefinitionUpdate,
    EnumOptionsResponse
)
from app.services.field_types import EnumDefinitionService
from app.dtos.custom_response_dto import CustomResponse
from app.utils.response import create_response


router = APIRouter()


@router.get(
    "/",
    response_model=CustomResponse[List[EnumDefinitionResponse]],
    summary="List all enum definitions",
    description="Get a list of all enum definitions with optional filters"
)
async def list_enums(
    active_only: bool = False,
    source_type: Optional[DataSourceType] = None,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize())
):
    """List all enum definitions"""
    service = EnumDefinitionService(db)
    enums = await service.list_enums(active_only, source_type)
    
    return create_response(
        data=[EnumDefinitionResponse.model_validate(enum) for enum in enums]
    )


@router.get(
    "/{enum_id}",
    response_model=CustomResponse[EnumDefinitionResponse],
    summary="Get enum definition by ID",
    description="Get a specific enum definition by its ID"
)
async def get_enum(
    enum_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize())
):
    """Get enum definition by ID"""
    service = EnumDefinitionService(db)
    enum_def = await service.get_enum(enum_id)
    
    return create_response(
        data=EnumDefinitionResponse.model_validate(enum_def)
    )


@router.get(
    "/by-name/{name}",
    response_model=CustomResponse[EnumDefinitionResponse],
    summary="Get enum definition by name",
    description="Get a specific enum definition by its name"
)
async def get_enum_by_name(
    name: str,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize())
):
    """Get enum definition by name"""
    service = EnumDefinitionService(db)
    enum_def = await service.get_enum_by_name(name)
    
    return create_response(
        data=EnumDefinitionResponse.model_validate(enum_def)
    )


@router.get(
    "/{enum_id}/options",
    response_model=CustomResponse[EnumOptionsResponse],
    summary="Get resolved enum options",
    description="Get the resolved options for an enum (static, database, or API)"
)
async def get_enum_options(
    enum_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize())
):
    """Get resolved enum options"""
    service = EnumDefinitionService(db)
    enum_def = await service.get_enum(enum_id)
    options = await service.resolve_enum_options(enum_id)
    
    return create_response(
        data=EnumOptionsResponse(
            enum_id=enum_def.id,
            enum_name=enum_def.name,
            options=options
        )
    )


@router.post(
    "/",
    response_model=CustomResponse[EnumDefinitionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create enum definition",
    description="Create a new enum definition"
)
async def create_enum(
    enum_in: EnumDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(authorize(allowed_roles=[UserRole.ADMIN.value]))
):
    """Create a new enum definition"""
    service = EnumDefinitionService(db)
    
    # Set created_by if not provided
    if not enum_in.created_by:
        enum_in.created_by = current_user.username
    
    enum_def = await service.create_enum(enum_in)
    
    return create_response(
        data=EnumDefinitionResponse.model_validate(enum_def),
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    "/{enum_id}",
    response_model=CustomResponse[EnumDefinitionResponse],
    summary="Update enum definition",
    description="Update an existing enum definition"
)
async def update_enum(
    enum_id: int,
    enum_in: EnumDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize(allowed_roles=[UserRole.ADMIN.value]))
):
    """Update enum definition"""
    service = EnumDefinitionService(db)
    enum_def = await service.update_enum(enum_id, enum_in)
    
    return create_response(
        data=EnumDefinitionResponse.model_validate(enum_def)
    )


@router.delete(
    "/{enum_id}",
    response_model=CustomResponse[str],
    summary="Delete enum definition",
    description="Delete an enum definition"
)
async def delete_enum(
    enum_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize(allowed_roles=[UserRole.ADMIN.value]))
):
    """Delete enum definition"""
    service = EnumDefinitionService(db)
    await service.delete_enum(enum_id)
    
    return create_response(
        data="Enum definition deleted successfully",
        status_code=status.HTTP_200_OK
    )
