"""add_nasipcourt_justice_stack_v2

Revision ID: b50f4f545527
Revises: 0b58f82c13ae
Create Date: 2025-12-02 18:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b50f4f545527'
down_revision: Union[str, None] = '0b58f82c13ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create JusticeEventType enum (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE justiceeventtype AS ENUM (
                'spam', 'toxic', 'exploit', 'fraud', 'ncr_reset', 
                'key_suspend', 'community_attack', 'low_quality_burst',
                'duplicate_proof', 'too_fast_completion', 'auto_reject',
                'appeal_rejected', 'manual_flag'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Create justice_risk_events table (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TABLE IF NOT EXISTS justice_risk_events (
                id SERIAL PRIMARY KEY,
                event_uuid VARCHAR(64) NOT NULL UNIQUE,
                user_id INTEGER NOT NULL REFERENCES users(id),
                score_ai FLOAT NOT NULL,
                score_human FLOAT,
                event_type justiceeventtype NOT NULL,
                status VARCHAR NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                meta JSONB,
                source VARCHAR
            );
        EXCEPTION
            WHEN duplicate_table THEN null;
        END $$;
    """)
    
    # Create indexes for justice_risk_events (idempotent)
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_risk_events_user_status ON justice_risk_events(user_id, status);
        CREATE INDEX IF NOT EXISTS ix_risk_events_score_ai ON justice_risk_events(score_ai);
        CREATE INDEX IF NOT EXISTS ix_risk_events_timestamp ON justice_risk_events(timestamp);
        CREATE UNIQUE INDEX IF NOT EXISTS ix_justice_risk_events_event_uuid ON justice_risk_events(event_uuid);
        CREATE INDEX IF NOT EXISTS ix_justice_risk_events_user_id ON justice_risk_events(user_id);
        CREATE INDEX IF NOT EXISTS ix_justice_risk_events_event_type ON justice_risk_events(event_type);
        CREATE INDEX IF NOT EXISTS ix_justice_risk_events_status ON justice_risk_events(status);
    """)
    
    # Create justice_cases table (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TABLE IF NOT EXISTS justice_cases (
                id SERIAL PRIMARY KEY,
                event_id INTEGER NOT NULL UNIQUE REFERENCES justice_risk_events(id),
                validators INTEGER[],
                validator_votes JSONB,
                decision VARCHAR,
                consensus_reached BOOLEAN NOT NULL DEFAULT FALSE,
                consensus_at TIMESTAMP,
                appeal_allowed BOOLEAN NOT NULL DEFAULT TRUE,
                appeal_fee_paid BOOLEAN NOT NULL DEFAULT FALSE,
                appeal_id INTEGER REFERENCES justice_task_appeals(id),
                resolved_at TIMESTAMP,
                resolved_by INTEGER REFERENCES users(id),
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL
            );
        EXCEPTION
            WHEN duplicate_table THEN null;
        END $$;
    """)
    
    # Create indexes for justice_cases
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_justice_cases_status ON justice_cases(decision);
        CREATE INDEX IF NOT EXISTS ix_justice_cases_consensus ON justice_cases(consensus_reached);
        CREATE UNIQUE INDEX IF NOT EXISTS ix_justice_cases_event_id ON justice_cases(event_id);
    """)
    
    # Create justice_penalties table (idempotent)
    op.execute("""
        DO $$ BEGIN
            CREATE TABLE IF NOT EXISTS justice_penalties (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                case_id INTEGER NOT NULL REFERENCES justice_cases(id),
                event_id INTEGER NOT NULL REFERENCES justice_risk_events(id),
                penalty_type VARCHAR NOT NULL,
                amount FLOAT,
                duration_days INTEGER,
                risk_score_delta FLOAT,
                reason VARCHAR NOT NULL,
                applied_at TIMESTAMP NOT NULL,
                applied_by INTEGER REFERENCES users(id),
                execution_metadata JSONB
            );
        EXCEPTION
            WHEN duplicate_table THEN null;
        END $$;
    """)
    
    # Create indexes for justice_penalties
    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_justice_penalties_user ON justice_penalties(user_id);
        CREATE INDEX IF NOT EXISTS ix_justice_penalties_type ON justice_penalties(penalty_type);
        CREATE INDEX IF NOT EXISTS ix_justice_penalties_case_id ON justice_penalties(case_id);
        CREATE INDEX IF NOT EXISTS ix_justice_penalties_event_id ON justice_penalties(event_id);
        CREATE INDEX IF NOT EXISTS ix_justice_penalties_applied_at ON justice_penalties(applied_at);
    """)
    
    # Legacy create_table calls removed - using raw SQL for idempotency
    op.create_table(
        'justice_risk_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_uuid', sa.String(length=64), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('score_ai', sa.Float(), nullable=False),
        sa.Column('score_human', sa.Float(), nullable=True),
        sa.Column('event_type', postgresql.ENUM('spam', 'toxic', 'exploit', 'fraud', 'ncr_reset', 'key_suspend', 'community_attack', 'low_quality_burst', 'duplicate_proof', 'too_fast_completion', 'auto_reject', 'appeal_rejected', 'manual_flag', name='justiceeventtype', create_type=False), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('meta', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_risk_events_user_status', 'justice_risk_events', ['user_id', 'status'], unique=False)
    op.create_index('ix_risk_events_score_ai', 'justice_risk_events', ['score_ai'], unique=False)
    op.create_index('ix_risk_events_timestamp', 'justice_risk_events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_justice_risk_events_event_uuid'), 'justice_risk_events', ['event_uuid'], unique=True)
    op.create_index(op.f('ix_justice_risk_events_user_id'), 'justice_risk_events', ['user_id'], unique=False)
    op.create_index(op.f('ix_justice_risk_events_event_type'), 'justice_risk_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_justice_risk_events_status'), 'justice_risk_events', ['status'], unique=False)
    
    # Create justice_cases table
    op.create_table(
        'justice_cases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('validators', postgresql.ARRAY(sa.Integer()), nullable=True),
        sa.Column('validator_votes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('decision', sa.String(), nullable=True),
        sa.Column('consensus_reached', sa.Boolean(), nullable=False),
        sa.Column('consensus_at', sa.DateTime(), nullable=True),
        sa.Column('appeal_allowed', sa.Boolean(), nullable=False),
        sa.Column('appeal_fee_paid', sa.Boolean(), nullable=False),
        sa.Column('appeal_id', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['justice_risk_events.id'], ),
        sa.ForeignKeyConstraint(['appeal_id'], ['justice_task_appeals.id'], ),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id')
    )
    op.create_index('ix_justice_cases_status', 'justice_cases', ['decision'], unique=False)
    op.create_index('ix_justice_cases_consensus', 'justice_cases', ['consensus_reached'], unique=False)
    op.create_index(op.f('ix_justice_cases_event_id'), 'justice_cases', ['event_id'], unique=True)
    
    # Create justice_penalties table
    op.create_table(
        'justice_penalties',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('case_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('penalty_type', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('duration_days', sa.Integer(), nullable=True),
        sa.Column('risk_score_delta', sa.Float(), nullable=True),
        sa.Column('reason', sa.String(), nullable=False),
        sa.Column('applied_at', sa.DateTime(), nullable=False),
        sa.Column('applied_by', sa.Integer(), nullable=True),
        sa.Column('execution_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['case_id'], ['justice_cases.id'], ),
        sa.ForeignKeyConstraint(['event_id'], ['justice_risk_events.id'], ),
        sa.ForeignKeyConstraint(['applied_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_justice_penalties_user', 'justice_penalties', ['user_id'], unique=False)
    op.create_index('ix_justice_penalties_type', 'justice_penalties', ['penalty_type'], unique=False)
    op.create_index(op.f('ix_justice_penalties_case_id'), 'justice_penalties', ['case_id'], unique=False)
    op.create_index(op.f('ix_justice_penalties_event_id'), 'justice_penalties', ['event_id'], unique=False)
    op.create_index(op.f('ix_justice_penalties_applied_at'), 'justice_penalties', ['applied_at'], unique=False)


def downgrade() -> None:
    # Drop tables
    op.drop_index(op.f('ix_justice_penalties_applied_at'), table_name='justice_penalties')
    op.drop_index(op.f('ix_justice_penalties_event_id'), table_name='justice_penalties')
    op.drop_index(op.f('ix_justice_penalties_case_id'), table_name='justice_penalties')
    op.drop_index('ix_justice_penalties_type', table_name='justice_penalties')
    op.drop_index('ix_justice_penalties_user', table_name='justice_penalties')
    op.drop_table('justice_penalties')
    
    op.drop_index(op.f('ix_justice_cases_event_id'), table_name='justice_cases')
    op.drop_index('ix_justice_cases_consensus', table_name='justice_cases')
    op.drop_index('ix_justice_cases_status', table_name='justice_cases')
    op.drop_table('justice_cases')
    
    op.drop_index(op.f('ix_justice_risk_events_status'), table_name='justice_risk_events')
    op.drop_index(op.f('ix_justice_risk_events_event_type'), table_name='justice_risk_events')
    op.drop_index(op.f('ix_justice_risk_events_user_id'), table_name='justice_risk_events')
    op.drop_index(op.f('ix_justice_risk_events_event_uuid'), table_name='justice_risk_events')
    op.drop_index('ix_risk_events_timestamp', table_name='justice_risk_events')
    op.drop_index('ix_risk_events_score_ai', table_name='justice_risk_events')
    op.drop_index('ix_risk_events_user_status', table_name='justice_risk_events')
    op.drop_table('justice_risk_events')
    
    # Drop enum
    op.execute('DROP TYPE IF EXISTS justiceeventtype')
