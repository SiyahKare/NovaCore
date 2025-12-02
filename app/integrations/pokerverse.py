"""
NovaCore - PokerVerse Integration Client
Helper for communicating with PokerVerse backend.
"""
from typing import Any

import httpx

from app.core.logging import get_logger

logger = get_logger("integrations.pokerverse")


class PokerVerseClient:
    """
    PokerVerse integration client.
    
    Normal flow: PokerVerse → NovaCore (POST /events/poker)
    Opsiyonel: NovaCore → PokerVerse callback
    """

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or "http://pokerverse:8003"
        self.timeout = 10.0

    async def notify_balance_update(
        self,
        user_id: int,
        new_balance: float,
    ) -> bool:
        """Notify PokerVerse of balance update (for table limits)."""
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
                "poker_notify_failed",
                user_id=user_id,
                error=str(e),
            )
            return False

    async def notify_vip_table_access(
        self,
        user_id: int,
        tier: str,
        vip_priority: int,
    ) -> bool:
        """Notify PokerVerse of VIP table access eligibility."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/webhooks/vip-access",
                    json={
                        "user_id": user_id,
                        "tier": tier,
                        "vip_priority": vip_priority,
                        "vip_tables_enabled": tier in ["GOLD", "DIAMOND"],
                        "source": "novacore",
                    },
                )
                response.raise_for_status()
                return True
        except Exception as e:
            logger.warning(
                "poker_vip_notify_failed",
                user_id=user_id,
                error=str(e),
            )
            return False

    async def get_active_tables(self) -> list[dict[str, Any]]:
        """Get list of active poker tables."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/api/v1/tables/active")
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning("poker_tables_fetch_failed", error=str(e))
            return []

    async def health_check(self) -> dict[str, Any]:
        """Check PokerVerse health."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
                response.raise_for_status()
                return {"status": "healthy", "data": response.json()}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

