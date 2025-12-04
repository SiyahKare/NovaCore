"""add_abuse_risk_score_tables

Revision ID: 68c43ecf99b3
Revises: a199b487ec78
Create Date: 2025-12-02 14:10:08.139039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '68c43ecf99b3'
down_revision: Union[str, None] = 'a199b487ec78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if tables exist before creating
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    # Create abuse_user_risk_profiles table (if not exists)
    if 'abuse_user_risk_profiles' not in existing_tables:
        op.create_table(
            'abuse_user_risk_profiles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('risk_score', sa.Float(), nullable=False),
            sa.Column('risk_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('last_event_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_abuse_user_risk_profiles_user_id'), 'abuse_user_risk_profiles', ['user_id'], unique=True)
        op.create_index(op.f('ix_abuse_user_risk_profiles_risk_score'), 'abuse_user_risk_profiles', ['risk_score'], unique=False)
        op.create_index(op.f('ix_abuse_user_risk_profiles_last_event_at'), 'abuse_user_risk_profiles', ['last_event_at'], unique=False)
    
    # Create abuse_events table (if not exists)
    if 'abuse_events' not in existing_tables:
        # Check if enum exists
        enum_exists = False
        try:
            conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'abuseeventtype'"))
            result = conn.execute(sa.text("SELECT 1 FROM pg_type WHERE typname = 'abuseeventtype'"))
            enum_exists = result.fetchone() is not None
        except:
            pass
        
        if not enum_exists:
            op.execute("CREATE TYPE abuseeventtype AS ENUM ('LOW_QUALITY_BURST', 'DUPLICATE_PROOF', 'TOO_FAST_COMPLETION', 'AUTO_REJECT', 'APPEAL_REJECTED', 'MANUAL_FLAG')")
        
        op.create_table(
            'abuse_events',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('event_type', sa.Enum('LOW_QUALITY_BURST', 'DUPLICATE_PROOF', 'TOO_FAST_COMPLETION', 'AUTO_REJECT', 'APPEAL_REJECTED', 'MANUAL_FLAG', name='abuseeventtype'), nullable=False),
            sa.Column('delta', sa.Float(), nullable=False),
            sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_abuse_events_user_id'), 'abuse_events', ['user_id'], unique=False)
        op.create_index(op.f('ix_abuse_events_event_type'), 'abuse_events', ['event_type'], unique=False)
        op.create_index(op.f('ix_abuse_events_created_at'), 'abuse_events', ['created_at'], unique=False)
        op.create_index('ix_abuse_events_user_type', 'abuse_events', ['user_id', 'event_type'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_abuse_events_user_type', table_name='abuse_events')
    op.drop_index(op.f('ix_abuse_events_created_at'), table_name='abuse_events')
    op.drop_index(op.f('ix_abuse_events_event_type'), table_name='abuse_events')
    op.drop_index(op.f('ix_abuse_events_user_id'), table_name='abuse_events')
    op.drop_table('abuse_events')
    op.drop_index(op.f('ix_abuse_user_risk_profiles_last_event_at'), table_name='abuse_user_risk_profiles')
    op.drop_index(op.f('ix_abuse_user_risk_profiles_risk_score'), table_name='abuse_user_risk_profiles')
    op.drop_index(op.f('ix_abuse_user_risk_profiles_user_id'), table_name='abuse_user_risk_profiles')
    op.drop_table('abuse_user_risk_profiles')
    op.execute('DROP TYPE IF EXISTS abuseeventtype')
