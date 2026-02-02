"""add_audit_trail_columns

Revision ID: audit_trail_001
Revises: fa9440a97cd1
Create Date: 2026-02-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'audit_trail_001'
down_revision: Union[str, None] = 'fa9440a97cd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add audit trail columns to audit_logs table."""
    # Add changes column for before/after tracking
    op.add_column('audit_logs', sa.Column('changes', sa.JSON(), nullable=True, comment='Before and after values in JSON format'))
    
    # Add created_by, updated_by, deleted_by columns
    op.add_column('audit_logs', sa.Column('created_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True, comment='User ID who created this record'))
    op.add_column('audit_logs', sa.Column('updated_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True, comment='User ID who updated this record'))
    op.add_column('audit_logs', sa.Column('deleted_by', sa.Integer(), sa.ForeignKey('users.id'), nullable=True, comment='User ID who deleted this record'))


def downgrade() -> None:
    """Remove audit trail columns from audit_logs table."""
    op.drop_column('audit_logs', 'deleted_by')
    op.drop_column('audit_logs', 'updated_by')
    op.drop_column('audit_logs', 'created_by')
    op.drop_column('audit_logs', 'changes')
