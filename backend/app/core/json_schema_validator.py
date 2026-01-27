"""
JSON Schema Validator with Nested Conditional Logic Support
Compliant with JSON Schema Draft-07 specification
Includes validator caching for performance optimization
"""
from typing import Dict, Any, List, Tuple, Optional
import jsonschema
from jsonschema import validate, ValidationError, Draft7Validator
from jsonschema.exceptions import SchemaError
from functools import lru_cache
import hashlib
import json


# Global validator cache using LRU cache (thread-safe)
@lru_cache(maxsize=256)
def _get_cached_validator(schema_hash: str, schema_json: str) -> Draft7Validator:
    """
    Get or create cached Draft7Validator
    
    Uses schema hash for cache key to avoid recompiling same schemas
    
    Args:
        schema_hash: SHA256 hash of schema (for cache key)
        schema_json: JSON string of schema (for validation)
        
    Returns:
        Compiled Draft7Validator instance
    """
    schema = json.loads(schema_json)
    return Draft7Validator(schema)


class JSONSchemaValidator:
    """
    Standard JSON Schema validator with conditional logic support
    
    Supports:
    - type validation
    - required fields (strict empty check)
    - nested conditions (if/then/else)
    - dependencies
    - default values
    - data type enforcement
    """
    
    @staticmethod
    def is_empty_value(value: Any) -> bool:
        """
        Check if a value should be considered 'empty' for required field validation.
        
        Empty values include:
        - None / null
        - Empty string ""
        - Empty array []
        - Empty object {} (for Address/JSON fields)
        - Whitespace-only string "   "
        
        Returns:
            True if value is considered empty
        """
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        if isinstance(value, dict) and len(value) == 0:
            return True
        return False
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], schema: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Strictly validate required fields - reject empty values.
        
        Args:
            data: Data to validate
            schema: JSON Schema with required fields
            
        Returns:
            List of errors for missing/empty required fields
        """
        errors = []
        required_fields = schema.get("required", [])
        properties = schema.get("properties", {})
        
        for field_name in required_fields:
            value = data.get(field_name)
            field_schema = properties.get(field_name, {})
            field_type = field_schema.get("type", "string")
            
            # Check if value is empty
            if JSONSchemaValidator.is_empty_value(value):
                errors.append({
                    "field": field_name,
                    "message": f"Required field '{field_name}' is missing or empty",
                    "constraint": "required"
                })
                continue
            
            # For object types (like Address), validate nested required fields
            if field_type == "object" and isinstance(value, dict):
                nested_required = field_schema.get("required", [])
                nested_properties = field_schema.get("properties", {})
                for nested_field in nested_required:
                    nested_value = value.get(nested_field)
                    if JSONSchemaValidator.is_empty_value(nested_value):
                        errors.append({
                            "field": f"{field_name}.{nested_field}",
                            "message": f"Required field '{field_name}.{nested_field}' is missing or empty",
                            "constraint": "required"
                        })
        
        return errors
    
    @staticmethod
    def validate_type_strict(value: Any, expected_type: str, field_name: str) -> Optional[Dict[str, str]]:
        """
        Strictly validate that value type matches expected type.
        
        Rules:
        - Text fields: CANNOT accept integers or floats
        - Numeric fields: CANNOT accept strings
        - Date fields: CANNOT accept numbers (must be string in date format)
        - Boolean fields: CANNOT accept strings or numbers
        
        Args:
            value: Value to check
            expected_type: Expected JSON Schema type
            field_name: Name of field for error message
            
        Returns:
            Error dict if type mismatch, None if valid
        """
        if value is None:
            return None  # Let required validation handle this
        
        type_mapping = {
            'string': (str,),
            'number': (int, float),
            'integer': (int,),
            'boolean': (bool,),
            'array': (list,),
            'object': (dict,)
        }
        
        forbidden_types = {
            'string': (int, float, bool, list, dict),  # Text fields reject numbers/booleans
            'number': (str, bool, list, dict),          # Number fields reject strings
            'integer': (str, float, bool, list, dict),  # Integer fields reject strings and floats
            'boolean': (str, int, float, list, dict),   # Boolean fields reject everything else
            'array': (str, int, float, bool, dict),
            'object': (str, int, float, bool, list)
        }
        
        # Check if value is of a forbidden type
        forbidden = forbidden_types.get(expected_type, ())
        if isinstance(value, forbidden):
            actual_type = type(value).__name__
            return {
                "field": field_name,
                "message": f"Field '{field_name}' expects type '{expected_type}' but received '{actual_type}'. Type mismatch is not allowed.",
                "constraint": "type"
            }
        
        # Special check: Integer field should reject floats with decimals
        if expected_type == 'integer' and isinstance(value, float):
            if not value.is_integer():
                return {
                    "field": field_name,
                    "message": f"Field '{field_name}' expects integer but received float with decimal: {value}",
                    "constraint": "type"
                }
        
        return None
    
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
        Validate data against JSON Schema with STRICT validation.
        
        This method:
        1. Validates required fields (rejects empty values)
        2. Validates type strictness (text fields reject numbers, etc.)
        3. Runs standard JSONSchema validation with cached validator
        
        Args:
            data: Data to validate
            schema: JSON Schema to validate against
            
        Returns:
            Tuple of (is_valid, errors)
            errors format: [{"field": "...", "message": "...", "constraint": "..."}]
        """
        errors = []
        
        # Apply default values first
        data_with_defaults = JSONSchemaValidator._apply_defaults(data, schema)
        
        # 1. STRICT Required Field Validation - Check for empty values
        required_errors = JSONSchemaValidator.validate_required_fields(data_with_defaults, schema)
        errors.extend(required_errors)
        
        # 2. STRICT Type Validation - Reject type mismatches
        properties = schema.get("properties", {})
        for field_name, field_schema in properties.items():
            if field_name in data_with_defaults:
                value = data_with_defaults[field_name]
                expected_type = field_schema.get("type")
                if expected_type:
                    type_error = JSONSchemaValidator.validate_type_strict(value, expected_type, field_name)
                    if type_error:
                        errors.append(type_error)
                
                # Validate nested object types
                if field_schema.get("type") == "object" and isinstance(value, dict):
                    nested_properties = field_schema.get("properties", {})
                    for nested_name, nested_schema in nested_properties.items():
                        if nested_name in value:
                            nested_value = value[nested_name]
                            nested_type = nested_schema.get("type")
                            if nested_type:
                                nested_error = JSONSchemaValidator.validate_type_strict(
                                    nested_value, nested_type, f"{field_name}.{nested_name}"
                                )
                                if nested_error:
                                    errors.append(nested_error)
        
        # 3. Standard JSONSchema Validation with cached validator
        # Create schema hash for caching
        schema_json = json.dumps(schema, sort_keys=True)
        schema_hash = hashlib.sha256(schema_json.encode()).hexdigest()
        
        # Get cached validator (or create new one)
        validator = _get_cached_validator(schema_hash, schema_json)
        
        for error in validator.iter_errors(data_with_defaults):
            field_path = ".".join(str(p) for p in error.absolute_path) if error.absolute_path else "root"
            
            # Skip if we already have a required error for this field
            if error.validator == "required":
                continue  # Our strict validation already handles this
            
            errors.append({
                "field": field_path or error.path[0] if error.path else "unknown",
                "message": error.message,
                "constraint": error.validator
            })
        
        # Remove duplicate errors
        seen = set()
        unique_errors = []
        for e in errors:
            key = (e["field"], e["constraint"])
            if key not in seen:
                seen.add(key)
                unique_errors.append(e)
        
        return len(unique_errors) == 0, unique_errors
    
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
