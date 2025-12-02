"""
NovaCore - Aurora AI Integration Client
Helper for communicating with Aurora AI backend.
"""
from typing import Any

import httpx

from app.core.logging import get_logger

logger = get_logger("integrations.aurora")


class AuroraClient:
    """
    Aurora AI integration client.
    
    Normal flow: Aurora → NovaCore (POST /events/aurora)
    Opsiyonel: NovaCore → Aurora (routing, credits info)
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or "http://aurora:8004"
        self.timeout = 10.0

    async def get_routing_info(
        self,
        user_id: int,
        tier: str,
        vip_priority: int,
        ai_credits_bonus: float,
    ) -> dict[str, Any]:
        """
        Get AI routing recommendation based on user loyalty.
        
        Higher tier users get:
        - Better AI models
        - Priority queue
        - Bonus credits
        """
        routing = {
            "user_id": user_id,
            "tier": tier,
            "vip_priority": vip_priority,
            "ai_credits_bonus": ai_credits_bonus,
            "recommended_model": self._get_recommended_model(tier),
            "priority_queue": vip_priority >= 50,
            "max_tokens_per_request": self._get_max_tokens(tier),
        }
        return routing

    def _get_recommended_model(self, tier: str) -> str:
        """Get recommended AI model based on tier."""
        models = {
            "BRONZE": "aurora-basic",
            "SILVER": "aurora-standard",
            "GOLD": "aurora-premium",
            "DIAMOND": "aurora-elite",
        }
        return models.get(tier, "aurora-basic")

    def _get_max_tokens(self, tier: str) -> int:
        """Get max tokens per request based on tier."""
        limits = {
            "BRONZE": 1000,
            "SILVER": 2000,
            "GOLD": 4000,
            "DIAMOND": 8000,
        }
        return limits.get(tier, 1000)

    async def notify_credits_update(
        self,
        user_id: int,
        tier: str,
        ai_credits_bonus: float,
    ) -> bool:
        """Notify Aurora of user credits/bonus update."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/webhooks/credits-update",
                    json={
                        "user_id": user_id,
                        "tier": tier,
                        "ai_credits_bonus": ai_credits_bonus,
                        "source": "novacore",
                    },
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.warning(
                "aurora_credits_notify_failed",
                user_id=user_id,
                error=str(e),
            )
            return False

    async def get_ai_profiles(self) -> list[dict[str, Any]]:
        """Get list of available AI performer profiles."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/profiles")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning("aurora_profiles_fetch_failed", error=str(e))
            return []

    async def health_check(self) -> dict[str, Any]:
        """Check Aurora health."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return {"status": "healthy", "data": response.json()}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

