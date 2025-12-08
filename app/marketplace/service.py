# app/marketplace/service.py
"""
Marketplace Service - Business Logic

Vatandaş → Üretir → Marketplace'e düşer → KOBİ satın alır
"""
from typing import List, Optional
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.marketplace.models import (
    MarketplaceItem,
    MarketplacePurchase,
    MarketplaceItemStatus,
)
from app.wallet.service import WalletService
from app.wallet.schemas import TransactionCreate
from app.wallet.models import LedgerEntryType
from app.core.config import settings
from app.core.logging import get_logger
from datetime import datetime

logger = get_logger("marketplace")


class MarketplaceService:
    """Marketplace business logic."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.wallet_service = WalletService(session)
    
    async def list_items(
        self,
        item_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        status: Optional[str] = None,
    ) -> List[MarketplaceItem]:
        """
        Marketplace item'lerini listele.
        
        Args:
            item_type: Filtreleme için item tipi
            limit: Sayfa boyutu
            offset: Sayfa offset'i
            status: Durum filtresi (default: ACTIVE)
        """
        query = select(MarketplaceItem)
        
        # Status filtresi (default: ACTIVE)
        if status:
            query = query.where(MarketplaceItem.status == status)
        else:
            query = query.where(MarketplaceItem.status == MarketplaceItemStatus.ACTIVE)
        
        # Item type filtresi
        if item_type:
            query = query.where(MarketplaceItem.item_type == item_type)
        
        # Sıralama ve sayfalama
        query = query.order_by(MarketplaceItem.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_item(
        self,
        item_id: int,
    ) -> MarketplaceItem:
        """
        Tek bir marketplace item getir.
        
        Args:
            item_id: Item ID
        
        Returns:
            MarketplaceItem
        
        Raises:
            ValueError: Item bulunamadı veya aktif değil
        """
        item = await self.session.get(MarketplaceItem, item_id)
        
        if not item:
            raise ValueError("Marketplace item not found")
        
        if item.status != MarketplaceItemStatus.ACTIVE:
            raise ValueError("Bu ürün şu an satışta değil.")
        
        return item
    
    async def create_from_quest(
        self,
        *,
        creator_id: int,
        source_quest_id: int,
        title: str,
        description: str,
        item_type: str,
        price_ncr: float,
        ai_score: float,
        tags: Optional[List[str]] = None,
        preview_text: Optional[str] = None,
        content: Optional[str] = None,
    ) -> MarketplaceItem:
        """
        Quest completion sonrası Marketplace Bridge burayı çağırır.
        
        Args:
            creator_id: İçerik üreticisi user_id
            source_quest_id: UserQuest.id
            title: Item başlığı
            description: Item açıklaması
            item_type: Item tipi (hook, caption_pack, vb.)
            price_ncr: Satış fiyatı
            ai_score: AI kalite skoru
            tags: Tag listesi
            preview_text: Önizleme metni
        
        Returns:
            Oluşturulan MarketplaceItem
        """
        # Status belirleme: AI Score 70+ ise ACTIVE, değilse DRAFT
        status = (
            MarketplaceItemStatus.ACTIVE
            if ai_score >= 70.0
            else MarketplaceItemStatus.DRAFT
        )
        
        item = MarketplaceItem(
            creator_id=creator_id,
            source_quest_id=source_quest_id,
            title=title,
            description=description,
            item_type=item_type,
            price_ncr=price_ncr,
            ai_score=ai_score,
            status=status,
            tags=",".join(tags) if tags else None,
            preview_text=preview_text or description[:200],  # İlk 200 karakter
            content=content,  # QuestProof'tan gelen içerik
            activated_at=datetime.utcnow() if status == MarketplaceItemStatus.ACTIVE else None,
        )
        
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        
        logger.info(
            "marketplace_item_created",
            item_id=item.id,
            creator_id=creator_id,
            item_type=item_type,
            ai_score=ai_score,
            status=status,
        )
        
        return item
    
    async def purchase_item(
        self,
        *,
        buyer_id: int,
        item_id: int,
    ) -> MarketplacePurchase:
        """
        Satın alma akışı:
        
        1. Item'i bul ve kontrol et
        2. Duplicate purchase kontrolü
        3. Buyer'ın NCR bakiyesini kontrol et
        4. NCR transfer (buyer → creator & treasury)
        5. Purchase kaydı oluştur
        6. Item istatistiklerini güncelle
        
        Args:
            buyer_id: Satın alan kullanıcı ID
            item_id: Satın alınacak item ID
        
        Returns:
            MarketplacePurchase kaydı
        
        Raises:
            ValueError: Item bulunamadı, aktif değil, yetersiz bakiye veya duplicate purchase
        """
        from datetime import datetime
        from sqlmodel import select
        
        # Item'i getir
        item = await self.get_item(item_id)
        
        # Duplicate purchase kontrolü
        duplicate_stmt = select(MarketplacePurchase).where(
            MarketplacePurchase.buyer_id == buyer_id,
            MarketplacePurchase.item_id == item_id,
        )
        duplicate_result = await self.session.execute(duplicate_stmt)
        existing_purchase = duplicate_result.scalar_one_or_none()
        
        if existing_purchase:
            # Duplicate purchase: Exception fırlat
            logger.info(
                "duplicate_purchase_prevented",
                buyer_id=buyer_id,
                item_id=item_id,
                existing_purchase_id=existing_purchase.id,
            )
            raise ValueError(
                f"Bu ürünü zaten daha önce satın aldınız. Purchase ID: {existing_purchase.id}"
            )
        
        # Bakiye kontrolü
        buyer_balance = await self.wallet_service.get_balance(buyer_id, "NCR")
        if buyer_balance.balance < Decimal(str(item.price_ncr)):
            raise ValueError(
                f"Yetersiz bakiye. Mevcut: {buyer_balance.balance} NCR, "
                f"Gerekli: {item.price_ncr} NCR"
            )
        
        # Pay hesaplama
        price = Decimal(str(item.price_ncr))
        creator_cut = round(price * Decimal(str(item.revenue_share_creator)), 4)
        treasury_cut = price - creator_cut
        
        # NCR transferleri
        
        # 1. Buyer'dan çıkar
        await self.wallet_service.create_transaction(
            TransactionCreate(
                user_id=buyer_id,
                amount=price,
                token="NCR",
                type=LedgerEntryType.SPEND,
                source_app="marketplace",
                reference_id=str(item_id),
                reference_type="marketplace_purchase",
                metadata={
                    "item_id": item_id,
                    "item_type": item.item_type,
                    "direction": "out",
                },
            )
        )
        
        # 2. Creator'a ver
        await self.wallet_service.create_transaction(
            TransactionCreate(
                user_id=item.creator_id,
                amount=creator_cut,
                token="NCR",
                type=LedgerEntryType.EARN,
                source_app="marketplace",
                reference_id=str(item_id),
                reference_type="marketplace_sale",
                related_user_id=buyer_id,
                metadata={
                    "item_id": item_id,
                    "item_type": item.item_type,
                    "revenue_share": "creator",
                    "direction": "in",
                },
            )
        )
        
        # 3. Treasury'ye ver
        await self.wallet_service.create_transaction(
            TransactionCreate(
                user_id=settings.NCR_TREASURY_USER_ID,
                amount=treasury_cut,
                token="NCR",
                type=LedgerEntryType.EARN,
                source_app="marketplace",
                reference_id=str(item_id),
                reference_type="marketplace_treasury",
                related_user_id=buyer_id,
                metadata={
                    "item_id": item_id,
                    "item_type": item.item_type,
                    "revenue_share": "treasury",
                    "direction": "in",
                },
            )
        )
        
        # Purchase kaydı oluştur
        purchase = MarketplacePurchase(
            item_id=item.id,
            buyer_id=buyer_id,
            creator_id=item.creator_id,
            price_ncr=float(price),
            creator_share_ncr=float(creator_cut),
            treasury_share_ncr=float(treasury_cut),
        )
        
        self.session.add(purchase)
        
        # Item istatistiklerini güncelle
        item.purchase_count += 1
        item.total_revenue_ncr += float(price)
        
        await self.session.commit()
        await self.session.refresh(purchase)
        
        logger.info(
            "marketplace_purchase_completed",
            purchase_id=purchase.id,
            buyer_id=buyer_id,
            creator_id=item.creator_id,
            item_id=item_id,
            price_ncr=float(price),
            creator_share=float(creator_cut),
            treasury_share=float(treasury_cut),
        )
        
        return purchase
    
    async def get_creator_items(
        self,
        creator_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> List[MarketplaceItem]:
        """Creator'ın item'lerini getir."""
        query = (
            select(MarketplaceItem)
            .where(MarketplaceItem.creator_id == creator_id)
            .order_by(MarketplaceItem.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_creator_sales(
        self,
        creator_id: int,
    ) -> dict:
        """Creator'ın satış istatistiklerini getir."""
        query = select(MarketplacePurchase).where(
            MarketplacePurchase.creator_id == creator_id
        )
        
        result = await self.session.execute(query)
        purchases = list(result.scalars().all())
        
        total_sales = len(purchases)
        total_revenue = sum(p.creator_share_ncr for p in purchases)
        
        return {
            "creator_id": creator_id,
            "total_sales": total_sales,
            "total_revenue_ncr": total_revenue,
            "purchases": purchases[:10],  # Son 10 satış
        }

