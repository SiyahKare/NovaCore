"""
NasipQuest Bot Handlers
Telegram bot komutları ve mesaj handler'ları
"""
from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.markdown import bold, code

from .api_client import api_client, InsufficientFundsError, AlreadyPurchasedError
from .storyquest_client import storyquest_client
from .config import config

router = Router()

# StoryQuest run_id storage (user_id -> run_id mapping)
# Telegram callback data limiti 64 byte, bu yüzden run_id'yi saklıyoruz
_storyquest_runs: dict[int, str] = {}  # user_id -> run_id

# "Cevap yaz" modu - kullanıcı text input bekleniyor
_waiting_for_reply: dict[int, str] = {}  # user_id -> run_id (reply bekleyenler)


def build_cta_keyboard(cta: dict | None, run_id: str) -> InlineKeyboardMarkup | None:
    """
    CTA'dan inline keyboard oluştur.
    
    Args:
        cta: CTA dict (None olabilir)
        run_id: Story run ID'si
    
    Returns:
        InlineKeyboardMarkup veya None (cta yoksa/boşsa)
    """
    # cta hiç yoksa / null ise: buton yok, crash yok
    if not cta:
        return None
    
    question_id = cta.get("question_id")
    options = cta.get("options") or []
    
    # options boşsa da buton yaratma
    if not question_id or not options:
        return None
    
    rows = []
    for opt in options:
        choice_id = opt.get("id", "")
        choice_label = opt.get("label", "")
        # Callback data: term|{question_id}|{choice_id}
        rows.append([
            InlineKeyboardButton(
                text=choice_label,
                callback_data=f"term|{question_id}|{choice_id}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=rows) if rows else None

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
    
    # Deep link: /start terminal → /terminal çalıştır
    if start_param == "terminal":
        await cmd_terminal(message)
        return
    
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
            # Onboarding mesajı
            onboarding_message = (
                f"✨ {bold('Hoş geldin, vatandaş.')}\n\n"
                f"Bu sistem seni sömürmek için değil, seni eski sistemden kurtarmak için var.\n\n"
                f"NasipQuest = Görev yap → NCR kazan → Marketplace'te sat → Gerçek iş.\n\n"
                f"Eski sistem: Sen çalış, patron kazansın.\n"
                f"Yeni sistem: Sen üret, sen kazan.\n\n"
                f"---\n\n"
                f"📋 {bold('Nasıl Çalışır?')}\n\n"
                f"1️⃣ Her gün 3 görev gelir:\n"
                f"   • 💸 MONEY (Para/İş)\n"
                f"   • 🧠 SKILL (Öğrenme/Üretim)\n"
                f"   • 🧭 INTEGRITY (Dürüstlük/Şeffaflık)\n\n"
                f"2️⃣ Görevleri tamamla → NCR + XP kazan\n\n"
                f"3️⃣ Kaliteli içerik üret → Marketplace'e düşer\n\n"
                f"4️⃣ KOBİ'ler senin içeriğini satın alır → Sen kazanırsın\n\n"
                f"5️⃣ Treasury şişer → Sistem büyür\n\n"
                f"Basit. Gerçek.\n\n"
                f"---\n\n"
                f"🚀 {bold('İlk Adım')}\n\n"
                f"Şimdi {code('/görevler')} yaz ve bugünkü görevlerini gör.\n\n"
                f"Her görev 1-2 dakika sürer.\n"
                f"Dürüst ol, gerçek ol.\n\n"
                f"Başla: {code('/görevler')}"
            )
            await message.answer(onboarding_message, parse_mode="Markdown")
        else:
            await message.answer("❌ Bağlantı hatası. Lütfen tekrar dene.")
    except Exception as e:
        await message.answer(f"❌ Hata: {str(e)}")


@router.message(Command("panel", "web"))
async def cmd_panel(message: Message):
    """Web paneline yönlendir."""
    from nasipquest_bot.config import config
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    
    telegram_user_id = message.from_user.id
    
    # Web panel URL'i oluştur (telegram_user_id parametresi ile)
    panel_url = f"{config.FRONTEND_URL}/onboarding?telegram_user_id={telegram_user_id}"
    
    text = (
        f"🌐 {bold('Web Paneli')}\n\n"
        f"Quest geçmişini, marketplace'i ve dashboard'u web panelinde görüntüleyebilirsin.\n\n"
        f"Otomatik giriş için aşağıdaki butona tıkla:"
    )
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="🚀 Web Paneline Git",
        url=panel_url
    )
    
    await message.answer(text, parse_mode="Markdown", reply_markup=keyboard.as_markup())


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


@router.message(Command("terminal"))
async def cmd_terminal(message: Message):
    """
    /terminal - StoryQuest Terminal'i başlat
    
    Yeni bir film/story run başlatır.
    Grup/kanallarda çalışmaz, bot'a yönlendirir.
    """
    # Grup/kanal kontrolü - sadece private chat'te çalışsın
    if message.chat.type in ("group", "supergroup", "channel"):
        bot_username = (await message.bot.get_me()).username
        await message.answer(
            f"🎬 *SeferVerse Terminal*\n\n"
            f"Hikayeyi özel sohbette oynamalısın.\n\n"
            f"👉 [@{bot_username}](https://t.me/{bot_username}?start=terminal) ile başla!",
            parse_mode="Markdown",
        )
        return
    
    telegram_user_id = message.from_user.id
    
    try:
        # 🎨 Loading göstergesi
        await message.answer("🎨 *SeferVerse Terminal başlatılıyor...*\n_AI dünyayı inşa ediyor._", parse_mode="Markdown")
        await message.bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")

        # StoryQuest Engine'e bağlan ve terminal başlat
        user = message.from_user
        
        # Profil fotoğrafı URL'ini almaya çalış (opsiyonel - şimdilik es geçiyoruz veya implemente ediyoruz)
        # user_photo_url = ... 
        
        result = await storyquest_client.start_terminal(
            telegram_user_id=telegram_user_id,
            user_display_name=user.full_name,
            user_username=user.username,
            seed=2025,  # Default seed
        )
        
        # DEBUG LOG
        import json
        import logging
        logger = logging.getLogger(__name__)
        logger.info("=" * 50)
        logger.info("RAW RESPONSE: %s", json.dumps(result, indent=2, ensure_ascii=False))
        raw_file_url = result.get("file_url")
        logger.info("file_url value: %s", repr(raw_file_url))
        logger.info("=" * 50)
        
        # Response'dan bilgileri al
        run_id = result.get("run_id")
        caption = result.get("caption", "") or "..."
        
        # file_url kontrolü: Sadece HTTP/HTTPS URL'leri kabul et (local path'leri reddet)
        file_url = None
        if raw_file_url and isinstance(raw_file_url, str) and raw_file_url.strip():
            if raw_file_url.startswith(("http://", "https://")):
                file_url = raw_file_url
                logger.info("Valid HTTP URL: %s", file_url)
            else:
                logger.warning("file_url is not HTTP URL (local path?): %s - skipping photo", raw_file_url)
        
        cta = result.get("cta")  # None olabilir!
        
        # Run_id'yi sakla (callback data limiti için)
        if run_id:
            _storyquest_runs[telegram_user_id] = run_id
        
        # CTA'dan keyboard oluştur (güvenli)
        keyboard = build_cta_keyboard(cta, run_id) if run_id else None
        
        # CTA varsa question'ı ekle
        text = f"{bold('🎬 StoryQuest Terminal')}\n\n"
        text += f"{caption}\n\n"
        
        if cta and cta.get("question"):
            text += f"{bold(cta.get('question'))}\n\n"
        
        # CTA yoksa ending/epilog mesajı
        if not cta:
            text += "Yeni bir hikaye başlatmak için /terminal komutunu kullan."
        
        # Foto/video varsa onu gönder, yoksa text mesaj
        # file_url kontrolü: None, boş string veya geçersiz URL kontrolü
        if file_url and isinstance(file_url, str) and file_url.strip() and file_url.startswith(("http://", "https://")):
            logger.info("Sending photo with file_url: %s", file_url)
            try:
                await message.answer_photo(
                    photo=file_url,
                    caption=text,
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                )
            except Exception as photo_error:
                logger.error("Photo send error: %s", str(photo_error))
                # Foto gönderme başarısız olursa text mesaj gönder
                await message.answer(
                    text,
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                )
        else:
            logger.info("No valid file_url (value: %s), sending text message", repr(file_url))
            await message.answer(
                text,
                parse_mode="Markdown",
                reply_markup=keyboard,
            )
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Terminal error: %s", str(e), exc_info=True)
        await message.answer(f"❌ Hata: {str(e)}")


@router.callback_query(F.data.startswith("term|"))
async def handle_terminal_choice(callback: CallbackQuery):
    """
    Terminal choice callback handler.
    
    Callback data format: term|{question_id}|{choice_id}
    Run_id saklı dict'ten alınır.
    """
    try:
        telegram_user_id = callback.from_user.id
        
        # Run_id'yi saklı dict'ten al
        run_id = _storyquest_runs.get(telegram_user_id)
        if not run_id:
            await callback.answer("❌ Hikaye oturumu bulunamadı. /terminal ile yeniden başlat.", show_alert=True)
            return
        
        # Callback data'yı parse et
        # Format: term|{question_id}|{choice_id}
        if "|" not in callback.data:
            await callback.answer("❌ Geçersiz seçim.", show_alert=True)
            return
        
        parts = callback.data.split("|")
        if len(parts) < 3:
            await callback.answer("❌ Geçersiz seçim.", show_alert=True)
            return
        
        question_id = parts[1]
        choice_id = parts[2]
        
        # 🎨 Loading göstergesi
        await callback.answer("🎨 Sahne oluşturuluyor...", show_alert=False)
        
        # Geçici mesaj gönder
        loading_msg = await callback.message.edit_caption(
            caption="🎨 *Sahne oluşturuluyor...*\n_AI sanatçısı fırçasını kullanıyor._",
            parse_mode="Markdown"
        ) if callback.message.caption else await callback.message.edit_text(
            text="🎨 *Sahne oluşturuluyor...*\n_AI sanatçısı fırçasını kullanıyor._",
            parse_mode="Markdown"
        )
        
        # Chat action (typing/upload_photo)
        await callback.message.bot.send_chat_action(
            chat_id=callback.message.chat.id, 
            action="upload_photo"
        )
        
        # StoryQuest Engine'e seçim gönder
        result = await storyquest_client.make_choice(
            run_id=run_id,
            question_id=question_id,
            choice_id=choice_id,
        )
        
        # Response'dan bilgileri al
        caption = result.get("caption", "") or "..."
        # Escape karakterlerini düzelt
        if isinstance(caption, str):
            caption = caption.replace("\\n", "\n").replace("\\.",".")
        
        file_url = result.get("file_url")  # Doğru field adı: file_url
        cta = result.get("cta")  # None olabilir!
        is_final = result.get("is_final", False)
        ending = result.get("ending")
        reward = result.get("reward", {})
        
        # Ending'den reward ve badge al (eğer varsa)
        if ending and isinstance(ending, dict):
            # Ending caption'ı kullan (daha detaylı)
            ending_caption = ending.get("caption", "")
            if ending_caption:
                caption = ending_caption.replace("\\n", "\n").replace("\\.",".")
            # Ending'deki reward'ı kullan
            if ending.get("reward"):
                reward = ending["reward"]
        
        # Mesaj formatla
        text = f"{caption}\n\n"
        
        if is_final:
            # Hikaye bitti
            text += f"{bold('🎬 Hikaye Tamamlandı!')}\n\n"
            if reward:
                nasip = reward.get("nasip", 0)
                xp = reward.get("xp", 0)
                badge = reward.get("badge", "") or (ending.get("badge") if ending else "")
                if nasip > 0 or xp > 0 or badge:
                    text += f"🎁 *Ödüller:*\n"
                    if nasip > 0:
                        text += f"  • 💫 {nasip} Nasip\n"
                    if xp > 0:
                        text += f"  • ⭐ {xp} XP\n"
                    if badge:
                        text += f"  • 🏅 Badge: {badge}\n"
                    text += "\n"
            text += "Yeni bir hikaye başlatmak için /terminal komutunu kullan."
            
            # file_url varsa foto gönder, yoksa text edit
            # file_url kontrolü: None, boş string veya geçersiz URL kontrolü
            if file_url and isinstance(file_url, str) and file_url.strip() and file_url.startswith(("http://", "https://")):
                try:
                    await callback.message.delete()
                    await callback.message.answer_photo(
                        photo=file_url,
                        caption=text,
                        parse_mode="Markdown",
                    )
                except Exception as photo_error:
                    logger.error("Photo send error: %s", str(photo_error))
                    # Foto gönderme başarısız olursa text edit
                    await callback.message.edit_text(
                        text,
                        parse_mode="Markdown",
                    )
            else:
                await callback.message.edit_text(
                    text,
                    parse_mode="Markdown",
                )
            await callback.answer("✅ Hikaye tamamlandı!")
        else:
            # Devam ediyor - CTA varsa question ekle
            if cta and cta.get("question"):
                text += f"{bold(cta.get('question'))}\n\n"
            
            # Run_id'yi güncelle (yeni step için)
            _storyquest_runs[telegram_user_id] = run_id
            
            # CTA'dan keyboard oluştur (güvenli)
            keyboard = build_cta_keyboard(cta, run_id)
            
            # CTA yoksa ending mesajı
            if not cta:
                text += "Yeni bir hikaye başlatmak için /terminal komutunu kullan."
            
            # file_url varsa foto gönder, yoksa text edit
            # file_url kontrolü: None, boş string veya geçersiz URL kontrolü
            if file_url and isinstance(file_url, str) and file_url.strip() and file_url.startswith(("http://", "https://")):
                try:
                    await callback.message.delete()
                    await callback.message.answer_photo(
                        photo=file_url,
                        caption=text,
                        parse_mode="Markdown",
                        reply_markup=keyboard,
                    )
                except Exception as photo_error:
                    logger.error("Photo send error: %s", str(photo_error))
                    # Foto gönderme başarısız olursa text edit
                    await callback.message.edit_text(
                        text,
                        parse_mode="Markdown",
                        reply_markup=keyboard,
                    )
            else:
                await callback.message.edit_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=keyboard,
                )
            await callback.answer("✅ Seçim yapıldı!")
        
    except Exception as e:
        await callback.answer(f"❌ Hata: {str(e)}", show_alert=True)


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


# ═══════════════════════════════════════════════════════════════════════════════
# BROADCAST / GRUP YAYIN KOMUTLARI
# ═══════════════════════════════════════════════════════════════════════════════

def get_admin_user_ids() -> list[int]:
    """Admin user ID'lerini .env'den al."""
    import os
    admin_str = os.getenv("ADMIN_USER_IDS", "")
    if not admin_str:
        return []
    return [int(x.strip()) for x in admin_str.split(",") if x.strip().isdigit()]


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    """
    /broadcast <mesaj> - Gruba/kanala yayın yap
    
    Sadece adminler kullanabilir.
    Örnek: /broadcast 🎬 Yeni SeferVerse bölümü yayında!
    """
    # Admin kontrolü
    admin_ids = get_admin_user_ids()
    if message.from_user.id not in admin_ids:
        await message.answer(f"❌ Bu komutu kullanma yetkiniz yok. (ID: {message.from_user.id})")
        return
    
    # Mesajı al
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("❌ Kullanım: /broadcast <mesaj>")
        return
    
    # Grup/kanal ID'sini al
    channel_id = config.BROADCAST_CHANNEL_ID or config.BROADCAST_GROUP_ID
    if not channel_id:
        await message.answer("❌ Broadcast hedefi ayarlanmamış. .env'de BROADCAST_CHANNEL_ID veya BROADCAST_GROUP_ID ayarlayın.")
        return
    
    try:
        bot = message.bot
        
        await bot.send_message(
            chat_id=channel_id,
            text=text,
            parse_mode="Markdown",
        )
        await message.answer(f"✅ Mesaj gönderildi: {channel_id}")
    except Exception as e:
        await message.answer(f"❌ Gönderim hatası: {str(e)}")


@router.message(Command("broadcast_seferverse"))
async def cmd_broadcast_seferverse(message: Message):
    """
    /broadcast_seferverse - SeferVerse intro'sunu gruba yayınla
    
    Sadece adminler kullanabilir.
    """
    # Admin kontrolü
    admin_ids = get_admin_user_ids()
    if message.from_user.id not in admin_ids:
        await message.answer(f"❌ Bu komutu kullanma yetkiniz yok. (ID: {message.from_user.id})")
        return
    
    # Bot username'i al
    bot_info = await message.bot.get_me()
    bot_username = bot_info.username
    
    # SeferVerse manifesto
    seferverse_text = f"""🌌 *SeferVerse*

Ardında yanmış toprak.
Önünde adı bile olmayan bir dünya.

Siyah kumlar, sanki geçmişin küllerinden yapılmış gibi
sessizce uzanıyor ufka doğru.

Gökyüzünde ay yok. Güneş yok.
Sadece devasa bir *Siyah Kare* var.

Çünkü geri dönmek diye bir seçenek kalmadı.
Kaderi yazan sensin.

Her SEFER, bilinmeyene atılan ilk adımdır.
Ve sen o adımı zaten attın.

━━━━━━━━━━━━━━━━━━━━━━
🎬 [Hikayeye başla](https://t.me/{bot_username}?start=terminal)
━━━━━━━━━━━━━━━━━━━━━━

#SeferVerse #SiyahKare #KodunÖtesi #Nasip"""
    
    channel_id = config.BROADCAST_CHANNEL_ID or config.BROADCAST_GROUP_ID
    if not channel_id:
        await message.answer("❌ Broadcast hedefi ayarlanmamış.")
        return
    
    try:
        bot = message.bot
        
        # Önce görsel üret/getir
        result = await storyquest_client.start_terminal(
            telegram_user_id=0,  # System broadcast
            seed=2025,
        )
        file_url = result.get("file_url")
        
        if file_url and file_url.startswith("http"):
            await bot.send_photo(
                chat_id=channel_id,
                photo=file_url,
                caption=seferverse_text,
                parse_mode="Markdown",
            )
        else:
            await bot.send_message(
                chat_id=channel_id,
                text=seferverse_text,
                parse_mode="Markdown",
            )
        
        await message.answer(f"✅ SeferVerse yayını gönderildi: {channel_id}")
    except Exception as e:
        await message.answer(f"❌ Gönderim hatası: {str(e)}")


@router.message(Command("export_ig"))
async def cmd_export_ig(message: Message):
    """
    /export_ig - SeferVerse içeriğini Instagram için export et
    
    Görsel URL + Caption + Hashtag verir, manuel paylaşım için.
    """
    # Admin kontrolü
    admin_ids = get_admin_user_ids()
    if message.from_user.id not in admin_ids:
        await message.answer("❌ Bu komutu kullanma yetkiniz yok.")
        return
    
    await message.answer("🎨 Instagram içeriği hazırlanıyor...")
    
    try:
        # Görsel üret
        result = await storyquest_client.start_terminal(
            telegram_user_id=0,
            seed=2025,
        )
        file_url = result.get("file_url", "")
        
        # Instagram caption
        ig_caption = """🌌 SeferVerse

Ardında yanmış toprak.
Önünde adı bile olmayan bir dünya.

Siyah kumlar, sanki geçmişin küllerinden yapılmış gibi sessizce uzanıyor ufka doğru.

Gökyüzünde ay yok. Güneş yok.
Sadece devasa bir Siyah Kare var.

Çünkü geri dönmek diye bir seçenek kalmadı.
Kaderi yazan sensin.

Her SEFER, bilinmeyene atılan ilk adımdır.
Ve sen o adımı zaten attın.

🎬 Hikayeye katıl: Bio'daki link

#SeferVerse #SiyahKare #KodunÖtesi #Nasip #InteractiveStory #AIArt #DigitalArt #TurkishSciFi #BilimKurgu #DijitalSanat #Hikaye #SeçimliMacera"""

        # Export mesajı
        export_text = f"""📸 *Instagram Export*

━━━━━━━━━━━━━━━━━━━━━━
🖼️ *Görsel URL:*
`{file_url}`

━━━━━━━━━━━━━━━━━━━━━━
📝 *Caption (kopyala):*
━━━━━━━━━━━━━━━━━━━━━━"""

        await message.answer(export_text, parse_mode="Markdown")
        await message.answer(ig_caption)  # Plain text - kolay kopyalama için
        
        # Görseli de gönder (kolay indirme için)
        if file_url and file_url.startswith("http"):
            await message.answer_photo(
                photo=file_url,
                caption="⬆️ Instagram için görsel (uzun bas → kaydet)"
            )
    
    except Exception as e:
        await message.answer(f"❌ Export hatası: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# MEKTUP CEVABI - GPT Puanlama
# ═══════════════════════════════════════════════════════════════════════════════

@router.callback_query(F.data.startswith("term|") & F.data.endswith("|write_reply"))
async def handle_write_reply_choice(callback: CallbackQuery):
    """
    "Cevap yaz" seçimi - kullanıcıyı text input moduna al.
    """
    telegram_user_id = callback.from_user.id
    run_id = _storyquest_runs.get(telegram_user_id)
    
    if not run_id:
        await callback.answer("❌ Hikaye oturumu bulunamadı. /terminal ile başla.", show_alert=True)
        return
    
    # Kullanıcıyı "cevap bekleniyor" moduna al
    _waiting_for_reply[telegram_user_id] = run_id
    
    await callback.message.edit_text(
        f"✍️ *Mektuba Cevap Yaz*\n\n"
        f"Kalem elinde, kağıt önünde.\n"
        f"Yıllardır söyleyemediklerini şimdi yazacaksın.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 Cevabını yaz ve gönder.\n"
        f"(En az 20 karakter)\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💡 _İpucu: Ne kadar samimi ve içten yazarsan,_\n"
        f"_hikayenin sonu o kadar farklı olacak._",
        parse_mode="Markdown",
    )
    await callback.answer("✍️ Cevabını yaz...")


@router.message(F.text & ~F.text.startswith("/"))
async def handle_text_reply(message: Message):
    """
    Kullanıcının yazdığı mektup cevabını işle.
    """
    telegram_user_id = message.from_user.id
    
    # Bu kullanıcı cevap bekliyor mu?
    if telegram_user_id not in _waiting_for_reply:
        return  # Normal mesaj, ignore et
    
    run_id = _waiting_for_reply[telegram_user_id]
    user_reply = message.text.strip()
    
    # Çok kısa cevap kontrolü
    if len(user_reply) < 20:
        await message.answer(
            "📝 Cevabın çok kısa. En az 20 karakter yaz.\n\n"
            "_Duygularını ifade et, ne hissediyorsun?_",
            parse_mode="Markdown",
        )
        return
    
    # Kullanıcıyı listeden çıkar
    del _waiting_for_reply[telegram_user_id]
    
    # GPT'ye gönder ve puanla
    await message.answer("🔮 Cevabın değerlendiriliyor...")
    
    try:
        result = await storyquest_client.score_reply(
            run_id=run_id,
            user_reply=user_reply,
        )
        
        toplam = result.get("toplam", 50)
        samimiyet = result.get("samimiyet", 0)
        empati = result.get("empati", 0)
        karar = result.get("karar", 0)
        yorum = result.get("yorum", "")
        ending_type = result.get("ending_type", "journey")
        reward = result.get("reward", {})
        
        # Puan görseli
        if toplam >= 80:
            emoji = "💖"
            rating = "Yürekten"
        elif toplam >= 60:
            emoji = "💝"
            rating = "Samimi"
        elif toplam >= 40:
            emoji = "📝"
            rating = "Normal"
        else:
            emoji = "❄️"
            rating = "Soğuk"
        
        # Sonuç mesajı
        score_text = f"""📊 *Cevap Değerlendirmesi*

{emoji} *{rating}* — {toplam}/100 puan

━━━━━━━━━━━━━━━━━━━━━━
💗 Samimiyet: {samimiyet}/40
🤝 Empati: {empati}/30
🎯 Karar: {karar}/30
━━━━━━━━━━━━━━━━━━━━━━

_{yorum}_

"""
        
        # Ödül
        if reward:
            nasip = reward.get("nasip", 0)
            xp = reward.get("xp", 0)
            badge = reward.get("badge")
            if nasip > 0 or xp > 0:
                score_text += f"\n🎁 *Ödül:*"
                if nasip > 0:
                    score_text += f" 💫 {nasip} Nasip"
                if xp > 0:
                    score_text += f" ⭐ {xp} XP"
                if badge:
                    score_text += f"\n🏅 Badge: {badge}"
        
        await message.answer(score_text, parse_mode="Markdown")
        
        # Şimdi ending'i göster
        # Ending'e göre seçim yap
        ending_choice_id = f"gpt_{ending_type}"
        
        # Normal choice flow'una gir
        choice_result = await storyquest_client.make_choice(
            run_id=run_id,
            question_id="sv_terminal_q3_reply",
            choice_id=ending_choice_id if ending_type != "journey" else "go_border",
        )
        
        # Final mesajı göster
        caption = choice_result.get("caption", "")
        if isinstance(caption, str):
            caption = caption.replace("\\n", "\n")
        
        ending_text = f"{caption}\n\n{bold('🎬 Hikaye Tamamlandı!')}"
        ending_text += "\n\nYeni bir hikaye başlatmak için /terminal komutunu kullan."
        
        file_url = choice_result.get("file_url")
        if file_url and file_url.startswith("http"):
            await message.answer_photo(
                photo=file_url,
                caption=ending_text,
                parse_mode="Markdown",
            )
        else:
            await message.answer(ending_text, parse_mode="Markdown")
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error("Reply scoring error: %s", str(e), exc_info=True)
        await message.answer(f"❌ Değerlendirme hatası: {str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
# ENGAGING MESAJLAR - Admin Gruplarına Otomatik Mesajlar
# ═══════════════════════════════════════════════════════════════════════════════

def get_engaging_messages() -> list[dict]:
    """
    Engaging mesaj pool'u.
    Her mesaj: {"text": "...", "type": "quest|story|motivation|event"}
    """
    import random
    from datetime import datetime
    
    bot_username = "nasipquest_bot"  # Bot username (runtime'da güncellenecek)
    
    messages = [
        # Quest hatırlatmaları
        {
            "text": f"""🎯 *Günlük Görevler Hazır!*

Bugünün quest'lerini tamamla, NCR kazan!

💸 MONEY — Para/İş görevleri
🧠 SKILL — Öğrenme/Üretim görevleri  
🧭 INTEGRITY — Dürüstlük/Şeffaflık görevleri

━━━━━━━━━━━━━━━━━━━━━━
👉 [Görevleri Gör](https://t.me/{bot_username}?start=start)
━━━━━━━━━━━━━━━━━━━━━━

#NasipQuest #Görevler #NCR""",
            "type": "quest"
        },
        {
            "text": f"""📋 *Bugün Ne Yaptın?*

Her gün 3 görev gelir.
Her görev 1-2 dakika sürer.
Her görev NCR + XP kazandırır.

Basit. Gerçek.

━━━━━━━━━━━━━━━━━━━━━━
🎯 [Görevleri Gör](https://t.me/{bot_username}?start=start)
━━━━━━━━━━━━━━━━━━━━━━

#NasipQuest #GünlükGörev""",
            "type": "quest"
        },
        
        # SeferVerse hikaye güncellemeleri
        {
            "text": f"""🌌 *SeferVerse - Yeni Bölüm*

Ardında yanmış toprak.
Önünde adı bile olmayan bir dünya.

Siyah kumlar, sanki geçmişin küllerinden yapılmış gibi
sessizce uzanıyor ufka doğru.

Gökyüzünde ay yok. Güneş yok.
Sadece devasa bir *Siyah Kare* var.

Çünkü geri dönmek diye bir seçenek kalmadı.
Kaderi yazan sensin.

━━━━━━━━━━━━━━━━━━━━━━
🎬 [Hikayeye Başla](https://t.me/{bot_username}?start=terminal)
━━━━━━━━━━━━━━━━━━━━━━

#SeferVerse #SiyahKare #KodunÖtesi""",
            "type": "story"
        },
        {
            "text": f"""🎬 *SeferVerse Terminal*

Her SEFER, bilinmeyene atılan ilk adımdır.
Ve sen o adımı zaten attın.

━━━━━━━━━━━━━━━━━━━━━━
👉 [Terminal'i Aç](https://t.me/{bot_username}?start=terminal)
━━━━━━━━━━━━━━━━━━━━━━

#SeferVerse #InteractiveStory""",
            "type": "story"
        },
        
        # Motivasyon mesajları
        {
            "text": f"""💪 *Eski Sistem vs Yeni Sistem*

❌ Eski sistem: Sen çalış, patron kazansın.
✅ Yeni sistem: Sen üret, sen kazan.

━━━━━━━━━━━━━━━━━━━━━━
🚀 [NasipQuest'e Katıl](https://t.me/{bot_username}?start=start)
━━━━━━━━━━━━━━━━━━━━━━

#NasipQuest #YeniSistem""",
            "type": "motivation"
        },
        {
            "text": f"""🎯 *NasipQuest Mantığı*

1️⃣ Görev yap → NCR kazan
2️⃣ Marketplace'te sat → Gerçek iş
3️⃣ Treasury şişer → Sistem büyür

Basit. Gerçek.

━━━━━━━━━━━━━━━━━━━━━━
👉 [Başla](https://t.me/{bot_username}?start=start)
━━━━━━━━━━━━━━━━━━━━━━

#NasipQuest #Ekonomi""",
            "type": "motivation"
        },
        {
            "text": f"""🌟 *Dürüst Ol, Gerçek Ol*

Kaliteli içerik üret → Marketplace'e düşer
KOBİ'ler satın alır → Sen kazanırsın

━━━━━━━━━━━━━━━━━━━━━━
📋 [Görevleri Gör](https://t.me/{bot_username}?start=start)
━━━━━━━━━━━━━━━━━━━━━━

#NasipQuest #Dürüstlük""",
            "type": "motivation"
        },
        
        # Event duyuruları
        {
            "text": f"""🔥 *Nasip Friday*

Her Cuma özel event!
XP multiplier + NCR bonus.

━━━━━━━━━━━━━━━━━━━━━━
🎯 [Katıl](https://t.me/{bot_username}?start=start)
━━━━━━━━━━━━━━━━━━━━━━

#NasipFriday #Event""",
            "type": "event"
        },
        {
            "text": f"""⚔️ *Quest War*

Haftalık liderlik yarışması!
En çok quest tamamlayan kazanır.

━━━━━━━━━━━━━━━━━━━━━━
🏆 [Leaderboard](https://t.me/{bot_username}?start=start)
━━━━━━━━━━━━━━━━━━━━━━

#QuestWar #Yarışma""",
            "type": "event"
        },
    ]
    
    return messages


def get_admin_group_ids() -> list[str]:
    """Admin grup ID'lerini .env'den al."""
    admin_groups_str = config.ADMIN_GROUPS
    if not admin_groups_str:
        return []
    return [gid.strip() for gid in admin_groups_str.split(",") if gid.strip()]


async def check_bot_is_admin(bot, chat_id: str) -> bool:
    """
    Botun bu grupta admin olup olmadığını kontrol et.
    """
    try:
        from aiogram.types import ChatMemberStatus
        member = await bot.get_chat_member(chat_id=chat_id, user_id=(await bot.get_me()).id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.CREATOR)
    except Exception:
        return False


@router.message(Command("engage_groups"))
async def cmd_engage_groups(message: Message):
    """
    /engage_groups - Admin olduğu gruplara engaging mesaj gönder
    
    Sadece adminler kullanabilir.
    """
    # Admin kontrolü
    admin_ids = get_admin_user_ids()
    if message.from_user.id not in admin_ids:
        await message.answer(f"❌ Bu komutu kullanma yetkiniz yok. (ID: {message.from_user.id})")
        return
    
    await message.answer("🔄 Gruplara engaging mesajlar gönderiliyor...")
    
    # Bot username'i al
    bot_info = await message.bot.get_me()
    bot_username = bot_info.username
    
    # Mesaj pool'undan rastgele seç
    import random
    messages = get_engaging_messages()
    # Bot username'i güncelle
    for msg in messages:
        msg["text"] = msg["text"].replace("nasipquest_bot", bot_username)
    
    selected_message = random.choice(messages)
    
    # Admin grup ID'lerini al
    admin_group_ids = get_admin_group_ids()
    
    if not admin_group_ids:
        await message.answer(
            "❌ Admin grup ID'leri ayarlanmamış.\n\n"
            ".env dosyasına şunu ekle:\n"
            "`ADMIN_GROUPS=-1001234567890,-1009876543210`\n\n"
            "Grup ID'lerini öğrenmek için @userinfobot'u gruba ekle."
        )
        return
    
    # Her gruba mesaj gönder
    success_count = 0
    fail_count = 0
    results = []
    
    for group_id in admin_group_ids:
        try:
            # Admin kontrolü
            is_admin = await check_bot_is_admin(message.bot, group_id)
            if not is_admin:
                results.append(f"⚠️ {group_id}: Bot admin değil")
                fail_count += 1
                continue
            
            # Mesaj gönder
            await message.bot.send_message(
                chat_id=group_id,
                text=selected_message["text"],
                parse_mode="Markdown",
                disable_web_page_preview=False,
            )
            results.append(f"✅ {group_id}: Gönderildi")
            success_count += 1
            
            # Rate limit için kısa bekleme
            import asyncio
            await asyncio.sleep(1)
            
        except Exception as e:
            results.append(f"❌ {group_id}: {str(e)}")
            fail_count += 1
    
    # Sonuç raporu
    report = f"""📊 *Engaging Mesaj Raporu*

✅ Başarılı: {success_count}
❌ Başarısız: {fail_count}
📝 Mesaj Tipi: {selected_message['type']}

━━━━━━━━━━━━━━━━━━━━━━
*Detaylar:*
"""
    for result in results:
        report += f"{result}\n"
    
    await message.answer(report, parse_mode="Markdown")


@router.message(Command("list_admin_groups"))
async def cmd_list_admin_groups(message: Message):
    """
    /list_admin_groups - Botun admin olduğu grupları listele
    
    Sadece adminler kullanabilir.
    """
    # Admin kontrolü
    admin_ids = get_admin_user_ids()
    if message.from_user.id not in admin_ids:
        await message.answer(f"❌ Bu komutu kullanma yetkiniz yok. (ID: {message.from_user.id})")
        return
    
    admin_group_ids = get_admin_group_ids()
    
    if not admin_group_ids:
        await message.answer(
            "❌ Admin grup ID'leri ayarlanmamış.\n\n"
            ".env dosyasına şunu ekle:\n"
            "`ADMIN_GROUPS=-1001234567890,-1009876543210`"
        )
        return
    
    # Her grubun bilgisini al
    report = f"📋 *Admin Grupları*\n\n"
    
    for group_id in admin_group_ids:
        try:
            chat = await message.bot.get_chat(chat_id=group_id)
            is_admin = await check_bot_is_admin(message.bot, group_id)
            status = "✅ Admin" if is_admin else "❌ Admin değil"
            
            report += f"{status}\n"
            report += f"ID: `{group_id}`\n"
            report += f"İsim: {chat.title or 'N/A'}\n"
            report += f"Tip: {chat.type}\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            
        except Exception as e:
            report += f"❌ {group_id}: {str(e)}\n"
            report += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    await message.answer(report, parse_mode="Markdown")
