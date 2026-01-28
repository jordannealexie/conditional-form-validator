"""add updated_at to resource_relationships

Revision ID: add_rebac_updated_at
Revises: 
Create Date: 2026-01-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_rebac_updated_at'
down_revision = None  # Update this with your latest migration
branch_labels = None
depends_on = None


def upgrade():
    # Add updated_at column to resource_relationships if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'resource_relationships' 
                AND column_name = 'updated_at'
            ) THEN
                ALTER TABLE resource_relationships 
                ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE;
            END IF;
        END $$;
    """)


def downgrade():
    op.drop_column('resource_relationships', 'updated_at')
