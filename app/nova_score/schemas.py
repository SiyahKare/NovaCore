# novacore/app/nova_score/schemas.py

from typing import Optional

from pydantic import BaseModel, Field





class ComponentScore(BaseModel):

    value: float = Field(..., ge=0, le=100)

    confidence: float = Field(..., ge=0.0, le=1.0)





class NovaScoreComponents(BaseModel):

    ECO: ComponentScore

    REL: ComponentScore

    SOC: ComponentScore

    ID: ComponentScore

    CON: ComponentScore





class NovaScoreResponse(BaseModel):

    user_id: str

    nova_score: int = Field(..., ge=0, le=1000)

    components: NovaScoreComponents

    cp: int = Field(..., description="Ceza puanı (Adalet modülünden)")

    confidence_overall: float = Field(

        ..., ge=0.0, le=1.0, description="Feature coverage'a göre genel güven"

    )

    explanation: Optional[str] = Field(

        None,

        description="Kısa açıklama: düşük veri / recall / kısıtlanmış policy vs.",

    )

