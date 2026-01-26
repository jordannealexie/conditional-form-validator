"""add_field_types_and_enums_tables

Revision ID: 20260126_add_field_types
Revises: 20260121_143018
Create Date: 2026-01-26 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260126_add_field_types'
down_revision: Union[str, None] = '20260121_143018'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum_definitions table
    op.create_table(
        'enum_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(length=50), nullable=False, server_default='static'),
        sa.Column('static_options', sa.JSON(), nullable=True),
        sa.Column('table_name', sa.String(length=100), nullable=True),
        sa.Column('value_column', sa.String(length=100), nullable=True),
        sa.Column('label_column', sa.String(length=100), nullable=True),
        sa.Column('filter_conditions', sa.JSON(), nullable=True),
        sa.Column('api_url', sa.String(length=500), nullable=True),
        sa.Column('api_method', sa.String(length=10), nullable=True),
        sa.Column('api_headers', sa.JSON(), nullable=True),
        sa.Column('api_transform', sa.Text(), nullable=True),
        sa.Column('custom_query', sa.Text(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_enum_definitions_id'), 'enum_definitions', ['id'], unique=False)
    op.create_index(op.f('ix_enum_definitions_name'), 'enum_definitions', ['name'], unique=True)

    # Create field_type_definitions table
    op.create_table(
        'field_type_definitions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('base_type', sa.String(length=50), nullable=False),
        sa.Column('schema_definition', sa.JSON(), nullable=False),
        sa.Column('ui_widget', sa.String(length=100), nullable=True),
        sa.Column('ui_options', sa.JSON(), nullable=True),
        sa.Column('validation_rules', sa.JSON(), nullable=True),
        sa.Column('default_value', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_field_type_definitions_id'), 'field_type_definitions', ['id'], unique=False)
    op.create_index(op.f('ix_field_type_definitions_name'), 'field_type_definitions', ['name'], unique=True)

    # Create form_field_mappings table
    op.create_table(
        'form_field_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('field_name', sa.String(length=100), nullable=False),
        sa.Column('field_type_id', sa.Integer(), nullable=True),
        sa.Column('enum_definition_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['form_templates.id'], ),
        sa.ForeignKeyConstraint(['field_type_id'], ['field_type_definitions.id'], ),
        sa.ForeignKeyConstraint(['enum_definition_id'], ['enum_definitions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('template_id', 'field_name', name='uq_template_field')
    )
    op.create_index(op.f('ix_form_field_mappings_id'), 'form_field_mappings', ['id'], unique=False)
    op.create_index(op.f('ix_form_field_mappings_template_id'), 'form_field_mappings', ['template_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_form_field_mappings_template_id'), table_name='form_field_mappings')
    op.drop_index(op.f('ix_form_field_mappings_id'), table_name='form_field_mappings')
    op.drop_table('form_field_mappings')
    
    op.drop_index(op.f('ix_field_type_definitions_name'), table_name='field_type_definitions')
    op.drop_index(op.f('ix_field_type_definitions_id'), table_name='field_type_definitions')
    op.drop_table('field_type_definitions')
    
    op.drop_index(op.f('ix_enum_definitions_name'), table_name='enum_definitions')
    op.drop_index(op.f('ix_enum_definitions_id'), table_name='enum_definitions')
    op.drop_table('enum_definitions')
