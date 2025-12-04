# app/marketplace/models.py
"""
Marketplace Core - SQLModel İskeleti

Citizen Quest'ten geçen içeriklerin satılabilir versiyonu.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


class MarketplaceItemStatus(str):
    """Marketplace item durumu."""
    DRAFT = "draft"          # İçerik geldi ama onay bekliyor
    ACTIVE = "active"        # Satışta
    DISABLED = "disabled"    # Manuel kapatıldı
    ARCHIVED = "archived"    # Tarihsel


class MarketplaceItemType(str):
    """
    Marketplace item tipi (Legacy - kullanılmıyor).
    
    Yeni sistem: app.marketplace.catalog.MarketplaceItemType enum'ını kullan.
    """
    HOOK = "hook"
    CAPTION_PACK = "caption_pack"
    SCRIPT = "script"
    PROMPT = "prompt"
    RESEARCH_PACK = "research_pack"
    OTHER = "other"


class MarketplaceItem(SQLModel, table=True):
    """
    Citizen Quest'ten geçen içeriklerin satılabilir versiyonu.
    
    Vatandaş → Üretir → AI Score 70+ → Marketplace'e düşer → KOBİ satın alır
    """
    __tablename__ = "marketplace_items"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Kaynağı
    creator_id: int = Field(index=True, description="NovaCore user_id")
    source_quest_id: Optional[int] = Field(
        default=None,
        index=True,
        # foreign_key="user_quests.id",  # Opsiyonel - tablo yoksa hata verir
        description="UserQuest.id referansı"
    )
    
    # Katalog bilgisi
    title: str = Field(max_length=255)
    description: str
    item_type: str = Field(
        default=MarketplaceItemType.OTHER,
        index=True,
        description="hook, caption_pack, script, prompt, research_pack, other"
    )
    preview_text: Optional[str] = None
    preview_media_url: Optional[str] = None
    
    # Content (satın alma sonrası buyer'a gönderilecek)
    content: Optional[str] = Field(
        default=None,
        description="Satın alınan içerik (JSON stringified veya plain text)"
    )
    
    # Fiyatlandırma
    price_ncr: float = Field(gt=0, description="Satış fiyatı (NCR)")
    revenue_share_creator: float = Field(
        default=0.70,
        description="Creator payı (%70)"
    )
    revenue_share_treasury: float = Field(
        default=0.30,
        description="Treasury payı (%30)"
    )
    
    # Kalite / Onay
    ai_score: float = Field(default=0.0, ge=0.0, le=100.0, description="AI kalite skoru")
    manual_verified: bool = Field(default=False, description="Manuel onaylandı mı?")
    status: str = Field(
        default=MarketplaceItemStatus.DRAFT,
        index=True,
        description="draft, active, disabled, archived"
    )
    
    # Meta
    tags: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Virgülle ayrılmış tag listesi: 'beauty,hook,tiktok'"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    activated_at: Optional[datetime] = None
    
    # İstatistikler
    purchase_count: int = Field(default=0, description="Toplam satış sayısı")
    total_revenue_ncr: float = Field(default=0.0, description="Toplam gelir (NCR)")
    
    # İlişki (opsiyonel - seed script için gerekli değil)
    # purchases: list["MarketplacePurchase"] = Relationship(back_populates="item")


class MarketplacePurchase(SQLModel, table=True):
    """
    Bir kullanıcının bir MarketplaceItem satın alması.
    
    %70 Creator'a, %30 Treasury'ye dağıtılır.
    """
    __tablename__ = "marketplace_purchases"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    item_id: int = Field(foreign_key="marketplace_items.id", index=True)
    buyer_id: int = Field(index=True, description="Satın alan kullanıcı")
    creator_id: int = Field(index=True, description="İçerik üreticisi (cache)")
    price_ncr: float = Field(gt=0, description="Ödenen fiyat")
    
    # Dağılım
    creator_share_ncr: float = Field(description="Creator'a giden pay")
    treasury_share_ncr: float = Field(description="Treasury'ye giden pay")
    
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # İlişki (opsiyonel - seed script için gerekli değil)
    # item: MarketplaceItem = Relationship(back_populates="purchases")

