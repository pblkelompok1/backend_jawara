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
revision: str = '002'
down_revision = '001'
branch_labels = None
depends_on = None

def upgrade() -> None:
    
    # Create m_rt table
    op.create_table(
        'm_rt',
        sa.Column('rt_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('rt_name', sa.String(), nullable=False, unique=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),

        sa.ForeignKeyConstraint(['user_id'], ['m_user.user_id']), # For RT head
    )


# Create m_occupation table
    op.create_table(
        'm_occupation',
        sa.Column('occupation_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('occupation_name', sa.String(), nullable=False, unique=True),
    )


    # Create m_family table
    op.create_table(
        'm_family',
        sa.Column('family_id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('family_name', sa.String(), nullable=False, unique=True),
        sa.Column('kk_path', sa.String(), nullable=False, unique=True),
        sa.Column('status', sa.String(), nullable=False, unique=True),
        sa.Column('resident_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('rt_id', sa.Integer(), nullable=False),

        sa.ForeignKeyConstraint(['rt_id'], ['m_rt.rt_id']),
    )


    # Create m_resident table
    op.create_table(
        'm_resident',
        sa.Column("resident_id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('nik', sa.String(), nullable=False, unique=True),
        sa.Column('phone', sa.String(), nullable=False),  
        sa.Column('place_of_birth', sa.String(), nullable=False),
        sa.Column('date_of_birth', sa.Date(), nullable=False),
        sa.Column('gender', sa.String(), nullable=False),
        sa.Column('is_deceased', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('family_role', sa.String(), nullable=False),
        sa.Column('religion', sa.String(), nullable=False),
        sa.Column('domicile_status', sa.String(), nullable=False),
        sa.Column('blood_type', sa.String(), nullable=False),
        sa.Column('occupation', sa.String(), nullable=False),
        sa.Column('profile_img_path', sa.String(), nullable=False, server_default='"default_profile.png"'),
        sa.Column('ktp_path', sa.String(), nullable=False, server_default='"default_profile.png"'),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('occupation_id', sa.Integer(), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),

        sa.ForeignKeyConstraint(['user_id'], ['m_user.user_id']),
        sa.ForeignKeyConstraint(['occupation_id'], ['m_occupation.occupation_id']),
        sa.ForeignKeyConstraint(['family_id'], ['m_family.family_id']),
    )


    op.create_foreign_key(
        'fk_family_resident',
        'm_family', 'm_resident',
        ['resident_id'], ['resident_id']
    )


    # Create m_home table
    op.create_table(
        'm_home',
        sa.Column('home_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('home_name', sa.String(), nullable=False, unique=True),
        sa.Column('home_address', sa.String(), nullable=False, unique=True),
        sa.Column('status', sa.String(), nullable=False, unique=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),

        sa.ForeignKeyConstraint(['family_id'], ['m_family.family_id']),
    )


    # Create r_home_history table
    op.create_table(
        't_home_history',
        sa.Column('home_id', sa.Integer),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),

        sa.Column('moved_in_date', sa.Date(), nullable=False),
        sa.Column('moved_out_date', sa.Date(), nullable=True),

        sa.ForeignKeyConstraint(['home_id'], ['m_home.home_id']),
        sa.ForeignKeyConstraint(['family_id'], ['m_family.family_id']),
    )


    # Create m_family_movement table
    op.create_table(
        'm_family_movement',
        sa.Column('family_movement_id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('reason', sa.String(), nullable=False, unique=True),
        sa.Column('old_address', sa.String(), nullable=False, unique=True),
        sa.Column('new_address', sa.String(), nullable=False, unique=True),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=False),

        sa.ForeignKeyConstraint(['family_id'], ['m_family.family_id']),
    )


def downgrade() -> None:
    op.execute("DROP TABLE t_home_history CASCADE")
    op.execute("DROP TABLE m_family_movement CASCADE")
    op.execute("DROP TABLE m_resident CASCADE")
    op.execute("DROP TABLE m_home CASCADE")
    op.execute("DROP TABLE m_family CASCADE")
    op.execute("DROP TABLE m_rt CASCADE")
    op.execute("DROP TABLE m_occupation CASCADE")

