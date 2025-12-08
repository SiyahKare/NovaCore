# app/telemetry/academy_router.py
"""
Academy Module Progress & Completion Tracking
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select, func, and_
from datetime import datetime
from typing import List, Dict, Any

from app.core.db import get_session
from app.core.security import get_current_user
from app.identity.models import User
from app.telemetry.models import TelemetryEvent
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/academy", tags=["academy"])


class ModuleProgress(BaseModel):
    """Module progress information."""
    module: str
    viewed: bool
    completed: bool
    viewed_at: datetime | None = None
    completed_at: datetime | None = None


class AcademyProgressResponse(BaseModel):
    """User's academy progress."""
    modules: List[ModuleProgress]
    total_modules: int
    completed_modules: int
    completion_percentage: float


@router.get(
    "/progress",
    response_model=AcademyProgressResponse,
    summary="Get Academy Progress",
    description="Get user's academy module progress and completion status.",
)
async def get_academy_progress(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AcademyProgressResponse:
    """
    Get user's academy module progress.
    
    Returns which modules have been viewed and completed.
    """
    # Define all academy modules
    all_modules = ["constitution", "novascore", "justice", "dao"]
    
    # Get all academy events for this user
    events_query = select(TelemetryEvent).where(
        and_(
            TelemetryEvent.user_id == current_user.id,
            TelemetryEvent.event.in_(["academy_module_viewed", "academy_module_completed"]),
        )
    ).order_by(TelemetryEvent.created_at.desc())
    
    events_result = await session.execute(events_query)
    events = events_result.scalars().all()
    
    # Build progress map
    progress_map: Dict[str, Dict[str, Any]] = {}
    for module in all_modules:
        progress_map[module] = {
            "viewed": False,
            "completed": False,
            "viewed_at": None,
            "completed_at": None,
        }
    
    # Process events
    for event in events:
        module = event.payload.get("module") if event.payload else None
        if not module or module not in progress_map:
            continue
        
        if event.event == "academy_module_viewed":
            if not progress_map[module]["viewed"]:
                progress_map[module]["viewed"] = True
                progress_map[module]["viewed_at"] = event.created_at
        elif event.event == "academy_module_completed":
            progress_map[module]["completed"] = True
            if not progress_map[module]["completed_at"]:
                progress_map[module]["completed_at"] = event.created_at
    
    # Build response
    modules = [
        ModuleProgress(
            module=module,
            viewed=progress_map[module]["viewed"],
            completed=progress_map[module]["completed"],
            viewed_at=progress_map[module]["viewed_at"],
            completed_at=progress_map[module]["completed_at"],
        )
        for module in all_modules
    ]
    
    completed_count = sum(1 for m in modules if m.completed)
    completion_percentage = (completed_count / len(all_modules)) * 100 if all_modules else 0
    
    return AcademyProgressResponse(
        modules=modules,
        total_modules=len(all_modules),
        completed_modules=completed_count,
        completion_percentage=completion_percentage,
    )


@router.post(
    "/modules/{module}/complete",
    status_code=status.HTTP_200_OK,
    summary="Mark Module as Completed",
    description="Mark an academy module as completed for the current user.",
)
async def complete_module(
    module: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> Dict[str, str]:
    """
    Mark an academy module as completed.
    
    This creates a telemetry event for module completion.
    """
    # Validate module name
    valid_modules = ["constitution", "novascore", "justice", "dao"]
    if module not in valid_modules:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid module. Must be one of: {', '.join(valid_modules)}",
        )
    
    # Check if already completed (to avoid duplicates)
    existing_query = select(TelemetryEvent).where(
        and_(
            TelemetryEvent.user_id == current_user.id,
            TelemetryEvent.event == "academy_module_completed",
            TelemetryEvent.payload["module"].astext == module,
        )
    ).limit(1)
    
    existing_result = await session.execute(existing_query)
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        return {"status": "already_completed", "message": "Module already marked as completed"}
    
    # Create completion event
    event = TelemetryEvent(
        user_id=current_user.id,
        event="academy_module_completed",
        payload={"module": module},
        source="citizen-portal",
    )
    
    session.add(event)
    await session.commit()
    await session.refresh(event)
    
    return {"status": "completed", "message": f"Module '{module}' marked as completed"}

