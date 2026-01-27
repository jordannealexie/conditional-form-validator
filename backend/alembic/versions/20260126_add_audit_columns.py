"""add_audit_columns_to_existing_tables

Revision ID: 20260126_add_audit_columns
Revises: 20260126_add_field_types
Create Date: 2026-01-26 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260126_add_audit_columns'
down_revision: Union[str, None] = 'a9facb9ee02f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Add audit columns to existing tables for tracking user actions.
    All columns are nullable to maintain backward compatibility.
    """
    
    # ==========================================
    # 1. USERS TABLE - Update audit columns
    # ==========================================
    
    # Drop existing updated_by column (was String)
    op.drop_column('users', 'updated_by')
    
    # Add updated_by as Integer FK to users.id
    op.add_column('users', 
        sa.Column('updated_by', sa.Integer(), nullable=True, comment='User ID who last updated this record')
    )
    op.create_foreign_key(
        'fk_users_updated_by_users',
        'users', 'users',
        ['updated_by'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_users_updated_by', 'users', ['updated_by'])
    
    # Ensure updated_at is nullable
    op.alter_column('users', 'updated_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=True
    )
    
    # ==========================================
    # 2. ROLES TABLE - Update audit columns
    # ==========================================
    
    # Drop existing created_by and updated_by columns (were String)
    op.drop_column('roles', 'created_by')
    op.drop_column('roles', 'updated_by')
    
    # Add created_by and updated_by as Integer FK to users.id
    op.add_column('roles',
        sa.Column('created_by', sa.Integer(), nullable=True, comment='User ID of creator')
    )
    op.create_foreign_key(
        'fk_roles_created_by_users',
        'roles', 'users',
        ['created_by'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_roles_created_by', 'roles', ['created_by'])
    
    op.add_column('roles',
        sa.Column('updated_by', sa.Integer(), nullable=True, comment='User ID of last updater')
    )
    op.create_foreign_key(
        'fk_roles_updated_by_users',
        'roles', 'users',
        ['updated_by'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_roles_updated_by', 'roles', ['updated_by'])
    
    # ==========================================
    # 3. FORM_SUBMISSIONS TABLE - Update audit columns
    # ==========================================
    
    # Make fieldman_id nullable (legacy field)
    op.alter_column('form_submissions', 'fieldman_id',
        existing_type=sa.String(100),
        nullable=True
    )
    
    # Drop existing submitted_by, reviewed_by, validated_by columns (were String)
    op.drop_column('form_submissions', 'submitted_by')
    op.drop_column('form_submissions', 'reviewed_by')
    op.drop_column('form_submissions', 'validated_by')
    
    # Add submitted_by as Integer FK to users.id
    op.add_column('form_submissions',
        sa.Column('submitted_by', sa.Integer(), nullable=True, comment='User ID of submitter')
    )
    op.create_foreign_key(
        'fk_form_submissions_submitted_by_users',
        'form_submissions', 'users',
        ['submitted_by'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_form_submissions_submitted_by', 'form_submissions', ['submitted_by'])
    
    # Add reviewed_by as Integer FK to users.id
    op.add_column('form_submissions',
        sa.Column('reviewed_by', sa.Integer(), nullable=True, comment='User ID of reviewer (approval/rejection)')
    )
    op.create_foreign_key(
        'fk_form_submissions_reviewed_by_users',
        'form_submissions', 'users',
        ['reviewed_by'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_form_submissions_reviewed_by', 'form_submissions', ['reviewed_by'])
    
    # Add validated_by as Integer FK to users.id
    op.add_column('form_submissions',
        sa.Column('validated_by', sa.Integer(), nullable=True, comment='User ID who validated/approved')
    )
    op.create_foreign_key(
        'fk_form_submissions_validated_by_users',
        'form_submissions', 'users',
        ['validated_by'], ['id'],
        ondelete='SET NULL'
    )
    op.create_index('ix_form_submissions_validated_by', 'form_submissions', ['validated_by'])


def downgrade() -> None:
    """
    Revert audit column changes.
    """
    
    # ==========================================
    # FORM_SUBMISSIONS TABLE - Revert changes
    # ==========================================
    
    # Drop new Integer FK columns
    op.drop_index('ix_form_submissions_validated_by', table_name='form_submissions')
    op.drop_constraint('fk_form_submissions_validated_by_users', 'form_submissions', type_='foreignkey')
    op.drop_column('form_submissions', 'validated_by')
    
    op.drop_index('ix_form_submissions_reviewed_by', table_name='form_submissions')
    op.drop_constraint('fk_form_submissions_reviewed_by_users', 'form_submissions', type_='foreignkey')
    op.drop_column('form_submissions', 'reviewed_by')
    
    op.drop_index('ix_form_submissions_submitted_by', table_name='form_submissions')
    op.drop_constraint('fk_form_submissions_submitted_by_users', 'form_submissions', type_='foreignkey')
    op.drop_column('form_submissions', 'submitted_by')
    
    # Restore old String columns
    op.add_column('form_submissions',
        sa.Column('validated_by', sa.String(100), nullable=True, comment='Username who validated/approved')
    )
    op.add_column('form_submissions',
        sa.Column('reviewed_by', sa.String(100), nullable=True, comment='Username of reviewer (approval/rejection)')
    )
    op.add_column('form_submissions',
        sa.Column('submitted_by', sa.String(100), nullable=True, comment='Username of submitter (replaces fieldman_id)')
    )
    
    # Revert fieldman_id to NOT NULL
    op.alter_column('form_submissions', 'fieldman_id',
        existing_type=sa.String(100),
        nullable=False
    )
    
    # ==========================================
    # ROLES TABLE - Revert changes
    # ==========================================
    
    # Drop new Integer FK columns
    op.drop_index('ix_roles_updated_by', table_name='roles')
    op.drop_constraint('fk_roles_updated_by_users', 'roles', type_='foreignkey')
    op.drop_column('roles', 'updated_by')
    
    op.drop_index('ix_roles_created_by', table_name='roles')
    op.drop_constraint('fk_roles_created_by_users', 'roles', type_='foreignkey')
    op.drop_column('roles', 'created_by')
    
    # Restore old String columns
    op.add_column('roles',
        sa.Column('updated_by', sa.String(100), nullable=True, comment='Username of last updater')
    )
    op.add_column('roles',
        sa.Column('created_by', sa.String(100), nullable=True, comment='Username of creator')
    )
    
    # ==========================================
    # USERS TABLE - Revert changes
    # ==========================================
    
    # Revert updated_at to NOT NULL
    op.alter_column('users', 'updated_at',
        existing_type=sa.DateTime(timezone=True),
        nullable=False
    )
    
    # Drop new Integer FK column
    op.drop_index('ix_users_updated_by', table_name='users')
    op.drop_constraint('fk_users_updated_by_users', 'users', type_='foreignkey')
    op.drop_column('users', 'updated_by')
    
    # Restore old String column
    op.add_column('users',
        sa.Column('updated_by', sa.String(100), nullable=True, comment='Username of user who last updated this record')
    )
