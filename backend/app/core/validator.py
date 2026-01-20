import re
import jsonschema
from typing import Any, Dict, List, Optional, Union, Tuple
from jsonschema import Draft7Validator, ValidationError as JsonSchemaValidationError

class FormValidator:
    """
    Advanced form validator engine supporting JSONSchema and nested conditional logic.
    """
    
    COMPARISON_OPERATORS = {
        "equals": lambda a, b: a == b,
        "not_equals": lambda a, b: a != b,
        "greater_than": lambda a, b: float(a) > float(b) if a is not None and b is not None else False,
        "less_than": lambda a, b: float(a) < float(b) if a is not None and b is not None else False,
        "greater_or_equal": lambda a, b: float(a) >= float(b) if a is not None and b is not None else False,
        "less_or_equal": lambda a, b: float(a) <= float(b) if a is not None and b is not None else False,
        "in": lambda a, b: a in b if b is not None and isinstance(b, list) else False,
        "not_in": lambda a, b: a not in b if b is not None and isinstance(b, list) else False,
        "contains": lambda a, b: b in a if a is not None and (isinstance(a, list) or isinstance(a, str)) else False,
        "matches": lambda a, b: bool(re.search(b, str(a))) if a is not None and b is not None else False,
        "is_empty": lambda a, b: not a,
        "is_not_empty": lambda a, b: bool(a),
    }

    @classmethod
    def validate(cls, data: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation entry point.
        Checks JSONSchema first, then evaluates conditional visibility and requirements.
        """
        fields = template.get("fields", [])
        schema = template.get("schema_json") or template.get("json_schema")
        
        if not schema and fields:
            schema = cls.generate_jsonschema(fields)
        
        errors = []
        
        # 1. Base JSONSchema Validation
        validator = Draft7Validator(schema)
        schema_errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
        
        # 2. Determine visible fields based on conditional logic
        visible_fields = cls.get_visible_fields(data, fields)
        visible_field_ids = {f["id"] for f in visible_fields}
        
        # 3. Filter schema errors to only include visible fields
        # Note: If a field is hidden, its validation errors are ignored
        for error in schema_errors:
            field_path = ".".join([str(p) for p in error.path])
            
            # For 'required' errors from jsonschema, the path is often empty,
            # but the message contains the field name. 
            if not field_path and error.validator == "required":
                match = re.search(r"'([^']+)'", error.message)
                if match:
                    field_path = match.group(1)

            # Check if the root of the path is a visible field
            root_field = str(error.path[0]) if error.path else field_path
            if root_field in visible_field_ids or not root_field or not fields:
                errors.append({
                    "field": field_path or "__root__",
                    "message": cls._format_error_message(error),
                    "code": error.validator.upper() if hasattr(error, 'validator') else "VALIDATION_ERROR"
                })

        # 4. Check 'required' for visible fields that might not be in the JSONSchema required list
        # or were conditional but the JSONSchema didn't capture it perfectly
        for field in visible_fields:
            if field.get("required") is True:
                val = cls._get_value(data, field["id"])
                if val is None or val == "":
                    # Check if already caught by JSONSchema 'required'
                    if not any(e["field"] == field["id"] and e["code"] == "REQUIRED" for e in errors):
                        errors.append({
                            "field": field["id"],
                            "message": f"{field['label']} is required",
                            "code": "REQUIRED_FIELD"
                        })

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": []
        }

    @classmethod
    def get_visible_fields(cls, data: Dict[str, Any], fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Returns the list of fields that should be visible given the current data.
        """
        visible = []
        for field in fields:
            show_if = field.get("show_if")
            if not show_if or cls.evaluate_condition(data, show_if):
                visible.append(field)
        return visible

    @classmethod
    def evaluate_condition(cls, data: Dict[str, Any], condition: Union[Dict, List, bool]) -> bool:
        """
        Recursively evaluates a condition object.
        Supports:
        - {"field": "status", "operator": "equals", "value": "Employed"}
        - {"all": [...]} (AND)
        - {"any": [...]} (OR)
        - {"not": {...}} (NOT)
        """
        if isinstance(condition, bool):
            return condition
        
        if not isinstance(condition, dict):
            return True

        # Logical Operators
        if "all" in condition:
            return all(cls.evaluate_condition(data, c) for c in condition["all"])
        if "any" in condition:
            return any(cls.evaluate_condition(data, c) for c in condition["any"])
        if "not" in condition:
            return not cls.evaluate_condition(data, condition["not"])

        # Comparison Operator
        field_id = condition.get("field")
        operator = condition.get("operator")
        target_value = condition.get("value")
        
        if not field_id or not operator:
            return True
            
        current_value = cls._get_value(data, field_id)
        
        op_func = cls.COMPARISON_OPERATORS.get(operator)
        if op_func:
            try:
                return op_func(current_value, target_value)
            except Exception:
                return False
        
        return True

    @staticmethod
    def _get_value(data: Dict[str, Any], path: str) -> Any:
        """Helper to get nested value from dict using dot notation."""
        parts = path.split('.')
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    @classmethod
    def generate_jsonschema(cls, fields: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generates a JSONSchema from a list of field definitions.
        """
        properties = {}
        required = []
        
        for field in fields:
            f_id = field["id"]
            f_type = field.get("type", "text")
            
            # Map simple types
            schema_prop = {"title": field.get("label", f_id)}
            
            if f_type == "text":
                schema_prop["type"] = "string"
            elif f_type == "email":
                schema_prop["type"] = "string"
                schema_prop["format"] = "email"
            elif f_type == "number":
                schema_prop["type"] = "number"
            elif f_type == "date":
                schema_prop["type"] = "string"
                schema_prop["format"] = "date"
            elif f_type == "checkbox":
                schema_prop["type"] = "boolean"
            elif f_type == "select":
                schema_prop["type"] = "string"
                if "options" in field:
                    schema_prop["enum"] = field["options"]
            elif f_type == "file":
                schema_prop["type"] = "string"
                schema_prop["description"] = "File token or URL"
            elif f_type == "textarea":
                schema_prop["type"] = "string"
            
            # Additional constraints
            if "min_length" in field:
                schema_prop["minLength"] = field["min_length"]
            if "max_length" in field:
                schema_prop["maxLength"] = field["max_length"]
            if "minimum" in field:
                schema_prop["minimum"] = field["minimum"]
            if "maximum" in field:
                schema_prop["maximum"] = field["maximum"]
            if "pattern" in field:
                schema_prop["pattern"] = field["pattern"]

            properties[f_id] = schema_prop
            
            # Note: We don't add to 'required' here if it's conditional.
            # Base required fields (always required)
            if field.get("required") is True and not field.get("show_if"):
                required.append(f_id)

        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": True # Allow flexibility
        }

    @staticmethod
    def _format_error_message(error: JsonSchemaValidationError) -> str:
        """Custom user-friendly error messages."""
        if error.validator == "required":
            match = re.search(r"'([^']+)'", error.message)
            if match:
                return f"{match.group(1)} is required"
        return error.message
