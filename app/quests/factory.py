"""
QuestFactory - Runtime Quest Generation
MVP Pack V1 entegrasyonu ile güncellenmiş QuestFactory
"""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from dataclasses import dataclass

from .enums import QuestType
from .mvp_pack_v1 import (
    BASE_QUEST_DEFS,
    QuestSlot,
    get_daily_quest_set,
    get_quest_by_id,
    QuestDefinition,
)


@dataclass
class RuntimeQuest:
    """QuestFactory'nin runtime çıktısı."""
    uuid: str
    type: QuestType
    key: str
    title: str
    description: str
    base_ncr: float
    base_xp: int


class QuestFactory:
    """
    Quest generation factory.
    
    MVP Pack V1 entegrasyonu:
    - Her gün 3 slot (MONEY, SKILL, INTEGRITY)
    - NovaScore sinyalleri
    - AbuseGuard uyumlu
    """
    
    @staticmethod
    def generate_for_user(
        user_id: int,
        count: int = 3,
        use_mvp_pack: bool = True,
        completed_one_time_quests: Optional[List[str]] = None,
    ) -> List[RuntimeQuest]:
        """
        Kullanıcı için günlük quest seti üretir.
        
        Args:
            user_id: Kullanıcı ID
            count: Kaç quest üretilecek (MVP Pack için genelde 3)
            use_mvp_pack: MVP Pack V1 kullanılsın mı? (default: True)
            completed_one_time_quests: Tamamlanmış tek seferlik görev ID'leri
        
        Returns:
            RuntimeQuest listesi
        """
        if use_mvp_pack:
            return QuestFactory._generate_mvp_pack(user_id, completed_one_time_quests)
        else:
            return QuestFactory._generate_legacy(user_id, count)
    
    @staticmethod
    def _generate_mvp_pack(
        user_id: int,
        completed_one_time_quests: Optional[List[str]] = None,
    ) -> List[RuntimeQuest]:
        """
        MVP Pack V1 ile günlük quest seti üret.
        
        Her gün 3 slot:
        - MONEY
        - SKILL
        - INTEGRITY
        """
        quests = []
        daily_set = get_daily_quest_set(user_id, completed_one_time_quests)
        
        for slot, quest_def in daily_set.items():
            quests.append(
                RuntimeQuest(
                    uuid=str(uuid.uuid4()),
                    type=quest_def.quest_type,
                    key=quest_def.quest_id,
                    title=quest_def.title,
                    description=quest_def.instructions,  # Instructions kullanıcıya gösterilir
                    base_ncr=quest_def.base_ncr,
                    base_xp=quest_def.base_xp,
                )
            )
        
        return quests
    
    @staticmethod
    def _generate_legacy(user_id: int, count: int = 5) -> List[RuntimeQuest]:
        """
        Legacy quest generation (backward compatibility).
        """
        quests = []
        
        # Örnek quest'ler (Legacy)
        quest_templates = [
            {
                "type": QuestType.MICROTASK,
                "key": "DAILY_LOGIN",
                "title": "Günlük Giriş",
                "description": "Bot'a giriş yap ve bugünkü quest'leri görüntüle",
                "base_ncr": 2.0,
                "base_xp": 10,
            },
            {
                "type": QuestType.REFLECTION,
                "key": "DAILY_REFLECTION",
                "title": "Günlük Düşünce",
                "description": "Bugün hakkında kısa bir düşünce paylaş",
                "base_ncr": 5.0,
                "base_xp": 25,
            },
            {
                "type": QuestType.SOCIAL,
                "key": "SOCIAL_SHARE",
                "title": "Sosyal Paylaşım",
                "description": "NasipQuest'i sosyal medyada paylaş",
                "base_ncr": 8.0,
                "base_xp": 40,
            },
            {
                "type": QuestType.QUIZ,
                "key": "DAILY_QUIZ",
                "title": "Günlük Quiz",
                "description": "Bugünkü quiz'i çöz",
                "base_ncr": 10.0,
                "base_xp": 50,
            },
            {
                "type": QuestType.MEME,
                "key": "MEME_CREATE",
                "title": "Meme Üret",
                "description": "Yaratıcı bir meme oluştur ve paylaş",
                "base_ncr": 15.0,
                "base_xp": 75,
            },
        ]
        
        # İlk N quest'i seç
        selected = quest_templates[:count]
        
        for template in selected:
            quests.append(
                RuntimeQuest(
                    uuid=str(uuid.uuid4()),
                    type=template["type"],
                    key=template["key"],
                    title=template["title"],
                    description=template["description"],
                    base_ncr=template["base_ncr"],
                    base_xp=template["base_xp"],
                )
            )
        
        return quests
    
    @staticmethod
    def get_quest_definition(quest_id: str) -> Optional[QuestDefinition]:
        """Quest ID'ye göre tanım getir (MVP Pack V1)."""
        return get_quest_by_id(quest_id)

