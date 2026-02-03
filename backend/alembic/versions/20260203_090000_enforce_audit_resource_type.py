"""enforce_audit_resource_type

Revision ID: 20260203_enforce_audit_resource_type
Revises: audit_trail_001
Create Date: 2026-02-03 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260203_enforce_audit_resource_type"
down_revision: Union[str, None] = "audit_trail_001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Backfill resource_type and enforce NOT NULL."""
    connection = op.get_bind()

    # Normalize existing resource_type values
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'user' WHERE resource_type IN ('users')"))
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'role' WHERE resource_type IN ('roles')"))
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'template' WHERE resource_type IN ('templates', 'forms', 'form_template', 'form_templates')"))

    # Backfill missing resource_type based on action names
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'user' WHERE resource_type IS NULL AND action LIKE 'user_%'"))
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'user' WHERE resource_type IS NULL AND action IN ('update_profile')"))
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'role' WHERE resource_type IS NULL AND action LIKE 'role_%'"))
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'template' WHERE resource_type IS NULL AND action LIKE 'template_%'"))
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'auth' WHERE resource_type IS NULL AND action IN ('register', 'login', 'login_attempt', 'change_password')"))
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'submission' WHERE resource_type IS NULL AND action LIKE 'submission_%'"))
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'application' WHERE resource_type IS NULL AND action LIKE 'application_%'"))
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'form' WHERE resource_type IS NULL AND action LIKE 'form_%'"))

    # Ensure no NULLs remain
    connection.execute(sa.text("UPDATE audit_logs SET resource_type = 'system' WHERE resource_type IS NULL"))

    # Enforce NOT NULL with a safe default going forward
    op.alter_column(
        "audit_logs",
        "resource_type",
        existing_type=sa.String(),
        nullable=False,
        server_default="system",
    )


def downgrade() -> None:
    """Revert NOT NULL constraint on resource_type."""
    op.alter_column(
        "audit_logs",
        "resource_type",
        existing_type=sa.String(),
        nullable=True,
        server_default=None,
    )
