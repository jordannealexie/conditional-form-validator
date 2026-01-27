from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, TIMESTAMP, JSON, Uuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import uuid


class SubmissionStatus(str, Enum):
    """Form submission status enumeration"""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    VALIDATED = "validated"
    REJECTED = "rejected"


class Bank(Base):
    """Bank model for multi-tenant form system"""
    __tablename__ = "banks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    logo_url = Column(String(500), nullable=True)
    primary_color = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    form_templates = relationship("FormTemplate", back_populates="bank", cascade="all, delete-orphan")
    bank_users = relationship("User", back_populates="bank")


class FormTemplate(Base):
    """Form template with JSONSchema validation rules and UI schema"""
    __tablename__ = "form_templates"

    id = Column(Integer, primary_key=True, index=True)
    bank_id = Column(Integer, ForeignKey('banks.id'), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)  # Template name (e.g., "Credit Card Application")
    version = Column(String(20), nullable=False)  # Semantic versioning: "1.0.0", "1.1.0", etc.
    form_type = Column(String(100), nullable=True)  # Optional form type category (e.g., "credit_card", "loan")
    
    # JSON Schema for validation
    schema_json = Column(JSON, nullable=False) # Spec says 'schema_json'
    
    # Fields array for UI rendering and conditional logic
    fields = Column(JSON, nullable=True)
    
    # UI Schema for rendering hints (additional styling, etc.)
    ui_schema = Column(JSON, nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True, nullable=False) # Spec says 'active'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_onupdate=func.now())
    created_by = Column(String(100), nullable=True)  # Username of creator
    
    # Relationships
    bank = relationship("Bank", back_populates="form_templates")
    submissions = relationship("FormSubmission", back_populates="template", cascade="all, delete-orphan")
    
    # Unique constraint: One version per bank + form_type combination
    __table_args__ = (
        {'schema': None},
    )


class FormSubmission(Base):
    """Form submission with validation status"""
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey('form_templates.id'), nullable=False, index=True)
    fieldman_id = Column(String(100), nullable=True, index=True)  # Legacy field
    submitted_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True, comment="User ID of submitter (replaces fieldman_id)")
    
    # Submission metadata
    status = Column(String(20), default=SubmissionStatus.DRAFT, nullable=False, index=True)
    
    # Actual form data (validated against schema_json)
    data_json = Column(JSON, nullable=False)
    file_tokens = Column(JSON, nullable=True)
    
    # Validation results
    validation_errors = Column(JSON, nullable=True)
    is_valid = Column(Boolean, default=False, nullable=False)
    
    # Review/Validation audit fields - User IDs (FKs to users.id)
    reviewed_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment="User ID of reviewer (approval/rejection)")
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_comment = Column(Text, nullable=True)
    validated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True, comment="User ID who validated/approved")
    validated_on = Column(DateTime(timezone=True), nullable=True, index=True, comment="Timestamp of validation/approval")
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_onupdate=func.now())
    
    # Relationships
    template = relationship("FormTemplate", back_populates="submissions")
    files = relationship("FormFile", back_populates="submission", cascade="all, delete-orphan")


class FormFile(Base):
    """File metadata for form uploads with token-based access"""
    __tablename__ = "file_uploads"  # Spec says 'file_uploads'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(Uuid(as_uuid=True), default=uuid.uuid4, nullable=False, unique=True, index=True)  # Spec says 'token'
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(255), nullable=False, unique=True)  # Spec says 'storage_path'
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)
    
    submission_id = Column(Integer, ForeignKey('form_submissions.id'), nullable=True, index=True)
    field_id = Column(String(100), nullable=False)  # Field identifier this file belongs to
    
    # Timestamps
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    uploaded_by = Column(String(100), nullable=False)  # Username who uploaded the file
    
    # Relationships
    submission = relationship("FormSubmission", back_populates="files")
