# app/marketplace/seed.py
"""
Marketplace Seed Script - Demo Data

"Barış HATEMOĞLU girse ne görür?" için vitrin doldurma.
"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.marketplace.models import MarketplaceItem, MarketplaceItemStatus
from app.marketplace.catalog import MarketplaceItemType
from app.core.db import get_session
from app.core.logging import get_logger

logger = get_logger("marketplace_seed")


# Demo creators (fake user_id'ler)
DEMO_CREATORS = {
    "burak": 1001,
    "betul": 1002,
    "random_genc": 1003,
}

# Seed items - gerçekçi Türkçe içerikler
SEED_ITEMS = [
    # Burak'ın ürünleri
    {
        "creator_id": DEMO_CREATORS["burak"],
        "title": "Viral Hook: 'Bu ülkede en büyük yalan ne biliyor musun?'",
        "description": "TikTok/Instagram Reels için çarpıcı giriş cümlesi. Merak uyandırıcı, viral potansiyelli.",
        "item_type": MarketplaceItemType.VIRAL_HOOK.value,
        "price_ncr": 2.5,
        "ai_score": 85.0,
        "preview_text": "Bu ülkede en büyük yalan ne biliyor musun?",
        "tags": "hook,viral,content,reels,tiktok",
    },
    {
        "creator_id": DEMO_CREATORS["burak"],
        "title": "Caption Pack: Premium Motivasyon (5'li)",
        "description": "Instagram/TikTok için hazır yazı paketi. Premium motivasyon tarzı, estetik dil.",
        "item_type": MarketplaceItemType.CAPTION_PACK.value,
        "price_ncr": 4.2,
        "ai_score": 78.0,
        "preview_text": "1. Başarı bir yolculuktur, varış değil. 2. Her gün küçük bir adım at...",
        "tags": "caption,instagram,tiktok,content,motivation",
    },
    {
        "creator_id": DEMO_CREATORS["burak"],
        "title": "Hashtag Set: Fitness & Wellness (20 adet)",
        "description": "Fitness ve wellness niche'i için optimize edilmiş hashtag seti. Keşfet algoritması için.",
        "item_type": MarketplaceItemType.HASHTAG_SET.value,
        "price_ncr": 3.0,
        "ai_score": 82.0,
        "preview_text": "#fitness #wellness #health #motivation #workout #fitlife...",
        "tags": "hashtag,instagram,tiktok,social,fitness",
    },
    
    # Betül'ün ürünleri
    {
        "creator_id": DEMO_CREATORS["betul"],
        "title": "TikTok Trend Report: Bugünün 5 Sound'u",
        "description": "Bugün trend olan 5 sound + 5 konsept. Ajanslar için hazır paket.",
        "item_type": MarketplaceItemType.TIKTOK_TREND_REPORT.value,
        "price_ncr": 9.5,
        "ai_score": 91.0,
        "preview_text": "1. Sound: 'Sigma mindset' - Konsept: Motivasyon videosu...",
        "tags": "trend,tiktok,research,report,agency",
    },
    {
        "creator_id": DEMO_CREATORS["betul"],
        "title": "Local Niche Pack: İzmit'te 5 Viral Çekim Noktası",
        "description": "İzmit'te viral çekim yapılabilecek 5 lokasyon. Türkiye'de deli satar.",
        "item_type": MarketplaceItemType.LOCAL_NICHE_PACK.value,
        "price_ncr": 11.0,
        "ai_score": 88.0,
        "preview_text": "1. İzmit Saat Kulesi - Klasik ama etkili, gün batımında...",
        "tags": "local,niche,city,türkiye,izmit",
    },
    {
        "creator_id": DEMO_CREATORS["betul"],
        "title": "SEO Video Description: YouTube Optimizasyonu",
        "description": "Creator YouTube videoları için optimize edilmiş açıklama template'i.",
        "item_type": MarketplaceItemType.SEO_VIDEO_DESCRIPTION.value,
        "price_ncr": 6.5,
        "ai_score": 79.0,
        "preview_text": "Bu videoda... [Anahtar kelimeler]... Abone olmayı unutma!",
        "tags": "seo,youtube,video,description",
    },
    
    # Random Genç'in ürünleri
    {
        "creator_id": DEMO_CREATORS["random_genc"],
        "title": "Viral Hook: 'Seni en çok ezen anını 3 cümlede anlat'",
        "description": "Duygusal bağ kurucu hook. Storytelling için mükemmel.",
        "item_type": MarketplaceItemType.VIRAL_HOOK.value,
        "price_ncr": 2.0,
        "ai_score": 75.0,
        "preview_text": "Seni en çok ezen anını 3 cümlede anlat.",
        "tags": "hook,viral,content,storytelling",
    },
    {
        "creator_id": DEMO_CREATORS["random_genc"],
        "title": "Hashtag Set: Beauty & Makeup (25 adet)",
        "description": "Beauty ve makeup niche'i için hashtag seti. Yüksek engagement potansiyeli.",
        "item_type": MarketplaceItemType.HASHTAG_SET.value,
        "price_ncr": 3.5,
        "ai_score": 84.0,
        "preview_text": "#beauty #makeup #makeuptutorial #beautyblogger #skincare...",
        "tags": "hashtag,instagram,beauty,makeup",
    },
    {
        "creator_id": DEMO_CREATORS["random_genc"],
        "title": "Short Script: 30 Saniyelik Motivasyon Videosu",
        "description": "3 sahne, aksiyon cümlesi, kapanış. Creator'lar direkt videoya okur.",
        "item_type": MarketplaceItemType.SHORT_SCRIPT.value,
        "price_ncr": 5.0,
        "ai_score": 80.0,
        "preview_text": "Sahne 1: [Aksiyon] Sahne 2: [Dönüşüm] Sahne 3: [Kapanış]",
        "tags": "script,video,content,creator,motivation",
    },
]


async def seed_marketplace(session: AsyncSession, clear_existing: bool = False):
    """
    Marketplace'e seed data ekle.
    
    Args:
        session: Database session
        clear_existing: Mevcut seed item'leri temizle (default: False)
    """
    if clear_existing:
        # Seed item'leri temizle (sadece demo creator'ların item'leri)
        from sqlmodel import select, delete
        stmt = select(MarketplaceItem).where(
            MarketplaceItem.creator_id.in_(list(DEMO_CREATORS.values()))
        )
        result = await session.execute(stmt)
        existing_items = result.scalars().all()
        
        for item in existing_items:
            await session.delete(item)
        
        await session.commit()
        logger.info("seed_items_cleared", count=len(existing_items))
    
    # Seed items oluştur
    created_items = []
    
    for item_data in SEED_ITEMS:
        # Aynı item zaten var mı kontrol et
        from sqlmodel import select
        stmt = select(MarketplaceItem).where(
            MarketplaceItem.creator_id == item_data["creator_id"],
            MarketplaceItem.title == item_data["title"],
        )
        result = await session.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            logger.info("seed_item_already_exists", title=item_data["title"])
            continue
        
        # Yeni item oluştur
        item = MarketplaceItem(
            creator_id=item_data["creator_id"],
            title=item_data["title"],
            description=item_data["description"],
            item_type=item_data["item_type"],
            price_ncr=item_data["price_ncr"],
            ai_score=item_data["ai_score"],
            preview_text=item_data["preview_text"],
            tags=item_data["tags"],
            status=MarketplaceItemStatus.ACTIVE,
            activated_at=datetime.utcnow(),
            revenue_share_creator=0.70,
            revenue_share_treasury=0.30,
        )
        
        session.add(item)
        created_items.append(item)
    
    await session.commit()
    
    # Refresh items
    for item in created_items:
        await session.refresh(item)
    
    logger.info(
        "marketplace_seeded",
        items_created=len(created_items),
        total_seed_items=len(SEED_ITEMS),
    )
    
    return created_items


async def main():
    """Seed script main function."""
    from app.core.db import async_session_factory
    
    async with async_session_factory() as session:
        try:
            items = await seed_marketplace(session, clear_existing=False)
            print(f"✅ Marketplace seeded: {len(items)} items oluşturuldu")
            print("\n📦 Oluşturulan item'ler:")
            for item in items:
                print(f"  - {item.title} ({item.item_type}) - {item.price_ncr} NCR")
        except Exception as e:
            logger.error("seed_failed", error=str(e))
            print(f"❌ Seed failed: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

