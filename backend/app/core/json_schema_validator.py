"""
JSON Schema Validator with Nested Conditional Logic Support
Compliant with JSON Schema Draft-07 specification
"""
from typing import Dict, Any, List, Tuple, Optional
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator
from jsonschema.exceptions import SchemaError


class JSONSchemaValidator:
    """
    Standard JSON Schema validator with conditional logic support
    
    Supports:
    - type validation
    - required fields
    - nested conditions (if/then/else)
    - dependencies
    - default values
    - data type enforcement
    """
    
    @staticmethod
    def validate_schema(schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate that a schema is valid JSON Schema
        
        Args:
            schema: JSON Schema to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            Draft7Validator.check_schema(schema)
            return True, None
        except SchemaError as e:
            return False, str(e)
    
    @staticmethod
    def validate_data(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Validate data against JSON Schema
        
        Args:
            data: Data to validate
            schema: JSON Schema to validate against
            
        Returns:
            Tuple of (is_valid, errors)
            errors format: [{"field": "...", "message": "...", "constraint": "..."}]
        """
        validator = Draft7Validator(schema)
        errors = []
        
        # Apply default values first
        data_with_defaults = JSONSchemaValidator._apply_defaults(data, schema)
        
        # Validate
        for error in validator.iter_errors(data_with_defaults):
            field_path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
            
            errors.append({
                "field": field_path or error.path[0] if error.path else "unknown",
                "message": error.message,
                "constraint": error.validator
            })
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _apply_defaults(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values from schema to data
        
        Args:
            data: Input data
            schema: JSON Schema with default values
            
        Returns:
            Data with defaults applied
        """
        result = data.copy()
        
        if "properties" not in schema:
            return result
        
        for field_name, field_schema in schema["properties"].items():
            if field_name not in result and "default" in field_schema:
                result[field_name] = field_schema["default"]
            
            # Recursively apply defaults for nested objects
            if field_name in result and field_schema.get("type") == "object":
                result[field_name] = JSONSchemaValidator._apply_defaults(
                    result[field_name],
                    field_schema
                )
        
        return result
    
    @staticmethod
    def get_required_fields(schema: Dict[str, Any]) -> List[str]:
        """
        Extract required fields from schema
        
        Args:
            schema: JSON Schema
            
        Returns:
            List of required field names
        """
        return schema.get("required", [])
    
    @staticmethod
    def evaluate_conditionals(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate conditional logic (if/then/else) in schema
        
        JSON Schema conditionals example:
        {
          "if": { "properties": { "age": { "minimum": 18 } } },
          "then": { "required": ["telephone"] }
        }
        
        Args:
            data: Input data
            schema: JSON Schema with conditionals
            
        Returns:
            Effective schema after applying conditionals
        """
        effective_schema = schema.copy()
        
        # Check for if/then/else
        if "if" in schema:
            # Validate data against "if" condition
            if_validator = Draft7Validator(schema["if"])
            condition_met = if_validator.is_valid(data)
            
            if condition_met and "then" in schema:
                # Merge "then" schema
                effective_schema = JSONSchemaValidator._merge_schemas(
                    effective_schema,
                    schema["then"]
                )
            elif not condition_met and "else" in schema:
                # Merge "else" schema
                effective_schema = JSONSchemaValidator._merge_schemas(
                    effective_schema,
                    schema["else"]
                )
        
        return effective_schema
    
    @staticmethod
    def _merge_schemas(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two schemas (for conditional logic)
        
        Args:
            base: Base schema
            override: Schema to merge in
            
        Returns:
            Merged schema
        """
        result = base.copy()
        
        for key, value in override.items():
            if key == "required" and key in result:
                # Merge required arrays
                result[key] = list(set(result[key] + value))
            elif isinstance(value, dict) and key in result and isinstance(result[key], dict):
                # Recursively merge dicts
                result[key] = JSONSchemaValidator._merge_schemas(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @staticmethod
    def extract_field_metadata(schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract field metadata from JSON Schema for UI rendering
        
        Args:
            schema: JSON Schema
            
        Returns:
            List of field metadata dicts
        """
        fields = []
        
        if "properties" not in schema:
            return fields
        
        for field_name, field_schema in schema["properties"].items():
            field_meta = {
                "name": field_name,
                "type": field_schema.get("type", "string"),
                "title": field_schema.get("title", field_name),
                "description": field_schema.get("description"),
                "default": field_schema.get("default"),
                "required": field_name in schema.get("required", []),
                "constraints": {}
            }
            
            # Extract constraints
            if "minLength" in field_schema:
                field_meta["constraints"]["minLength"] = field_schema["minLength"]
            if "maxLength" in field_schema:
                field_meta["constraints"]["maxLength"] = field_schema["maxLength"]
            if "minimum" in field_schema:
                field_meta["constraints"]["minimum"] = field_schema["minimum"]
            if "maximum" in field_schema:
                field_meta["constraints"]["maximum"] = field_schema["maximum"]
            if "pattern" in field_schema:
                field_meta["constraints"]["pattern"] = field_schema["pattern"]
            if "enum" in field_schema:
                field_meta["constraints"]["enum"] = field_schema["enum"]
            
            fields.append(field_meta)
        
        return fields
