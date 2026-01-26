"""
Pydantic schemas for field type system
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from app.models.field_types import PredefinedFieldType, DataSourceType


# ============================================================================
# Enum Definition Schemas
# ============================================================================

class EnumDefinitionBase(BaseModel):
    """Base schema for enum definitions"""
    name: str = Field(..., min_length=1, max_length=100, description="Unique enum name")
    display_name: str = Field(..., min_length=1, max_length=255, description="Display name")
    description: Optional[str] = Field(None, description="Enum description")
    source_type: DataSourceType = Field(DataSourceType.STATIC, description="Data source type")
    static_options: Optional[List[Dict[str, Any]]] = Field(None, description="Static options list")
    table_name: Optional[str] = Field(None, description="Database table name")
    value_column: Optional[str] = Field(None, description="Column for option value")
    label_column: Optional[str] = Field(None, description="Column for option label")
    filter_conditions: Optional[Dict[str, Any]] = Field(None, description="Filter conditions")
    api_url: Optional[str] = Field(None, description="API endpoint URL")
    api_method: Optional[str] = Field("GET", description="HTTP method")
    api_headers: Optional[Dict[str, str]] = Field(None, description="API headers")
    api_transform: Optional[str] = Field(None, description="Transform function")
    custom_query: Optional[str] = Field(None, description="Custom SQL query")
    active: bool = Field(True, description="Whether enum is active")


class EnumDefinitionCreate(EnumDefinitionBase):
    """Schema for creating enum definition"""
    created_by: Optional[str] = Field(None, description="Username of creator")


class EnumDefinitionUpdate(BaseModel):
    """Schema for updating enum definition"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    source_type: Optional[DataSourceType] = None
    static_options: Optional[List[Dict[str, Any]]] = None
    table_name: Optional[str] = None
    value_column: Optional[str] = None
    label_column: Optional[str] = None
    filter_conditions: Optional[Dict[str, Any]] = None
    api_url: Optional[str] = None
    api_method: Optional[str] = None
    api_headers: Optional[Dict[str, str]] = None
    api_transform: Optional[str] = None
    custom_query: Optional[str] = None
    active: Optional[bool] = None


class EnumDefinitionResponse(EnumDefinitionBase):
    """Schema for enum definition response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class EnumOptionsResponse(BaseModel):
    """Schema for resolved enum options"""
    enum_id: int
    enum_name: str
    options: List[Dict[str, Any]] = Field(..., description="List of {value, label} options")


# ============================================================================
# Field Type Definition Schemas
# ============================================================================

class FieldTypeDefinitionBase(BaseModel):
    """Base schema for field type definitions"""
    name: str = Field(..., min_length=1, max_length=100, description="Unique field type name")
    display_name: str = Field(..., min_length=1, max_length=255, description="Display name")
    description: Optional[str] = Field(None, description="Field type description")
    base_type: str = Field(..., description="Base predefined field type")
    schema_definition: Dict[str, Any] = Field(..., description="JSONSchema definition")
    ui_widget: Optional[str] = Field(None, description="UI widget type")
    ui_options: Optional[Dict[str, Any]] = Field(None, description="UI configuration")
    validation_rules: Optional[Dict[str, Any]] = Field(None, description="Custom validation rules")
    default_value: Optional[Any] = Field(None, description="Default value")
    active: bool = Field(True, description="Whether field type is active")


class FieldTypeDefinitionCreate(FieldTypeDefinitionBase):
    """Schema for creating field type definition"""
    created_by: Optional[str] = Field(None, description="Username of creator")


class FieldTypeDefinitionUpdate(BaseModel):
    """Schema for updating field type definition"""
    display_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    base_type: Optional[str] = None
    schema_definition: Optional[Dict[str, Any]] = None
    ui_widget: Optional[str] = None
    ui_options: Optional[Dict[str, Any]] = None
    validation_rules: Optional[Dict[str, Any]] = None
    default_value: Optional[Any] = None
    active: Optional[bool] = None


class FieldTypeDefinitionResponse(FieldTypeDefinitionBase):
    """Schema for field type definition response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Field Configuration Schemas
# ============================================================================

class FieldConfig(BaseModel):
    """Configuration for a single form field"""
    name: str = Field(..., description="Field name (property key)")
    label: str = Field(..., description="Human-readable label")
    type: str = Field(..., description="Field type (predefined or custom)")
    description: Optional[str] = Field(None, description="Field description/help text")
    required: bool = Field(False, description="Whether field is required")
    default: Optional[Any] = Field(None, description="Default value")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    
    # Validation
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    
    # Enum configuration
    enum_definition_id: Optional[int] = Field(None, description="ID of enum definition")
    options: Optional[List[Dict[str, Any]]] = Field(None, description="Static options for enum")
    
    # Conditional logic
    visible_when: Optional[Dict[str, Any]] = Field(None, description="Visibility conditions")
    required_when: Optional[Dict[str, Any]] = Field(None, description="Required conditions")
    disabled_when: Optional[Dict[str, Any]] = Field(None, description="Disabled conditions")
    
    # UI configuration
    ui_widget: Optional[str] = Field(None, description="Override UI widget")
    ui_options: Optional[Dict[str, Any]] = Field(None, description="UI-specific options")
    
    # Complex types
    properties: Optional[Dict[str, "FieldConfig"]] = Field(None, description="Properties for object type")
    items: Optional["FieldConfig"] = Field(None, description="Item schema for array type")


class FormSchemaBuilder(BaseModel):
    """Schema for building complete form schemas"""
    fields: List[FieldConfig] = Field(..., description="List of field configurations")
    title: Optional[str] = Field(None, description="Form title")
    description: Optional[str] = Field(None, description="Form description")
    conditionals: Optional[List[Dict[str, Any]]] = Field(None, description="Form-level conditional logic")


class FormSchemaResponse(BaseModel):
    """Response containing generated form schema"""
    schema_json: Dict[str, Any] = Field(..., description="Generated JSONSchema")
    ui_schema: Dict[str, Any] = Field(..., description="Generated UI schema")
    fields: List[FieldConfig] = Field(..., description="Field configurations")


# ============================================================================
# Predefined Field Type Schemas
# ============================================================================

class PredefinedFieldTypeInfo(BaseModel):
    """Information about a predefined field type"""
    type: PredefinedFieldType
    display_name: str
    description: str
    base_schema: Dict[str, Any]
    ui_schema: Dict[str, Any]
    example_value: Any


class PredefinedFieldTypeListResponse(BaseModel):
    """List of all predefined field types"""
    field_types: List[PredefinedFieldTypeInfo]
