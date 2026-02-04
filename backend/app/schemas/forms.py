"""
Pydantic schemas for form system API requests and responses
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
import uuid
from app.utils.validators import validate_template_version


# ============================================================================
# Bank Schemas
# ============================================================================

class BankBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Bank name")
    code: str = Field(..., min_length=1, max_length=50, description="Bank code (unique identifier)")
    logo_url: Optional[str] = Field(None, description="Bank logo URL")
    primary_color: Optional[str] = Field(None, description="Bank primary brand color (HEX)")
    description: Optional[str] = Field(None, description="Bank description")
    active: bool = Field(True, description="Whether the bank is active")


class BankCreate(BankBase):
    """Schema for creating a new bank"""
    pass


class BankUpdate(BaseModel):
    """Schema for updating a bank"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    code: Optional[str] = Field(None, min_length=1, max_length=50)
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class BankResponse(BankBase):
    """Schema for bank response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Form Template Schemas
# ============================================================================

class FormTemplateBase(BaseModel):
    bank_id: int = Field(..., description="Bank ID this template belongs to")
    name: str = Field(..., min_length=1, max_length=255, description="Template name (unique per bank)")
    version: str = Field(..., description="Semantic version as FLOAT (e.g., '1.0', '2.5')")
    form_type: Optional[str] = Field(None, max_length=100, description="Form type category (e.g., 'credit_card', 'loan')")
    schema_json: Dict[str, Any] = Field(..., description="JSONSchema for validation")
    fields: Optional[List[Dict[str, Any]]] = Field(None, description="Fields array for UI rendering and conditional logic")
    ui_schema: Optional[Dict[str, Any]] = Field(None, description="UI rendering hints")
    description: Optional[str] = Field(None, description="Form description")
    active: bool = Field(True, description="Whether this template version is active")
    
    @field_validator('version')
    @classmethod
    def validate_version_format(cls, v: str) -> str:
        """Validate version is FLOAT format only (e.g., '1.0', '2.5')"""
        return validate_template_version(v)


class FormTemplateCreate(FormTemplateBase):
    """Schema for creating a new form template"""
    created_by: Optional[str] = Field(None, description="Username of creator")


class FormTemplateUpdate(BaseModel):
    """Schema for updating a form template"""
    schema_json: Optional[Dict[str, Any]] = None
    fields: Optional[List[Dict[str, Any]]] = None
    ui_schema: Optional[Dict[str, Any]] = None
    name: Optional[str] = Field(None, max_length=255)
    version: Optional[str] = None
    form_type: Optional[str] = Field(None, max_length=100)
    bank_id: Optional[int] = Field(None, description="Bank ID")
    description: Optional[str] = None
    active: Optional[bool] = None


class FormTemplateResponse(FormTemplateBase):
    """Schema for form template response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    bank: Optional[BankResponse] = None
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Form Submission Schemas
# ============================================================================

class FormSubmissionBase(BaseModel):
    template_id: int = Field(..., description="Form template ID")
    fieldman_id: str = Field(..., min_length=1, max_length=100, description="Username of fieldman")
    data_json: Dict[str, Any] = Field(..., description="Form data (must match template schema)")


class FormSubmissionCreate(BaseModel):
    """Schema for creating a new form submission"""
    template_id: int = Field(..., description="Form template ID")
    fieldman_id: Optional[str] = Field(None, max_length=100, description="Override; usually set by backend from current user")
    data_json: Optional[Dict[str, Any]] = Field(None, description="Form data")
    submission_data: Optional[Dict[str, Any]] = Field(None, description="Alias for data_json (API compatibility)")
    file_tokens: Optional[List[str]] = Field(None, description="List of file tokens from uploads")
    status: Optional[str] = Field("draft", description="Submission status")
    visible_fields: Optional[List[str]] = Field(None, description="List of currently visible field IDs (for conditional validation)")


class FormSubmissionUpdate(BaseModel):
    """Schema for updating a form submission (draft only)"""
    data_json: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class FormSubmissionResponse(BaseModel):
    """Schema for form submission response"""
    id: int
    template_id: int
    fieldman_id: Optional[str] = None
    submitted_by: Optional[int] = Field(None, description="User ID of submitter")  # User ID, not username
    data_json: Dict[str, Any]
    file_tokens: Optional[List[str]] = None
    status: str
    validation_errors: Optional[List[Dict[str, Any]]] = None
    is_valid: bool
    template: Optional[FormTemplateResponse] = None
    submitted_at: Optional[datetime] = None
    # Legacy review fields (backwards compatible)
    reviewed_by: Optional[int] = Field(None, description="User ID of reviewer")  # User ID, not username
    reviewed_at: Optional[datetime] = None
    reviewed_comment: Optional[str] = None
    # New validation audit fields
    validated_by: Optional[int] = Field(None, description="User ID who validated/approved")  # User ID, not username
    validated_on: Optional[datetime] = None  # When approved/rejected
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class SubmissionReviewRequest(BaseModel):
    """Schema for supervisor review"""
    action: str = Field(..., description="approve or reject")
    comment: Optional[str] = None


# ============================================================================
# File Schemas
# ============================================================================

class FileUploadResponse(BaseModel):
    """Schema for file upload response"""
    file_id: int
    field_id: str
    original_filename: str
    storage_path: str
    file_size: int
    mime_type: str
    token: uuid.UUID
    uploaded_at: datetime
    message: str = "File uploaded successfully"


class FormFileResponse(BaseModel):
    """Schema for form file metadata"""
    id: int
    submission_id: Optional[int] = None
    field_id: str
    original_filename: str
    storage_path: str
    file_size: int
    mime_type: str
    token: uuid.UUID
    uploaded_at: datetime
    uploaded_by: str
    
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Validation Schemas
# ============================================================================

class ValidationError(BaseModel):
    """Schema for a  single validation error"""
    field: str = Field(..., description="Field path that failed validation")
    message: str = Field(..., description="Error message")
    constraint: Optional[str] = Field(None, description="Constraint that was violated")


class ValidationResult(BaseModel):
    """Schema for validation result"""
    is_valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    message: str


class ValidateSubmissionRequest(BaseModel):
    """Schema for submission validation request"""
    template_id: int
    submission_data: Dict[str, Any] # Request uses submission_data for flexibility
    visible_fields: Optional[List[str]] = Field(None, description="List of currently visible field IDs (for conditional validation)")


# ============================================================================
# List/Filter Schemas
# ============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    total: int
    page: int
    page_size: int
    data: List[Any]


class BankListResponse(BaseModel):
    """Schema for bank list response"""
    total: int
    data: List[BankResponse]


class FormTemplateListResponse(BaseModel):
    """Schema for form template list response"""
    total: int
    data: List[FormTemplateResponse]


class FormSubmissionListResponse(BaseModel):
    """Schema for form submission list response"""
    total: int
    page: int
    page_size: int
    data: List[FormSubmissionResponse]
