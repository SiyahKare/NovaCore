# 🎯 Quest Submission Pipeline V2 - Vatandaş Aksiyon → Sistem Hafızası

**"Vatandaş bir şey yazdığında bu nasıl proof olur, nereye kaydolur, nasıl skorlanır?"**

---

## 📋 Pipeline Özeti

```
Vatandaş → Text Gönderir → QuestProof Kaydı → AI Scoring → AbuseGuard → Reward → NovaScore Update → Marketplace
```

---

## 1️⃣ Backend Core - Quest Submission API

### Endpoint

```http
POST /api/v1/telegram/quests/submit
```

### Request Body

```json
{
  "quest_uuid": "abc-123-def",
  "proof_type": "text",
  "proof_payload_ref": "telegram_msg_123456",
  "proof_content": "Bugün 200 TL yol + kahve yaktım, 0 TL kazandım.",
  "source": "telegram",
  "message_id": "123456",
  "ai_score": null
}
```

### Response Model (`QuestSubmitResponse`)

```json
{
  "status": "approved" | "pending_review" | "rejected" | "under_review",
  "quest_uuid": "abc-123-def",
  "quest_id": 42,
  "reason": "approved" | "queued_for_ai_scoring" | "abuse_guard_block",
  "risk_delta": 0.5,
  "ai_score": 85.0,
  "final_reward_ncr": 12.5,
  "final_reward_xp": 150,
  "final_score": 85.0,
  "marketplace_item_id": 123
}
```

---

## 2️⃣ Pipeline Adımları (Detaylı)

### Adım 1: Quest Bul ve Kontrol Et

```python
# app/quests/completion.py::submit_quest_proof()

uq = get_user_quest(db, user_id, quest_uuid)

# Kontroller:
- Quest var mı? → 404
- Quest expired mi? → 400 "Quest has expired"
- Quest status ASSIGNED/SUBMITTED mi? → 400 "Quest not in completable state"
```

### Adım 2: AbuseGuard Pre-Check

```python
abuse_guard = AbuseGuard(session)
risk_profile = await abuse_guard.get_or_create_profile(user_id)
risk_snapshot = risk_profile.risk_score

# Cooldown kontrolü
if abuse_guard.requires_cooldown(risk_snapshot):
    raise ValueError("Account on cooldown due to abuse risk")
```

**Çıkış:**
- ✅ Devam et
- 🚫 Cooldown → Quest REJECTED, response: `status="rejected", reason="abuse_guard_block"`

### Adım 3: QuestProof Kaydı Oluştur

```python
quest_proof = QuestProof(
    user_id=user_id,
    user_quest_id=uq.id,
    source=source,
    message_id=message_id,
    proof_type=proof_type,
    content=proof_content or proof_payload_ref,
)

session.add(quest_proof)
uq.status = QuestStatus.SUBMITTED
uq.submitted_at = now
```

**Çıkış:**
- QuestProof kaydı oluşturuldu
- UserQuest status → SUBMITTED

### Adım 4: AI Scoring

```python
# Quest kategorisini çıkar
quest_category = _infer_category_from_quest(uq)

# AI Scoring (PRODUCTION/RESEARCH için)
if quest_category in [QuestCategory.PRODUCTION, QuestCategory.RESEARCH]:
    scoring_result = await score_quest(scoring_input)
    final_ai_score = scoring_result.score
    scoring_flags = scoring_result.flags
    suggested_tags = scoring_result.suggested_tags
else:
    # Auto-pass (MODERATION/RITUAL için)
    final_ai_score = 70.0
    scoring_flags = []
    suggested_tags = []

# QuestProof'a kaydet
quest_proof.ai_score = final_ai_score
quest_proof.ai_flags = ",".join(scoring_flags) if scoring_flags else None
quest_proof.ai_tags = ",".join(suggested_tags) if suggested_tags else None
uq.final_score = final_ai_score
```

**Çıkış:**
- AI Score (0-100)
- Flags (nsfw_or_toxic, low_quality, cliche)
- Tags (suggested)

### Adım 5: AbuseGuard Post-Check

```python
# Scoring flags kontrolü
if "nsfw_or_toxic" in scoring_flags:
    await abuse_guard.register_event(
        user_id=user_id,
        event_type=AbuseEventType.TOXIC_CONTENT,
        meta={"quest_uuid": quest_uuid, "flags": scoring_flags},
    )

if "low_quality" in scoring_flags and final_ai_score < 40:
    await abuse_guard.register_event(
        user_id=user_id,
        event_type=AbuseEventType.LOW_QUALITY_BURST,
        meta={"quest_uuid": quest_uuid, "ai_score": final_ai_score},
    )
```

**Çıkış:**
- RiskScore güncellendi
- Event log kaydedildi

### Adım 6: RewardEngine v2 ile NCR/XP Hesapla

```python
reward_ncr, reward_xp, edge_multiplier = await calculate_ncr_reward_v2(
    session=session,
    base_ncr=uq.base_reward_ncr,
    base_xp=uq.base_reward_xp,
    user_id=user_id,
    level=user_state["level"],
    streak=user_state["streak"],
    siyah_score=user_state["siyah_score"],
    risk_score=user_state["risk_score"],
    ai_score=final_ai_score,
    nova_score=None,  # TODO: NovaScore service'den çek
    citizen_level=None,  # TODO: NovaScore'dan çıkar
)
```

**Çıkış:**
- Final NCR reward
- Final XP reward
- Edge multiplier

### Adım 7: Treasury Cap Uygula

```python
treasury_adjusted_ncr, treasury_meta = await apply_treasury_cap(
    session=session,
    pre_treasury_ncr=reward_ncr,
)

uq.final_reward_ncr = treasury_adjusted_ncr
uq.final_reward_xp = reward_xp
uq.house_edge_snapshot = edge_multiplier
```

**Çıkış:**
- Treasury-adjusted NCR
- Treasury metadata

### Adım 8: Quest Finalize (Status Belirleme)

```python
# HITL kontrolü
hitl_required = abuse_guard.requires_forced_hitl(risk_snapshot)

if hitl_required or final_ai_score < 50:
    # HITL required
    uq.status = QuestStatus.UNDER_REVIEW
    
    if final_ai_score < 50:
        await abuse_guard.register_event(
            user_id=user_id,
            event_type=AbuseEventType.AUTO_REJECT,
            meta={"quest_uuid": quest_uuid, "ai_score": final_ai_score},
        )
else:
    # Direkt onay
    uq.status = QuestStatus.APPROVED
    uq.resolved_at = datetime.utcnow()
```

**Çıkış:**
- Status: APPROVED | UNDER_REVIEW | REJECTED

### Adım 9: Wallet + XP Service'e Yaz (APPROVED ise)

```python
if uq.status == QuestStatus.APPROVED:
    # NCR reward
    wallet_service = WalletService(session)
    await wallet_service.create_transaction(
        TransactionCreate(
            user_id=user_id,
            amount=treasury_adjusted_ncr,
            token="NCR",
            type=LedgerEntryType.EARN,
            source_app="nasipquest",
            reference_id=uq.quest_uuid,
            reference_type="quest_completion",
        )
    )
    
    # XP reward
    loyalty_service = XpLoyaltyService(session)
    await loyalty_service.create_xp_event(
        XpEventCreate(
            user_id=user_id,
            amount=reward_xp,
            event_type="QUEST_COMPLETED",
            source_app="nasipquest",
        )
    )
```

**Çıkış:**
- NCR wallet'a eklendi
- XP eklendi

### Adım 10: Marketplace Bridge (AI Score 70+)

```python
if uq.status == QuestStatus.APPROVED and final_ai_score >= 70:
    marketplace_item_id = await check_and_send_to_marketplace(
        session=session,
        user_quest=uq,
        ai_score=final_ai_score,
    )
```

**Çıkış:**
- MarketplaceItem oluşturuldu (status=ACTIVE)
- Item ID döndü

---

## 3️⃣ Telegram Bot Entegrasyonu

### `/görevler` veya `/tasks` Komutu

**Handler:** `nasipquest_bot/handlers.py::cmd_tasks`

**Akış:**
1. `GET /api/v1/telegram/quests/today` → Günlük quest'leri getir
2. Quest'leri formatla ve göster
3. Inline keyboard ile quest seçimi

### Text Yakalama Handler

**Handler:** `nasipquest_bot/handlers_quest_proof.py::handle_proof_text`

**MVP Mantık:**
- Kullanıcı text gönderdiğinde (command değilse)
- Bugün için ASSIGNED durumunda olan ilk quest'e bağla
- Proof gönder

**Akış:**
```python
@router.message(F.text & ~F.text.startswith("/"))
async def handle_proof_text(message: Message):
    # Aktif quest bul
    active_quest = await api_client.get_next_assignable_quest(telegram_user_id)
    
    # Proof gönder
    result = await api_client.submit_quest(
        quest_uuid=active_quest["quest_uuid"],
        proof_content=message.text,
        ...
    )
    
    # Response'a göre mesaj gönder
    if result.status == "approved":
        # ✅ Gönderin Onaylandı! + Ödül bilgisi
    elif result.status == "pending_review":
        # ⏳ Gönderin Kaydedildi
    elif result.status == "rejected":
        # 🚫 Gönderin Reddedildi
```

---

## 4️⃣ AI Scoring Worker (Async İşçi)

**Not:** Şu an AI Scoring sync olarak `submit_quest_proof()` içinde yapılıyor. İleride async worker'a taşınabilir.

### Worker Tasarımı (Gelecek)

```python
async def process_ai_scoring_job(job: ScoringJob, db: Session):
    """
    Async worker: AI scoring job'larını işle.
    
    Queue'dan job al → AI scoring yap → Quest finalize et
    """
    uq = db.get(UserQuest, job.quest_id)
    proof = db.get(QuestProof, job.proof_id)
    
    # 1) LLM / scoring API çağır
    score = await ai_scoring_service.score(
        quest_type=uq.type,
        text=proof.content,
    )
    
    # 2) AbuseGuard post-check
    risk_delta = await abuse_guard.postcheck(
        user_id=uq.user_id,
        quest=uq,
        score=score,
    )
    
    # 3) Final NCR & XP hesapla
    reward = await reward_engine.calculate(
        quest=uq,
        score=score,
        risk_profile=get_risk_profile(uq.user_id, db),
    )
    
    # 4) Quest finalize
    if score >= uq.min_score:
        uq.status = QuestStatus.APPROVED
    else:
        uq.status = QuestStatus.REJECTED
    
    uq.final_score = score
    db.add(uq)
    
    # 5) Cüzdan / XP / NovaScore update
    if uq.status == QuestStatus.APPROVED:
        await wallet_service.add_ncr(uq.user_id, reward.ncr)
        await xp_service.add_xp(uq.user_id, reward.xp)
        await nova_score_service.update_from_quest(uq.user_id, uq, score)
    
    await risk_service.update_risk(uq.user_id, risk_delta)
    db.commit()
```

---

## 5️⃣ NovaScore Update Fonksiyonu

**Timing:** Quest APPROVED olduktan sonra çağrılacak.

```python
async def nova_score_service.update_from_quest(
    user_id: int,
    quest: UserQuest,
    ai_score: float,
) -> None:
    """
    Quest completion'dan NovaScore güncelle.
    
    İçeride:
    - ECO/REL/SOC/ID/CON ağırlıkları
    - CP cezası
    - Quest kategorisine göre component update
    """
    # TODO: NovaScore calculator'a entegre et
    pass
```

---

## 6️⃣ Status Mapping

| Status | Reason | Açıklama |
|--------|--------|----------|
| `pending_review` | `queued_for_ai_scoring` | AI scoring bekleniyor |
| `approved` | `approved` | Quest onaylandı, ödül verildi |
| `rejected` | `abuse_guard_block` | AbuseGuard tarafından reddedildi |
| `rejected` | `auto_reject` | AI score < 50 |
| `under_review` | `under_review` | HITL (Human-in-the-Loop) gerekli |

---

## 7️⃣ Test Senaryoları

### Senaryo 1: Happy Path

```
1. /görevler → Quest seç
2. Text gönder → Proof kaydedildi
3. AI Scoring → Score 85
4. AbuseGuard → Risk OK
5. Reward → NCR + XP verildi
6. Marketplace → Item oluşturuldu
7. Response → status="approved"
```

### Senaryo 2: Low Quality

```
1. Text gönder → Proof kaydedildi
2. AI Scoring → Score 35
3. AbuseGuard → LOW_QUALITY_BURST event
4. Quest → UNDER_REVIEW
5. Response → status="under_review"
```

### Senaryo 3: Toxic Content

```
1. Text gönder → Proof kaydedildi
2. AI Scoring → Score 20, flag="nsfw_or_toxic"
3. AbuseGuard → TOXIC_CONTENT event, RiskScore +2
4. Quest → REJECTED
5. Response → status="rejected", reason="abuse_guard_block"
```

---

## 8️⃣ Sonraki Adımlar

1. ✅ **Quest Submission Pipeline** (Tamamlandı)
2. ✅ **Telegram `/görevler` + text yakalama** (Tamamlandı)
3. 🔜 **NovaScore update fonksiyonu** (Sonraki sprint)
4. 🔜 **AI Scoring Worker** (Async worker'a taşıma)
5. 🔜 **`/myscore` ve `/history` komutları** (Sonraki sprint)

---

**Pipeline hazır ve çalışıyor!** 🚀

