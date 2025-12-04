# app/quests/telegram_formatter.py
"""
Telegram Bot için Quest Formatting

MVP Pack V1 görevlerini Telegram mesaj formatına çevirir.
"""
from typing import List
from .mvp_pack_v1 import QuestDefinition, QuestSlot
from .factory import RuntimeQuest


def format_daily_quests_for_telegram(quests: List[RuntimeQuest]) -> str:
    """
    Günlük quest'leri Telegram mesaj formatına çevir.
    
    Örnek çıktı:
    ```
    📌 Bugünkü NasipQuest görevlerin:

    1) 💸 MONEY
       [daily_income_snapshot]
       👉 "Bugün cebine giren/çıkan parayı tek cümleyle yaz."

    2) 🧠 SKILL
       [daily_micro_content]
       👉 "Nasip / Rızık / Gerçek temalı 1 cümlelik söz yaz."

    3) 🧭 INTEGRITY
       [swamp_story_v1]
       👉 "Seni en çok ezen anını 3-5 cümlede anlat."
    ```
    """
    from .mvp_pack_v1 import get_quest_by_id
    
    slot_emojis = {
        QuestSlot.MONEY: "💸",
        QuestSlot.SKILL: "🧠",
        QuestSlot.INTEGRITY: "🧭",
    }
    
    slot_names = {
        QuestSlot.MONEY: "MONEY",
        QuestSlot.SKILL: "SKILL",
        QuestSlot.INTEGRITY: "INTEGRITY",
    }
    
    lines = ["📌 Bugünkü NasipQuest görevlerin:\n"]
    
    for idx, quest in enumerate(quests, 1):
        quest_def = get_quest_by_id(quest.key)
        
        if quest_def:
            emoji = slot_emojis.get(quest_def.slot, "📋")
            slot_name = slot_names.get(quest_def.slot, "OTHER")
            
            lines.append(f"{idx}) {emoji} {slot_name}")
            lines.append(f"   [{quest.key}]")
            lines.append(f"   👉 {quest_def.instructions[:100]}...")  # İlk 100 karakter
            lines.append("")
        else:
            # Legacy quest
            lines.append(f"{idx}) 📋 {quest.title}")
            lines.append(f"   [{quest.key}]")
            lines.append(f"   👉 {quest.description}")
            lines.append("")
    
    return "\n".join(lines)


def format_quest_detail_for_telegram(quest: RuntimeQuest) -> str:
    """
    Tek bir quest'in detayını Telegram formatında göster.
    """
    from .mvp_pack_v1 import get_quest_by_id
    
    quest_def = get_quest_by_id(quest.key)
    
    if not quest_def:
        # Legacy quest
        return f"📋 *{quest.title}*\n\n{quest.description}\n\n💰 Ödül: {quest.base_ncr} NCR + {quest.base_xp} XP"
    
    slot_emojis = {
        QuestSlot.MONEY: "💸",
        QuestSlot.SKILL: "🧠",
        QuestSlot.INTEGRITY: "🧭",
    }
    
    emoji = slot_emojis.get(quest_def.slot, "📋")
    
    lines = [
        f"{emoji} *{quest.title}*",
        "",
        quest_def.instructions,
        "",
        f"💰 Ödül: {quest.base_ncr} NCR + {quest.base_xp} XP",
    ]
    
    if quest_def.one_time_only:
        lines.append("⚠️ Bu görev tek seferliktir.")
    
    if quest_def.requires_hitl:
        lines.append("👤 Bu görev insan moderasyonundan geçecek.")
    
    if quest_def.min_length:
        lines.append(f"📏 Minimum {quest_def.min_length} karakter gerekli.")
    
    return "\n".join(lines)

