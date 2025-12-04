# app/nova_score/models.py
"""
NovaScore Core Models - Single Source of Truth

DRY: Tüm NovaScore modelleri buradan beslenir.
"""
from pydantic import BaseModel, Field


class NovaScoreBreakdown(BaseModel):
    """
    NovaScore bileşenleri - tek kaynak model.
    
    Tüm modüller (calculator, schemas, router) bu modeli kullanır.
    """
    activity: float = Field(ge=0.0, le=25.0, description="Düzen ve süreklilik (0-25)")
    quality: float = Field(ge=0.0, le=25.0, description="Üretilen işin kalitesi (0-25)")
    ethics: float = Field(ge=0.0, le=25.0, description="Risk tersinden (0-25)")
    contribution: float = Field(ge=0.0, le=15.0, description="Tribe'e katkı (0-15)")
    economic: float = Field(ge=0.0, le=10.0, description="NCR stake/kullanım (0-10)")

