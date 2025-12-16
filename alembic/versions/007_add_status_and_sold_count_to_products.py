"""Add status and sold_count to products

Revision ID: 007
Revises: 006
Create Date: 2025-12-15 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007'
down_revision = '999'  # After relations are added
branch_labels = None
depends_on = None


def upgrade():
    """Add status and sold_count columns to m_product table"""
    # Add status column with default 'active'
    op.add_column(
        'm_product',
        sa.Column('status', sa.String(20), nullable=False, server_default='active')
    )
    
    # Add sold_count column with default 0
    op.add_column(
        'm_product',
        sa.Column('sold_count', sa.Integer(), nullable=False, server_default='0')
    )
    
    print("✅ Added 'status' and 'sold_count' columns to m_product table")


def downgrade():
    """Remove status and sold_count columns from m_product table"""
    op.drop_column('m_product', 'sold_count')
    op.drop_column('m_product', 'status')
    
    print("✅ Removed 'status' and 'sold_count' columns from m_product table")
