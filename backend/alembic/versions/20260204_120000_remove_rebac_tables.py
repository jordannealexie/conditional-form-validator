"""remove_relationship_tables

Revision ID: 20260204_remove_rebac_tables
Revises: 20260203_enforce_audit_resource_type
Create Date: 2026-02-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260204_remove_rebac_tables"
down_revision: Union[str, None] = "20260203_enforce_audit_resource_type"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Drop relationship tables."""
    conn = op.get_bind()
    conn.execute(sa.text("DROP TABLE IF EXISTS resource_relationships"))


def downgrade() -> None:
    """Recreate resource_relationships table (minimal)."""
    op.create_table(
        "resource_relationships",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("subject_type", sa.String(), nullable=False),
        sa.Column("subject_id", sa.String(), nullable=False),
        sa.Column("resource_type", sa.String(), nullable=False),
        sa.Column("resource_id", sa.String(), nullable=False),
        sa.Column("parent_resource_type", sa.String(), nullable=False),
        sa.Column("parent_resource_id", sa.String(), nullable=False),
        sa.Column("relationship_type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
