"""add_missing_audit_fields_clean

Revision ID: b5ea35f03526
Revises: 20260126_add_field_types
Create Date: 2026-01-26 05:32:22.800325

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5ea35f03526'
down_revision: Union[str, None] = '20260126_add_field_types'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - only add missing audit fields."""
    # 1. Add updated_by to users table (updated_at already exists)
    op.add_column('users', sa.Column('updated_by', sa.String(100), nullable=True))
    
    # 2. Add audit fields to roles table (created_at already exists)
    op.add_column('roles', sa.Column('created_by', sa.String(100), nullable=True))
    op.add_column('roles', sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('roles', sa.Column('updated_by', sa.String(100), nullable=True))
    
    # 3. Add aliases for form_submissions (keep original columns for backwards compatibility)
    op.add_column('form_submissions', sa.Column('submitted_by', sa.String(100), nullable=True))
    op.add_column('form_submissions', sa.Column('validated_by', sa.String(100), nullable=True))
    op.add_column('form_submissions', sa.Column('validated_on', sa.DateTime(timezone=True), nullable=True))
    
    # Copy data from old columns to new columns
    op.execute("UPDATE form_submissions SET submitted_by = fieldman_id WHERE fieldman_id IS NOT NULL")
    op.execute("UPDATE form_submissions SET validated_by = reviewed_by WHERE reviewed_by IS NOT NULL")
    op.execute("UPDATE form_submissions SET validated_on = reviewed_at WHERE reviewed_at IS NOT NULL")
    
    # 4. Add strict_type_checking to field_type_definitions (validation_rules already exists)
    op.add_column('field_type_definitions', sa.Column('strict_type_checking', sa.Boolean(), server_default='true', nullable=False))
    
    # 5. Convert existing versions to FLOAT format (e.g., 1.0.0 -> 1.0)
    op.execute("""
        UPDATE form_templates 
        SET version = SUBSTRING(version FROM '^[0-9]+\\.[0-9]+')
        WHERE version ~ '^[0-9]+\\.[0-9]+\\.'
    """)
    
    # 6. Add version format constraint to form_templates (enforce FLOAT format like 1.0, 2.5)
    op.execute("""
        ALTER TABLE form_templates 
        ADD CONSTRAINT version_format_check 
        CHECK (version ~ '^[0-9]+\\.[0-9]+$')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TABLE form_templates DROP CONSTRAINT IF EXISTS version_format_check")
    op.drop_column('field_type_definitions', 'strict_type_checking')
    op.drop_column('form_submissions', 'validated_on')
    op.drop_column('form_submissions', 'validated_by')
    op.drop_column('form_submissions', 'submitted_by')
    op.drop_column('roles', 'updated_by')
    op.drop_column('roles', 'updated_at')
    op.drop_column('roles', 'created_by')
    op.drop_column('users', 'updated_by')

