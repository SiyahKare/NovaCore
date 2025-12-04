"""
NasipQuest Bot Handlers
Telegram bot komutları ve mesaj handler'ları
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.markdown import bold, code

from .api_client import api_client, InsufficientFundsError, AlreadyPurchasedError
from .config import config

router = Router()

# Citizen Quest Engine imports
from app.quests.telegram_formatter import (
    format_daily_quests_for_telegram,
    format_quest_detail_for_telegram,
)


# --- Helper Functions ---

def format_profile(profile: dict) -> str:
    """Profil bilgisini formatla."""
    text = f"👤 {bold('Profil')}\n\n"
    text += f"💰 Bakiye: {code(profile.get('wallet_balance', '0'))} NCR\n"
    text += f"⭐ XP: {code(str(profile.get('xp_total', 0)))} ({profile.get('tier', 'Bronze')})\n"
    text += f"📊 Seviye: {code(str(profile.get('level', 1)))}\n"
    
    if profile.get('xp_to_next_level', 0) > 0:
        text += f"⬆️ Sonraki seviye: {code(str(profile.get('xp_to_next_level', 0)))} XP kaldı\n"
    
    if profile.get('nova_score'):
        text += f"\n🎯 NovaScore: {code(str(profile.get('nova_score', 0)))}\n"
    
    if profile.get('cp_value', 0) > 0:
        text += f"⚖️ CP: {code(str(profile.get('cp_value', 0)))}\n"
        text += f"🔒 Regime: {code(profile.get('regime', 'NORMAL'))}\n"
    
    return text


def format_task(task: dict) -> str:
    """Görev bilgisini formatla."""
    text = f"📋 {bold(task.get('title', 'Görev'))}\n"
    text += f"{task.get('description', '')}\n\n"
    text += f"🎁 Ödül: +{task.get('reward_xp', 0)} XP, +{task.get('reward_ncr', '0')} NCR\n"
    
    if task.get('difficulty'):
        text += f"⚡ Zorluk: {task.get('difficulty', 'easy')}\n"
    
    if task.get('cooldown_seconds', 0) > 0:
        text += f"⏱️ Cooldown: {task.get('cooldown_seconds', 0)} saniye\n"
    
    return text


def format_event(event: dict) -> str:
    """Event bilgisini formatla."""
    text = f"🔥 {bold(event.get('name', 'Event'))}\n\n"
    text += f"{event.get('description', '')}\n\n"
    
    if event.get('reward_multiplier_xp', 1.0) > 1.0:
        text += f"⚡ XP Multiplier: {code(str(event.get('reward_multiplier_xp', 1.0)))}\n"
    
    if event.get('reward_multiplier_ncr', 1.0) > 1.0:
        text += f"💰 NCR Multiplier: {code(str(event.get('reward_multiplier_ncr', 1.0)))}\n"
    
    if event.get('is_joined'):
        text += f"\n✅ Katıldın!\n"
        if event.get('user_rank'):
            text += f"🏆 Sıralama: {code(str(event.get('user_rank')))}.\n"
        if event.get('user_score'):
            score = event.get('user_score', {})
            text += f"📊 Skor: {code(str(score.get('xp', 0)))} XP, {code(str(score.get('tasks_completed', 0)))} görev\n"
    else:
        text += f"\n❌ Henüz katılmadın. /join_{event.get('id')} ile katılabilirsin.\n"
    
    return text


# --- Command Handlers ---

@router.message(CommandStart())
async def cmd_start(message: Message):
    """Bot başlatma - Telegram user'ı NovaCore'a link et."""
    telegram_user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Start param kontrolü (eğer varsa)
    start_param = None
    if message.text and len(message.text.split()) > 1:
        start_param = message.text.split()[1]
    
    try:
        # NovaCore'a link et
        result = await api_client.link_user(
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            start_param=start_param,
        )
        
        if result.get("success"):
            await message.answer(
                f"✨ {bold('Hoş geldin!')}\n\n"
                f"NovaCore'a bağlandın.\n"
                f"User ID: {code(str(result.get('user_id', 'N/A')))}\n\n"
                f"Komutlar için /help yazabilirsin."
            )
        else:
            await message.answer("❌ Bağlantı hatası. Lütfen tekrar dene.")
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Yardım menüsü."""
    help_text = f"""
{bold('📚 NasipQuest Bot Komutları')}

{bold('Temel:')}
/start - Bot'u başlat ve NovaCore'a bağlan
/help - Bu yardım menüsü
/profile - Profil bilgilerini göster
/wallet - Cüzdan ve XP bilgisi

{bold('Görevler:')}
/tasks - Aktif görevleri listele (Legacy)
/quests - Günlük quest'ler (Yeni! 🎯)
/complete <task_id> - Görevi tamamla

{bold('Eventler:')}
/events - Aktif event'leri göster
/nasipfriday - Nasip Friday event'i
/war - Quest War leaderboard

{bold('Sosyal:')}
/leaderboard - Global leaderboard
/me - Detaylı profil kartı
/refer <code> - Referral ödülü talep et

{bold('Yardım:')}
/help - Bu menü
"""
    await message.answer(help_text)


@router.message(Command("profile", "wallet"))
async def cmd_profile(message: Message):
    """Profil ve cüzdan bilgisi."""
    telegram_user_id = message.from_user.id
    
    try:
        profile = await api_client.get_profile(telegram_user_id)
        text = format_profile(profile)
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("tasks"))
async def cmd_tasks(message: Message):
    """Görev listesi (Legacy - eski task API)."""
    telegram_user_id = message.from_user.id
    
    try:
        tasks_data = await api_client.get_tasks(telegram_user_id)
        tasks = tasks_data.get("tasks", [])
        
        if not tasks:
            await message.answer("📋 Şu an aktif görev yok.")
            return
        
        text = f"{bold('📋 Aktif Görevler')}\n\n"
        for task in tasks:
            text += format_task(task)
            text += "\n"
        
        # Inline keyboard ile görev tamamlama butonları
        keyboard = []
        for task in tasks[:5]:  # Max 5 görev
            if task.get("status") == "available":
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"✅ {task.get('title', task.get('id'))}",
                        callback_data=f"complete_{task.get('id')}"
                    )
                ])
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
        
        await message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


def format_quest(quest: dict) -> str:
    """Quest bilgisini formatla."""
    status_emoji = {
        "assigned": "📌",
        "submitted": "⏳",
        "under_review": "🔍",
        "approved": "✅",
        "rejected": "❌",
        "expired": "⏰",
    }
    status = quest.get("status", "assigned")
    emoji = status_emoji.get(status, "📋")
    
    text = f"{emoji} {bold(quest.get('title', 'Quest'))}\n"
    text += f"{quest.get('description', '')}\n\n"
    
    # Base rewards
    base_ncr = quest.get("base_reward_ncr", 0)
    base_xp = quest.get("base_reward_xp", 0)
    text += f"🎁 Ödül: +{code(str(base_xp))} XP, +{code(str(base_ncr))} NCR\n"
    
    # Final rewards (eğer varsa)
    final_ncr = quest.get("final_reward_ncr")
    final_xp = quest.get("final_reward_xp")
    if final_ncr is not None and final_xp is not None:
        text += f"💰 Final: +{code(str(final_xp))} XP, +{code(str(final_ncr))} NCR\n"
    
    # Status
    status_text = {
        "assigned": "Atandı - Başla!",
        "submitted": "Gönderildi - Onay bekleniyor",
        "under_review": "İncelemede - DAO kontrolü",
        "approved": "Onaylandı - Ödül verildi",
        "rejected": "Reddedildi",
        "expired": "Süresi doldu",
    }
    text += f"📊 Durum: {status_text.get(status, status)}\n"
    
    # Expires at
    if quest.get("expires_at"):
        text += f"⏱️ Bitiş: {quest.get('expires_at')}\n"
    
    return text


@router.message(Command("quests"))
async def cmd_quests(message: Message):
    """Günlük quest'leri getir (Production-Ready Quest Engine)."""
    telegram_user_id = message.from_user.id
    
    try:
        quests_data = await api_client.get_quests(telegram_user_id)
        quests = quests_data.get("quests", [])
        total_available = quests_data.get("total_available", 0)
        
        if not quests:
            await message.answer(
                f"{bold('📚 Günlük Questler')}\n\n"
                "Şu an aktif quest yok. Yarın tekrar dene! 🎯",
                parse_mode="Markdown"
            )
            return
        
        text = f"{bold('📚 Günlük Questler')}\n\n"
        text += f"Toplam {code(str(total_available))} quest mevcut\n\n"
        
        # Quest'leri listele
        for idx, quest in enumerate(quests, 1):
            text += f"{code(f'{idx}.')} {format_quest(quest)}\n"
        
        # Inline keyboard ile quest seçimi
        keyboard = []
        for quest in quests:
            if quest.get("status") == "assigned":
                quest_uuid = quest.get("quest_uuid")
                title = quest.get("title", "Quest")
                # Kısa başlık (max 30 karakter)
                short_title = title[:27] + "..." if len(title) > 30 else title
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"🎯 {short_title}",
                        callback_data=f"quest_select_{quest_uuid}"
                    )
                ])
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
        
        await message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("complete"))
async def cmd_complete(message: Message):
    """Görev tamamlama."""
    telegram_user_id = message.from_user.id
    
    # Komuttan task_id al
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("❌ Kullanım: /complete <task_id>\nÖrnek: /complete daily_login")
        return
    
    task_id = parts[1]
    
    try:
        result = await api_client.submit_task(
            telegram_user_id=telegram_user_id,
            task_id=task_id,
            proof="completed_via_bot",
        )
        
        if result.get("success"):
            await message.answer(
                f"✅ {result.get('message', 'Görev tamamlandı!')}\n"
                f"Yeni bakiye: {code(result.get('new_balance', '0'))} NCR\n"
                f"Yeni XP: {code(str(result.get('new_xp_total', 0)))}",
                parse_mode="Markdown"
            )
        else:
            await message.answer("❌ Görev tamamlanamadı.")
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("events"))
async def cmd_events(message: Message):
    """Aktif event'leri listele."""
    telegram_user_id = message.from_user.id
    
    try:
        events_data = await api_client.get_active_events(telegram_user_id)
        events = events_data.get("events", [])
        
        if not events:
            await message.answer("🔥 Şu an aktif event yok.")
            return
        
        text = f"{bold('🔥 Aktif Eventler')}\n\n"
        for event in events:
            text += format_event(event)
            text += "\n"
        
        # Join butonları
        keyboard = []
        for event in events[:5]:
            if not event.get("is_joined"):
                keyboard.append([
                    InlineKeyboardButton(
                        text=f"🎯 {event.get('name', 'Event')} - Katıl",
                        callback_data=f"join_event_{event.get('id')}"
                    )
                ])
        
        reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard) if keyboard else None
        
        await message.answer(text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("nasipfriday"))
async def cmd_nasipfriday(message: Message):
    """Nasip Friday event'i."""
    telegram_user_id = message.from_user.id
    
    try:
        events_data = await api_client.get_active_events(telegram_user_id)
        events = events_data.get("events", [])
        
        # Nasip Friday event'ini bul
        nasip_friday = None
        for event in events:
            if event.get("event_type") == "NASIP_FRIDAY":
                nasip_friday = event
                break
        
        if not nasip_friday:
            await message.answer("🔥 Şu an Nasip Friday event'i aktif değil.")
            return
        
        text = format_event(nasip_friday)
        
        keyboard = None
        if not nasip_friday.get("is_joined"):
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                InlineKeyboardButton(
                    text="🎯 Nasip Friday'e Katıl",
                    callback_data=f"join_event_{nasip_friday.get('id')}"
                )
            ]])
        
        await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("war"))
async def cmd_war(message: Message):
    """Quest War leaderboard."""
    telegram_user_id = message.from_user.id
    
    try:
        events_data = await api_client.get_active_events(telegram_user_id)
        events = events_data.get("events", [])
        
        # Quest War event'ini bul
        quest_war = None
        for event in events:
            if event.get("event_type") == "QUEST_WAR":
                quest_war = event
                break
        
        if not quest_war:
            await message.answer("⚔️ Şu an Quest War event'i aktif değil.")
            return
        
        # Leaderboard'u getir
        leaderboard_data = await api_client.get_event_leaderboard(
            event_id=quest_war.get("id"),
            limit=10
        )
        
        entries = leaderboard_data.get("entries", [])
        
        text = f"{bold('⚔️ Quest War Leaderboard')}\n\n"
        for entry in entries:
            rank = entry.get("rank", 0)
            username = entry.get("username") or entry.get("display_name", "Anonim")
            xp = entry.get("total_xp_earned", 0)
            tasks = entry.get("tasks_completed", 0)
            
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
            text += f"{medal} {rank}. {code(username)}\n"
            text += f"   {code(str(xp))} XP, {code(str(tasks))} görev\n\n"
        
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("leaderboard", "top"))
async def cmd_leaderboard(message: Message):
    """Global leaderboard."""
    try:
        leaderboard_data = await api_client.get_leaderboard(period="all_time", limit=10)
        entries = leaderboard_data.get("entries", [])
        
        text = f"{bold('🏆 Global Leaderboard')}\n\n"
        for entry in entries:
            rank = entry.get("rank", 0)
            username = entry.get("username") or entry.get("display_name", "Anonim")
            xp = entry.get("xp_total", 0)
            level = entry.get("level", 1)
            
            medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "🏅"
            text += f"{medal} {rank}. {code(username)}\n"
            text += f"   {code(str(xp))} XP, Seviye {code(str(level))}\n\n"
        
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("me"))
async def cmd_me(message: Message):
    """Detaylı profil kartı."""
    telegram_user_id = message.from_user.id
    
    try:
        profile = await api_client.get_profile_card(telegram_user_id)
        
        text = f"{bold('👤 Profil Kartı')}\n\n"
        text += f"👤 {profile.get('display_name', 'Anonim')}\n"
        text += f"⭐ XP: {code(str(profile.get('xp_total', 0)))}\n"
        text += f"📊 Seviye: {code(str(profile.get('level', 1)))} ({profile.get('tier', 'Bronze')})\n"
        text += f"✅ Tamamlanan Görevler: {code(str(profile.get('tasks_completed', 0)))}\n"
        text += f"👥 Referral Sayısı: {code(str(profile.get('referrals_count', 0)))}\n"
        
        if profile.get('rank_all_time'):
            text += f"🏆 Global Sıralama: {code(str(profile.get('rank_all_time')))}.\n"
        
        if profile.get('achievements'):
            text += f"\n{bold('🏅 Başarılar:')}\n"
            for achievement in profile.get('achievements', []):
                text += f"  • {achievement}\n"
        
        await message.answer(text, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


# --- Callback Handlers ---

@router.callback_query(F.data.startswith("complete_"))
async def callback_complete_task(callback: CallbackQuery):
    """Görev tamamlama callback."""
    task_id = callback.data.replace("complete_", "")
    telegram_user_id = callback.from_user.id
    
    await callback.answer("Görev tamamlanıyor...")
    
    try:
        result = await api_client.submit_task(
            telegram_user_id=telegram_user_id,
            task_id=task_id,
            proof="completed_via_bot",
        )
        
        if result.get("success"):
            await callback.message.edit_text(
                f"✅ {result.get('message', 'Görev tamamlandı!')}\n"
                f"Yeni bakiye: {code(result.get('new_balance', '0'))} NCR\n"
                f"Yeni XP: {code(str(result.get('new_xp_total', 0)))}",
                parse_mode="Markdown"
            )
        else:
            await callback.answer("❌ Görev tamamlanamadı.", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Hata: {str(e)}", show_alert=True)


@router.callback_query(F.data.startswith("join_event_"))
async def callback_join_event(callback: CallbackQuery):
    """Event'e katılma callback."""
    event_id = int(callback.data.replace("join_event_", ""))
    telegram_user_id = callback.from_user.id
    
    await callback.answer("Event'e katılıyorsun...")
    
    try:
        result = await api_client.join_event(
            telegram_user_id=telegram_user_id,
            event_id=event_id,
        )
        
        if result.get("success"):
            await callback.message.edit_text(
                f"✅ {result.get('message', 'Event\'e katıldın!')}",
                parse_mode="Markdown"
            )
        else:
            await callback.answer("❌ Event'e katılamadın.", show_alert=True)
    except Exception as e:
        await callback.answer(f"❌ Hata: {str(e)}", show_alert=True)



@router.callback_query(F.data.startswith("quest_select_"))
async def callback_quest_select(callback: CallbackQuery):
    """Quest seçimi callback - proof gönderme ekranına yönlendir."""
    await callback.answer()
    
    quest_uuid = callback.data.replace("quest_select_", "")
    telegram_user_id = callback.from_user.id
    
    try:
        # Quest detaylarını getir
        quests_data = await api_client.get_quests(telegram_user_id)
        quests = quests_data.get("quests", [])
        
        quest = None
        for q in quests:
            if q.get("quest_uuid") == quest_uuid:
                quest = q
                break
        
        if not quest:
            await callback.message.edit_text("❌ Quest bulunamadı.")
            return
        
        # Proof gönderme talimatları
        proof_type = quest.get("proof_type") or "text"
        text = f"{bold('📝 Quest: ' + quest.get('title', 'Quest'))}\n\n"
        text += f"{quest.get('description', '')}\n\n"
        text += f"🎁 Ödül: +{code(str(quest.get('base_reward_xp', 0)))} XP, +{code(str(quest.get('base_reward_ncr', 0)))} NCR\n\n"
        
        if proof_type == "text":
            text += "💬 Bu quest için metin göndermen gerekiyor.\n"
            text += "Aşağıdaki butona tıklayarak quest'i tamamlayabilirsin.\n"
        elif proof_type == "photo":
            text += "📸 Bu quest için fotoğraf göndermen gerekiyor.\n"
            text += "Fotoğraf göndererek quest'i tamamlayabilirsin.\n"
        else:
            text += "📎 Bu quest için kanıt göndermen gerekiyor.\n"
            text += "Kanıt göndererek quest'i tamamlayabilirsin.\n"
        
        # Basit proof gönderme butonu
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(
                text="✅ Quest'i Tamamla",
                callback_data=f"quest_submit_{quest_uuid}_{proof_type}"
            )
        ]])
        
        await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
    except Exception as e:
        await callback.message.edit_text(f"❌ Hata: {str(e)}")


@router.callback_query(F.data.startswith("quest_submit_"))
async def callback_quest_submit(callback: CallbackQuery):
    """Quest proof gönderme callback."""
    await callback.answer("Quest gönderiliyor...")
    
    parts = callback.data.split("_")
    quest_uuid = parts[2] if len(parts) > 2 else None
    proof_type = parts[3] if len(parts) > 3 else "text"
    
    if not quest_uuid:
        await callback.message.edit_text("❌ Quest UUID bulunamadı.")
        return
    
    telegram_user_id = callback.from_user.id
    
    try:
        # Basit text proof gönder
        result = await api_client.submit_quest(
            telegram_user_id=telegram_user_id,
            quest_uuid=quest_uuid,
            proof_type=proof_type,
            proof_payload_ref=f"telegram_callback_{callback.id}",
            ai_score=None,  # Bot tarafında AI scoring yok, backend'de yapılacak
        )
        
        # Response'dan bilgi al
        status = result.get("status", "unknown")
        final_reward_ncr = result.get("final_reward_ncr")
        final_reward_xp = result.get("final_reward_xp")
        
        if status == "approved":
            text = f"{bold('✅ Quest Onaylandı!')}\n\n"
            if final_reward_ncr and final_reward_xp:
                text += f"💰 Ödül: +{code(str(final_reward_xp))} XP, +{code(str(final_reward_ncr))} NCR\n"
            text += f"🎉 Tebrikler! Quest başarıyla tamamlandı."
        elif status == "submitted":
            text = f"{bold('⏳ Quest Gönderildi')}\n\n"
            text += "Quest'in onaylanması bekleniyor. Kısa süre içinde sonuç alacaksın!"
        elif status == "under_review":
            text = f"{bold('🔍 Quest İncelemede')}\n\n"
            text += "Quest DAO tarafından inceleniyor. Sonuç yakında bildirilecek."
        else:
            text = f"{bold('📋 Quest Durumu')}\n\n"
            text += f"Durum: {code(status)}"
        
        await callback.message.edit_text(text, parse_mode="Markdown")
    except Exception as e:
        await callback.message.edit_text(f"❌ Hata: {str(e)}")


# =============================================================================
# CITIZEN QUEST ENGINE - Telegram Komutları
# =============================================================================

@router.message(Command("tasks"))
@router.message(Command("görevler"))
async def cmd_tasks(message: Message):
    """
    /tasks veya /görevler - Bugünün görev listesi
    
    Citizen Quest Engine - MVP Pack V1 görevlerini gösterir.
    """
    telegram_user_id = message.from_user.id
    
    try:
        # Günlük quest'leri getir
        result = await api_client.get_quests_today(telegram_user_id)
        quests = result.get("quests", []) if isinstance(result, dict) else result
        
        if not quests:
            await message.answer(
                "📋 Bugün için henüz görev yok.\n"
                "Görevler oluşturuluyor...",
            )
            return
        
        # Quest'leri RuntimeQuest formatına çevir (formatting için)
        from app.quests.factory import RuntimeQuest
        runtime_quests = []
        for q in quests:
            runtime_quests.append(
                RuntimeQuest(
                    uuid=q.get("quest_uuid", ""),
                    type=q.get("quest_type", "reflection"),
                    key=q.get("key", ""),
                    title=q.get("title", "Quest"),
                    description=q.get("description", ""),
                    base_ncr=q.get("base_reward_ncr", 0.0),
                    base_xp=q.get("base_reward_xp", 0),
                )
            )
        
        # Telegram formatına çevir
        formatted = format_daily_quests_for_telegram(runtime_quests)
        
        # Inline keyboard ile quest seçimi
        keyboard_buttons = []
        for idx, quest in enumerate(quests[:5], 1):  # İlk 5 quest
            quest_uuid = quest.get("quest_uuid", "")
            title_short = quest.get("title", "Quest")[:30]
            keyboard_buttons.append([
                InlineKeyboardButton(
                    text=f"{idx}. {title_short}",
                    callback_data=f"quest_select_{quest_uuid}"
                )
            ])
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
        
        await message.answer(formatted, parse_mode="Markdown", reply_markup=keyboard)
    
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("complete"))
async def cmd_complete(message: Message):
    """
    /complete <quest_uuid> - Quest proof gönderme
    
    Kullanım: /complete <quest_uuid>
    Örnek: /complete abc-123-def-456
    """
    telegram_user_id = message.from_user.id
    command_parts = message.text.split()
    
    if len(command_parts) < 2:
        await message.answer(
            "📝 Kullanım: /complete <quest_uuid>\n\n"
            "Quest UUID'yi görmek için /tasks komutunu kullan."
        )
        return
    
    quest_uuid = command_parts[1]
    
    try:
        # Proof gönder (text olarak mesajın geri kalanı)
        proof_text = " ".join(command_parts[2:]) if len(command_parts) > 2 else "completed_via_command"
        
        result = await api_client.submit_quest(
            telegram_user_id=telegram_user_id,
            quest_uuid=quest_uuid,
            proof_type="text",
            proof_payload_ref=f"telegram_cmd_{message.message_id}",
            proof_content=proof_text,
            message_id=str(message.message_id),
            ai_score=None,
        )
        
        status = result.get("status", "unknown")
        final_reward_ncr = result.get("final_reward_ncr")
        final_reward_xp = result.get("final_reward_xp")
        
        if status == "approved":
            text = f"{bold('✅ Quest Onaylandı!')}\n\n"
            if final_reward_ncr and final_reward_xp:
                text += f"💰 Ödül: +{code(str(final_reward_xp))} XP, +{code(str(final_reward_ncr))} NCR\n"
            text += f"🎉 Tebrikler!"
        elif status == "submitted":
            text = f"{bold('⏳ Quest Gönderildi')}\n\n"
            text += "Quest'in onaylanması bekleniyor."
        else:
            text = f"📋 Quest Durumu: {code(status)}"
        
        await message.answer(text, parse_mode="Markdown")
    
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("earnings"))
async def cmd_earnings(message: Message):
    """
    /earnings - NCR kazançları
    
    Son 7 günlük NCR kazançlarını gösterir.
    """
    telegram_user_id = message.from_user.id
    
    try:
        # Wallet balance ve transaction history getir
        wallet_data = await api_client.get_wallet(telegram_user_id)
        balance = wallet_data.get("balance", 0.0)
        
        # Son işlemler (quest ödülleri)
        transactions = wallet_data.get("recent_transactions", [])
        
        # Quest ödüllerini filtrele
        quest_earnings = [
            t for t in transactions
            if t.get("source") == "quest_reward" and t.get("amount", 0) > 0
        ]
        
        # Son 7 günlük toplam
        from datetime import datetime, timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        total_7d = sum(
            t.get("amount", 0) for t in quest_earnings
            if datetime.fromisoformat(t.get("created_at", "").replace("Z", "+00:00")) > seven_days_ago
        )
        
        text = f"{bold('💰 NCR Kazançları')}\n\n"
        text += f"💵 Toplam Bakiye: {code(str(balance))} NCR\n"
        text += f"📅 Son 7 Gün: {code(str(total_7d))} NCR\n\n"
        
        if quest_earnings:
            text += f"{bold('Son Quest Ödülleri:')}\n"
            for t in quest_earnings[:5]:  # Son 5 ödül
                amount = t.get("amount", 0)
                created_at = t.get("created_at", "")[:10]  # Sadece tarih
                text += f"  • {code(str(amount))} NCR ({created_at})\n"
        else:
            text += "Henüz quest ödülü yok.\n"
            text += "Görevleri tamamlamak için /tasks komutunu kullan."
        
        await message.answer(text, parse_mode="Markdown")
    
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")
