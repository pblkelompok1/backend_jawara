"""Create report tables

Revision ID: 005
Revises: 004
Create Date: 2025-12-11 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    # Create m_report table
    op.create_table(
        'm_report',
        sa.Column('report_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('category', sa.String(), nullable=False, server_default='lainnya'),
        sa.Column('report_name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='unsolved'),
        sa.Column('evidence', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    op.create_table(
        'm_letter',
        sa.Column('letter_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('letter_name', sa.String(), nullable=False),
        sa.Column('template_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    
    op.create_table(
        't_letter_transaction',
        sa.Column('letter_transaction_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('application_date', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('letter_result_path', sa.String(), nullable=True),
        sa.Column('rejection_reason', sa.String(), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_user.user_id'), nullable=False),
        sa.Column('letter_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_letter.letter_id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
    )
    

def downgrade():
    # Drop tables in reverse order
    op.drop_table('t_letter_transaction', if_exists=True)
    op.drop_table('m_letter', if_exists=True)
    op.drop_table('m_report', if_exists=True)