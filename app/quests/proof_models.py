"""
Quest Proof Models - Proof Submission & Storage
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Column, Text


class QuestProof(SQLModel, table=True):
    """
    Quest proof submission kaydı.
    
    Vatandaş → Proof gönderir → Burada saklanır → AI scoring → Reward
    """
    __tablename__ = "quest_proofs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # İlişki
    user_id: int = Field(index=True, foreign_key="users.id")
    user_quest_id: int = Field(index=True, foreign_key="user_quests.id")
    
    # Source tracking
    source: str = Field(
        max_length=50,
        description="telegram | web | api | mobile",
        default="telegram",
    )
    message_id: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Telegram message_id / external reference",
    )
    
    # Proof content
    proof_type: str = Field(
        max_length=50,
        description="text | photo | link | mixed",
    )
    content: str = Field(
        sa_column=Column(Text),
        description="Proof içeriği (text veya JSON stringified)",
    )
    
    # Metadata (renamed to avoid SQLModel conflict)
    proof_metadata: Optional[str] = Field(
        default=None,
        sa_column=Column(Text, name="metadata"),
        description="JSON metadata (file_url, dimensions, etc.)",
    )
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # AI Scoring result (cache)
    ai_score: Optional[float] = Field(
        default=None,
        description="AI scoring sonucu (0-100)",
    )
    ai_flags: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Comma-separated flags: nsfw_or_toxic,low_quality,cliche",
    )
    ai_tags: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Comma-separated suggested tags",
    )

