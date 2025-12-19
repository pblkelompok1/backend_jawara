"""Create marketplace tables

Revision ID: 006
Revises: 005
Create Date: 2025-12-14 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '006'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade():
    # Create m_transaction_method table
    op.create_table(
        'm_transaction_method',
        sa.Column('transaction_method_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('method_name', sa.String(100), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Create m_product table
    op.create_table(
        'm_product',
        sa.Column('product_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('price', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),
        sa.Column('stock', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('more_detail', postgresql.JSON(), nullable=True),
        sa.Column('images_path', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_user.user_id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Create t_product_transaction table
    op.create_table(
        't_product_transaction',
        sa.Column('product_transaction_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('address', sa.String(255), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, server_default='Belum Dibayar'),
        sa.Column('total_price', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('payment_proof_path', sa.String(500), nullable=True),
        sa.Column('is_cod', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_user.user_id'), nullable=False),
        sa.Column('transaction_method_id', sa.Integer(), sa.ForeignKey('m_transaction_method.transaction_method_id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
    )
    
    # Create t_list_product_transaction table (junction table)
    op.create_table(
        't_list_product_transaction',
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_product.product_id'), primary_key=True),
        sa.Column('product_transaction_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('t_product_transaction.product_transaction_id'), primary_key=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price_at_transaction', sa.Integer(), nullable=False),
    )
    
    # Create t_product_rating table
    op.create_table(
        't_product_rating',
        sa.Column('rating_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_product.product_id'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_user.user_id'), nullable=False),
        sa.Column('rating_value', sa.SmallInteger(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.CheckConstraint('rating_value >= 1 AND rating_value <= 5', name='check_rating_value_range'),
    )
    


def downgrade():
    # Drop tables in reverse order
    op.drop_table('t_product_rating', if_exists=True)
    op.drop_table('t_list_product_transaction', if_exists=True)
    op.drop_table('t_product_transaction', if_exists=True)
    op.drop_table('m_product', if_exists=True)
    op.drop_table('m_transaction_method', if_exists=True)
