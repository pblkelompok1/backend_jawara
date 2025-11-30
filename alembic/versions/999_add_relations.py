"""Add relations between tables after all base tables are created.

Revision ID: 999
Revises: 003
Create Date: 2025-11-30 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '999'
down_revision = '003'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add foreign key constraint from m_user.resident_id to m_resident.resident_id
    op.create_foreign_key('fk_user_resident', 'm_user', 'm_resident', ['resident_id'], ['resident_id'])

    # Add other relations here if needed

def downgrade() -> None:
    op.drop_constraint('fk_user_resident', 'm_user', type_='foreignkey')
    op.drop_column('m_user', 'resident_id')
