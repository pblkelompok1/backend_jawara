"""Remove rt_id column and foreign key from m_family

Revision ID: 003
Revises: 002
Create Date: 2025-11-30 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Drop foreign key constraint if exists
    op.drop_constraint('m_family_rt_id_fkey', 'm_family', type_='foreignkey')
    # Drop rt_id column
    op.drop_column('m_family', 'rt_id')


def downgrade():
    # Add rt_id column back
    op.add_column('m_family', sa.Column('rt_id', sa.Integer(), nullable=False))
    # Recreate foreign key constraint
    op.create_foreign_key('m_family_rt_id_fkey', 'm_family', 'm_rt', ['rt_id'], ['rt_id'])
