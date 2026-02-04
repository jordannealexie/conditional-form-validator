"""
Utility helpers for audit logging with bulk operations.

This module provides helper functions and decorators for easier audit logging.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


def calculate_edited_fields(before: Dict[str, Any], after: Dict[str, Any]) -> List[str]:
    """
    Calculate which fields were edited by comparing before and after states.
    
    Args:
        before: State before the change
        after: State after the change
        
    Returns:
        List of field names that were changed
    """
    if not before or not after:
        return []
    
    edited = []
    all_keys = set(before.keys()) | set(after.keys())
    
    for key in all_keys:
        before_val = before.get(key)
        after_val = after.get(key)
        
        # Skip password fields
        if "password" in key.lower():
            continue
            
        if before_val != after_val:
            edited.append(key)
    
    return edited


def sanitize_for_audit(data: Dict[str, Any], sensitive_fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Sanitize data for audit logging by removing or masking sensitive fields.
    
    Args:
        data: Dictionary to sanitize
        sensitive_fields: List of field names to mask (default: password fields)
        
    Returns:
        Sanitized dictionary safe for audit logging
    """
    if sensitive_fields is None:
        sensitive_fields = ["password", "password_hash", "hashed_password", "secret", "token"]
    
    sanitized = {}
    for key, value in data.items():
        # Check if field is sensitive
        if any(sensitive in key.lower() for sensitive in sensitive_fields):
            sanitized[key] = "***REDACTED***"
        elif isinstance(value, dict):
            sanitized[key] = sanitize_for_audit(value, sensitive_fields)
        elif isinstance(value, list):
            sanitized[key] = [
                sanitize_for_audit(item, sensitive_fields) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            sanitized[key] = value
    
    return sanitized


def model_to_dict(model_instance: Any, exclude: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Convert a SQLAlchemy model instance to a dictionary for audit logging.
    
    Args:
        model_instance: SQLAlchemy model instance
        exclude: List of field names to exclude
        
    Returns:
        Dictionary representation of the model
    """
    if exclude is None:
        exclude = []
    
    result = {}
    
    # Get all columns from the model
    if hasattr(model_instance, "__table__"):
        for column in model_instance.__table__.columns:
            if column.name not in exclude:
                value = getattr(model_instance, column.name, None)
                
                # Convert datetime to ISO string
                if isinstance(value, datetime):
                    result[column.name] = value.isoformat()
                else:
                    result[column.name] = value
    
    return result


def prepare_bulk_audit_entries(
    action: str,
    entity_type: str,
    entities: List[Any],
    actor_user_id: Optional[int] = None,
    actor_username: Optional[str] = None,
    before_states: Optional[List[Dict[str, Any]]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Prepare multiple audit entries for bulk insertion.
    
    This is a helper for creating bulk audit entries when you have a list of entities.
    
    Args:
        action: Action performed (created, updated, deleted)
        entity_type: Type of entity (user, role, form_template, etc.)
        entities: List of entity instances
        actor_user_id: User ID who performed the action
        actor_username: Username who performed the action
        before_states: Optional list of before states for updates/deletes
        ip_address: IP address of the actor
        user_agent: User agent of the actor
        
    Returns:
        List of audit entry dictionaries ready for bulk insertion
    """
    entries = []
    
    for idx, entity in enumerate(entities):
        # Convert entity to dict
        after_state = model_to_dict(entity, exclude=["password_hash", "password"])
        after_state = sanitize_for_audit(after_state)
        
        # Get before state if provided
        before_state = None
        if before_states and idx < len(before_states):
            before_state = sanitize_for_audit(before_states[idx])
        
        # Calculate edited fields
        edited_fields = []
        if before_state and after_state:
            edited_fields = calculate_edited_fields(before_state, after_state)
        
        # Build changes
        changes = {}
        if before_state:
            changes["before"] = before_state
        if after_state and action != "deleted":
            changes["after"] = after_state
        if edited_fields:
            changes["edited_fields"] = edited_fields
        
        # Get entity ID
        entity_id = getattr(entity, "id", None)
        
        entry = {
            "action": action,
            "resource_type": entity_type.lower(),
            "resource_id": str(entity_id) if entity_id else None,
            "user_id": actor_user_id,
            "username": actor_username,
            "status": "success",
            "ip_address": ip_address,
            "user_agent": user_agent,
            "changes": changes if changes else None,
            "created_by": actor_user_id if action == "created" else None,
            "updated_by": actor_user_id if action == "updated" else None,
            "deleted_by": actor_user_id if action == "deleted" else None,
        }
        
        entries.append(entry)
    
    return entries
