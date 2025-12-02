"""
NovaCore Agency Routes
"""
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.agency.models import OperatorRole
from app.agency.schemas import (
    AgencyCreate,
    AgencyResponse,
    AgencyUpdate,
    AgencyWithStats,
    OperatorAdd,
    OperatorResponse,
    OperatorUpdate,
    PerformerCreate,
    PerformerResponse,
    PerformerUpdate,
    RevenueSplit,
)
from app.agency.service import AgencyService
from app.core.db import get_session
from app.core.security import get_current_user
from app.identity.models import User

router = APIRouter(prefix="/api/v1", tags=["agency"])


# ============ Agency Endpoints ============
@router.get(
    "/agency/my",
    response_model=AgencyWithStats,
    summary="My Agency",
    description="Get current user's agency with stats.",
)
async def get_my_agency(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AgencyWithStats:
    """Get current user's owned agency."""
    service = AgencyService(session)
    agency = await service.get_user_agency(current_user.id)

    if not agency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't have an agency",
        )

    return await service.get_agency_with_stats(agency.id)


@router.post(
    "/agency",
    response_model=AgencyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Agency",
    description="Create a new agency (become an agency owner).",
)
async def create_agency(
    data: AgencyCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AgencyResponse:
    """Create new agency."""
    service = AgencyService(session)

    # Check if user already has an agency
    existing = await service.get_user_agency(current_user.id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already own an agency",
        )

    return await service.create_agency(current_user.id, data)


@router.get(
    "/agency/{agency_id}",
    response_model=AgencyWithStats,
    summary="Get Agency",
    description="Get agency by ID with stats.",
)
async def get_agency(
    agency_id: int,
    session: AsyncSession = Depends(get_session),
) -> AgencyWithStats:
    """Get agency by ID."""
    service = AgencyService(session)
    return await service.get_agency_with_stats(agency_id)


@router.patch(
    "/agency/{agency_id}",
    response_model=AgencyResponse,
    summary="Update Agency",
    description="Update agency (owner/patronice only).",
)
async def update_agency(
    agency_id: int,
    data: AgencyUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> AgencyResponse:
    """Update agency."""
    service = AgencyService(session)

    # Check access
    await service.check_operator_access(
        current_user.id,
        agency_id,
        [OperatorRole.PATRONICE],
    )

    agency = await service.get_agency(agency_id)
    if not agency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agency not found",
        )

    return await service.update_agency(agency, data)


# ============ Operator Endpoints ============
@router.get(
    "/agency/{agency_id}/operators",
    response_model=list[OperatorResponse],
    summary="List Operators",
    description="List agency operators.",
)
async def list_operators(
    agency_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> list[OperatorResponse]:
    """List agency operators."""
    service = AgencyService(session)

    # Check access
    await service.check_operator_access(current_user.id, agency_id)

    return await service.get_operators(agency_id)


@router.post(
    "/agency/{agency_id}/operators",
    response_model=OperatorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add Operator",
    description="Add operator to agency (patronice only).",
)
async def add_operator(
    agency_id: int,
    data: OperatorAdd,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OperatorResponse:
    """Add operator to agency."""
    service = AgencyService(session)

    # Check access - only patronice can add operators
    await service.check_operator_access(
        current_user.id,
        agency_id,
        [OperatorRole.PATRONICE],
    )

    return await service.add_operator(agency_id, data)


@router.patch(
    "/agency/{agency_id}/operators/{operator_id}",
    response_model=OperatorResponse,
    summary="Update Operator",
    description="Update operator (patronice only).",
)
async def update_operator(
    agency_id: int,
    operator_id: int,
    data: OperatorUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> OperatorResponse:
    """Update operator."""
    service = AgencyService(session)

    await service.check_operator_access(
        current_user.id,
        agency_id,
        [OperatorRole.PATRONICE],
    )

    return await service.update_operator(operator_id, data)


# ============ Performer Endpoints ============
@router.get(
    "/agency/{agency_id}/performers",
    response_model=list[PerformerResponse],
    summary="List Performers",
    description="List agency performers.",
)
async def list_performers(
    agency_id: int,
    session: AsyncSession = Depends(get_session),
    active_only: bool = Query(True),
) -> list[PerformerResponse]:
    """List agency performers."""
    service = AgencyService(session)
    return await service.get_agency_performers(agency_id, active_only)


@router.post(
    "/agency/{agency_id}/performers",
    response_model=PerformerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Performer",
    description="Create performer for agency.",
)
async def create_performer(
    agency_id: int,
    data: PerformerCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PerformerResponse:
    """Create performer."""
    service = AgencyService(session)

    # Check access - patronice or manager
    await service.check_operator_access(
        current_user.id,
        agency_id,
        [OperatorRole.PATRONICE, OperatorRole.MANAGER],
    )

    return await service.create_performer(agency_id, data)


@router.get(
    "/performers/{performer_id}",
    response_model=PerformerResponse,
    summary="Get Performer",
    description="Get performer by ID.",
)
async def get_performer(
    performer_id: int,
    session: AsyncSession = Depends(get_session),
) -> PerformerResponse:
    """Get performer by ID."""
    service = AgencyService(session)
    performer = await service.get_performer(performer_id)

    if not performer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performer not found",
        )

    return PerformerResponse.model_validate(performer)


@router.get(
    "/performers/handle/{handle}",
    response_model=PerformerResponse,
    summary="Get Performer by Handle",
    description="Get performer by handle.",
)
async def get_performer_by_handle(
    handle: str,
    session: AsyncSession = Depends(get_session),
) -> PerformerResponse:
    """Get performer by handle."""
    service = AgencyService(session)
    performer = await service.get_performer_by_handle(handle)

    if not performer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performer not found",
        )

    return PerformerResponse.model_validate(performer)


@router.patch(
    "/performers/{performer_id}",
    response_model=PerformerResponse,
    summary="Update Performer",
    description="Update performer.",
)
async def update_performer(
    performer_id: int,
    data: PerformerUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> PerformerResponse:
    """Update performer."""
    service = AgencyService(session)

    performer = await service.get_performer(performer_id)
    if not performer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Performer not found",
        )

    # Check access
    await service.check_operator_access(
        current_user.id,
        performer.agency_id,
        [OperatorRole.PATRONICE, OperatorRole.MANAGER],
    )

    return await service.update_performer(performer, data)


# ============ Revenue Split ============
@router.get(
    "/performers/{performer_id}/revenue-split",
    response_model=RevenueSplit,
    summary="Calculate Revenue Split",
    description="Calculate revenue split for a performer.",
)
async def calculate_revenue_split(
    performer_id: int,
    amount: Decimal = Query(..., gt=0),
    session: AsyncSession = Depends(get_session),
) -> RevenueSplit:
    """Calculate revenue split for performer."""
    service = AgencyService(session)
    return await service.calculate_revenue_split(performer_id, amount)

