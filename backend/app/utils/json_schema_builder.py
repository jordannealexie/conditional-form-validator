"""
Utility for building JSONSchema definitions from field types
Provides predefined schemas for common field types
"""
from typing import Dict, Any, List, Optional
from app.models.field_types import PredefinedFieldType


class JSONSchemaBuilder:
    """Builder for creating JSONSchema definitions from field types"""
    
    @staticmethod
    def get_base_schema(field_type: PredefinedFieldType) -> Dict[str, Any]:
        """
        Get base JSONSchema for a predefined field type
        
        Args:
            field_type: Predefined field type enum
            
        Returns:
            JSONSchema definition dict
        """
        schemas = {
            # Text types
            PredefinedFieldType.TEXT: {
                "type": "string",
                "minLength": 1,
                "maxLength": 255
            },
            
            PredefinedFieldType.LONG_TEXT: {
                "type": "string",
                "minLength": 1,
                "maxLength": 10000
            },
            
            PredefinedFieldType.EMAIL: {
                "type": "string",
                "format": "email",
                "pattern": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            },
            
            PredefinedFieldType.PHONE: {
                "type": "string",
                "pattern": r"^\+?[1-9]\d{1,14}$",  # E.164 format
                "description": "Phone number in E.164 format"
            },
            
            PredefinedFieldType.PASSWORD: {
                "type": "string",
                "minLength": 8,
                "maxLength": 128,
                "pattern": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]",
                "description": "Password must contain uppercase, lowercase, number, and special character"
            },
            
            PredefinedFieldType.URL: {
                "type": "string",
                "format": "uri",
                "pattern": r"^https?://.+"
            },
            
            # Numeric types
            PredefinedFieldType.NUMBER: {
                "type": "number"
            },
            
            PredefinedFieldType.INTEGER: {
                "type": "integer"
            },
            
            PredefinedFieldType.CURRENCY: {
                "type": "number",
                "minimum": 0,
                "multipleOf": 0.01,
                "description": "Currency amount (2 decimal places)"
            },
            
            PredefinedFieldType.PERCENTAGE: {
                "type": "number",
                "minimum": 0,
                "maximum": 100,
                "description": "Percentage value (0-100)"
            },
            
            # Date/Time types
            PredefinedFieldType.DATE: {
                "type": "string",
                "format": "date",
                "pattern": r"^\d{4}-\d{2}-\d{2}$"
            },
            
            PredefinedFieldType.TIME: {
                "type": "string",
                "format": "time",
                "pattern": r"^\d{2}:\d{2}:\d{2}$"
            },
            
            PredefinedFieldType.DATETIME: {
                "type": "string",
                "format": "date-time"
            },
            
            # Selection types
            PredefinedFieldType.BOOLEAN: {
                "type": "boolean"
            },
            
            PredefinedFieldType.ENUM: {
                "type": "string",
                "enum": []  # Will be populated with options
            },
            
            PredefinedFieldType.MULTI_SELECT: {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "uniqueItems": True
            },
            
            # Special types
            PredefinedFieldType.FILE: {
                "type": "string",
                "format": "uuid",
                "description": "File upload token"
            },
            
            PredefinedFieldType.RATING: {
                "type": "integer",
                "minimum": 1,
                "maximum": 5
            },
            
            PredefinedFieldType.JSON_FIELD: {
                "type": "object"
            },
            
            # Complex types
            PredefinedFieldType.ADDRESS: {
                "type": "object",
                "properties": {
                    "street": {"type": "string", "minLength": 1},
                    "barangay": {"type": "string", "minLength": 1},
                    "city": {"type": "string", "minLength": 1},
                    "province": {"type": "string", "minLength": 1},
                    "zip_code": {"type": "string", "pattern": r"^\d{4}$"},
                    "country": {"type": "string", "default": "Philippines"}
                },
                "required": ["street", "barangay", "city", "province", "zip_code"]
            },
            
            PredefinedFieldType.ARRAY: {
                "type": "array",
                "items": {}  # Will be specified by user
            },
            
            PredefinedFieldType.OBJECT: {
                "type": "object",
                "properties": {}  # Will be specified by user
            }
        }
        
        return schemas.get(field_type, {"type": "string"})
    
    @staticmethod
    def add_validation_rules(
        schema: Dict[str, Any],
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add validation rules to a schema
        
        Args:
            schema: Base schema
            rules: Validation rules to add
            
        Returns:
            Enhanced schema with validation rules
        """
        enhanced_schema = schema.copy()
        
        # String validations
        if rules.get("minLength"):
            enhanced_schema["minLength"] = rules["minLength"]
        if rules.get("maxLength"):
            enhanced_schema["maxLength"] = rules["maxLength"]
        if rules.get("pattern"):
            enhanced_schema["pattern"] = rules["pattern"]
        
        # Numeric validations
        if rules.get("minimum") is not None:
            enhanced_schema["minimum"] = rules["minimum"]
        if rules.get("maximum") is not None:
            enhanced_schema["maximum"] = rules["maximum"]
        if rules.get("exclusiveMinimum") is not None:
            enhanced_schema["exclusiveMinimum"] = rules["exclusiveMinimum"]
        if rules.get("exclusiveMaximum") is not None:
            enhanced_schema["exclusiveMaximum"] = rules["exclusiveMaximum"]
        if rules.get("multipleOf"):
            enhanced_schema["multipleOf"] = rules["multipleOf"]
        
        # Array validations
        if rules.get("minItems"):
            enhanced_schema["minItems"] = rules["minItems"]
        if rules.get("maxItems"):
            enhanced_schema["maxItems"] = rules["maxItems"]
        if rules.get("uniqueItems") is not None:
            enhanced_schema["uniqueItems"] = rules["uniqueItems"]
        
        # Enum validations
        if rules.get("enum"):
            enhanced_schema["enum"] = rules["enum"]
        
        # Const validation
        if rules.get("const") is not None:
            enhanced_schema["const"] = rules["const"]
        
        return enhanced_schema
    
    @staticmethod
    def create_conditional_schema(
        condition: Dict[str, Any],
        then_schema: Dict[str, Any],
        else_schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create conditional schema using if/then/else
        
        Args:
            condition: Condition to check (if)
            then_schema: Schema to apply if condition is true (then)
            else_schema: Schema to apply if condition is false (else)
            
        Returns:
            Conditional schema
        """
        schema = {
            "if": condition,
            "then": then_schema
        }
        
        if else_schema:
            schema["else"] = else_schema
        
        return schema
    
    @staticmethod
    def create_composite_schema(
        schemas: List[Dict[str, Any]],
        composition: str = "allOf"
    ) -> Dict[str, Any]:
        """
        Create composite schema using allOf, anyOf, or oneOf
        
        Args:
            schemas: List of schemas to combine
            composition: Type of composition (allOf, anyOf, oneOf)
            
        Returns:
            Composite schema
        """
        if composition not in ["allOf", "anyOf", "oneOf"]:
            raise ValueError(f"Invalid composition type: {composition}")
        
        return {composition: schemas}
    
    @staticmethod
    def create_dependent_schema(
        field_name: str,
        dependent_schemas: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Create dependent schema where fields are required based on other field values
        
        Args:
            field_name: Field that others depend on
            dependent_schemas: Map of value -> schema
            
        Returns:
            Schema with dependencies
        """
        return {
            "dependencies": {
                field_name: {
                    "oneOf": [
                        {
                            "properties": {
                                field_name: {"const": value}
                            },
                            **schema
                        }
                        for value, schema in dependent_schemas.items()
                    ]
                }
            }
        }
    
    @staticmethod
    def build_form_schema(
        fields: List[Dict[str, Any]],
        required_fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Build complete form schema from field definitions
        
        Args:
            fields: List of field definitions
            required_fields: List of required field names
            
        Returns:
            Complete JSONSchema for form
        """
        properties = {}
        
        for field in fields:
            field_name = field.get("name")
            field_type = field.get("type")
            field_config = field.get("config", {})
            
            if not field_name or not field_type:
                continue
            
            # Get base schema for field type
            try:
                base_schema = JSONSchemaBuilder.get_base_schema(
                    PredefinedFieldType(field_type)
                )
            except ValueError:
                # Custom field type - use provided schema
                base_schema = field_config.get("schema", {"type": "string"})
            
            # Add validation rules
            if "validation" in field_config:
                base_schema = JSONSchemaBuilder.add_validation_rules(
                    base_schema,
                    field_config["validation"]
                )
            
            # Add enum options
            if field_type == PredefinedFieldType.ENUM.value and "options" in field_config:
                base_schema["enum"] = [opt["value"] for opt in field_config["options"]]
            
            # Add description
            if "description" in field_config:
                base_schema["description"] = field_config["description"]
            
            # Add default value
            if "default" in field_config:
                base_schema["default"] = field_config["default"]
            
            properties[field_name] = base_schema
        
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties
        }
        
        if required_fields:
            schema["required"] = required_fields
        
        return schema
    
    @staticmethod
    def get_ui_schema(field_type: PredefinedFieldType) -> Dict[str, Any]:
        """
        Get recommended UI schema for a field type
        
        Args:
            field_type: Predefined field type
            
        Returns:
            UI schema recommendations
        """
        ui_schemas = {
            PredefinedFieldType.TEXT: {
                "ui:widget": "text"
            },
            PredefinedFieldType.LONG_TEXT: {
                "ui:widget": "textarea",
                "ui:options": {
                    "rows": 5
                }
            },
            PredefinedFieldType.EMAIL: {
                "ui:widget": "email"
            },
            PredefinedFieldType.PHONE: {
                "ui:widget": "tel"
            },
            PredefinedFieldType.PASSWORD: {
                "ui:widget": "password"
            },
            PredefinedFieldType.URL: {
                "ui:widget": "uri"
            },
            PredefinedFieldType.NUMBER: {
                "ui:widget": "updown"
            },
            PredefinedFieldType.INTEGER: {
                "ui:widget": "updown"
            },
            PredefinedFieldType.CURRENCY: {
                "ui:widget": "currency",
                "ui:options": {
                    "currency": "PHP"
                }
            },
            PredefinedFieldType.PERCENTAGE: {
                "ui:widget": "range"
            },
            PredefinedFieldType.DATE: {
                "ui:widget": "date"
            },
            PredefinedFieldType.TIME: {
                "ui:widget": "time"
            },
            PredefinedFieldType.DATETIME: {
                "ui:widget": "datetime"
            },
            PredefinedFieldType.BOOLEAN: {
                "ui:widget": "checkbox"
            },
            PredefinedFieldType.ENUM: {
                "ui:widget": "select"
            },
            PredefinedFieldType.MULTI_SELECT: {
                "ui:widget": "checkboxes"
            },
            PredefinedFieldType.FILE: {
                "ui:widget": "file"
            },
            PredefinedFieldType.RATING: {
                "ui:widget": "rating"
            },
            PredefinedFieldType.ADDRESS: {
                "ui:widget": "address"
            }
        }
        
        return ui_schemas.get(field_type, {})
