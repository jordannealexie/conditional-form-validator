# Import all models for Alembic to detect
from app.db.base_class import Base
from app.models.user import User, Role, RefreshToken
from app.models.forms import Bank, FormTemplate, FormSubmission, FormFile
from app.models.field_types import EnumDefinition, FieldTypeDefinition, FormFieldMapping
from app.models.audit import AuditLog
from app.models.lookup import Department, Location