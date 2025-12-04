"""
Marketplace Content Delivery - Purchase sonrası içerik teslimi
"""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from .models import MarketplaceItem, MarketplacePurchase
from app.core.logging import get_logger

logger = get_logger("marketplace_delivery")


async def get_purchase_content(
    session: AsyncSession,
    purchase_id: int,
) -> Optional[str]:
    """
    Purchase sonrası buyer'a gönderilecek content'i getir.
    
    Args:
        session: Database session
        purchase_id: MarketplacePurchase.id
    
    Returns:
        Content string (JSON veya plain text) veya None
    """
    stmt = select(MarketplacePurchase).where(
        MarketplacePurchase.id == purchase_id
    )
    result = await session.execute(stmt)
    purchase = result.scalar_one_or_none()
    
    if not purchase:
        logger.warning(
            "purchase_not_found",
            purchase_id=purchase_id,
        )
        return None
    
    # Item'den content'i al
    item_stmt = select(MarketplaceItem).where(
        MarketplaceItem.id == purchase.item_id
    )
    item_result = await session.execute(item_stmt)
    item = item_result.scalar_one_or_none()
    
    if not item:
        logger.warning(
            "item_not_found_for_purchase",
            purchase_id=purchase_id,
            item_id=purchase.item_id,
        )
        return None
    
    return item.content


async def format_content_for_delivery(
    content: str,
    item_type: str,
) -> str:
    """
    Content'i Telegram bot'a gönderilebilir formata çevir.
    
    Args:
        content: Raw content (JSON veya plain text)
        item_type: Item tipi (hook, caption_pack, vb.)
    
    Returns:
        Formatted string
    """
    # Eğer JSON ise parse et
    import json
    
    try:
        parsed = json.loads(content)
        
        # Hook Pack formatı
        if item_type in ["hook", "viral_hook"]:
            if isinstance(parsed, list):
                return "\n".join([f"• {hook}" for hook in parsed])
            elif isinstance(parsed, dict) and "hooks" in parsed:
                return "\n".join([f"• {hook}" for hook in parsed["hooks"]])
        
        # Caption Pack formatı
        elif item_type in ["caption_pack", "caption"]:
            if isinstance(parsed, list):
                return "\n\n---\n\n".join([f"{idx+1}. {caption}" for idx, caption in enumerate(parsed)])
            elif isinstance(parsed, dict) and "captions" in parsed:
                return "\n\n---\n\n".join([f"{idx+1}. {caption}" for idx, caption in enumerate(parsed["captions"])])
        
        # Script formatı
        elif item_type in ["script", "story_script"]:
            if isinstance(parsed, dict) and "scripts" in parsed:
                return "\n\n---\n\n".join([
                    f"**Script {idx+1}:**\n{script}"
                    for idx, script in enumerate(parsed["scripts"])
                ])
        
        # Default: JSON'u pretty print
        return json.dumps(parsed, indent=2, ensure_ascii=False)
    
    except (json.JSONDecodeError, TypeError):
        # Plain text ise direkt döndür
        return content

