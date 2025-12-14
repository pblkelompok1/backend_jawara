"""Create activity tables

Revision ID: 004
Revises: 003
Create Date: 2025-12-11 18:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create m_activity table
    op.create_table(
        'm_activity',
        sa.Column('activity_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('activity_name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('organizer', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='akan_datang'),
        sa.Column('banner_img', sa.String(), nullable=True, server_default='storage/banner/1.png'),
        sa.Column('preview_images', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('category', sa.String(), nullable=False, server_default='lainnya'),
    )

    # Create t_dashboard_banner table
    op.create_table(
        't_dashboard_banner',
        sa.Column('banner_id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('position', sa.Integer(), nullable=False),
        sa.Column('activity_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('m_activity.activity_id'), nullable=False),
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('t_dashboard_banner', if_exists=True)
    op.drop_table('m_activity', if_exists=True)