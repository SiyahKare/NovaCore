# novacore/app/nova_score/router.py

from fastapi import APIRouter, Depends, HTTPException, status

from math import isfinite

from typing import Optional



from .schemas import NovaScoreResponse, NovaScoreComponents, ComponentScore

from ..consent.schemas import UserPrivacyProfileResponse

from ..consent.router import get_consent_service, ConsentService, get_current_user_id

from ..justice.router import get_justice_service, JusticeService



router = APIRouter(prefix="/api/v1/nova-score", tags=["nova-score"])





# --- Service Abstraction ---



class NovaScoreService:

    """

    NovaScore hesaplama motoru.

    Data access'i soyutluyoruz, sen DB/engine ile doldurursun.

    """



    def __init__(self, justice_service: JusticeService):

        self.justice_service = justice_service



    async def get_user_cp(self, user_id: str) -> int:

        cp_state = await self.justice_service.get_cp(user_id)

        return cp_state.cp_value



    async def get_economy_features(

        self, user_id: str, pp: UserPrivacyProfileResponse

    ) -> ComponentScore:

        if not (pp.policy and pp.policy.economy.allowed):

            return ComponentScore(value=0.0, confidence=0.0)



        # TODO: economyRepo'dan hacim vs çek

        value = 60.0  # dummy

        confidence = 1.0

        return ComponentScore(value=value, confidence=confidence)



    async def get_reliability_features(

        self, user_id: str, pp: UserPrivacyProfileResponse

    ) -> ComponentScore:

        if not (pp.policy and pp.policy.behavioral.allowed):

            return ComponentScore(value=0.0, confidence=0.0)



        # TODO: response time, completion rate vs

        value = 70.0

        confidence = 1.0

        return ComponentScore(value=value, confidence=confidence)



    async def get_social_features(

        self, user_id: str, pp: UserPrivacyProfileResponse

    ) -> ComponentScore:

        if not (pp.policy and pp.policy.behavioral.allowed):

            return ComponentScore(value=0.0, confidence=0.0)



        # TODO: rating, report oranı vs

        value = 65.0

        confidence = 1.0

        return ComponentScore(value=value, confidence=confidence)



    async def get_identity_features(

        self, user_id: str, pp: UserPrivacyProfileResponse

    ) -> ComponentScore:

        if not pp.policy:

            return ComponentScore(value=0.0, confidence=0.0)



        # TODO: KYC, anomaly skorları vs

        value = 80.0

        confidence = 1.0

        return ComponentScore(value=value, confidence=confidence)



    async def get_contribution_features(

        self, user_id: str, pp: UserPrivacyProfileResponse

    ) -> ComponentScore:

        if not (pp.policy and pp.policy.behavioral.allowed):

            return ComponentScore(value=0.0, confidence=0.0)



        # TODO: referral, bug report, beta katılımı vs

        value = 50.0

        confidence = 0.8

        return ComponentScore(value=value, confidence=confidence)



    def combine(self, components: NovaScoreComponents, cp: int) -> tuple[int, float, Optional[str]]:

        c = components



        weighted = (

            2.0 * c.ECO.value * c.ECO.confidence

            + 1.5 * c.REL.value * c.REL.confidence

            + 1.5 * c.SOC.value * c.SOC.confidence

            + 1.0 * c.ID.value * c.ID.confidence

            + 1.0 * c.CON.value * c.CON.confidence

        )



        max_possible = (

            2.0 * 100 * c.ECO.confidence

            + 1.5 * 100 * c.REL.confidence

            + 1.5 * 100 * c.SOC.confidence

            + 1.0 * 100 * c.ID.confidence

            + 1.0 * 100 * c.CON.confidence

        )



        if max_possible <= 0 or not isfinite(max_possible):

            ratio = 0.0

        else:

            ratio = max(min(weighted / max_possible, 1.0), 0.0)



        score = int(round(ratio * 1000))

        score = max(0, score - cp * 3)



        # overall confidence = ortalama confidence

        conf_overall = (

            c.ECO.confidence

            + c.REL.confidence

            + c.SOC.confidence

            + c.ID.confidence

            + c.CON.confidence

        ) / 5.0



        explanation = None

        if conf_overall < 0.4:

            explanation = (

                "Veri kapsamın düşük. Bazı veri kategorilerine izin vermediğin veya "

                "geri çekme hakkını kullandığın için NovaScore daha ihtiyatlı hesaplanıyor."

            )



        # response objeyi burada tam üretmiyoruz, router içinde user_id set edeceğiz.

        # sadece skor ve meta logic burada.

        return score, conf_overall, explanation





def get_nova_score_service(

    justice_service: JusticeService = Depends(get_justice_service),

) -> NovaScoreService:

    return NovaScoreService(justice_service)





# --- ENDPOINT ---



@router.get(

    "/me",

    response_model=NovaScoreResponse,

    summary="Giriş yapan kullanıcının güncel NovaScore'unu getir",

)

async def get_my_nova_score(

    consent_service: ConsentService = Depends(get_consent_service),

    nova_score_service: NovaScoreService = Depends(get_nova_score_service),

    current_user_id: str = Depends(get_current_user_id),

):

    user_id = current_user_id



    # 1) privacy profile çek

    try:
        pp = await consent_service.get_privacy_profile(user_id)
    except HTTPException as e:
        if e.status_code == status.HTTP_404_NOT_FOUND:
            # Privacy profile not found - user hasn't completed consent
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Privacy profile not found. Please complete the consent flow first.",
            )
        raise



    # 2) component skorlarını policy-aware şekilde hesapla

    ECO = await nova_score_service.get_economy_features(user_id, pp)

    REL = await nova_score_service.get_reliability_features(user_id, pp)

    SOC = await nova_score_service.get_social_features(user_id, pp)

    IDc = await nova_score_service.get_identity_features(user_id, pp)

    CON = await nova_score_service.get_contribution_features(user_id, pp)



    components = NovaScoreComponents(ECO=ECO, REL=REL, SOC=SOC, ID=IDc, CON=CON)



    # 3) CP çek (Adalet modülünden)

    cp = await nova_score_service.get_user_cp(user_id)



    # 4) skor + confidence + açıklama hesapla

    score, conf_overall, explanation = nova_score_service.combine(components, cp)



    # Recall bilgisine göre explanation güçlendir

    recall_state = "NONE"

    if pp.recall_requested_at:

        recall_state = "REQUESTED"



    if recall_state != "NONE":

        extra_msg = (

            " Verilerini YZ eğitiminden geri çekme talebinde bulunduğun için, "

            "geçmiş verilerin bir kısmı artık kullanılmıyor. NovaScore daha "

            "ihtiyatlı ve kısmi verilere dayanarak hesaplanıyor."

        )

        if explanation:

            explanation = explanation + extra_msg

        else:

            explanation = extra_msg



    return NovaScoreResponse(

        user_id=user_id,

        nova_score=score,

        components=components,

        cp=cp,

        confidence_overall=conf_overall,

        explanation=explanation,

    )

