"""
ABAC (Attribute-Based Access Control) schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# User Attribute Schemas
class UserAttributeCreate(BaseModel):
    """Schema for creating a user attribute"""
    user_id: int
    attribute_key: str = Field(..., description="Attribute name (e.g., 'clearance_level', 'team')")
    attribute_value: str = Field(..., description="Attribute value")


class UserAttributeResponse(BaseModel):
    """Schema for user attribute response"""
    id: int
    user_id: int
    attribute_key: str
    attribute_value: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Resource Attribute Schemas
class ResourceAttributeCreate(BaseModel):
    """Schema for creating a resource attribute"""
    resource_type: str = Field(..., description="Resource type (e.g., 'document', 'project')")
    resource_id: str = Field(..., description="Resource identifier")
    attribute_key: str = Field(..., description="Attribute name (e.g., 'sensitivity', 'owner')")
    attribute_value: str = Field(..., description="Attribute value")


class ResourceAttributeResponse(BaseModel):
    """Schema for resource attribute response"""
    id: int
    resource_type: str
    resource_id: str
    attribute_key: str
    attribute_value: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# ABAC Policy Schemas
class ABACPolicyCreate(BaseModel):
    """Schema for creating an ABAC policy"""
    name: str = Field(..., description="Unique policy name")
    description: Optional[str] = Field(None, description="Policy description")
    rules: Dict[str, Any] = Field(..., description="Policy rules in JSON format")
    # Example rules structure:
    # {
    #     "conditions": [
    #         {"attribute": "department", "operator": "equals", "value": "Engineering"},
    #         {"attribute": "level", "operator": ">=", "value": 5}
    #     ],
    #     "permissions": {
    #         "resource": "documents",
    #         "action": "read"
    #     }
    # }
    is_active: bool = Field(default=True, description="Whether the policy is active")


class ABACPolicyUpdate(BaseModel):
    """Schema for updating an ABAC policy"""
    description: Optional[str] = None
    rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ABACPolicyResponse(BaseModel):
    """Schema for ABAC policy response"""
    id: int
    name: str
    description: Optional[str]
    rules: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ABAC Permission Check Schemas
class ABACCheckRequest(BaseModel):
    """Schema for checking ABAC permission"""
    username: str = Field(..., description="Username to check")
    resource: str = Field(..., description="Resource to access")
    action: str = Field(..., description="Action to perform")
    resource_type: Optional[str] = Field(None, description="Resource type (for attribute lookup)")
    resource_id: Optional[str] = Field(None, description="Resource ID (for attribute lookup)")


class ABACCheckResponse(BaseModel):
    """Schema for ABAC permission check response"""
    username: str
    resource: str
    action: str
    has_permission: bool
    matched_policies: List[str] = Field(default_factory=list, description="Names of policies that granted access")
    reason: Optional[str] = Field(None, description="Explanation of the decision")


# ============ ABAC Metadata Schemas for Policy Builder UI ============

class OperatorDefinition(BaseModel):
    """Definition of an operator with user-friendly label"""
    value: str = Field(..., description="Technical operator value (e.g., '==', '!=')")
    label: str = Field(..., description="User-friendly label (e.g., 'is', 'is not')")
    description: Optional[str] = Field(None, description="Help text for the operator")


class ValueOption(BaseModel):
    """A single option for dropdown values"""
    value: str = Field(..., description="The actual value to store")
    label: str = Field(..., description="User-friendly display label")


class AttributeDefinition(BaseModel):
    """Complete definition of an attribute for the policy builder"""
    key: str = Field(..., description="Attribute key (e.g., 'user.department')")
    label: str = Field(..., description="User-friendly label (e.g., 'Department')")
    description: Optional[str] = Field(None, description="Help text for the attribute")
    value_type: str = Field(..., description="Type: 'number', 'string', 'enum', 'boolean'")
    operators: List[OperatorDefinition] = Field(..., description="Allowed operators for this attribute")
    value_source: Optional[str] = Field(None, description="API endpoint to fetch values, null for manual input")
    static_values: Optional[List[ValueOption]] = Field(None, description="Static list of values if not from API")
    input_placeholder: Optional[str] = Field(None, description="Placeholder text for input field")
    validation_pattern: Optional[str] = Field(None, description="Regex pattern for validation")
    allow_attribute_reference: Optional[bool] = Field(False, description="Whether this attribute can be compared to another attribute")
    reference_attributes: Optional[List[ValueOption]] = Field(None, description="List of attributes that can be used as reference values")


class AttributeGroup(BaseModel):
    """Group of related attributes"""
    name: str = Field(..., description="Group name (e.g., 'User Attributes')")
    description: Optional[str] = Field(None, description="Group description")
    attributes: List[AttributeDefinition] = Field(..., description="Attributes in this group")


class ABACMetadataResponse(BaseModel):
    """Complete ABAC metadata for the policy builder UI"""
    attribute_groups: List[AttributeGroup] = Field(..., description="Grouped attributes for the UI")
    global_operators: Optional[List[OperatorDefinition]] = Field(None, description="All available operators")
    
    class Config:
        from_attributes = True


# Lookup table schemas
class DepartmentBase(BaseModel):
    """Base schema for Department"""
    name: str = Field(..., min_length=1, max_length=100, description="Department name")
    code: Optional[str] = Field(None, max_length=20, description="Short code")
    description: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(True, description="Whether this option is available")
    display_order: int = Field(0, description="Sort order in dropdowns")


class DepartmentCreate(DepartmentBase):
    """Schema for creating a department"""
    pass


class DepartmentResponse(DepartmentBase):
    """Schema for department response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LocationBase(BaseModel):
    """Base schema for Location"""
    name: str = Field(..., min_length=1, max_length=100, description="Location name")
    code: Optional[str] = Field(None, max_length=20, description="Short code")
    description: Optional[str] = Field(None, max_length=255)
    region: Optional[str] = Field(None, max_length=100, description="Region for grouping")
    is_active: bool = Field(True, description="Whether this option is available")
    display_order: int = Field(0, description="Sort order in dropdowns")


class LocationCreate(LocationBase):
    """Schema for creating a location"""
    pass


class LocationResponse(LocationBase):
    """Schema for location response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

