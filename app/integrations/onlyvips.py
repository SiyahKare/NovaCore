"""
NovaCore - OnlyVips Integration Client
Helper for communicating with OnlyVips backend.
"""
from typing import Any

import httpx

from app.core.logging import get_logger

logger = get_logger("integrations.onlyvips")


class OnlyVipsClient:
    """
    OnlyVips integration client.
    
    Normal flow: OnlyVips → NovaCore (POST /events/onlyvips)
    Opsiyonel: NovaCore → OnlyVips callback
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or "http://onlyvips:8002"
        self.timeout = 10.0

    async def notify_vip_status_change(
        self,
        user_id: int,
        new_tier: str,
        vip_priority: int,
    ) -> bool:
        """Notify OnlyVips of VIP status change."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/webhooks/vip-update",
                    json={
                        "user_id": user_id,
                        "new_tier": new_tier,
                        "vip_priority": vip_priority,
                        "source": "novacore",
                    },
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.warning(
                "onlyvips_notify_failed",
                user_id=user_id,
                error=str(e),
            )
            return False

    async def notify_quest_reward(
        self,
        user_id: int,
        quest_id: str,
        ncr_reward: float,
        xp_reward: int,
    ) -> bool:
        """Notify OnlyVips of quest completion processing."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/webhooks/quest-processed",
                    json={
                        "user_id": user_id,
                        "quest_id": quest_id,
                        "ncr_reward": ncr_reward,
                        "xp_reward": xp_reward,
                        "source": "novacore",
                    },
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.warning(
                "onlyvips_quest_notify_failed",
                user_id=user_id,
                error=str(e),
            )
            return False

    async def health_check(self) -> dict[str, Any]:
        """Check OnlyVips health."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return {"status": "healthy", "data": response.json()}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

