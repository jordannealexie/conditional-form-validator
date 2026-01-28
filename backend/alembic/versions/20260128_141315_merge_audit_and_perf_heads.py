"""merge_audit_and_perf_heads

Revision ID: 34e723e20fc5
Revises: 20260126_add_audit_columns, perf_indexes_001
Create Date: 2026-01-28 14:13:15.394247

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34e723e20fc5'
down_revision: Union[str, None] = ('20260126_add_audit_columns', 'perf_indexes_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
