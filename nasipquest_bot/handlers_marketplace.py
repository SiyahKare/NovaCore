"""
NasipQuest Bot - Marketplace Handlers
Telegram bot marketplace komutları
"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.markdown import bold, code

from .api_client import api_client, InsufficientFundsError, AlreadyPurchasedError

router = Router(name="marketplace")

ITEMS_PER_PAGE = 10


def _format_item_line(item: dict, idx: int) -> str:
    """Marketplace item'ini formatla."""
    name = item.get("title") or item.get("name") or "Adsız ürün"
    item_type = item.get("item_type", "").replace("_", " ").title()
    ai_score = item.get("ai_score") or item.get("quality_score") or "—"
    price = item.get("price_ncr") or item.get("price") or 0
    
    return (
        f"{idx}. {bold(name)}\n"
        f"   • Tür: {code(item_type)}\n"
        f"   • Skor: {code(str(ai_score))}\n"
        f"   • Fiyat: {code(f'{price:.2f} NCR')}\n"
    )


def _build_item_keyboard(item_id: int) -> InlineKeyboardMarkup:
    """Item için satın alma butonu oluştur."""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 Satın al",
                    callback_data=f"buy:{item_id}",
                )
            ]
        ]
    )


@router.message(Command("market"))
async def cmd_market(message: Message):
    """
    /market - Marketplace TOP ürünleri
    
    En yüksek skorlu aktif ürünleri gösterir.
    """
    telegram_user_id = message.from_user.id
    
    try:
        # TOP 10 aktif ürün (yüksek skorlu olanları getir)
        items = await api_client.list_marketplace_items(
            telegram_user_id=telegram_user_id,
            limit=ITEMS_PER_PAGE,
            status="active",
        )
        
        # API response bir dict olabilir (items listesi içinde)
        if isinstance(items, dict):
            items = items.get("items", [])
        
        if not items:
            await message.answer(
                "🛒 Şu an vitrinde ürün yok.\n\n"
                "Biraz NasipQuest görevi tamamlayalım ki vitrin dolsun.\n"
                "Görevler için: /tasks"
            )
            return
        
        # İlk item'i en üstte vurgula
        text_lines = [f"{bold('🛒 SiyahKare Marketplace')} — TOP ürünler:\n"]
        
        for idx, item in enumerate(items, start=1):
            text_lines.append(_format_item_line(item, idx))
        
        # İlk item için "Satın al" butonu
        first_item = items[0]
        first_item_id = first_item.get("id")
        
        if first_item_id:
            keyboard = _build_item_keyboard(first_item_id)
        else:
            keyboard = None
        
        await message.answer(
            "\n".join(text_lines),
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.callback_query(F.data.startswith("buy:"))
async def cb_buy_item(callback: CallbackQuery):
    """Satın alma callback handler."""
    telegram_user_id = callback.from_user.id
    
    # Item ID parse et
    _, raw_id = callback.data.split(":", 1)
    try:
        item_id = int(raw_id)
    except ValueError:
        await callback.answer("Geçersiz ürün ID.", show_alert=True)
        return
    
    await callback.answer()  # Spinner'ı kapat
    
    try:
        # Önce item detayını çek (fiyat/yazar göstermek için)
        item = await api_client.get_marketplace_item(
            telegram_user_id=telegram_user_id,
            item_id=item_id,
        )
        
        if not item:
            await callback.message.answer("Bu ürün artık mevcut değil.")
            return
        
        name = item.get("title") or item.get("name") or "Adsız ürün"
        price = item.get("price_ncr") or item.get("price") or 0
        
        # Kullanıcıya mini onay mesajı
        await callback.message.answer(
            f"{bold('💳 Satın alma işlemi başlatılıyor...')}\n\n"
            f"Ürün: {bold(name)}\n"
            f"Fiyat: {code(f'{price:.2f} NCR')}",
            parse_mode="Markdown",
        )
        
        # Satın alma isteği
        purchase = await api_client.purchase_marketplace_item(
            telegram_user_id=telegram_user_id,
            item_id=item_id,
        )
        
        # Başarılı
        creator_share = purchase.get("creator_share_ncr", 0)
        treasury_share = purchase.get("treasury_share_ncr", 0)
        item_type = item.get("item_type", "")
        content = item.get("content")
        
        # Content delivery
        if content:
            # Content'i formatla ve gönder
            from app.marketplace.delivery import format_content_for_delivery
            formatted_content = format_content_for_delivery(content, item_type)
            
            await callback.message.answer(
                f"{bold('✅ Satın alma başarılı!')}\n\n"
                f"Ürün: {bold(name)}\n"
                f"Ödenen: {code(f'{price:.2f} NCR')}\n\n"
                f"{bold('📦 İçerik:')}\n\n{formatted_content}",
                parse_mode="Markdown",
            )
        else:
            # Content yoksa sadece ödeme bilgisi
            await callback.message.answer(
                f"{bold('✅ Satın alma başarılı!')}\n\n"
                f"Ürün: {bold(name)}\n"
                f"Ödenen: {code(f'{price:.2f} NCR')}\n"
                f"Creator payı: {code(f'{creator_share:.2f} NCR')}\n"
                f"Treasury payı: {code(f'{treasury_share:.2f} NCR')}\n\n"
                f"ℹ️ İçerik hazırlanıyor, yakında gönderilecek.",
                parse_mode="Markdown",
            )
    
    except InsufficientFundsError:
        await callback.message.answer(
            f"{bold('🚫 NCR bakiyen yetersiz.')}\n\n"
            f"💡 Çözüm: {code('/tasks')} ile görev tamamla, NCR kazan."
        )
    
    except AlreadyPurchasedError:
        await callback.message.answer(
            f"{bold('ℹ️ Bu ürünü zaten daha önce almışsın.')}\n\n"
            f"Envanterinden veya panelden kullanabilirsin."
        )
    
    except Exception as e:
        await callback.message.answer(
            f"{bold('⚠️ Satın alma sırasında bir hata oluştu.')}\n\n"
            f"Biraz sonra tekrar dene.\n\n"
            f"Hata: {code(str(e))}"
        )


@router.message(Command("buy"))
async def cmd_buy(message: Message):
    """
    /buy <item_id> - Marketplace item satın al
    
    Kullanım: /buy 12
    """
    telegram_user_id = message.from_user.id
    command_parts = message.text.split()
    
    if len(command_parts) < 2:
        await message.answer(
            f"{bold('📝 Kullanım:')} {code('/buy <ürün_id>')}\n\n"
            f"Ürün ID'lerini görmek için {code('/market')} komutunu kullan."
        )
        return
    
    try:
        item_id = int(command_parts[1])
    except ValueError:
        await message.answer("Geçersiz ürün ID. Sayı olmalı.")
        return
    
    try:
        # Item detayını çek
        item = await api_client.get_marketplace_item(
            telegram_user_id=telegram_user_id,
            item_id=item_id,
        )
        
        if not item:
            await message.answer("Bu ürün artık mevcut değil.")
            return
        
        name = item.get("title") or item.get("name") or "Adsız ürün"
        price = item.get("price_ncr") or item.get("price") or 0
        
        # Satın alma
        purchase = await api_client.purchase_marketplace_item(
            telegram_user_id=telegram_user_id,
            item_id=item_id,
        )
        
        # Başarılı
        creator_share = purchase.get("creator_share_ncr", 0)
        treasury_share = purchase.get("treasury_share_ncr", 0)
        item_type = item.get("item_type", "")
        content = item.get("content")
        
        # Content delivery
        if content:
            # Content'i formatla ve gönder
            from app.marketplace.delivery import format_content_for_delivery
            formatted_content = format_content_for_delivery(content, item_type)
            
            await message.answer(
                f"{bold('✅ Satın alma başarılı!')}\n\n"
                f"Ürün: {bold(name)}\n"
                f"Ödenen: {code(f'{price:.2f} NCR')}\n\n"
                f"{bold('📦 İçerik:')}\n\n{formatted_content}",
                parse_mode="Markdown",
            )
        else:
            # Content yoksa sadece ödeme bilgisi
            await message.answer(
                f"{bold('✅ Satın alma başarılı!')}\n\n"
                f"Ürün: {bold(name)}\n"
                f"Ödenen: {code(f'{price:.2f} NCR')}\n"
                f"Creator payı: {code(f'{creator_share:.2f} NCR')}\n"
                f"Treasury payı: {code(f'{treasury_share:.2f} NCR')}\n\n"
                f"ℹ️ İçerik hazırlanıyor, yakında gönderilecek.",
                parse_mode="Markdown",
            )
    
    except InsufficientFundsError:
        await message.answer(
            f"{bold('🚫 NCR bakiyen yetersiz.')}\n\n"
            f"💡 Çözüm: {code('/tasks')} ile görev tamamla, NCR kazan."
        )
    
    except AlreadyPurchasedError:
        await message.answer(
            f"{bold('ℹ️ Bu ürünü zaten daha önce almışsın.')}\n\n"
            f"Envanterinden veya panelden kullanabilirsin."
        )
    
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("my_items"))
async def cmd_my_items(message: Message):
    """
    /my_items - Kendi marketplace item'lerimi göster
    
    Creator olarak yüklediğin ürünleri listeler.
    """
    telegram_user_id = message.from_user.id
    
    try:
        items = await api_client.get_my_marketplace_items(
            telegram_user_id=telegram_user_id,
            limit=20,
        )
        
        # API response bir dict olabilir
        if isinstance(items, dict):
            items = items.get("items", [])
        
        if not items:
            await message.answer(
                f"{bold('📦 Kendi Ürünlerim')}\n\n"
                f"Henüz marketplace'e ürün eklememişsin.\n\n"
                f"Quest tamamlayarak ürün oluşturabilirsin: {code('/tasks')}"
            )
            return
        
        text_lines = [f"{bold('📦 Kendi Ürünlerim')}\n\n"]
        
        for idx, item in enumerate(items, start=1):
            name = item.get("title") or "Adsız ürün"
            status = item.get("status", "unknown")
            price = item.get("price_ncr", 0)
            purchase_count = item.get("purchase_count", 0)
            total_revenue = item.get("total_revenue_ncr", 0)
            
            status_emoji = {
                "active": "✅",
                "draft": "⏳",
                "disabled": "🚫",
                "archived": "📦",
            }.get(status, "❓")
            
            text_lines.append(
                f"{idx}. {status_emoji} {bold(name)}\n"
                f"   • Durum: {code(status)}\n"
                f"   • Fiyat: {code(f'{price:.2f} NCR')}\n"
                f"   • Satış: {code(str(purchase_count))} adet\n"
                f"   • Toplam Gelir: {code(f'{total_revenue:.2f} NCR')}\n"
            )
        
        await message.answer("\n".join(text_lines), parse_mode="Markdown")
    
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("my_sales"))
async def cmd_my_sales(message: Message):
    """
    /my_sales - Satış istatistiklerimi göster
    
    Creator olarak marketplace'ten kazandığın NCR'ı gösterir.
    """
    telegram_user_id = message.from_user.id
    
    try:
        sales_data = await api_client.get_my_marketplace_sales(
            telegram_user_id=telegram_user_id,
        )
        
        creator_id = sales_data.get("creator_id")
        total_sales = sales_data.get("total_sales", 0)
        total_revenue_ncr = sales_data.get("total_revenue_ncr", 0)
        purchases = sales_data.get("purchases", [])
        
        text = f"{bold('💰 Satış İstatistiklerim')}\n\n"
        text += f"Toplam Satış: {code(str(total_sales))} adet\n"
        text += f"Toplam Gelir: {code(f'{total_revenue_ncr:.2f} NCR')}\n\n"
        
        if purchases:
            text += f"{bold('Son Satışlar:')}\n"
            for purchase in purchases[:5]:  # Son 5 satış
                item_title = purchase.get("item_title", "Bilinmeyen ürün")
                creator_share = purchase.get("creator_share_ncr", 0)
                created_at = purchase.get("created_at", "")[:10]  # Sadece tarih
                text += f"  • {item_title}: {code(f'{creator_share:.2f} NCR')} ({created_at})\n"
        else:
            text += "Henüz satış yok.\n"
            text += f"Ürünlerini görmek için: {code('/my_items')}"
        
        await message.answer(text, parse_mode="Markdown")
    
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")

