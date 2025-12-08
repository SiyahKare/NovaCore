"""
NovaCore API Client
Bot'tan NovaCore API'ye HTTP istekleri için helper
"""
import httpx
from typing import Optional, Dict, Any

from .config import config


# --- Marketplace Exceptions ---

class InsufficientFundsError(Exception):
    """Yetersiz bakiye hatası."""
    pass


class AlreadyPurchasedError(Exception):
    """Zaten satın alınmış hatası."""
    pass


class NovaCoreClient:
    """NovaCore API client."""
    
    def __init__(self):
        self.base_url = config.NOVACORE_URL
        self.bridge_token = config.BRIDGE_TOKEN
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=30.0,
            headers={
                "X-TG-BRIDGE-TOKEN": self.bridge_token,
                "Content-Type": "application/json",
            }
        )
    
    async def call(
        self,
        endpoint: str,
        method: str = "GET",
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        NovaCore API'ye istek gönder.
        
        Args:
            endpoint: API endpoint (örn: "/api/v1/telegram/me")
            method: HTTP method (GET, POST, etc.)
            params: Query parameters
            data: Request body (POST için)
        
        Returns:
            API response dict
        """
        try:
            if method.upper() == "GET":
                response = await self.client.get(endpoint, params=params)
            elif method.upper() == "POST":
                response = await self.client.post(endpoint, params=params, json=data)
            elif method.upper() == "PATCH":
                response = await self.client.patch(endpoint, params=params, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_detail = e.response.json().get("detail", str(e))
            except:
                error_detail = str(e)
            
            # HTTP status code'a göre exception fırlat
            if e.response.status_code == 402:  # Payment Required
                raise InsufficientFundsError(error_detail)
            elif e.response.status_code == 409:  # Conflict
                raise AlreadyPurchasedError(error_detail)
            
            raise Exception(f"NovaCore API error: {error_detail}")
        except Exception as e:
            # Zaten custom exception ise direkt fırlat
            if isinstance(e, (InsufficientFundsError, AlreadyPurchasedError)):
                raise
            raise Exception(f"API call failed: {str(e)}")
    
    async def link_user(
        self,
        telegram_user_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        start_param: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Telegram kullanıcısını NovaCore'a link et."""
        return await self.call(
            "/api/v1/telegram/link",
            method="POST",
            data={
                "telegram_user_id": telegram_user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "start_param": start_param,
            }
        )
    
    async def get_profile(self, telegram_user_id: int) -> Dict[str, Any]:
        """Kullanıcı profilini getir."""
        return await self.call(
            "/api/v1/telegram/me",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def get_tasks(self, telegram_user_id: int) -> Dict[str, Any]:
        """Görev listesini getir."""
        return await self.call(
            "/api/v1/telegram/tasks",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def submit_task(
        self,
        telegram_user_id: int,
        task_id: str,
        proof: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Görev tamamla."""
        return await self.call(
            f"/api/v1/telegram/tasks/{task_id}/submit",
            method="POST",
            params={"telegram_user_id": telegram_user_id},
            data={
                "proof": proof,
                "metadata": metadata or {},
            }
        )
    
    async def get_active_events(self, telegram_user_id: int) -> Dict[str, Any]:
        """Aktif event'leri getir."""
        return await self.call(
            "/api/v1/telegram/events/active",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def join_event(self, telegram_user_id: int, event_id: int) -> Dict[str, Any]:
        """Event'e katıl."""
        return await self.call(
            f"/api/v1/telegram/events/{event_id}/join",
            method="POST",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def get_event_leaderboard(self, event_id: int, limit: int = 20) -> Dict[str, Any]:
        """Event leaderboard'unu getir."""
        return await self.call(
            f"/api/v1/telegram/events/{event_id}/leaderboard",
            params={"limit": limit}
        )
    
    async def get_leaderboard(self, period: str = "all_time", limit: int = 10) -> Dict[str, Any]:
        """Global leaderboard'u getir."""
        return await self.call(
            "/api/v1/telegram/leaderboard",
            params={"period": period, "limit": limit}
        )
    
    async def get_profile_card(self, telegram_user_id: int) -> Dict[str, Any]:
        """Profil kartını getir."""
        return await self.call(
            "/api/v1/telegram/profile-card",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def claim_referral(
        self,
        telegram_user_id: int,
        referral_code: str,
    ) -> Dict[str, Any]:
        """Referral ödülü talep et."""
        return await self.call(
            "/api/v1/telegram/referral/claim",
            method="POST",
            params={"telegram_user_id": telegram_user_id},
            data={"referral_code": referral_code}
        )
    
    async def get_quests(self, telegram_user_id: int) -> Dict[str, Any]:
        """Günlük quest'leri getir (legacy)."""
        return await self.call(
            "/api/v1/telegram/quests/today",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def get_quests_today(self, telegram_user_id: int) -> Dict[str, Any]:
        """Günlük quest'leri getir (Citizen Quest Engine)."""
        return await self.call(
            "/api/v1/telegram/quests/today",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def submit_quest(
        self,
        telegram_user_id: int,
        quest_uuid: str,
        proof_type: str,
        proof_payload_ref: str,
        proof_content: Optional[str] = None,
        message_id: Optional[str] = None,
        ai_score: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Quest proof gönder.
        
        Args:
            telegram_user_id: Telegram user ID
            quest_uuid: Quest UUID
            proof_type: text | photo | link | mixed
            proof_payload_ref: Reference (file_id, URL, etc.)
            proof_content: Direct text content (for text proofs)
            message_id: Telegram message_id for tracking
            ai_score: Optional pre-calculated AI score
        """
        return await self.call(
            "/api/v1/telegram/quests/submit",
            method="POST",
            params={"telegram_user_id": telegram_user_id},
            data={
                "quest_uuid": quest_uuid,
                "proof_type": proof_type,
                "proof_payload_ref": proof_payload_ref,
                "proof_content": proof_content,
                "source": "telegram",
                "message_id": message_id,
                "ai_score": ai_score,
            }
        )
    
    async def get_next_assignable_quest(
        self,
        telegram_user_id: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Kullanıcının bir sonraki atanabilir quest'ini getir.
        
        MVP: Bugün için ASSIGNED durumunda olan ilk quest'i döndürür.
        """
        result = await self.call(
            "/api/v1/telegram/quests/active",
            params={"telegram_user_id": telegram_user_id}
        )
        
        quests = result.get("quests", []) if isinstance(result, dict) else result
        
        # ASSIGNED durumunda olan ilk quest'i bul
        for quest in quests:
            if quest.get("status") == "assigned":
                return quest
        
        return None
    
    async def get_wallet(self, telegram_user_id: int) -> Dict[str, Any]:
        """Wallet balance ve transaction history getir."""
        return await self.call(
            "/api/v1/wallet/me",
            params={"telegram_user_id": telegram_user_id}
        )
    
    # --- Marketplace Methods ---
    
    async def list_marketplace_items(
        self,
        telegram_user_id: int,
        limit: int = 10,
        offset: int = 0,
        item_type: Optional[str] = None,
        min_score: Optional[float] = None,
        status: str = "active",
    ) -> Dict[str, Any]:
        """
        Marketplace item'lerini listele.
        
        Args:
            telegram_user_id: Telegram user ID
            limit: Sayfa boyutu
            offset: Sayfa offset'i
            item_type: Item tipi filtresi
            min_score: Minimum AI score
            status: Durum filtresi (default: active)
        """
        params = {
            "telegram_user_id": telegram_user_id,
            "limit": limit,
            "offset": offset,
            "status": status,
        }
        if item_type:
            params["item_type"] = item_type
        if min_score:
            params["min_score"] = min_score
        
        return await self.call(
            "/api/v1/marketplace/items",
            params=params
        )
    
    async def get_marketplace_item(
        self,
        telegram_user_id: int,
        item_id: int,
    ) -> Dict[str, Any]:
        """Tek bir marketplace item getir."""
        return await self.call(
            f"/api/v1/marketplace/items/{item_id}",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def purchase_marketplace_item(
        self,
        telegram_user_id: int,
        item_id: int,
    ) -> Dict[str, Any]:
        """
        Marketplace item satın al.
        
        Raises:
            InsufficientFundsError: Yetersiz bakiye
            AlreadyPurchasedError: Zaten satın alınmış
            Exception: Diğer hatalar
        """
        # call() metodu zaten HTTP status code'a göre exception fırlatıyor
        return await self.call(
            f"/api/v1/marketplace/items/{item_id}/purchase",
            method="POST",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def get_my_marketplace_items(
        self,
        telegram_user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Kendi marketplace item'lerimi getir."""
        return await self.call(
            "/api/v1/marketplace/my-items",
            params={
                "telegram_user_id": telegram_user_id,
                "limit": limit,
                "offset": offset,
            }
        )
    
    async def get_my_marketplace_sales(
        self,
        telegram_user_id: int,
    ) -> Dict[str, Any]:
        """Satış istatistiklerimi getir."""
        return await self.call(
            "/api/v1/marketplace/my-sales",
            params={"telegram_user_id": telegram_user_id}
        )
    
    async def close(self):
        """Client'ı kapat."""
        await self.client.aclose()


# Global client instance
api_client = NovaCoreClient()

