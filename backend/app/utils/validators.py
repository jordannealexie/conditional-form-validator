"""
Validation utilities for form templates and submissions
Implements strict type checking and version validation
"""
import re
from typing import Any, Dict, List, Optional, Tuple
from pydantic import ValidationError


class VersionValidator:
    """Validates template version format (FLOAT only: e.g., 1.0, 2.5, 10.12)"""
    
    # Regex pattern for float version: digits.digits (e.g., 1.0, 2.5, 10.123)
    VERSION_PATTERN = re.compile(r'^\d+\.\d+$')
    
    @classmethod
    def validate(cls, version: Any) -> Tuple[bool, Optional[str]]:
        """
        Validate version format
        
        Args:
            version: Version value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Must be a string
        if not isinstance(version, str):
            return False, f"Version must be a string, got {type(version).__name__}"
        
        # Must match float pattern
        if not cls.VERSION_PATTERN.match(version):
            return False, f"Version must be a float format (e.g., '1.0', '2.5'), got '{version}'"
        
        # Additional check: ensure it can be parsed as float
        try:
            float_val = float(version)
            if float_val <= 0:
                return False, "Version must be a positive number"
        except ValueError:
            return False, f"Version '{version}' cannot be parsed as a float"
        
        return True, None
    
    @classmethod
    def is_valid(cls, version: Any) -> bool:
        """Check if version is valid"""
        is_valid, _ = cls.validate(version)
        return is_valid


class FieldTypeValidator:
    """Validates field types and enforces strict type checking"""
    
    # Type mapping from JSONSchema type to Python type
    TYPE_MAP = {
        'string': (str,),
        'number': (int, float),
        'integer': (int,),
        'boolean': (bool,),
        'array': (list,),
        'object': (dict,),
        'null': (type(None),)
    }
    
    # Reverse mapping - what types are NOT allowed for each JSONSchema type
    FORBIDDEN_TYPES = {
        'string': (int, float, bool, list, dict),
        'number': (str, bool, list, dict),
        'integer': (str, float, bool, list, dict),
        'boolean': (str, int, float, list, dict),
        'array': (str, int, float, bool, dict),
        'object': (str, int, float, bool, list)
    }
    
    @classmethod
    def validate_field_value(
        cls, 
        field_name: str,
        field_value: Any, 
        field_schema: Dict[str, Any],
        strict: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a field value against its schema with strict type checking
        
        Args:
            field_name: Name of the field
            field_value: Value to validate
            field_schema: JSONSchema definition for the field
            strict: Whether to enforce strict type checking
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not strict:
            return True, None
        
        expected_type = field_schema.get('type')
        if not expected_type:
            return True, None  # No type specified, skip validation
        
        # Handle null values
        if field_value is None:
            if expected_type == 'null' or 'null' in (expected_type if isinstance(expected_type, list) else []):
                return True, None
            # Check if field is required
            return True, None  # Let JSONSchema handle required validation
        
        # Get forbidden types for this schema type
        forbidden = cls.FORBIDDEN_TYPES.get(expected_type, ())
        actual_type = type(field_value)
        
        # Check if value type is forbidden
        if isinstance(field_value, forbidden):
            return False, (
                f"Field '{field_name}' expects type '{expected_type}' but got "
                f"'{actual_type.__name__}'. Type mismatch not allowed."
            )
        
        # Additional validation for specific types
        if expected_type == 'integer' and isinstance(field_value, float):
            if not field_value.is_integer():
                return False, f"Field '{field_name}' expects integer, got float with decimal: {field_value}"
        
        return True, None
    
    @classmethod
    def validate_template_fields(
        cls,
        fields: List[Dict[str, Any]],
        strict: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Validate all fields in a template definition
        
        Args:
            fields: List of field definitions
            strict: Whether to enforce strict validation
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        for field in fields:
            field_name = field.get('name', 'unknown')
            field_type = field.get('type')
            
            # Check if field type is valid
            if not field_type:
                errors.append(f"Field '{field_name}' missing 'type' property")
                continue
            
            # Validate that type is a recognized JSONSchema type
            if field_type not in cls.TYPE_MAP and field_type not in ['date', 'time', 'datetime', 'email', 'url']:
                errors.append(f"Field '{field_name}' has unrecognized type: '{field_type}'")
        
        return len(errors) == 0, errors
    
    @classmethod
    def validate_submission_data(
        cls,
        data: Dict[str, Any],
        template_fields: List[Dict[str, Any]],
        strict: bool = True
    ) -> Tuple[bool, List[str]]:
        """
        Validate submission data against template fields with strict type checking
        
        Args:
            data: Submission data dictionary
            template_fields: Template field definitions
            strict: Whether to enforce strict type checking
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Create a map of field names to their schemas
        field_map = {field.get('name'): field for field in template_fields if field.get('name')}
        
        # Validate each submitted value
        for field_name, field_value in data.items():
            if field_name not in field_map:
                continue  # Skip fields not in template (might be metadata)
            
            field_def = field_map[field_name]
            field_type = field_def.get('type')
            
            if not field_type:
                continue
            
            # Convert field type to JSONSchema type
            schema_type = cls._map_field_type_to_schema(field_type)
            
            # Validate value
            is_valid, error_msg = cls.validate_field_value(
                field_name,
                field_value,
                {'type': schema_type},
                strict
            )
            
            if not is_valid:
                errors.append(error_msg)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def _map_field_type_to_schema(field_type: str) -> str:
        """Map field type to JSONSchema type"""
        type_mapping = {
            'text': 'string',
            'long_text': 'string',
            'email': 'string',
            'phone': 'string',
            'password': 'string',
            'url': 'string',
            'date': 'string',
            'time': 'string',
            'datetime': 'string',
            'number': 'number',
            'integer': 'integer',
            'currency': 'number',
            'percentage': 'number',
            'boolean': 'boolean',
            'checkbox': 'boolean',
            'select': 'string',
            'enum': 'string',
            'multi_select': 'array',
            'file': 'string',
            'rating': 'number',
            'json': 'object',
            'address': 'object',
            'array': 'array',
            'object': 'object'
        }
        return type_mapping.get(field_type, 'string')


def validate_template_version(version: Any) -> str:
    """
    Validate template version and raise ValueError if invalid
    
    Args:
        version: Version value to validate
        
    Returns:
        Validated version string
        
    Raises:
        ValueError: If version format is invalid
    """
    is_valid, error_msg = VersionValidator.validate(version)
    if not is_valid:
        raise ValueError(error_msg)
    return str(version)


def validate_field_types(fields: List[Dict[str, Any]], strict: bool = True) -> List[Dict[str, Any]]:
    """
    Validate template fields and return validated fields
    
    Args:
        fields: List of field definitions
        strict: Whether to enforce strict validation
        
    Returns:
        Validated fields list
        
    Raises:
        ValueError: If validation fails
    """
    is_valid, errors = FieldTypeValidator.validate_template_fields(fields, strict)
    if not is_valid:
        raise ValueError(f"Field validation failed: {'; '.join(errors)}")
    return fields


def validate_submission_types(
    data: Dict[str, Any],
    template_fields: List[Dict[str, Any]],
    strict: bool = True
) -> Dict[str, Any]:
    """
    Validate submission data types
    
    Args:
        data: Submission data
        template_fields: Template field definitions
        strict: Whether to enforce strict type checking
        
    Returns:
        Validated data
        
    Raises:
        ValueError: If validation fails
    """
    is_valid, errors = FieldTypeValidator.validate_submission_data(data, template_fields, strict)
    if not is_valid:
        raise ValueError(f"Submission validation failed: {'; '.join(errors)}")
    return data
