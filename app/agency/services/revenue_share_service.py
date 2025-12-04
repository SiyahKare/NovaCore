"""
Revenue Share Service - Creator Pay-Out
Viral Ajans gelir paylaşımı mekanizması
"""
from decimal import Decimal
from typing import Dict, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.agency.models import CreatorAsset, CreatorAssetStatus
from app.wallet.service import WalletService
from app.wallet.schemas import TransactionCreate
from app.wallet.models import LedgerEntryType
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("revenue_share")

# ----------------------------------------------------
# SABİT TANIMLAR
# ----------------------------------------------------
CREATOR_SHARE_RATE = Decimal("0.20")  # %20 pay Creator'a
TREASURY_SHARE_RATE = Decimal("0.40")  # %40 Treasury'ye (Rezerv)
AGENCY_OPERATIONS_RATE = Decimal("0.40")  # %40 Ajansın Operasyon/Kâr Payı

# NCR fiyatı (TRY cinsinden) - NCRMarketState'den alınabilir, şimdilik sabit
DEFAULT_NCR_PRICE_TRY = Decimal("1.0")  # 1 NCR = 1 TRY (örnek)


class RevenueShareService:
    """Revenue share dağıtım servisi."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.wallet_service = WalletService(session)

    async def get_asset(self, asset_id: int) -> Optional[CreatorAsset]:
        """Asset'i getir."""
        result = await self.session.execute(
            select(CreatorAsset).where(CreatorAsset.id == asset_id)
        )
        return result.scalar_one_or_none()

    async def get_ncr_price_try(self) -> Decimal:
        """Mevcut NCR fiyatını getir (TRY cinsinden)."""
        from app.wallet.models import NCRMarketState
        result = await self.session.execute(
            select(NCRMarketState).order_by(NCRMarketState.id.desc()).limit(1)
        )
        market_state = result.scalar_one_or_none()
        
        if market_state and market_state.current_price_try > 0:
            return Decimal(str(market_state.current_price_try))
        
        return DEFAULT_NCR_PRICE_TRY

    async def distribute_campaign_revenue(
        self,
        asset_id: int,
        total_fiat_revenue: Decimal,
        fiat_currency: str = "TRY",
    ) -> Dict[str, Decimal]:
        """
        Bir CreatorAsset'in kampanyada kullanılması sonucu elde edilen
        toplam fiat geliri dağıtır.

        Args:
            asset_id: CreatorAsset ID
            total_fiat_revenue: Toplam fiat geliri (TRY)
            fiat_currency: Para birimi (varsayılan: TRY)

        Returns:
            Dağıtım sonuçları dict'i
        """
        # 1. Asset kontrolü
        asset = await self.get_asset(asset_id)
        if not asset:
            raise ValueError("Asset bulunamadı.")
        
        if asset.status != CreatorAssetStatus.APPROVED:
            raise ValueError(f"Asset onaylı değil. Mevcut durum: {asset.status}")

        # 2. Pay Hesaplama
        creator_fiat_share = total_fiat_revenue * CREATOR_SHARE_RATE
        treasury_fiat_share = total_fiat_revenue * TREASURY_SHARE_RATE
        agency_operations_share = total_fiat_revenue * AGENCY_OPERATIONS_RATE

        # 3. NCR fiyatını al
        ncr_price_try = await self.get_ncr_price_try()

        # 4. Creator Ödemesi (Fiat -> NCR Dönüşümü)
        # NCR ödemesi, fiat karşılığı üzerinden yapılır.
        creator_ncr_amount = creator_fiat_share / ncr_price_try

        # 5. NCR Cüzdanına Aktarım (Wallet Service)
        wallet_tx = await self.wallet_service.create_transaction(
            TransactionCreate(
                user_id=asset.user_id,
                amount=creator_ncr_amount,
                token="NCR",
                type=LedgerEntryType.EARN,
                source_app="agency_revenue_share",
                reference_id=str(asset_id),
                reference_type="creator_asset_revenue",
                metadata={
                    "asset_id": asset_id,
                    "asset_title": getattr(asset, "caption", "")[:100] if asset.caption else f"Asset #{asset_id}",
                    "total_fiat_revenue": str(total_fiat_revenue),
                    "creator_fiat_share": str(creator_fiat_share),
                    "creator_ncr_amount": str(creator_ncr_amount),
                    "ncr_price_try": str(ncr_price_try),
                    "fiat_currency": fiat_currency,
                },
            )
        )

        # 6. Treasury Kaydı (Fiat olarak - log için)
        # Treasury'ye fiat olarak gelen payın kaydını at
        # Şimdilik basit bir log mekanizması (ileride TreasuryService'e bağlanabilir)
        total_treasury_fiat = treasury_fiat_share + agency_operations_share
        
        # Treasury için NCR olarak da kayıt yapabiliriz (opsiyonel)
        # Şimdilik sadece metadata'da tutuyoruz
        
        logger.info(
            "revenue_share_distributed",
            asset_id=asset_id,
            user_id=asset.user_id,
            total_fiat_revenue=str(total_fiat_revenue),
            creator_ncr_amount=str(creator_ncr_amount),
            treasury_fiat=str(total_treasury_fiat),
            agency_operations_fiat=str(agency_operations_share),
        )

        # 7. Asset Durum Güncelleme
        asset.used_in_campaign = True
        asset.status = CreatorAssetStatus.USED_IN_CAMPAIGN
        asset.updated_at = datetime.utcnow()
        self.session.add(asset)
        await self.session.commit()
        await self.session.refresh(asset)

        return {
            "creator_ncr": creator_ncr_amount,
            "creator_fiat": creator_fiat_share,
            "treasury_fiat": treasury_fiat_share,
            "agency_operations_fiat": agency_operations_share,
            "total_fiat_processed": total_fiat_revenue,
            "ncr_price_try": ncr_price_try,
        }

