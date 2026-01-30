"""merge_heads

Revision ID: e9d1e841d767
Revises: 34e723e20fc5, add_rebac_updated_at
Create Date: 2026-01-30 02:15:12.928513

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9d1e841d767'
down_revision: Union[str, None] = ('34e723e20fc5', 'add_rebac_updated_at')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
