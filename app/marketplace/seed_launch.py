"""
Marketplace Seed Script - Launch Pack V1
İlk hafta için minimum vitrin: 20-30 ACTIVE item
"""
import asyncio
from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.marketplace.models import MarketplaceItem, MarketplaceItemStatus
from app.marketplace.catalog import MarketplaceItemType
from app.marketplace.service import MarketplaceService
from app.core.logging import get_logger

logger = get_logger("marketplace_seed")


# Demo creator user IDs (gerçek kullanıcılar yerine seed için)
DEMO_CREATOR_IDS = [1, 2, 3]  # İlk 3 user ID'yi demo creator olarak kullan


# Seed item tanımları
SEED_ITEMS = [
    # Viral Hook Pack (10 adet)
    {
        "title": "Viral Hook Pack #1",
        "description": "TikTok/Instagram Reels için çarpıcı giriş cümleleri",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 2.0,
        "ai_score": 78.0,
        "content": '["Bu ülkede en büyük yalan ne biliyor musun?", "Seni 10 yaş genç gösterecek şey", "Müşterilerim bana neden bu kadar güveniyor?", "3 dakikada saç rengini değiştiren teknik", "Yıllarca yanlış yaptığımız şey"]',
        "tags": "hook,viral,content,reels,tiktok",
    },
    {
        "title": "Viral Hook Pack #2",
        "description": "Motivasyon temalı viral hook'lar",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 1.8,
        "ai_score": 75.0,
        "content": '["Rızık seni bulur, sen rızkı arama", "Gerçek para, gerçek işten gelir", "Nasip varsa, yol açılır", "Eski sistem seni sömürür, yeni sistem seni kurtarır"]',
        "tags": "hook,viral,motivation,reels",
    },
    {
        "title": "Viral Hook Pack #3",
        "description": "İş/Kariyer temalı hook'lar",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 2.2,
        "ai_score": 82.0,
        "content": '["İşsiz kaldım, ev kirası ödeyemedim", "Patron bana 5 bin verdi, kendine 50 bin aldı", "Gerçek iş yapmak istiyorum, nereden başlamalıyım?"]',
        "tags": "hook,viral,career,business",
    },
    {
        "title": "Viral Hook Pack #4",
        "description": "Kişisel gelişim hook'ları",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 1.9,
        "ai_score": 76.0,
        "content": '["Bugün 1 skill için yaptığın en küçük hareket neydi?", "Kendini geliştirmek istiyorsun ama nereden başlamalı?", "Öğrenmek istiyorum ama zaman yok"]',
        "tags": "hook,viral,self-improvement,learning",
    },
    {
        "title": "Viral Hook Pack #5",
        "description": "İlişki/Sosyal temalı hook'lar",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 2.1,
        "ai_score": 79.0,
        "content": '["En güvendiğin 1 kişinin adını yaz", "Gerçek dostluk nedir?", "İnsanlar seni neden sevsin?"]',
        "tags": "hook,viral,relationship,social",
    },
    {
        "title": "Viral Hook Pack #6",
        "description": "Para/Finans temalı hook'lar",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 2.3,
        "ai_score": 84.0,
        "content": '["Bugün 200 TL yol + kahve yaktım, 0 TL kazandım", "Para kazanmak istiyorum ama nasıl?", "Gerçek para nereden gelir?"]',
        "tags": "hook,viral,money,finance",
    },
    {
        "title": "Viral Hook Pack #7",
        "description": "Günlük hayat hook'ları",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 1.7,
        "ai_score": 73.0,
        "content": '["Bugün cebine giren/çıkan parayı tek cümle yaz", "Günlük rutinini değiştirmek istiyorsun", "Hayatını değiştirmek için ne yapmalısın?"]',
        "tags": "hook,viral,daily-life,routine",
    },
    {
        "title": "Viral Hook Pack #8",
        "description": "Başarı/Hedef temalı hook'lar",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 2.4,
        "ai_score": 86.0,
        "content": '["Bu oyundan ne beklediğini 2 cümleyle yaz", "Hedeflerin neler?", "Başarı nedir senin için?"]',
        "tags": "hook,viral,success,goals",
    },
    {
        "title": "Viral Hook Pack #9",
        "description": "Zorluk/Mücadele temalı hook'lar",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 2.0,
        "ai_score": 77.0,
        "content": '["Seni ezen en ağır anı 3-5 cümle yaz", "Zorluklar seni nasıl şekillendirdi?", "En zor anında ne yaptın?"]',
        "tags": "hook,viral,struggle,challenge",
    },
    {
        "title": "Viral Hook Pack #10",
        "description": "Gelecek/Vizyon temalı hook'lar",
        "item_type": MarketplaceItemType.VIRAL_HOOK,
        "price_ncr": 2.5,
        "ai_score": 88.0,
        "content": '["5 yıl sonra nerede olmak istiyorsun?", "Hayalin nedir?", "Geleceğe dair planların neler?"]',
        "tags": "hook,viral,future,vision",
    },
    
    # Caption Pack (5 adet)
    {
        "title": "Caption Pack - Motivasyon",
        "description": "Instagram/TikTok için motivasyon caption'ları",
        "item_type": MarketplaceItemType.CAPTION_PACK,
        "price_ncr": 3.5,
        "ai_score": 80.0,
        "content": '["Rızık seni bulur, sen rızkı arama. Gerçek para, gerçek işten gelir.", "Nasip varsa, yol açılır. Eski sistem seni sömürür, yeni sistem seni kurtarır.", "Dürüst ol, gerçek ol. Gerçek iş yap, gerçek para kazan.", "Kendini geliştir, kendini kurtar. Başkasına bağımlı olma.", "Hedeflerin olsun, planların olsun. Ama gerçekçi olsun."]',
        "tags": "caption,motivation,instagram,tiktok",
    },
    {
        "title": "Caption Pack - İş/Kariyer",
        "description": "İş ve kariyer temalı caption'lar",
        "item_type": MarketplaceItemType.CAPTION_PACK,
        "price_ncr": 4.0,
        "ai_score": 83.0,
        "content": '["Gerçek iş yapmak istiyorum, nereden başlamalıyım? İşsiz kaldım, ev kirası ödeyemedim.", "Patron bana 5 bin verdi, kendine 50 bin aldı. Bu sistem adil değil.", "Kendi işimi kurmak istiyorum ama sermaye yok. Ne yapmalıyım?", "Yeni bir şey öğrenmek istiyorum ama zaman yok. Nasıl başlamalıyım?", "Para kazanmak istiyorum ama nasıl? Gerçek para nereden gelir?"]',
        "tags": "caption,career,business,work",
    },
    {
        "title": "Caption Pack - Kişisel Gelişim",
        "description": "Kişisel gelişim temalı caption'lar",
        "item_type": MarketplaceItemType.CAPTION_PACK,
        "price_ncr": 3.8,
        "ai_score": 81.0,
        "content": '["Bugün 1 skill için yaptığın en küçük hareket neydi? Küçük adımlar büyük değişiklikler yaratır.", "Kendini geliştirmek istiyorsun ama nereden başlamalı? İlk adımı at.", "Öğrenmek istiyorum ama zaman yok. 5 dakika ayır, başla.", "Hedeflerin neler? Planların var mı? Gerçekçi ol.", "Başarı nedir senin için? Para mı, mutluluk mu, özgürlük mü?"]',
        "tags": "caption,self-improvement,learning,growth",
    },
    {
        "title": "Caption Pack - Dürüstlük/Şeffaflık",
        "description": "Dürüstlük ve şeffaflık temalı caption'lar",
        "item_type": MarketplaceItemType.CAPTION_PACK,
        "price_ncr": 3.6,
        "ai_score": 79.0,
        "content": '["Dürüst ol, gerçek ol. Yalan söyleme, kendini kandırma.", "En güvendiğin 1 kişinin adını yaz. Gerçek dostluk nedir?", "Seni ezen en ağır anı 3-5 cümle yaz. Zorluklar seni nasıl şekillendirdi?", "Bu oyundan ne beklediğini 2 cümleyle yaz. Gerçekçi ol.", "Bugün başkasına yaptığın küçük iyiliği yaz. İyilik yap, iyilik bul."]',
        "tags": "caption,honesty,transparency,integrity",
    },
    {
        "title": "Caption Pack - Günlük Hayat",
        "description": "Günlük hayat temalı caption'lar",
        "item_type": MarketplaceItemType.CAPTION_PACK,
        "price_ncr": 3.4,
        "ai_score": 77.0,
        "content": '["Bugün cebine giren/çıkan parayı tek cümle yaz. Para nereye gidiyor?", "Günlük rutinini değiştirmek istiyorsun. İlk adımı at.", "Hayatını değiştirmek için ne yapmalısın? Küçük değişikliklerle başla.", "5 yıl sonra nerede olmak istiyorsun? Planların var mı?", "Hayalin nedir? Gerçekleştirmek için ne yapıyorsun?"]',
        "tags": "caption,daily-life,routine,change",
    },
    
    # Hashtag Set (3 adet)
    {
        "title": "Hashtag Set - Motivasyon",
        "description": "Motivasyon temalı hashtag seti",
        "item_type": MarketplaceItemType.HASHTAG_SET,
        "price_ncr": 2.5,
        "ai_score": 75.0,
        "content": '["#motivasyon", "#başarı", "#hedef", "#plan", "#gerçek", "#rızık", "#nasip", "#iş", "#para", "#kariyer", "#gelişim", "#öğrenme", "#değişim", "#ilerleme", "#başarıhikayesi"]',
        "tags": "hashtag,motivation,success",
    },
    {
        "title": "Hashtag Set - İş/Kariyer",
        "description": "İş ve kariyer temalı hashtag seti",
        "item_type": MarketplaceItemType.HASHTAG_SET,
        "price_ncr": 2.8,
        "ai_score": 78.0,
        "content": '["#iş", "#kariyer", "#işsizlik", "#patron", "#çalışan", "#maaş", "#sermaye", "#girişimcilik", "#işkur", "#cv", "#mülakat", "#işbulma", "#para", "#finans", "#ekonomi"]',
        "tags": "hashtag,career,business,work",
    },
    {
        "title": "Hashtag Set - Kişisel Gelişim",
        "description": "Kişisel gelişim temalı hashtag seti",
        "item_type": MarketplaceItemType.HASHTAG_SET,
        "price_ncr": 2.6,
        "ai_score": 76.0,
        "content": '["#gelişim", "#öğrenme", "#skill", "#yetenek", "#eğitim", "#kurs", "#kitap", "#okuma", "#yazma", "#kodlama", "#tasarım", "#sanat", "#müzik", "#spor", "#sağlık"]',
        "tags": "hashtag,self-improvement,learning",
    },
    
    # Short Script (2 adet)
    {
        "title": "Short Script - Motivasyon",
        "description": "30-45 saniyelik motivasyon script'i",
        "item_type": MarketplaceItemType.SHORT_SCRIPT,
        "price_ncr": 5.0,
        "ai_score": 82.0,
        "content": '{"scripts": ["Sahne 1: Eski sistem seni sömürüyor. Patron bana 5 bin verdi, kendine 50 bin aldı. Bu adil değil. Sahne 2: Yeni sistem seni kurtarıyor. Sen üret, sen kazan. Gerçek iş yap, gerçek para kazan. Sahne 3: Başla. Küçük adımlarla başla. Rızık seni bulur, sen rızkı arama."]}',
        "tags": "script,video,motivation,reels",
    },
    {
        "title": "Short Script - İş/Kariyer",
        "description": "30-45 saniyelik iş/kariyer script'i",
        "item_type": MarketplaceItemType.SHORT_SCRIPT,
        "price_ncr": 5.5,
        "ai_score": 85.0,
        "content": '{"scripts": ["Sahne 1: İşsiz kaldım, ev kirası ödeyemedim. Para yok, umut yok. Sahne 2: Yeni bir şey öğrenmeye başladım. Küçük adımlarla. Sahne 3: Şimdi kendi işimi yapıyorum. Gerçek para kazanıyorum. Sen de başlayabilirsin."]}',
        "tags": "script,video,career,business",
    },
    
    # TikTok Trend Report (2 adet)
    {
        "title": "TikTok Trend Report - Motivasyon",
        "description": "Günlük TikTok trend raporu (motivasyon temalı)",
        "item_type": MarketplaceItemType.TIKTOK_TREND_REPORT,
        "price_ncr": 9.0,
        "ai_score": 87.0,
        "content": '{"trends": [{"sound": "Motivasyon Sound #1", "concept": "Eski sistem vs yeni sistem", "example": "Patron bana 5 bin verdi, kendine 50 bin aldı"}, {"sound": "Motivasyon Sound #2", "concept": "Gerçek para nereden gelir", "example": "Gerçek iş yap, gerçek para kazan"}, {"sound": "Motivasyon Sound #3", "concept": "Küçük adımlarla başla", "example": "Bugün 1 skill için yaptığın en küçük hareket neydi?"}]}',
        "tags": "trend,tiktok,motivation,reels",
    },
    {
        "title": "Local Niche Pack - İstanbul",
        "description": "İstanbul için viral çekim noktaları",
        "item_type": MarketplaceItemType.LOCAL_NICHE_PACK,
        "price_ncr": 10.0,
        "ai_score": 89.0,
        "content": '["Galata Kulesi - En iyi çekim açısı: Karaköy tarafından", "Boğaz Köprüsü - Gün batımı saatlerinde çek", "Kadıköy Çarşı - Günlük hayat temalı içerik", "Beşiktaş Sahil - Spor/motivasyon içerikleri", "Taksim Meydanı - Şehir hayatı temalı içerik"]',
        "tags": "local,istanbul,location,niche",
    },
]


async def seed_marketplace_launch(session: AsyncSession) -> List[int]:
    """
    Launch Pack için marketplace seed.
    
    Returns:
        Oluşturulan item ID'leri
    """
    service = MarketplaceService(session)
    created_ids = []
    
    for idx, item_data in enumerate(SEED_ITEMS):
        creator_id = DEMO_CREATOR_IDS[idx % len(DEMO_CREATOR_IDS)]
        
        try:
            # Seed item için direkt MarketplaceItem oluştur
            item_type_str = item_data["item_type"].value if hasattr(item_data["item_type"], "value") else str(item_data["item_type"])
            tags_str = item_data["tags"] if isinstance(item_data["tags"], str) else ",".join(item_data["tags"])
            
            item = MarketplaceItem(
                creator_id=creator_id,
                source_quest_id=None,  # Seed item, quest'ten gelmiyor
                title=item_data["title"],
                description=item_data["description"],
                item_type=item_type_str,
                price_ncr=item_data["price_ncr"],
                ai_score=item_data["ai_score"],
                status=MarketplaceItemStatus.ACTIVE,
                tags=tags_str,
                preview_text=item_data["description"][:200],
                content=item_data["content"],
                revenue_share_creator=0.7,  # %70 creator
                revenue_share_treasury=0.3,  # %30 treasury
            )
            
            session.add(item)
            await session.commit()
            await session.refresh(item)
            
            created_ids.append(item.id)
            logger.info(
                "marketplace_seed_item_created",
                item_id=item.id,
                title=item_data["title"],
                item_type=item_data["item_type"],
                price_ncr=item_data["price_ncr"],
            )
        except Exception as e:
            logger.error(
                "marketplace_seed_item_failed",
                title=item_data["title"],
                error=str(e),
            )
            await session.rollback()  # Hata sonrası rollback
            continue
    
    logger.info(
        "marketplace_seed_completed",
        total_items=len(SEED_ITEMS),
        created_items=len(created_ids),
    )
    
    return created_ids


async def main():
    """Seed script main."""
    async for session in get_session():
        try:
            created_ids = await seed_marketplace_launch(session)
            print(f"✅ {len(created_ids)} marketplace item oluşturuldu.")
            print(f"Item ID'leri: {created_ids}")
        except Exception as e:
            logger.error("marketplace_seed_error", error=str(e))
            raise


if __name__ == "__main__":
    asyncio.run(main())

