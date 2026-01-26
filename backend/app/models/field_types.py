"""
Field type models for dynamic form builder system
Supports predefined and custom field types with JSONSchema validation
"""
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base


class PredefinedFieldType(str, Enum):
    """Predefined field types with built-in JSONSchema definitions"""
    
    # Simple text types
    TEXT = "text"
    LONG_TEXT = "long_text"
    EMAIL = "email"
    PHONE = "phone"
    PASSWORD = "password"
    URL = "url"
    
    # Numeric types
    NUMBER = "number"
    INTEGER = "integer"
    CURRENCY = "currency"
    PERCENTAGE = "percentage"
    
    # Date/Time types
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    
    # Selection types
    BOOLEAN = "boolean"
    ENUM = "enum"
    MULTI_SELECT = "multi_select"
    
    # Special types
    FILE = "file"
    RATING = "rating"
    JSON_FIELD = "json"
    
    # Complex types
    ADDRESS = "address"
    ARRAY = "array"
    OBJECT = "object"


class DataSourceType(str, Enum):
    """Types of data sources for dynamic enum options"""
    STATIC = "static"  # Hardcoded options in schema
    DATABASE_TABLE = "database_table"  # Reference to database table
    API_ENDPOINT = "api_endpoint"  # External API call
    CUSTOM_QUERY = "custom_query"  # Custom SQL query


class EnumDefinition(Base):
    """
    Reusable enum definitions that can be referenced in forms
    Supports both static options and database-backed options
    """
    __tablename__ = "enum_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Data source configuration
    source_type = Column(String(50), nullable=False, default=DataSourceType.STATIC)
    
    # Static options (for STATIC source_type)
    # Format: [{"value": "active", "label": "Active"}, ...]
    static_options = Column(JSON, nullable=True)
    
    # Database table configuration (for DATABASE_TABLE source_type)
    table_name = Column(String(100), nullable=True)
    value_column = Column(String(100), nullable=True)
    label_column = Column(String(100), nullable=True)
    filter_conditions = Column(JSON, nullable=True)  # Optional WHERE conditions
    
    # API endpoint configuration (for API_ENDPOINT source_type)
    api_url = Column(String(500), nullable=True)
    api_method = Column(String(10), nullable=True)  # GET, POST, etc.
    api_headers = Column(JSON, nullable=True)
    api_transform = Column(Text, nullable=True)  # JS function to transform response
    
    # Custom query (for CUSTOM_QUERY source_type)
    custom_query = Column(Text, nullable=True)
    
    # Metadata
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_onupdate=func.now())
    created_by = Column(String(100), nullable=True)


class FieldTypeDefinition(Base):
    """
    Custom field type definitions that extend or override predefined types
    Allows users to create reusable field configurations
    """
    __tablename__ = "field_type_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Base type this extends
    base_type = Column(String(50), nullable=False)  # References PredefinedFieldType
    
    # JSONSchema definition for this field type
    schema_definition = Column(JSON, nullable=False)
    
    # UI configuration
    ui_widget = Column(String(100), nullable=True)  # Widget to use for rendering
    ui_options = Column(JSON, nullable=True)  # Additional UI configuration
    
    # Validation rules
    validation_rules = Column(JSON, nullable=True)  # Custom validation functions
    
    # Default value
    default_value = Column(JSON, nullable=True)
    
    # Metadata
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_onupdate=func.now())
    created_by = Column(String(100), nullable=True)


class FormFieldMapping(Base):
    """
    Maps specific fields in a form template to field type definitions
    Allows tracking which fields use which types for easier management
    """
    __tablename__ = "form_field_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False, index=True)
    field_name = Column(String(100), nullable=False)  # Field name in the form
    field_type_id = Column(Integer, ForeignKey('field_type_definitions.id'), nullable=True)
    enum_definition_id = Column(Integer, ForeignKey('enum_definitions.id'), nullable=True)
    
    # Relationships
    template = relationship("FormTemplate")
    field_type = relationship("FieldTypeDefinition")
    enum_definition = relationship("EnumDefinition")
    
    # Unique constraint: One mapping per field per template
    __table_args__ = (
        UniqueConstraint('template_id', 'field_name', name='uq_template_field'),
    )
