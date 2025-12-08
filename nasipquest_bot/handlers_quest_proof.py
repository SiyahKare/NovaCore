"""
NasipQuest Bot - Quest Proof Text Handler
Vatandaş text gönderdiğinde aktif quest'e bağla
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.markdown import bold, code

from .api_client import api_client

router = Router(name="quest_proof")


# User state tracking (MVP: basit dict, ileride Redis/DB)
_user_active_quest: dict[int, str] = {}  # telegram_user_id -> quest_uuid


@router.message(F.text & ~F.text.startswith("/"))
async def handle_proof_text(message: Message):
    """
    Kullanıcı text gönderdiğinde aktif quest'e bağla.
    
    MVP: Bugün için ASSIGNED durumunda olan ilk quest'e bağla.
    """
    telegram_user_id = message.from_user.id
    
    # Eğer kullanıcının aktif quest'i varsa onu kullan
    quest_uuid = _user_active_quest.get(telegram_user_id)
    
    if not quest_uuid:
        # Bir sonraki atanabilir quest'i bul
        try:
            active_quest = await api_client.get_next_assignable_quest(telegram_user_id)
            
            if not active_quest:
                await message.answer(
                    f"{bold('📋 Bugün için açık görevin yok.')}\n\n"
                    f"Yeni görev almak için {code('/görevler')} yaz."
                )
                return
            
            quest_uuid = active_quest.get("quest_uuid")
            if quest_uuid:
                _user_active_quest[telegram_user_id] = quest_uuid
        except Exception as e:
            await message.answer(
                f"{bold('⚠️ Görev bulunamadı.')}\n\n"
                f"Hata: {code(str(e))}\n\n"
                f"Yeni görev almak için {code('/görevler')} yaz."
            )
            return
    
    if not quest_uuid:
        await message.answer(
            f"{bold('📋 Bugün için açık görevin yok.')}\n\n"
            f"Yeni görev almak için {code('/görevler')} yaz."
        )
        return
    
    # Proof gönder
    try:
        result = await api_client.submit_quest(
            telegram_user_id=telegram_user_id,
            quest_uuid=quest_uuid,
            proof_type="text",
            proof_payload_ref=f"telegram_msg_{message.message_id}",
            proof_content=message.text,
            message_id=str(message.message_id),
            ai_score=None,  # Backend'de AI scoring yapılacak
        )
        
        # Aktif quest'i temizle (bir sonraki text için yeni quest alınacak)
        _user_active_quest.pop(telegram_user_id, None)
        
        # Response'dan bilgi al
        status = result.get("status", "unknown")
        final_reward_ncr = result.get("final_reward_ncr")
        final_reward_xp = result.get("final_reward_xp")
        final_score = result.get("final_score")
        
        if status == "approved":
            text = f"{bold('✅ Gönderin Onaylandı!')}\n\n"
            if final_reward_ncr and final_reward_xp:
                text += f"💰 Ödül: +{code(str(final_reward_xp))} XP, +{code(str(final_reward_ncr))} NCR\n"
            if final_score:
                text += f"⭐ Kalite Skoru: {code(str(final_score))}\n"
            text += f"\n🎉 Tebrikler! Quest başarıyla tamamlandı."
        elif status == "submitted":
            text = f"{bold('⏳ Gönderin Kaydedildi')}\n\n"
            text += "Quest'in onaylanması bekleniyor. Kısa süre içinde sonuç alacaksın!"
        elif status == "under_review":
            text = f"{bold('🔍 Gönderin İncelemede')}\n\n"
            text += "Quest DAO tarafından inceleniyor. Sonuç yakında bildirilecek."
        elif status == "rejected":
            text = f"{bold('🚫 Gönderin Reddedildi')}\n\n"
            text += "Bu gönderi sistem tarafından reddedildi. Başka bir giriş yapmayı deneyebilirsin."
        else:
            text = f"{bold('📋 Quest Durumu')}\n\n"
            text += f"Durum: {code(status)}"
        
        await message.answer(text, parse_mode="Markdown")
    
    except Exception as e:
        error_msg = str(e)
        
        # AbuseGuard cooldown hatası
        if "cooldown" in error_msg.lower() or "abuse" in error_msg.lower():
            await message.answer(
                f"{bold('🚫 Hesabın Cooldown\'da')}\n\n"
                f"Risk skorun yüksek olduğu için şu an görev tamamlayamazsın.\n"
                f"Lütfen daha sonra tekrar dene."
            )
        # Quest expired
        elif "expired" in error_msg.lower():
            await message.answer(
                f"{bold('⏰ Quest Süresi Doldu')}\n\n"
                f"Bu quest'in süresi dolmuş. Yeni görev almak için {code('/görevler')} yaz."
            )
            _user_active_quest.pop(telegram_user_id, None)
        # Quest not found
        elif "not found" in error_msg.lower():
            await message.answer(
                f"{bold('❌ Quest Bulunamadı')}\n\n"
                f"Bu quest artık mevcut değil. Yeni görev almak için {code('/görevler')} yaz."
            )
            _user_active_quest.pop(telegram_user_id, None)
        else:
            await message.answer(
                f"{bold('⚠️ Hata Oluştu')}\n\n"
                f"Hata: {code(error_msg)}\n\n"
                f"Tekrar denemek için {code('/görevler')} yaz."
            )
