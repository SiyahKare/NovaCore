# app/marketplace/catalog.py
"""
SiyahKare Marketplace - Ürün Kataloğu V1

19 satılabilir dijital asset
KOBİ, içerik üreticisi, ajans, tekil creator hepsi satın alabilir
"""
from enum import Enum
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


class MarketplaceItemType(str, Enum):
    """
    19 Ürün Tipi - SiyahKare Marketplace V1
    
    En çok satacak ilk 5:
    1. Viral Hook
    2. Hashtag Set
    3. Caption Pack
    4. TikTok Trend Report
    5. Local Niche Pack
    """
    # A) HOOK & CONTENT PACKS (En Para Basan)
    VIRAL_HOOK = "viral_hook"                    # 1. Viral Hook (text) - 3-12 kelime
    SHORT_SCRIPT = "short_script"                 # 2. Short Script (30-45 saniye)
    CAPTION_PACK = "caption_pack"                 # 3. Caption Pack (5'li hazır yazı)
    STORY_PACK = "story_pack"                     # 4. Story Pack (Instagram 3 kare)
    SEO_VIDEO_DESCRIPTION = "seo_video_desc"     # 5. SEO Video Description
    KEYWORD_CLUSTER_PACK = "keyword_cluster"      # 6. Keyword Cluster Pack (30 anahtar kelime)
    HASHTAG_SET = "hashtag_set"                   # 7. Hashtag Set (15-25 tane)
    TIKTOK_TREND_REPORT = "tiktok_trend_report"   # 8. TikTok Trend Report (Günlük)
    
    # B) VISUAL / PROMPT VARLIKLARI
    PREMIUM_PROMPT_PACK = "premium_prompt_pack"   # 9. Premium Prompt Pack (4'lü)
    REELS_THUMBNAIL_PROMPT = "reels_thumbnail"    # 10. Reels Thumbnail Prompt
    STORYBOARD_MINI = "storyboard_mini"           # 11. Storyboard Mini (3 sahne)
    
    # C) RESEARCH-LEVEL ASSETS (En değerli - KOBİ'ler için)
    COMPETITOR_RESEARCH = "competitor_research"   # 12. Competitor Research (Mini)
    TREND_OPPORTUNITY_REPORT = "trend_opportunity" # 13. Trend Opportunity Report
    NANO_INDUSTRY_REPORT = "nano_industry_report" # 14. Nano-Industry Report
    LOCAL_NICHE_PACK = "local_niche_pack"         # 15. Local Niche Pack (Şehir bazlı)
    
    # D) MODERATION & TRUST (Ajansların en sevdiği)
    TOXIC_COMMENT_CLEANER = "toxic_comment_cleaner" # 16. Toxic Comment Cleaner Pack
    SPAM_DETECTION_REPORT = "spam_detection"      # 17. Spam Detection Report
    SHADOWBAN_RISK_CHECK = "shadowban_risk_check"  # 18. Shadowban Risk Check
    
    # E) COMMUNITY & RITUAL (Satılabilir Bonus)
    SOCIAL_VALUE_PACK = "social_value_pack"       # 19. Social Value Pack (5 adet söz)


@dataclass
class ProductDefinition:
    """Ürün tanımı ve fiyatlandırma politikası."""
    item_type: MarketplaceItemType
    name: str
    description: str
    price_range: Tuple[float, float]  # (min, max) NCR
    default_price: float  # Varsayılan fiyat
    quest_category: str  # PRODUCTION, RESEARCH, MODERATION, vb.
    quest_keywords: List[str]  # Quest key'inde bu kelimeler varsa bu ürün tipine map et
    ai_score_threshold: float = 70.0  # Marketplace'e gönderilmesi için minimum AI score
    tags: Optional[List[str]] = None  # Varsayılan tag'ler


# =============================================================================
# ÜRÜN KATALOĞU V1 - 19 Ürün
# =============================================================================

PRODUCT_CATALOG: Dict[MarketplaceItemType, ProductDefinition] = {
    # A) HOOK & CONTENT PACKS
    MarketplaceItemType.VIRAL_HOOK: ProductDefinition(
        item_type=MarketplaceItemType.VIRAL_HOOK,
        name="Viral Hook (Text)",
        description="3-12 kelimelik çarpıcı giriş cümlesi. TikTok/Instagram Reels için.",
        price_range=(1.5, 3.0),
        default_price=2.0,
        quest_category="PRODUCTION",
        quest_keywords=["hook", "viral", "giriş", "cümle", "reels"],
        tags=["hook", "viral", "content", "reels", "tiktok"],
    ),
    
    MarketplaceItemType.SHORT_SCRIPT: ProductDefinition(
        item_type=MarketplaceItemType.SHORT_SCRIPT,
        name="Short Script (30-45 saniye)",
        description="3 sahne, aksiyon cümlesi, kapanış cümlesi. Creator'lar direkt videoya okur.",
        price_range=(4.0, 6.0),
        default_price=5.0,
        quest_category="PRODUCTION",
        quest_keywords=["script", "video", "sahne", "kısa"],
        tags=["script", "video", "content", "creator"],
    ),
    
    MarketplaceItemType.CAPTION_PACK: ProductDefinition(
        item_type=MarketplaceItemType.CAPTION_PACK,
        name="Caption Pack (5'li)",
        description="Instagram/TikTok için hazır yazı paketi. Premium hüzün / premium motivasyon tarzı.",
        price_range=(3.0, 5.0),
        default_price=4.0,
        quest_category="PRODUCTION",
        quest_keywords=["caption", "yazı", "paket", "instagram"],
        tags=["caption", "instagram", "tiktok", "content"],
    ),
    
    MarketplaceItemType.STORY_PACK: ProductDefinition(
        item_type=MarketplaceItemType.STORY_PACK,
        name="Story Pack (Instagram 3 kare)",
        description="3 mini paragraf. Estetik dil. Instagram Stories için.",
        price_range=(5.0, 8.0),
        default_price=6.5,
        quest_category="PRODUCTION",
        quest_keywords=["story", "instagram", "kare", "paragraf"],
        tags=["story", "instagram", "content"],
    ),
    
    MarketplaceItemType.SEO_VIDEO_DESCRIPTION: ProductDefinition(
        item_type=MarketplaceItemType.SEO_VIDEO_DESCRIPTION,
        name="SEO Video Description",
        description="Creator YouTube videoları için optimize edilmiş açıklama.",
        price_range=(4.0, 8.0),
        default_price=6.0,
        quest_category="PRODUCTION",
        quest_keywords=["seo", "description", "youtube", "video", "açıklama"],
        tags=["seo", "youtube", "video", "description"],
    ),
    
    MarketplaceItemType.KEYWORD_CLUSTER_PACK: ProductDefinition(
        item_type=MarketplaceItemType.KEYWORD_CLUSTER_PACK,
        name="Keyword Cluster Pack",
        description="YouTube / TikTok keşfet için 30 anahtar kelime.",
        price_range=(6.0, 10.0),
        default_price=8.0,
        quest_category="RESEARCH",
        quest_keywords=["keyword", "cluster", "keşfet", "anahtar"],
        tags=["keyword", "seo", "research", "youtube", "tiktok"],
    ),
    
    MarketplaceItemType.HASHTAG_SET: ProductDefinition(
        item_type=MarketplaceItemType.HASHTAG_SET,
        name="Hashtag Set (Niche-specific)",
        description="15-25 tane hashtag. Çok hızlı satılır.",
        price_range=(2.0, 4.0),
        default_price=3.0,
        quest_category="PRODUCTION",
        quest_keywords=["hashtag", "tag", "etiket"],
        tags=["hashtag", "instagram", "tiktok", "social"],
    ),
    
    MarketplaceItemType.TIKTOK_TREND_REPORT: ProductDefinition(
        item_type=MarketplaceItemType.TIKTOK_TREND_REPORT,
        name="TikTok Trend Report (Günlük)",
        description="Bugün trend olan 5 sound + 5 konsept. Ajanslar bu ürüne bayılır.",
        price_range=(6.0, 12.0),
        default_price=9.0,
        quest_category="RESEARCH",
        quest_keywords=["trend", "tiktok", "report", "günlük", "sound"],
        tags=["trend", "tiktok", "research", "report"],
    ),
    
    # B) VISUAL / PROMPT VARLIKLARI
    MarketplaceItemType.PREMIUM_PROMPT_PACK: ProductDefinition(
        item_type=MarketplaceItemType.PREMIUM_PROMPT_PACK,
        name="Premium Prompt Pack (4'lü)",
        description="Foto/AI kapak görseli için. 'Fox goddess', 'Baron noir', 'Sigma vibe' gibi.",
        price_range=(6.0, 15.0),
        default_price=10.0,
        quest_category="PRODUCTION",
        quest_keywords=["prompt", "ai", "görsel", "kapak", "premium"],
        tags=["prompt", "ai", "visual", "premium"],
    ),
    
    MarketplaceItemType.REELS_THUMBNAIL_PROMPT: ProductDefinition(
        item_type=MarketplaceItemType.REELS_THUMBNAIL_PROMPT,
        name="Reels Thumbnail Prompt",
        description="Neon, sigma, motivational vibe thumbnail prompt'u.",
        price_range=(3.0, 6.0),
        default_price=4.5,
        quest_category="PRODUCTION",
        quest_keywords=["thumbnail", "reels", "prompt", "neon"],
        tags=["thumbnail", "reels", "prompt", "visual"],
    ),
    
    MarketplaceItemType.STORYBOARD_MINI: ProductDefinition(
        item_type=MarketplaceItemType.STORYBOARD_MINI,
        name="Storyboard Mini (3 sahne)",
        description="Video üreten creatorlar için 3 sahnelik storyboard.",
        price_range=(8.0, 20.0),
        default_price=14.0,
        quest_category="PRODUCTION",
        quest_keywords=["storyboard", "sahne", "video", "plan"],
        tags=["storyboard", "video", "production", "plan"],
    ),
    
    # C) RESEARCH-LEVEL ASSETS
    MarketplaceItemType.COMPETITOR_RESEARCH: ProductDefinition(
        item_type=MarketplaceItemType.COMPETITOR_RESEARCH,
        name="Competitor Research (Mini)",
        description="Bir rakip hesabın analizini çıkarır. 5 maddelik hızlı özet.",
        price_range=(10.0, 25.0),
        default_price=17.0,
        quest_category="RESEARCH",
        quest_keywords=["competitor", "rakip", "analiz", "research"],
        tags=["research", "competitor", "analysis", "kobi"],
    ),
    
    MarketplaceItemType.TREND_OPPORTUNITY_REPORT: ProductDefinition(
        item_type=MarketplaceItemType.TREND_OPPORTUNITY_REPORT,
        name="Trend Opportunity Report",
        description="Bugün fırsat olan 3 içerik fikri.",
        price_range=(10.0, 18.0),
        default_price=14.0,
        quest_category="RESEARCH",
        quest_keywords=["trend", "opportunity", "fırsat", "fikir"],
        tags=["trend", "opportunity", "research", "report"],
    ),
    
    MarketplaceItemType.NANO_INDUSTRY_REPORT: ProductDefinition(
        item_type=MarketplaceItemType.NANO_INDUSTRY_REPORT,
        name="Nano-Industry Report",
        description="'Kuaförler için 5 içerik fikri' gibi niche-specific rapor.",
        price_range=(15.0, 30.0),
        default_price=22.0,
        quest_category="RESEARCH",
        quest_keywords=["industry", "niche", "rapor", "kobi"],
        tags=["research", "industry", "niche", "kobi"],
    ),
    
    MarketplaceItemType.LOCAL_NICHE_PACK: ProductDefinition(
        item_type=MarketplaceItemType.LOCAL_NICHE_PACK,
        name="Local Niche Pack (Şehir bazlı)",
        description="'İzmit'te 5 viral çekim noktası' gibi şehir bazlı içerik paketi. Türkiye'de deli satar.",
        price_range=(8.0, 15.0),
        default_price=11.0,
        quest_category="RESEARCH",
        quest_keywords=["local", "şehir", "niche", "izmit", "ankara", "istanbul"],
        tags=["local", "niche", "city", "türkiye"],
    ),
    
    # D) MODERATION & TRUST
    MarketplaceItemType.TOXIC_COMMENT_CLEANER: ProductDefinition(
        item_type=MarketplaceItemType.TOXIC_COMMENT_CLEANER,
        name="Toxic Comment Cleaner Pack",
        description="20 problemli yorumu etiketler. Ajans için zaman kazancı.",
        price_range=(6.0, 12.0),
        default_price=9.0,
        quest_category="MODERATION",
        quest_keywords=["toxic", "comment", "temizlik", "moderation"],
        tags=["moderation", "toxic", "comment", "agency"],
    ),
    
    MarketplaceItemType.SPAM_DETECTION_REPORT: ProductDefinition(
        item_type=MarketplaceItemType.SPAM_DETECTION_REPORT,
        name="Spam Detection Report (Mini)",
        description="10 spam yorum → açıklamalı.",
        price_range=(4.0, 8.0),
        default_price=6.0,
        quest_category="MODERATION",
        quest_keywords=["spam", "detection", "rapor"],
        tags=["moderation", "spam", "detection", "agency"],
    ),
    
    MarketplaceItemType.SHADOWBAN_RISK_CHECK: ProductDefinition(
        item_type=MarketplaceItemType.SHADOWBAN_RISK_CHECK,
        name="Shadowban Risk Check (Mini)",
        description="Hesap incelemesi → 10 maddelik risk raporu. Çok değerli.",
        price_range=(15.0, 25.0),
        default_price=20.0,
        quest_category="MODERATION",
        quest_keywords=["shadowban", "risk", "check", "hesap"],
        tags=["moderation", "shadowban", "risk", "agency"],
    ),
    
    # E) COMMUNITY & RITUAL
    MarketplaceItemType.SOCIAL_VALUE_PACK: ProductDefinition(
        item_type=MarketplaceItemType.SOCIAL_VALUE_PACK,
        name="Social Value Pack",
        description="Sigma/motivasyon söz paketi (5 adet). Creator'lar bunları caption olarak kullanıyor.",
        price_range=(4.0, 8.0),
        default_price=6.0,
        quest_category="COMMUNITY",
        quest_keywords=["social", "value", "söz", "motivasyon", "sigma"],
        tags=["social", "value", "motivation", "caption"],
    ),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_product_definition(item_type: MarketplaceItemType) -> ProductDefinition:
    """Ürün tanımını getir."""
    return PRODUCT_CATALOG.get(item_type)


def infer_item_type_from_quest_key(quest_key: str) -> MarketplaceItemType:
    """
    Quest key'inden item tipini çıkar.
    
    Args:
        quest_key: Quest key (örn: "daily_micro_content")
    
    Returns:
        MarketplaceItemType
    """
    key_lower = quest_key.lower()
    
    # Her ürün tipi için keyword kontrolü
    for item_type, definition in PRODUCT_CATALOG.items():
        for keyword in definition.quest_keywords:
            if keyword.lower() in key_lower:
                return item_type
    
    # Default: En çok satan ürün tipi
    return MarketplaceItemType.VIRAL_HOOK


def calculate_price(
    item_type: MarketplaceItemType,
    ai_score: float,
    base_quest_reward: float = 0.0,
) -> float:
    """
    Ürün fiyatını hesapla.
    
    Args:
        item_type: Ürün tipi
        ai_score: AI kalite skoru (0-100)
        base_quest_reward: Quest ödülü (opsiyonel, fiyatlandırmaya etki edebilir)
    
    Returns:
        Fiyat (NCR)
    """
    definition = get_product_definition(item_type)
    
    if not definition:
        # Fallback: Quest ödülünün 3x'i
        return base_quest_reward * 3.0 if base_quest_reward > 0 else 5.0
    
    min_price, max_price = definition.price_range
    
    # AI Score'a göre fiyat ayarla (70-100 arası)
    # 70 = min_price, 100 = max_price
    if ai_score < 70:
        ai_score = 70.0
    if ai_score > 100:
        ai_score = 100.0
    
    # Linear interpolation
    score_factor = (ai_score - 70.0) / 30.0  # 0.0 - 1.0
    price = min_price + (max_price - min_price) * score_factor
    
    # Base quest reward varsa, onu da dikkate al (max %20 etki)
    if base_quest_reward > 0:
        quest_factor = min(base_quest_reward * 0.1, (max_price - min_price) * 0.2)
        price += quest_factor
    
    return round(price, 2)


def get_top_selling_products(limit: int = 5) -> List[MarketplaceItemType]:
    """
    En çok satacak ürünleri getir (Türkiye pazarı).
    
    Returns:
        En çok satacak ilk 5 ürün tipi
    """
    return [
        MarketplaceItemType.VIRAL_HOOK,           # 1. Viral Hook
        MarketplaceItemType.HASHTAG_SET,          # 2. Hashtag Set
        MarketplaceItemType.CAPTION_PACK,         # 3. Caption Pack
        MarketplaceItemType.TIKTOK_TREND_REPORT,  # 4. TikTok Trend Report
        MarketplaceItemType.LOCAL_NICHE_PACK,    # 5. Local Niche Pack
    ][:limit]

