# app/telemetry/models.py
"""
Aurora Telemetry Models - Growth & Education Event Tracking
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field, Column, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid


class TelemetryEvent(SQLModel, table=True):
    """Telemetry event for growth and education tracking."""
    __tablename__ = "telemetry_events"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(UUID(as_uuid=True), primary_key=True, index=True),
    )

    user_id: str = Field(index=True, description="User who triggered the event")
    event: str = Field(index=True, max_length=128, description="Event type (e.g., onboarding_completed)")
    payload: dict = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Event-specific metadata",
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    # Optional: session/context tracking
    session_id: Optional[str] = Field(default=None, index=True)
    source: Optional[str] = Field(default=None, max_length=64, description="Source: 'citizen-portal', 'admin-panel', etc.")

