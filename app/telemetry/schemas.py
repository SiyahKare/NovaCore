# app/telemetry/schemas.py
"""
NovaCore Telemetry Schemas - Growth & Education Event Tracking
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class TelemetryEventCreate(BaseModel):
    """Create a telemetry event."""
    event: str = Field(..., description="Event type (e.g., onboarding_completed, academy_module_viewed)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event-specific metadata")
    session_id: Optional[str] = Field(None, description="Optional session identifier")
    source: Optional[str] = Field(None, description="Source: 'citizen-portal', 'admin-panel', etc.")


class TelemetryEventResponse(BaseModel):
    """Telemetry event response."""
    id: str
    user_id: str
    event: str
    payload: Dict[str, Any]
    created_at: datetime
    session_id: Optional[str] = None
    source: Optional[str] = None


# Growth metrics response
class GrowthMetricsResponse(BaseModel):
    """Growth metrics for admin dashboard."""
    # Onboarding metrics
    onboarding_last_24h: int
    onboarding_last_7d: int
    onboarding_total: int

    # Academy metrics
    academy_views_last_24h: int
    academy_views_last_7d: int
    academy_module_completions_last_24h: int
    academy_module_completions_last_7d: int
    top_modules: list[Dict[str, Any]]  # [{module: "constitution", views: 42, completions: 12}]

    # Justice metrics
    recall_requests_last_24h: int
    recall_requests_total: int
    appeals_submitted_last_24h: int
    appeals_submitted_total: int

    # Engagement metrics
    active_users_last_24h: int
    active_users_last_7d: int

    generated_at: datetime

