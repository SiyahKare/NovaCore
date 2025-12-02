"""
NovaCore Agency Service
"""
from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.agency.models import Agency, AgencyOperator, OperatorRole, Performer
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
from app.core.logging import get_logger

logger = get_logger("agency")


class AgencyService:
    """Agency service."""

    def __init__(self, session: AsyncSession):
        self.session = session

    # ============ Agency CRUD ============
    async def get_agency(self, agency_id: int) -> Agency | None:
        """Get agency by ID."""
        result = await self.session.execute(
            select(Agency).where(Agency.id == agency_id)
        )
        return result.scalar_one_or_none()

    async def get_agency_by_slug(self, slug: str) -> Agency | None:
        """Get agency by slug."""
        result = await self.session.execute(
            select(Agency).where(Agency.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_user_agency(self, user_id: int) -> Agency | None:
        """Get agency owned by user."""
        result = await self.session.execute(
            select(Agency).where(Agency.owner_user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_agency(
        self,
        owner_user_id: int,
        data: AgencyCreate,
    ) -> AgencyResponse:
        """Create new agency."""
        # Check if slug exists
        existing = await self.get_agency_by_slug(data.slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agency slug already exists",
            )

        # Validate shares sum to 100
        total_share = data.default_performer_share + data.default_agency_share + data.default_treasury_share
        if total_share != 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Revenue shares must sum to 100, got {total_share}",
            )

        agency = Agency(
            name=data.name,
            slug=data.slug,
            description=data.description,
            owner_user_id=owner_user_id,
            default_performer_share=data.default_performer_share,
            default_agency_share=data.default_agency_share,
            default_treasury_share=data.default_treasury_share,
        )
        self.session.add(agency)
        await self.session.flush()
        await self.session.refresh(agency)

        # Add owner as PATRONICE operator
        operator = AgencyOperator(
            agency_id=agency.id,
            user_id=owner_user_id,
            role=OperatorRole.PATRONICE,
        )
        self.session.add(operator)
        await self.session.flush()

        logger.info(
            "agency_created",
            agency_id=agency.id,
            owner_user_id=owner_user_id,
            slug=data.slug,
        )

        return AgencyResponse.model_validate(agency)

    async def update_agency(
        self,
        agency: Agency,
        data: AgencyUpdate,
    ) -> AgencyResponse:
        """Update agency."""
        update_dict = data.model_dump(exclude_unset=True)

        # Validate shares if any are being updated
        performer_share = update_dict.get("default_performer_share", agency.default_performer_share)
        agency_share = update_dict.get("default_agency_share", agency.default_agency_share)
        treasury_share = update_dict.get("default_treasury_share", agency.default_treasury_share)

        total_share = performer_share + agency_share + treasury_share
        if total_share != 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Revenue shares must sum to 100, got {total_share}",
            )

        for field, value in update_dict.items():
            setattr(agency, field, value)

        agency.updated_at = datetime.utcnow()
        self.session.add(agency)
        await self.session.flush()
        await self.session.refresh(agency)

        logger.info("agency_updated", agency_id=agency.id)

        return AgencyResponse.model_validate(agency)

    async def get_agency_with_stats(self, agency_id: int) -> AgencyWithStats:
        """Get agency with performer count and earnings."""
        agency = await self.get_agency(agency_id)
        if not agency:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agency not found",
            )

        # Count performers
        count_result = await self.session.execute(
            select(func.count(Performer.id)).where(
                Performer.agency_id == agency_id,
                Performer.is_active == True,
            )
        )
        performer_count = count_result.scalar() or 0

        # Total earnings
        earnings_result = await self.session.execute(
            select(func.sum(Performer.total_earnings)).where(
                Performer.agency_id == agency_id
            )
        )
        total_earnings = Decimal(earnings_result.scalar() or 0)

        return AgencyWithStats(
            **AgencyResponse.model_validate(agency).model_dump(),
            performer_count=performer_count,
            total_earnings=total_earnings,
        )

    # ============ Operators ============
    async def add_operator(
        self,
        agency_id: int,
        data: OperatorAdd,
    ) -> OperatorResponse:
        """Add operator to agency."""
        # Check if already exists
        result = await self.session.execute(
            select(AgencyOperator).where(
                AgencyOperator.agency_id == agency_id,
                AgencyOperator.user_id == data.user_id,
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already an operator",
            )

        operator = AgencyOperator(
            agency_id=agency_id,
            user_id=data.user_id,
            role=data.role,
            custom_share=data.custom_share,
        )
        self.session.add(operator)
        await self.session.flush()
        await self.session.refresh(operator)

        logger.info(
            "operator_added",
            agency_id=agency_id,
            user_id=data.user_id,
            role=data.role.value,
        )

        return OperatorResponse.model_validate(operator)

    async def get_operators(self, agency_id: int) -> list[OperatorResponse]:
        """Get agency operators."""
        result = await self.session.execute(
            select(AgencyOperator).where(AgencyOperator.agency_id == agency_id)
        )
        operators = result.scalars().all()
        return [OperatorResponse.model_validate(op) for op in operators]

    async def update_operator(
        self,
        operator_id: int,
        data: OperatorUpdate,
    ) -> OperatorResponse:
        """Update operator."""
        result = await self.session.execute(
            select(AgencyOperator).where(AgencyOperator.id == operator_id)
        )
        operator = result.scalar_one_or_none()
        if not operator:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operator not found",
            )

        update_dict = data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(operator, field, value)

        operator.updated_at = datetime.utcnow()
        self.session.add(operator)
        await self.session.flush()
        await self.session.refresh(operator)

        return OperatorResponse.model_validate(operator)

    async def check_operator_access(
        self,
        user_id: int,
        agency_id: int,
        required_roles: list[OperatorRole] | None = None,
    ) -> AgencyOperator:
        """Check if user has operator access to agency."""
        result = await self.session.execute(
            select(AgencyOperator).where(
                AgencyOperator.agency_id == agency_id,
                AgencyOperator.user_id == user_id,
                AgencyOperator.is_active == True,
            )
        )
        operator = result.scalar_one_or_none()

        if not operator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized for this agency",
            )

        if required_roles and operator.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {[r.value for r in required_roles]}",
            )

        return operator

    # ============ Performers ============
    async def get_performer(self, performer_id: int) -> Performer | None:
        """Get performer by ID."""
        result = await self.session.execute(
            select(Performer).where(Performer.id == performer_id)
        )
        return result.scalar_one_or_none()

    async def get_performer_by_handle(self, handle: str) -> Performer | None:
        """Get performer by handle."""
        result = await self.session.execute(
            select(Performer).where(Performer.handle == handle)
        )
        return result.scalar_one_or_none()

    async def get_agency_performers(
        self,
        agency_id: int,
        active_only: bool = True,
    ) -> list[PerformerResponse]:
        """Get performers for an agency."""
        query = select(Performer).where(Performer.agency_id == agency_id)
        if active_only:
            query = query.where(Performer.is_active == True)

        result = await self.session.execute(query)
        performers = result.scalars().all()

        return [PerformerResponse.model_validate(p) for p in performers]

    async def create_performer(
        self,
        agency_id: int,
        data: PerformerCreate,
    ) -> PerformerResponse:
        """Create performer for agency."""
        # Check handle uniqueness
        existing = await self.get_performer_by_handle(data.handle)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Performer handle already exists",
            )

        # Validate shares
        total = data.share_performer + data.share_agency + data.share_treasury
        if total != 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Revenue shares must sum to 100, got {total}",
            )

        performer = Performer(
            agency_id=agency_id,
            user_id=data.user_id,
            display_name=data.display_name,
            handle=data.handle,
            bio=data.bio,
            avatar_url=data.avatar_url,
            type=data.type,
            is_test=data.is_test,
            share_performer=data.share_performer,
            share_agency=data.share_agency,
            share_treasury=data.share_treasury,
            ai_profile_id=data.ai_profile_id,
            tags=data.tags,
        )
        self.session.add(performer)
        await self.session.flush()
        await self.session.refresh(performer)

        logger.info(
            "performer_created",
            performer_id=performer.id,
            agency_id=agency_id,
            handle=data.handle,
            type=data.type.value,
        )

        return PerformerResponse.model_validate(performer)

    async def update_performer(
        self,
        performer: Performer,
        data: PerformerUpdate,
    ) -> PerformerResponse:
        """Update performer."""
        update_dict = data.model_dump(exclude_unset=True)

        # Validate shares if being updated
        if any(k in update_dict for k in ["share_performer", "share_agency", "share_treasury"]):
            performer_share = update_dict.get("share_performer", performer.share_performer)
            agency_share = update_dict.get("share_agency", performer.share_agency)
            treasury_share = update_dict.get("share_treasury", performer.share_treasury)

            total = performer_share + agency_share + treasury_share
            if total != 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Revenue shares must sum to 100, got {total}",
                )

        for field, value in update_dict.items():
            setattr(performer, field, value)

        performer.updated_at = datetime.utcnow()
        self.session.add(performer)
        await self.session.flush()
        await self.session.refresh(performer)

        logger.info("performer_updated", performer_id=performer.id)

        return PerformerResponse.model_validate(performer)

    # ============ Revenue Split ============
    async def calculate_revenue_split(
        self,
        performer_id: int,
        amount: Decimal,
    ) -> RevenueSplit:
        """Calculate revenue split for a performer."""
        performer = await self.get_performer(performer_id)
        if not performer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Performer not found",
            )

        performer_amount = amount * Decimal(performer.share_performer) / Decimal(100)
        agency_amount = amount * Decimal(performer.share_agency) / Decimal(100)
        treasury_amount = amount * Decimal(performer.share_treasury) / Decimal(100)

        return RevenueSplit(
            total_amount=amount,
            performer_amount=performer_amount,
            agency_amount=agency_amount,
            treasury_amount=treasury_amount,
            performer_id=performer_id,
            agency_id=performer.agency_id,
        )

    async def record_performer_earnings(
        self,
        performer_id: int,
        amount: int,
    ) -> None:
        """Record earnings for performer (updates stats)."""
        performer = await self.get_performer(performer_id)
        if performer:
            performer.total_earnings += amount
            performer.total_shows += 1
            performer.updated_at = datetime.utcnow()
            self.session.add(performer)
            await self.session.flush()

