"""
Telegram Gateway Schemas
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TelegramLinkRequest(BaseModel):
    """Telegram kullanıcısını NovaCore User ile eşleme isteği."""
    telegram_user_id: int = Field(..., description="Telegram user ID")
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    start_param: Optional[str] = Field(None, description="Telegram start parameter (JWT/signature)")
    webapp_init_data: Optional[str] = Field(None, description="Telegram WebApp initData")


class TelegramLinkResponse(BaseModel):
    """Telegram link response."""
    success: bool
    user_id: int
    telegram_account_id: int
    message: str


class TelegramMeResponse(BaseModel):
    """Telegram kullanıcısının tam profil bilgisi."""
    user_id: int
    telegram_user_id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    
    # Wallet
    wallet_balance: str = Field(..., description="NCR balance")
    
    # XP/Loyalty
    xp_total: int = 0
    level: int = 1
    tier: str = "Bronze"
    xp_to_next_level: int = 0
    
    # NovaScore
    nova_score: Optional[float] = None
    cp_value: int = 0
    regime: str = "NORMAL"
    
    # Timestamps
    first_seen_at: datetime
    last_seen_at: datetime


class TelegramTask(BaseModel):
    """Görev modeli (zenginleştirilmiş)."""
    id: str
    title: str
    description: str
    category: str  # "daily", "weekly", "special"
    difficulty: str = "easy"  # "easy", "medium", "hard", "expert"
    task_type: str = "microtask"  # "onchain", "social", "microtask", "quiz", "streak", "referral"
    proof_type: str = "none"  # "none", "screenshot", "link", "text", "quiz_answer", "onchain_tx"
    reward_xp: int = 0
    reward_ncr: str = "0"
    status: str = "available"  # "available", "in_progress", "completed", "claimed"
    cooldown_seconds: int = 0
    expires_at: Optional[datetime] = None
    streak_required: int = 0
    max_completions_per_user: int = 1


class TelegramTasksResponse(BaseModel):
    """Kullanıcıya özel görev listesi."""
    tasks: list[TelegramTask]
    total_available: int
    total_completed: int


class TelegramTaskSubmitRequest(BaseModel):
    """Görev tamamlama isteği."""
    task_id: str
    proof: Optional[str] = Field(None, description="Screenshot URL, text, or link")
    metadata: Optional[dict] = None


class TelegramTaskSubmitResponse(BaseModel):
    """Görev submit response."""
    success: bool
    task_id: str
    reward_xp: int = 0
    reward_ncr: str = "0"
    message: str
    new_balance: str
    new_xp_total: int


class TelegramReferralClaimRequest(BaseModel):
    """Referral claim request."""
    referral_code: str


class TelegramReferralClaimResponse(BaseModel):
    """Referral claim response."""
    success: bool
    reward_xp: int = 0
    reward_ncr: str = "0"
    message: str

