"""
NovaCore API Client
Bot'tan NovaCore API'ye HTTP istekleri için helper
"""
import httpx
from typing import Optional, Dict, Any

from .config import config


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
            
            raise Exception(f"NovaCore API error: {error_detail}")
        except Exception as e:
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
    
    async def close(self):
        """Client'ı kapat."""
        await self.client.aclose()


# Global client instance
api_client = NovaCoreClient()

