"""create user and refresh_session tables

Revision ID: 001
Revises: 
Create Date: 2025-11-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create m_user table
    op.create_table(
        'm_user',
        sa.Column("user_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('email', sa.String(), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),  # bcrypt hash is 60 chars, but 255 for safety
        sa.Column('role', sa.String(), nullable=False, server_default='citizen'),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
    )


    # Create m_refresh_session table
    op.create_table(
    'm_refresh_session',
    sa.Column('refresh_session_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('refresh_token_hash', sa.String(), nullable=False, unique=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    sa.Column('revoked', sa.Boolean(), nullable=False, server_default='false'),
    sa.ForeignKeyConstraint(['user_id'], ['m_user.user_id']),
)



def downgrade() -> None:
    op.drop_table('m_refresh_session')
    op.drop_table('m_user')
