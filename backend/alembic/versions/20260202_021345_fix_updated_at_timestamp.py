"""fix_updated_at_timestamp

Revision ID: fa9440a97cd1
Revises: 69ec3f6c799f
Create Date: 2026-02-02 02:13:45.357077

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa9440a97cd1'
down_revision: Union[str, None] = '69ec3f6c799f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
