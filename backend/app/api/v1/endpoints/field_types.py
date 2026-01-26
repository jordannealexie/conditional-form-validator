"""
API endpoints for field type definitions
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import authorize
from app.models.user import UserRole
from app.schemas.field_types import (
    FieldTypeDefinitionResponse,
    FieldTypeDefinitionCreate,
    FieldTypeDefinitionUpdate,
    PredefinedFieldTypeListResponse,
    FormSchemaBuilder,
    FormSchemaResponse
)
from app.services.field_types import (
    FieldTypeDefinitionService,
    FormSchemaGeneratorService
)
from app.dtos.custom_response_dto import CustomResponse
from app.utils.response import create_response


router = APIRouter()


# ============================================================================
# Predefined Field Types
# ============================================================================

@router.get(
    "/predefined",
    response_model=CustomResponse[PredefinedFieldTypeListResponse],
    summary="List predefined field types",
    description="Get information about all predefined field types"
)
async def list_predefined_types(
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize())
):
    """List all predefined field types"""
    service = FieldTypeDefinitionService(db)
    predefined_types = service.get_predefined_types()
    
    return create_response(
        data=PredefinedFieldTypeListResponse(field_types=predefined_types)
    )


# ============================================================================
# Custom Field Type Definitions
# ============================================================================

@router.get(
    "/",
    response_model=CustomResponse[List[FieldTypeDefinitionResponse]],
    summary="List custom field type definitions",
    description="Get a list of all custom field type definitions"
)
async def list_field_types(
    active_only: bool = False,
    base_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize())
):
    """List all custom field type definitions"""
    service = FieldTypeDefinitionService(db)
    field_types = await service.list_field_types(active_only, base_type)
    
    return create_response(
        data=[FieldTypeDefinitionResponse.model_validate(ft) for ft in field_types]
    )


@router.get(
    "/{field_type_id}",
    response_model=CustomResponse[FieldTypeDefinitionResponse],
    summary="Get field type definition by ID",
    description="Get a specific field type definition by its ID"
)
async def get_field_type(
    field_type_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize())
):
    """Get field type definition by ID"""
    service = FieldTypeDefinitionService(db)
    field_type = await service.get_field_type(field_type_id)
    
    return create_response(
        data=FieldTypeDefinitionResponse.model_validate(field_type)
    )


@router.get(
    "/by-name/{name}",
    response_model=CustomResponse[FieldTypeDefinitionResponse],
    summary="Get field type definition by name",
    description="Get a specific field type definition by its name"
)
async def get_field_type_by_name(
    name: str,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize())
):
    """Get field type definition by name"""
    service = FieldTypeDefinitionService(db)
    field_type = await service.get_field_type_by_name(name)
    
    return create_response(
        data=FieldTypeDefinitionResponse.model_validate(field_type)
    )


@router.post(
    "/",
    response_model=CustomResponse[FieldTypeDefinitionResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Create field type definition",
    description="Create a new custom field type definition"
)
async def create_field_type(
    field_type_in: FieldTypeDefinitionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(authorize(allowed_roles=[UserRole.ADMIN.value]))
):
    """Create a new field type definition"""
    service = FieldTypeDefinitionService(db)
    
    # Set created_by if not provided
    if not field_type_in.created_by:
        field_type_in.created_by = current_user.username
    
    field_type = await service.create_field_type(field_type_in)
    
    return create_response(
        data=FieldTypeDefinitionResponse.model_validate(field_type),
        status_code=status.HTTP_201_CREATED
    )


@router.put(
    "/{field_type_id}",
    response_model=CustomResponse[FieldTypeDefinitionResponse],
    summary="Update field type definition",
    description="Update an existing field type definition"
)
async def update_field_type(
    field_type_id: int,
    field_type_in: FieldTypeDefinitionUpdate,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize(allowed_roles=[UserRole.ADMIN.value]))
):
    """Update field type definition"""
    service = FieldTypeDefinitionService(db)
    field_type = await service.update_field_type(field_type_id, field_type_in)
    
    return create_response(
        data=FieldTypeDefinitionResponse.model_validate(field_type)
    )


@router.delete(
    "/{field_type_id}",
    response_model=CustomResponse[str],
    summary="Delete field type definition",
    description="Delete a field type definition"
)
async def delete_field_type(
    field_type_id: int,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize(allowed_roles=[UserRole.ADMIN.value]))
):
    """Delete field type definition"""
    service = FieldTypeDefinitionService(db)
    await service.delete_field_type(field_type_id)
    
    return create_response(
        data="Field type definition deleted successfully",
        status_code=status.HTTP_200_OK
    )


# ============================================================================
# Schema Generation
# ============================================================================

@router.post(
    "/generate-schema",
    response_model=CustomResponse[FormSchemaResponse],
    summary="Generate form schema",
    description="Generate complete JSONSchema and UI schema from field configurations"
)
async def generate_schema(
    schema_builder: FormSchemaBuilder,
    db: AsyncSession = Depends(get_db),
    _ = Depends(authorize(allowed_roles=[UserRole.ADMIN.value]))
):
    """Generate form schema from field configurations"""
    service = FormSchemaGeneratorService(db)
    result = await service.generate_schema(schema_builder)
    
    return create_response(
        data=FormSchemaResponse(**result)
    )
