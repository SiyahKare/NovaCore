"""Add consent and privacy profile tables

Revision ID: 92ddabb66c80
Revises: 
Create Date: 2025-12-01 10:48:34.234757

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON


# revision identifiers, used by Alembic.
revision: str = '92ddabb66c80'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create consent_sessions table
    op.create_table(
        'consent_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('client_fingerprint', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
    )

    # Create consent_clause_logs table
    op.create_table(
        'consent_clause_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column('session_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('clause_id', sa.String(), nullable=False, index=True),
        sa.Column('status', sa.String(), nullable=False, index=True),
        sa.Column('comprehension_passed', sa.Boolean(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), nullable=False),
    )

    # Create consent_redline table
    op.create_table(
        'consent_redline',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column('session_id', UUID(as_uuid=True), nullable=False, index=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('redline_status', sa.String(), nullable=False, index=True),
        sa.Column('user_note_hash', sa.String(), nullable=True),
        sa.Column('answered_at', sa.DateTime(), nullable=False),
    )

    # Create consent_records table
    op.create_table(
        'consent_records',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, index=True),
        sa.Column('user_id', sa.String(), nullable=False, index=True),
        sa.Column('contract_version', sa.String(), nullable=False, index=True),
        sa.Column('clauses_accepted', JSON, nullable=False),
        sa.Column('redline_accepted', sa.Boolean(), nullable=False, default=True),
        sa.Column('signature_text', sa.String(), nullable=False),
        sa.Column('contract_hash', sa.String(), nullable=False, index=True),
        sa.Column('signed_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('client_fingerprint', sa.String(), nullable=True),
    )

    # Create user_privacy_profiles table
    op.create_table(
        'user_privacy_profiles',
        sa.Column('user_id', sa.String(), primary_key=True),
        sa.Column('latest_consent_id', UUID(as_uuid=True), nullable=True),
        sa.Column('contract_version', sa.String(), nullable=True),
        sa.Column('data_usage_policy', JSON, nullable=False),
        sa.Column('consent_level', sa.String(), nullable=True),
        sa.Column('recall_mode', sa.String(), nullable=True),
        sa.Column('recall_requested_at', sa.DateTime(), nullable=True),
        sa.Column('recall_completed_at', sa.DateTime(), nullable=True),
        sa.Column('last_policy_updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['latest_consent_id'], ['consent_records.id']),
    )


def downgrade() -> None:
    op.drop_table('user_privacy_profiles')
    op.drop_table('consent_records')
    op.drop_table('consent_redline')
    op.drop_table('consent_clause_logs')
    op.drop_table('consent_sessions')
