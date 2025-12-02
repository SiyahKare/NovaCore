"""
NovaCore - FlirtMarket Integration Client
Helper for communicating with FlirtMarket backend.

v0.2: Bu client FlirtMarket'ten NovaCore'a değil,
      NovaCore'dan FlirtMarket'e (opsiyonel) callback için.
"""
from typing import Any

import httpx

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("integrations.flirt")


class FlirtMarketClient:
    """
    FlirtMarket integration client.
    
    Opsiyonel: NovaCore'dan FlirtMarket'e callback/notification göndermek için.
    Normal flow: FlirtMarket → NovaCore (POST /events/flirt)
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or "http://flirtmarket:8001"
        self.timeout = 10.0

    async def notify_balance_update(
        self,
        user_id: int,
        new_balance: float,
    ) -> bool:
        """Notify FlirtMarket of balance update (opsiyonel)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/webhooks/balance-update",
                    json={
                        "user_id": user_id,
                        "new_balance": new_balance,
                        "source": "novacore",
                    },
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.warning(
                "flirt_notify_failed",
                user_id=user_id,
                error=str(e),
            )
            return False

    async def notify_level_up(
        self,
        user_id: int,
        new_level: int,
        new_tier: str,
    ) -> bool:
        """Notify FlirtMarket of level up (for UI updates)."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/webhooks/level-up",
                    json={
                        "user_id": user_id,
                        "new_level": new_level,
                        "new_tier": new_tier,
                        "source": "novacore",
                    },
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.warning(
                "flirt_level_notify_failed",
                user_id=user_id,
                error=str(e),
            )
            return False

    async def health_check(self) -> dict[str, Any]:
        """Check FlirtMarket health."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return {"status": "healthy", "data": response.json()}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

