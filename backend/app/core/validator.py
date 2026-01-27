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

        # 4. Field-specific validation for visible fields
        field_validation_errors = cls._validate_field_configurations(data, visible_fields)
        errors.extend(field_validation_errors)
        
        # 5. Check 'required' for visible fields that might not be in the JSONSchema required list
        # or were conditional but the JSONSchema didn't capture it perfectly
        for field in visible_fields:
            if field.get("required") is True:
                val = cls._get_value(data, field["id"])
                if val is None or val == "":
                    # Check if already caught by JSONSchema 'required'
                    if not any(e["field"] == field["id"] and e["code"] == "REQUIRED" for e in errors):
                        errors.append({
                            "field": field["id"],
                            "message": f"{field.get('label', field['id'])} is required",
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
            elif f_type == "phone":
                schema_prop["type"] = "string"
                schema_prop["format"] = "phone"
                schema_prop["pattern"] = r"^(09|\+639)\d{9}$"
            elif f_type == "currency":
                schema_prop["type"] = "number"
                schema_prop["minimum"] = 0
                schema_prop["multipleOf"] = 0.01
            elif f_type == "percentage":
                schema_prop["type"] = "number"
                schema_prop["minimum"] = 0
                schema_prop["maximum"] = 100
            elif f_type == "boolean":
                schema_prop["type"] = "boolean"
            
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
    
    @classmethod
    def _validate_field_configurations(cls, data: Dict[str, Any], visible_fields: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Validate fields based on their specific configurations and types.
        Only validates fields that are visible and required.
        """
        errors = []
        
        for field in visible_fields:
            field_id = field["id"]
            field_type = field.get("type", "text")
            field_label = field.get("label", field_id)
            field_required = field.get("required", False)
            field_value = cls._get_value(data, field_id)
            
            # Skip validation if field is not required and has no value
            if not field_required and (field_value is None or field_value == ""):
                continue
            
            # Skip validation if field is required but empty (handled by required validation)
            if field_required and (field_value is None or field_value == ""):
                continue
                
            # Validate based on field type
            field_errors = cls._validate_field_type(field_id, field_value, field_type, field_label, field)
            errors.extend(field_errors)
            
            # Validate based on field configuration (validation rules)
            if "validation" in field:
                validation_errors = cls._validate_field_rules(field_id, field_value, field["validation"], field_label, field_type)
                errors.extend(validation_errors)
        
        return errors
    
    @classmethod
    def _validate_field_type(cls, field_id: str, value: Any, field_type: str, label: str, field_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate value based on field type."""
        errors = []
        
        if value is None or value == "":
            return errors
        
        try:
            if field_type == "email":
                email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                if not re.match(email_pattern, str(value)):
                    errors.append({
                        "field": field_id,
                        "message": f"{label} must be a valid email address",
                        "code": "INVALID_EMAIL"
                    })
            
            elif field_type == "phone":
                # Philippines phone format validation
                phone_pattern = r"^(09|\+639)\d{9}$"
                if not re.match(phone_pattern, str(value).strip()):
                    errors.append({
                        "field": field_id,
                        "message": f"{label} must be a valid Philippines phone number (09XXXXXXXXX or +639XXXXXXXXX)",
                        "code": "INVALID_PHONE"
                    })
            
            elif field_type in ["number", "currency", "percentage"]:
                try:
                    num_value = float(value)
                    if field_type == "currency" and num_value < 0:
                        errors.append({
                            "field": field_id,
                            "message": f"{label} cannot be negative",
                            "code": "INVALID_CURRENCY"
                        })
                    elif field_type == "percentage" and (num_value < 0 or num_value > 100):
                        errors.append({
                            "field": field_id,
                            "message": f"{label} must be between 0 and 100",
                            "code": "INVALID_PERCENTAGE"
                        })
                except (ValueError, TypeError):
                    errors.append({
                        "field": field_id,
                        "message": f"{label} must be a valid number",
                        "code": "INVALID_NUMBER"
                    })
            
            elif field_type == "select":
                options = field_config.get("options", [])
                if options and value not in options:
                    errors.append({
                        "field": field_id,
                        "message": f"{label} must be one of the allowed options",
                        "code": "INVALID_OPTION"
                    })
            
            elif field_type == "boolean":
                if not isinstance(value, bool):
                    errors.append({
                        "field": field_id,
                        "message": f"{label} must be true or false",
                        "code": "INVALID_BOOLEAN"
                    })
            
            elif field_type == "date":
                date_pattern = r"^\d{4}-\d{2}-\d{2}$"
                if not re.match(date_pattern, str(value)):
                    errors.append({
                        "field": field_id,
                        "message": f"{label} must be a valid date in YYYY-MM-DD format",
                        "code": "INVALID_DATE"
                    })
        
        except Exception as e:
            errors.append({
                "field": field_id,
                "message": f"Validation error for {label}: {str(e)}",
                "code": "VALIDATION_ERROR"
            })
        
        return errors
    
    @classmethod
    def _validate_field_rules(cls, field_id: str, value: Any, validation_rules: Dict[str, Any], label: str, field_type: str) -> List[Dict[str, Any]]:
        """Validate field based on validation rules."""
        errors = []
        
        if value is None or value == "":
            return errors
        
        str_value = str(value)
        
        try:
            # Length validations for string types
            if field_type in ["text", "textarea", "email", "phone"] and isinstance(value, str):
                if "minLength" in validation_rules:
                    min_length = validation_rules["minLength"]
                    if len(str_value) < min_length:
                        errors.append({
                            "field": field_id,
                            "message": f"{label} must be at least {min_length} characters long",
                            "code": "MIN_LENGTH"
                        })
                
                if "maxLength" in validation_rules:
                    max_length = validation_rules["maxLength"]
                    if len(str_value) > max_length:
                        errors.append({
                            "field": field_id,
                            "message": f"{label} must be no more than {max_length} characters long",
                            "code": "MAX_LENGTH"
                        })
            
            # Numeric validations
            if field_type in ["number", "currency", "percentage"]:
                try:
                    num_value = float(value)
                    
                    if "minimum" in validation_rules:
                        minimum = validation_rules["minimum"]
                        if num_value < minimum:
                            errors.append({
                                "field": field_id,
                                "message": f"{label} must be at least {minimum}",
                                "code": "MIN_VALUE"
                            })
                    
                    if "maximum" in validation_rules:
                        maximum = validation_rules["maximum"]
                        if num_value > maximum:
                            errors.append({
                                "field": field_id,
                                "message": f"{label} must be no more than {maximum}",
                                "code": "MAX_VALUE"
                            })
                
                except (ValueError, TypeError):
                    pass  # Already handled in type validation
            
            # Pattern validation for string fields
            if "pattern" in validation_rules and field_type in ["text", "email", "phone"]:
                pattern = validation_rules["pattern"]
                if not re.match(pattern, str_value):
                    errors.append({
                        "field": field_id,
                        "message": f"{label} format is not valid",
                        "code": "PATTERN_MISMATCH"
                    })
        
        except Exception as e:
            errors.append({
                "field": field_id,
                "message": f"Validation rule error for {label}: {str(e)}",
                "code": "RULE_ERROR"
            })
        
        return errors
