"""add_user_quests_table

Revision ID: add_user_quests
Revises: c6bc6ed47388
Create Date: 2025-12-02 20:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'add_user_quests'
down_revision: Union[str, None] = 'c6bc6ed47388'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create quest_type_enum (IF NOT EXISTS)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE quest_type_enum AS ENUM ('meme', 'quiz', 'reflection', 'social', 'onchain', 'microtask', 'streak', 'referral');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create quest_status_enum (IF NOT EXISTS)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE quest_status_enum AS ENUM ('assigned', 'submitted', 'under_review', 'approved', 'rejected', 'expired');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create user_quests table (enum'lar zaten var, SQLAlchemy tekrar oluşturmayacak)
    quest_type_enum = postgresql.ENUM('meme', 'quiz', 'reflection', 'social', 'onchain', 'microtask', 'streak', 'referral', name='quest_type_enum', create_type=False)
    quest_status_enum = postgresql.ENUM('assigned', 'submitted', 'under_review', 'approved', 'rejected', 'expired', name='quest_status_enum', create_type=False)
    
    op.create_table(
        'user_quests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('quest_uuid', sa.String(length=100), nullable=False),
        sa.Column('quest_type', quest_type_enum, nullable=False),
        sa.Column('key', sa.String(length=255), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('base_reward_ncr', sa.Float(), nullable=False),
        sa.Column('base_reward_xp', sa.Integer(), nullable=False),
        sa.Column('final_reward_ncr', sa.Float(), nullable=True),
        sa.Column('final_reward_xp', sa.Integer(), nullable=True),
        sa.Column('final_score', sa.Float(), nullable=True),
        sa.Column('status', quest_status_enum, nullable=False),
        sa.Column('assigned_at', sa.DateTime(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('proof_type', sa.String(length=50), nullable=True),
        sa.Column('proof_payload_ref', sa.String(length=500), nullable=True),
        sa.Column('abuse_risk_snapshot', sa.Float(), nullable=True),
        sa.Column('house_edge_snapshot', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_user_quests_user_id'), 'user_quests', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_quests_quest_uuid'), 'user_quests', ['quest_uuid'], unique=False)
    op.create_index(op.f('ix_user_quests_key'), 'user_quests', ['key'], unique=False)
    op.create_index(op.f('ix_user_quests_status'), 'user_quests', ['status'], unique=False)
    op.create_index(op.f('ix_user_quests_assigned_at'), 'user_quests', ['assigned_at'], unique=False)
    op.create_index(op.f('ix_user_quests_expires_at'), 'user_quests', ['expires_at'], unique=False)
    op.create_index('ix_user_quests_user_status', 'user_quests', ['user_id', 'status'], unique=False)
    op.create_index('ix_user_quests_user_expires', 'user_quests', ['user_id', 'expires_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_user_quests_user_expires', table_name='user_quests')
    op.drop_index('ix_user_quests_user_status', table_name='user_quests')
    op.drop_index(op.f('ix_user_quests_expires_at'), table_name='user_quests')
    op.drop_index(op.f('ix_user_quests_assigned_at'), table_name='user_quests')
    op.drop_index(op.f('ix_user_quests_status'), table_name='user_quests')
    op.drop_index(op.f('ix_user_quests_key'), table_name='user_quests')
    op.drop_index(op.f('ix_user_quests_quest_uuid'), table_name='user_quests')
    op.drop_index(op.f('ix_user_quests_user_id'), table_name='user_quests')
    op.drop_table('user_quests')
    op.execute('DROP TYPE IF EXISTS quest_status_enum')
    op.execute('DROP TYPE IF EXISTS quest_type_enum')

