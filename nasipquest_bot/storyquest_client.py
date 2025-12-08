"""
StoryQuest Engine API Client
Bot'tan StoryQuest Engine'e HTTP istekleri için helper
"""
import httpx
from typing import Optional, Dict, Any

from .config import config


class StoryQuestClient:
    """StoryQuest Engine API client."""
    
    def __init__(self):
        self.base_url = config.STORYQUEST_URL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
            }
        )
    
    async def start_terminal(
        self,
        telegram_user_id: int,
        user_identifier: Optional[str] = None,
        user_display_name: Optional[str] = None,
        user_username: Optional[str] = None,
        user_photo_url: Optional[str] = None,
        seed: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Terminal'i başlat - yeni bir story run başlat.
        
        Args:
            telegram_user_id: Telegram kullanıcı ID'si
            user_identifier: Kullanıcı identifier (default: telegram_{telegram_user_id})
            user_display_name: Görünen isim
            user_username: Kullanıcı adı
            user_photo_url: Profil fotoğrafı URL'i
            seed: Random seed (opsiyonel)
        
        Returns:
            StoryQuest response dict
        """
        if not user_identifier:
            user_identifier = f"telegram_{telegram_user_id}"
        
        # StoryQuest Engine'e kullanıcı detaylarını gönder
        payload = {
            "telegram_user_id": telegram_user_id,
            "user_identifier": user_identifier,
            "user_display_name": user_display_name,
            "user_username": user_username,
            "user_photo_url": user_photo_url,
        }
        
        if seed is not None:
            payload["seed"] = seed
        
        try:
            response = await self.client.post(
                "/api/storyquest/terminal/start",
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            raise Exception(f"StoryQuest API error: {error_detail}")
        except Exception as e:
            raise Exception(f"StoryQuest API call failed: {str(e)}")
    
    async def make_choice(
        self,
        run_id: str,
        question_id: str,
        choice_id: str,
    ) -> Dict[str, Any]:
        """
        Seçim yap - story'de bir seçenek seç.
        
        Args:
            run_id: Story run ID'si
            question_id: Soru ID'si (cta.question_id)
            choice_id: Seçilen seçeneğin ID'si (options[].id)
        
        Returns:
            StoryQuest response dict
        """
        payload = {
            "run_id": run_id,
            "question_id": question_id,
            "choice_id": choice_id,
        }
        
        try:
            response = await self.client.post(
                "/api/storyquest/terminal/choice",
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            raise Exception(f"StoryQuest API error: {error_detail}")
        except Exception as e:
            raise Exception(f"StoryQuest API call failed: {str(e)}")
    
    async def get_status(
        self,
        run_id: str,
        telegram_user_id: int,
    ) -> Dict[str, Any]:
        """
        Story run durumunu getir.
        
        Args:
            run_id: Story run ID'si
            telegram_user_id: Telegram kullanıcı ID'si
        
        Returns:
            StoryQuest status response dict
        """
        try:
            response = await self.client.get(
                f"/api/storyquest/terminal/status/{run_id}",
                params={"telegram_user_id": telegram_user_id},
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            raise Exception(f"StoryQuest API error: {error_detail}")
        except Exception as e:
            raise Exception(f"StoryQuest API call failed: {str(e)}")
    
    async def score_reply(
        self,
        run_id: str,
        user_reply: str,
    ) -> Dict[str, Any]:
        """
        Kullanıcının mektup cevabını GPT ile puanla.
        
        Args:
            run_id: Story run ID'si
            user_reply: Kullanıcının yazdığı cevap
        
        Returns:
            Scoring result dict
        """
        payload = {
            "run_id": run_id,
            "user_reply": user_reply,
        }
        
        try:
            response = await self.client.post(
                "/api/storyquest/terminal/score_reply",
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            raise Exception(f"StoryQuest API error: {error_detail}")
        except Exception as e:
            raise Exception(f"StoryQuest API call failed: {str(e)}")


# Global instance
storyquest_client = StoryQuestClient()

