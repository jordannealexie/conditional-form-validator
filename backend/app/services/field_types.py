"""
Service layer for field type system
Business logic for managing field types, enum definitions, and form schema generation
"""
from typing import List, Optional, Dict, Any
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.field_types import (
    EnumDefinition,
    FieldTypeDefinition,
    DataSourceType,
    PredefinedFieldType
)
from app.repositories.field_types import (
    EnumDefinitionRepository,
    FieldTypeDefinitionRepository,
    FormFieldMappingRepository
)
from app.schemas.field_types import (
    EnumDefinitionCreate,
    EnumDefinitionUpdate,
    FieldTypeDefinitionCreate,
    FieldTypeDefinitionUpdate,
    FieldConfig,
    FormSchemaBuilder,
    PredefinedFieldTypeInfo
)
from app.utils.json_schema_builder import JSONSchemaBuilder
from app.exceptions.http_exceptions import NotFoundError, ConflictError


class EnumDefinitionService:
    """Service for managing enum definitions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EnumDefinitionRepository()
    
    async def create_enum(self, obj_in: EnumDefinitionCreate) -> EnumDefinition:
        """Create a new enum definition"""
        # Check if name already exists
        existing = await self.repo.get_by_name(self.db, obj_in.name)
        if existing:
            raise ConflictError(
                error_code="ENUM_NAME_EXISTS",
                detail=f"Enum with name '{obj_in.name}' already exists"
            )
        
        # Validate source type configuration
        self._validate_enum_config(obj_in)
        
        return await self.repo.create(self.db, **obj_in.model_dump())
    
    async def get_enum(self, enum_id: int) -> EnumDefinition:
        """Get enum definition by ID"""
        enum_def = await self.repo.get_by_id(self.db, enum_id)
        if not enum_def:
            raise NotFoundError(
                error_code="ENUM_NOT_FOUND",
                detail=f"Enum with ID {enum_id} not found"
            )
        return enum_def
    
    async def get_enum_by_name(self, name: str) -> EnumDefinition:
        """Get enum definition by name"""
        enum_def = await self.repo.get_by_name(self.db, name)
        if not enum_def:
            raise NotFoundError(
                error_code="ENUM_NOT_FOUND",
                detail=f"Enum with name '{name}' not found"
            )
        return enum_def
    
    async def list_enums(
        self,
        active_only: bool = False,
        source_type: Optional[DataSourceType] = None
    ) -> List[EnumDefinition]:
        """List all enum definitions"""
        return await self.repo.get_all(self.db, active_only, source_type)
    
    async def update_enum(
        self,
        enum_id: int,
        obj_in: EnumDefinitionUpdate
    ) -> EnumDefinition:
        """Update enum definition"""
        enum_def = await self.get_enum(enum_id)
        
        # Validate updated configuration
        if obj_in.source_type:
            self._validate_enum_config(obj_in)
        
        update_data = obj_in.model_dump(exclude_unset=True)
        return await self.repo.update(self.db, enum_def, **update_data)
    
    async def delete_enum(self, enum_id: int) -> None:
        """Delete enum definition"""
        enum_def = await self.get_enum(enum_id)
        await self.repo.delete(self.db, enum_def)
    
    async def resolve_enum_options(self, enum_id: int) -> List[Dict[str, Any]]:
        """Resolve enum options based on source type"""
        enum_def = await self.get_enum(enum_id)
        
        if enum_def.source_type == DataSourceType.API_ENDPOINT:
            return await self._resolve_api_options(enum_def)
        
        return await self.repo.resolve_options(self.db, enum_def)
    
    async def _resolve_api_options(self, enum_def: EnumDefinition) -> List[Dict[str, Any]]:
        """Resolve options from API endpoint"""
        if not enum_def.api_url:
            raise ValueError("API URL not configured")
        
        headers = enum_def.api_headers or {}
        method = enum_def.api_method or "GET"
        
        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(enum_def.api_url, headers=headers)
            elif method == "POST":
                response = await client.post(enum_def.api_url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            data = response.json()
            
            # Transform response if transform function provided
            if enum_def.api_transform:
                # In production, use a safe sandbox like py_mini_racer
                # For now, assume data is already in correct format
                pass
            
            return data if isinstance(data, list) else []
    
    def _validate_enum_config(self, enum_config) -> None:
        """Validate enum configuration based on source type"""
        source_type = getattr(enum_config, 'source_type', None)
        
        if source_type == DataSourceType.STATIC:
            if not getattr(enum_config, 'static_options', None):
                raise ValueError("Static options required for STATIC source type")
        
        elif source_type == DataSourceType.DATABASE_TABLE:
            required = ['table_name', 'value_column', 'label_column']
            for field in required:
                if not getattr(enum_config, field, None):
                    raise ValueError(f"{field} required for DATABASE_TABLE source type")
        
        elif source_type == DataSourceType.API_ENDPOINT:
            if not getattr(enum_config, 'api_url', None):
                raise ValueError("api_url required for API_ENDPOINT source type")
        
        elif source_type == DataSourceType.CUSTOM_QUERY:
            if not getattr(enum_config, 'custom_query', None):
                raise ValueError("custom_query required for CUSTOM_QUERY source type")


class FieldTypeDefinitionService:
    """Service for managing custom field type definitions"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = FieldTypeDefinitionRepository()
    
    async def create_field_type(
        self,
        obj_in: FieldTypeDefinitionCreate
    ) -> FieldTypeDefinition:
        """Create a new field type definition"""
        # Check if name already exists
        existing = await self.repo.get_by_name(self.db, obj_in.name)
        if existing:
            raise ConflictError(
                error_code="FIELD_TYPE_NAME_EXISTS",
                detail=f"Field type with name '{obj_in.name}' already exists"
            )
        
        # Validate base type
        try:
            PredefinedFieldType(obj_in.base_type)
        except ValueError:
            raise ValueError(f"Invalid base type: {obj_in.base_type}")
        
        return await self.repo.create(self.db, **obj_in.model_dump())
    
    async def get_field_type(self, field_type_id: int) -> FieldTypeDefinition:
        """Get field type definition by ID"""
        field_type = await self.repo.get_by_id(self.db, field_type_id)
        if not field_type:
            raise NotFoundError(
                error_code="FIELD_TYPE_NOT_FOUND",
                detail=f"Field type with ID {field_type_id} not found"
            )
        return field_type
    
    async def get_field_type_by_name(self, name: str) -> FieldTypeDefinition:
        """Get field type definition by name"""
        field_type = await self.repo.get_by_name(self.db, name)
        if not field_type:
            raise NotFoundError(
                error_code="FIELD_TYPE_NOT_FOUND",
                detail=f"Field type with name '{name}' not found"
            )
        return field_type
    
    async def list_field_types(
        self,
        active_only: bool = False,
        base_type: Optional[str] = None
    ) -> List[FieldTypeDefinition]:
        """List all field type definitions"""
        return await self.repo.get_all(self.db, active_only, base_type)
    
    async def update_field_type(
        self,
        field_type_id: int,
        obj_in: FieldTypeDefinitionUpdate
    ) -> FieldTypeDefinition:
        """Update field type definition"""
        field_type = await self.get_field_type(field_type_id)
        
        # Validate base type if being updated
        if obj_in.base_type:
            try:
                PredefinedFieldType(obj_in.base_type)
            except ValueError:
                raise ValueError(f"Invalid base type: {obj_in.base_type}")
        
        update_data = obj_in.model_dump(exclude_unset=True)
        return await self.repo.update(self.db, field_type, **update_data)
    
    async def delete_field_type(self, field_type_id: int) -> None:
        """Delete field type definition"""
        field_type = await self.get_field_type(field_type_id)
        await self.repo.delete(self.db, field_type)
    
    def get_predefined_types(self) -> List[PredefinedFieldTypeInfo]:
        """Get information about all predefined field types"""
        predefined_info = []
        
        type_descriptions = {
            PredefinedFieldType.TEXT: ("Text Field", "Single-line text input", "John Doe"),
            PredefinedFieldType.LONG_TEXT: ("Long Text", "Multi-line text area", "Description..."),
            PredefinedFieldType.EMAIL: ("Email", "Email address input", "user@example.com"),
            PredefinedFieldType.PHONE: ("Phone Number", "Phone number input", "+639171234567"),
            PredefinedFieldType.PASSWORD: ("Password", "Password input (hidden)", "********"),
            PredefinedFieldType.URL: ("URL", "Website URL input", "https://example.com"),
            PredefinedFieldType.NUMBER: ("Number", "Numeric input (decimal)", "123.45"),
            PredefinedFieldType.INTEGER: ("Integer", "Whole number input", "42"),
            PredefinedFieldType.CURRENCY: ("Currency", "Money amount", "1234.56"),
            PredefinedFieldType.PERCENTAGE: ("Percentage", "Percentage value (0-100)", "75"),
            PredefinedFieldType.DATE: ("Date", "Date picker", "2026-01-26"),
            PredefinedFieldType.TIME: ("Time", "Time picker", "14:30:00"),
            PredefinedFieldType.DATETIME: ("Date & Time", "Date and time picker", "2026-01-26T14:30:00"),
            PredefinedFieldType.BOOLEAN: ("Boolean", "Yes/No checkbox", True),
            PredefinedFieldType.ENUM: ("Dropdown", "Single selection from list", "option1"),
            PredefinedFieldType.MULTI_SELECT: ("Multi-Select", "Multiple selections", ["option1", "option2"]),
            PredefinedFieldType.FILE: ("File Upload", "File upload input", "uuid-token"),
            PredefinedFieldType.RATING: ("Rating", "Star rating (1-5)", 4),
            PredefinedFieldType.JSON_FIELD: ("JSON", "JSON object", {"key": "value"}),
            PredefinedFieldType.ADDRESS: ("Address", "Complete address", {
                "street": "123 Main St",
                "barangay": "Poblacion",
                "city": "Manila",
                "province": "Metro Manila",
                "zip_code": "1000"
            }),
            PredefinedFieldType.ARRAY: ("Array", "List of items", []),
            PredefinedFieldType.OBJECT: ("Object", "Complex object", {}),
        }
        
        for field_type in PredefinedFieldType:
            display_name, description, example = type_descriptions.get(
                field_type,
                (field_type.value.title(), "", None)
            )
            
            predefined_info.append(PredefinedFieldTypeInfo(
                type=field_type,
                display_name=display_name,
                description=description,
                base_schema=JSONSchemaBuilder.get_base_schema(field_type),
                ui_schema=JSONSchemaBuilder.get_ui_schema(field_type),
                example_value=example
            ))
        
        return predefined_info


class FormSchemaGeneratorService:
    """Service for generating complete form schemas from field configurations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.enum_service = EnumDefinitionService(db)
        self.field_type_service = FieldTypeDefinitionService(db)
    
    async def generate_schema(
        self,
        schema_builder: FormSchemaBuilder
    ) -> Dict[str, Any]:
        """
        Generate complete JSONSchema and UI schema from field configurations
        
        Returns dict with schema_json, ui_schema, and fields
        """
        properties = {}
        required = []
        ui_schema = {}
        
        for field in schema_builder.fields:
            # Build field schema
            field_schema = await self._build_field_schema(field)
            properties[field.name] = field_schema
            
            # Track required fields
            if field.required:
                required.append(field.name)
            
            # Build UI schema
            ui_schema[field.name] = self._build_ui_schema(field)
        
        # Build complete schema
        schema_json = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties
        }
        
        if required:
            schema_json["required"] = required
        
        if schema_builder.title:
            schema_json["title"] = schema_builder.title
        
        if schema_builder.description:
            schema_json["description"] = schema_builder.description
        
        # Add conditional logic if present
        if schema_builder.conditionals:
            for conditional in schema_builder.conditionals:
                schema_json.update(conditional)
        
        return {
            "schema_json": schema_json,
            "ui_schema": ui_schema,
            "fields": [field.model_dump() for field in schema_builder.fields]
        }
    
    async def _build_field_schema(self, field: FieldConfig) -> Dict[str, Any]:
        """Build JSONSchema for a single field"""
        # Try to get predefined type
        try:
            field_type_enum = PredefinedFieldType(field.type)
            base_schema = JSONSchemaBuilder.get_base_schema(field_type_enum)
        except ValueError:
            # Try custom field type
            try:
                custom_type = await self.field_type_service.get_field_type_by_name(field.type)
                base_schema = custom_type.schema_definition.copy()
            except NotFoundError:
                # Fallback to string
                base_schema = {"type": "string"}
        
        # Add validation rules
        if field.validation:
            base_schema = JSONSchemaBuilder.add_validation_rules(
                base_schema,
                field.validation
            )
        
        # Handle enum options
        if field.type == PredefinedFieldType.ENUM.value:
            if field.enum_definition_id:
                options = await self.enum_service.resolve_enum_options(
                    field.enum_definition_id
                )
                base_schema["enum"] = [opt["value"] for opt in options]
            elif field.options:
                base_schema["enum"] = [opt["value"] for opt in field.options]
        
        # Add description
        if field.description:
            base_schema["description"] = field.description
        
        # Add default value
        if field.default is not None:
            base_schema["default"] = field.default
        
        # Handle complex types
        if field.properties:
            # Object type with nested properties
            base_schema["properties"] = {
                name: await self._build_field_schema(prop)
                for name, prop in field.properties.items()
            }
        
        if field.items:
            # Array type with item schema
            base_schema["items"] = await self._build_field_schema(field.items)
        
        return base_schema
    
    def _build_ui_schema(self, field: FieldConfig) -> Dict[str, Any]:
        """Build UI schema for a single field"""
        ui_schema = {}
        
        # Get base UI schema for field type
        try:
            field_type_enum = PredefinedFieldType(field.type)
            ui_schema = JSONSchemaBuilder.get_ui_schema(field_type_enum).copy()
        except ValueError:
            pass
        
        # Override with custom widget if specified
        if field.ui_widget:
            ui_schema["ui:widget"] = field.ui_widget
        
        # Add UI options
        if field.ui_options:
            ui_schema["ui:options"] = field.ui_options
        
        # Add placeholder
        if field.placeholder:
            ui_schema["ui:placeholder"] = field.placeholder
        
        # Add conditional visibility
        if field.visible_when:
            ui_schema["ui:visibleWhen"] = field.visible_when
        
        if field.disabled_when:
            ui_schema["ui:disabledWhen"] = field.disabled_when
        
        return ui_schema
