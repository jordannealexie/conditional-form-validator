"""Add performance indexes for common queries

Revision ID: perf_indexes_001
Revises: (your_previous_revision_id)
Create Date: 2026-01-27

This migration adds composite indexes and additional single-column indexes
for frequently queried fields to improve query performance.

Changes:
- Add composite index on form_submissions (status, created_at) for filtering and sorting
- Add composite index on form_submissions (template_id, status) for template-specific queries
- Add composite index on form_submissions (submitted_by, status) for user submissions
- Add index on form_submissions.created_at for time-based queries
- Add index on form_templates.form_type for filtering by type
- Add composite index on form_templates (bank_id, active) for bank-specific active templates

These indexes are designed to optimize:
1. Dashboard queries filtering by status and sorting by date
2. Template-specific submission lists
3. User submission history queries
4. Time-range analytics queries
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'perf_indexes_001'
down_revision = None  # Replace with your latest revision
branch_labels = None
depends_on = None


def upgrade():
    """Add performance-optimizing indexes"""
    
    # Composite index for submissions: status + created_at (for filtered listings with sorting)
    op.create_index(
        'ix_form_submissions_status_created',
        'form_submissions',
        ['status', 'created_at'],
        unique=False
    )
    
    # Composite index for submissions: template_id + status (for template-specific filtered queries)
    op.create_index(
        'ix_form_submissions_template_status',
        'form_submissions',
        ['template_id', 'status'],
        unique=False
    )
    
    # Composite index for submissions: submitted_by + status (for user-specific queries)
    op.create_index(
        'ix_form_submissions_submitted_by_status',
        'form_submissions',
        ['submitted_by', 'status'],
        unique=False
    )
    
    # Index on created_at for time-based queries
    op.create_index(
        'ix_form_submissions_created_at',
        'form_submissions',
        ['created_at'],
        unique=False
    )
    
    # Index on form_type for filtering templates by type
    op.create_index(
        'ix_form_templates_form_type',
        'form_templates',
        ['form_type'],
        unique=False
    )
    
    # Composite index for templates: bank_id + active (for active templates by bank)
    op.create_index(
        'ix_form_templates_bank_active',
        'form_templates',
        ['bank_id', 'active'],
        unique=False
    )
    
    # Index on file_uploads field_id for field-specific file queries
    op.create_index(
        'ix_file_uploads_field_id',
        'file_uploads',
        ['field_id'],
        unique=False
    )
    
    # Composite index for file_uploads: submission_id + field_id
    op.create_index(
        'ix_file_uploads_submission_field',
        'file_uploads',
        ['submission_id', 'field_id'],
        unique=False
    )


def downgrade():
    """Remove performance indexes"""
    
    # Drop all created indexes
    op.drop_index('ix_file_uploads_submission_field', table_name='file_uploads')
    op.drop_index('ix_file_uploads_field_id', table_name='file_uploads')
    op.drop_index('ix_form_templates_bank_active', table_name='form_templates')
    op.drop_index('ix_form_templates_form_type', table_name='form_templates')
    op.drop_index('ix_form_submissions_created_at', table_name='form_submissions')
    op.drop_index('ix_form_submissions_submitted_by_status', table_name='form_submissions')
    op.drop_index('ix_form_submissions_template_status', table_name='form_submissions')
    op.drop_index('ix_form_submissions_status_created', table_name='form_submissions')
