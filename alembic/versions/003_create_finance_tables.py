"""Remove rt_id column and foreign key from m_family

Revision ID: 003
Revises: 002
Create Date: 2025-11-30 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Create m_fee table
    op.create_table(
        'm_fee',
        sa.Column('fee_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('fee_name', sa.String(255), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('charge_date', sa.Date(), nullable=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('fee_category', sa.String(), nullable=False),
        sa.Column('automation_mode', sa.String(), nullable=True, server_default='weekly'),
        sa.Column('due_date', sa.Date(), nullable=True),
    )

    # Create t_fee_transaction table
    op.create_table(
        't_fee_transaction',
        sa.Column('fee_transaction_id', sa.Integer(), primary_key=True),
        sa.Column('transaction_date', sa.Date(), nullable=True),
        sa.Column('fee_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_fee.fee_id'), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('transaction_method', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='unpaid'),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_family.family_id'), nullable=False),
        sa.Column('evidence_path', sa.String(), nullable=False),
    )

    # Create t_fee_transaction table
    op.create_table(
        't_finance_transaction',
        sa.Column('finance_transaction_id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('transaction_date', sa.Date(), nullable=True),
        sa.Column('evidence_path', sa.String(), nullable=False),
    )
    

def downgrade():
    # Drop all tables created in upgrade (with if_exists to avoid errors)
    op.drop_table('t_finance_transaction', if_exists=True)
    op.drop_table('t_fee_transaction', if_exists=True)
    op.drop_table('m_fee', if_exists=True)