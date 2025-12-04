# app/scoring/models.py
"""
AI Scoring Service - Input/Output Models
"""
from typing import Literal, List
from pydantic import BaseModel, Field


class QuestScoringInput(BaseModel):
    """Quest scoring input model."""
    user_id: int
    quest_key: str
    category: str = Field(description="PRODUCTION / RESEARCH / MODERATION / COMMUNITY / LEARNING / RITUAL")
    proof_type: Literal["text", "image", "link", "mixed"] = "text"
    proof_payload: str = Field(description="Text içerik veya URL")
    lang: str = Field(default="tr", description="Dil kodu")


class QuestScoringOutput(BaseModel):
    """Quest scoring output model."""
    score: float = Field(ge=0.0, le=100.0, description="AI kalite skoru (0-100)")
    reasoning: str = Field(description="Kısa açıklama")
    flags: List[str] = Field(default_factory=list, description="Flag listesi: nsfw_or_toxic, cliche, low_quality, vb.")
    suggested_tags: List[str] = Field(default_factory=list, description="Önerilen tag'ler")

