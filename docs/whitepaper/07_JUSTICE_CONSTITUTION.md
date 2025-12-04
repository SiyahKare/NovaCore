# **SİYAHKARE – ADALET ANAYASASI v1.0**

**Whitepaper v1.0 — Justice Module & NovaScore Constitution**

---

## **1. Temel Prensipler**

AuroraOS "Adalet" Modülü, SiyahKare devletinin **otomatik ceza motoru**dur.

### **P1 – Otomatik Adalet, İnsan Onayı**
Sistem önce otomatik ceza keser, kritik eşiklerde **HITL / Ombudsman** devreye girer.

### **P2 – Ekonomik Ceza, Aşağılama Yok**
Ceza = **NCR / XP / erişim** üzerinden olur. Utandırma, alay, açık teşhir yok.

### **P3 – Şeffaflık**
Her cezanın yanında **RuleID + Sebep + Süre** görülür.

### **P4 – Tersine Çevrilebilirlik**
Kalıcı ban çok zor; çoğu ceza **zaman + düzgün davranış** ile silinir.

### **P5 – "Ahlaklı House Edge" Uyumu**
Ödül motoru ile ceza motoru **aynı RiskScore & SiyahScore** sinyallerini kullanır.

---

## **2. Adalet Sinyalleri (Justice Engine Input)**

Adalet modülü şu metriklerle beslenir:

| Sinyal | Aralık | Kaynak | Açıklama |
|--------|--------|--------|----------|
| `risk_score` | 0–10 | AbuseGuard | Genel risk skoru |
| `siyah_score` | 0–100 | AI Quality Engine | İçerik kalitesi |
| `cooldown_flags` | array | Event System | TOO_FAST_COMPLETION, LOW_QUALITY_BURST, MULTI_ACCOUNT |
| `toxicity_score` | 0–1 | NLP Engine | Mesaj & media analizi |
| `multi_device_score` | 0–1 | Device Fingerprint | Aynı IP/cihaz/numara şişirme |
| `fraud_flags` | array | Fraud Detection | REFERRAL_ABUSE, WASH_TRADING, vb. |

---

## **3. Ceza Tipleri (Sanction Types)**

| Kod | Tip | Açıklama |
|-----|-----|----------|
| **W1** | Uyarı (Warning) | UI'da banner + log entry. Ekonomiye dokunmaz. |
| **E1** | Ödül Düşürme (Reward Penalty) | `reward_multiplier` düşürülür (örn. 1.0 → 0.6). |
| **C1** | Cooldown | Yeni görev vermez / withdraw kapatır (x saat/gün). |
| **L1** | Limit | Günlük max NCR / görev sayısı düşürülür. |
| **S1** | Shadow Freeze (Soft Ban) | Görev vermez, ama "sistem yoğun" gibi gözükür. |
| **H1** | Human Review Flag | Zorunlu DAO/Ombudsman incelemesi. |

---

## **4. Kanun Tablosu (Rule Set v1.0)**

### **R01 – Hızlı Tamamlama / Emek Hırsızlığı**

**Trigger:**
- `completion_time < min_expected_time(task_type)`
- VEYA `TOO_FAST_COMPLETION` flag'i 3 kez / 24 saat

**Ceza:**
- İlk olay → `E1` (o görev ödülü = 0, RiskScore +1.0)
- Tekrarı (7 gün içinde) → `C1` (12–24 saat görev cooldown) + `E1`

**Recovery:**
- 7 gün içinde 5 görevi düzgün tamamlarsan ceza kalkar.

---

### **R02 – Düşük Kalite Serisi / Spam**

**Trigger:**
- Son 10 görevde `siyah_score_avg < 50`
- VEYA `LOW_QUALITY_BURST` flag

**Ceza:**
- `E1` → reward_multiplier = 0.7
- `L1` → günlük max görev = 2
- RiskScore +0.5

**Recovery:**
- Üst üste 5 görevi `siyah_score >= 70` tamamlarsan ceza kalkar.

---

### **R03 – Multi Account / Sybil Denemesi**

**Trigger:**
- Aynı cihaz/IP/numara → 3+ account, ortak referral zinciri
- VEYA "çok kısa sürede" peş peşe yeni kayıt + aynı cüzdan

**Ceza:**
- Şüpheli hesaplarda `S1` (shadow freeze)
- Ana hesapta `C1` (withdraw freeze 7 gün)
- RiskScore +3.0
- `H1` flag → Ombudsman paneline düşer.

**Recovery:**
- Ombudsman incelemesini bekle. Temiz çıkarsan ceza kaldırılır.

---

### **R04 – Toxicity & Taciz**

**Trigger:**
- `toxicity_score > 0.8` (ağır küfür, tehdit)
- VEYA NSFW media / illegal içerik upload

**Ceza:**
- Anında `C1` (chat write ban 24–72 saat)
- `E1` (reward_multiplier = 0.5, 7 gün)
- RiskScore +2.0

**Tekrarı:**
- 3 ihlal / 30 gün → `S1` + insan incelemesi.

---

### **R05 – Ekonomik Manipülasyon (Pump & Dump / Referral Abuse)**

**Trigger:**
- Referral'dan gelen hesapların %70+'ı 48 saat içinde **ban / risk 8+**
- NCR giriş-çıkış pattern'i "wash trading" gibi

**Ceza:**
- Referans bonusları iptal
- `C1` withdraw freeze (7–30 gün)
- RiskScore +3.0
- `H1` – DAO/ops incelemesi.

**Recovery:**
- DAO incelemesi zorunlu. Ekonomik manipülasyon ciddi suçtur.

---

### **R06 – Sistem Exploit / Bug Abuse**

**Trigger:**
- Aynı endpoint'e anormal istek
- Negatif bakiye, double-claim, vb. pattern tespiti

**Ceza:**
- Anında `C1` (full account freeze)
- Ombudsman / DevOps incelemesi zorunlu
- Net exploit ise kalıcı ban + log.

**Recovery:**
- DevOps ile iletişime geç. Bug report ise ödül alabilirsin.

---

## **5. Ceza Hesaplayıcı (Justice Engine)**

```python
def apply_justice(user_ctx, event) -> Sanction:
    risk = user_ctx.risk_score
    nova = user_ctx.nova_score

    # base multiplier: yüksek nova, cezayı biraz yumuşatır
    mercy = 1.0 - (nova / 200.0)   # NovaScore 100 ise -0.5

    rule = detect_rule(event, user_ctx)  # R01..R06

    base_cooldown_hours = {
        "R01": 12,
        "R02": 0,
        "R03": 168,
        "R04": 48,
        "R05": 168,
        "R06": 9999,
    }[rule.id]

    cooldown = int(base_cooldown_hours * (1.0 + risk/5.0) * mercy)

    return Sanction(
        rule_id=rule.id,
        type=rule.sanction_type,
        cooldown_hours=cooldown,
        reward_multiplier=rule.reward_multiplier,
        risk_delta=rule.risk_delta,
        requires_human=rule.requires_human,
    )
```

### **5.1 Merhamet Katsayısı (Mercy Factor)**

NovaScore yüksek olan vatandaşlar hafif ceza alır:

| NovaScore | Mercy Factor | Etki |
|-----------|--------------|------|
| 0 | 1.0 | Ceza tam uygulanır |
| 50 | 0.75 | Ceza %25 hafifler |
| 100 | 0.5 | Ceza %50 hafifler |

---

## **6. NovaScore v1.0 – Vatandaşlık Skoru**

**Amaç:**
"Bu adam sisteme **yararlı mı, güvenilir mi, stabil mi?**" sorusuna tek rakamla cevap.

0–100 arası, 60+ = güvenilir, 80+ = çekirdek citizen.

### **6.1 Skor Bileşenleri**

NovaScore **5 sütun** üzerinden gelir:

| Bileşen | Max Puan | Açıklama |
|---------|----------|----------|
| **ActivityScore** | 25 | Düzen ve süreklilik |
| **QualityScore** | 25 | Üretilen işin kalitesi (SiyahScore) |
| **EthicsScore** | 25 | RiskScore'un tersinden |
| **ContributionScore** | 15 | Tribe'e katkı (referral, DAO, validator) |
| **EconomicScore** | 10 | NCR stake / kullanım |
| **TOPLAM** | **100** | |

---

### **6.2 Formüller**

#### **A) ActivityScore (0–25)**

```python
activity = (
    min(streak_days, 30) / 30 * 15  # max 15
    + min(weekly_completed, 50) / 50 * 10  # max 10
)
```

- `streak_days` = max 30 kabul et
- `weekly_completed` = son 7 gün görev sayısı

---

#### **B) QualityScore (0–25)**

```python
quality = (siyah_avg / 100) * 25
```

- `siyah_avg` = son 20 görev kalite ortalaması (0–100)

---

#### **C) EthicsScore (0–25)**

```python
ethics = max(0.0, 25 * (1 - risk_score / 10))
```

- `risk_score` = 0–10 (AbuseGuard)
- 0 risk → full 25, 10 risk → 0

---

#### **D) ContributionScore (0–15)**

```python
contrib = (
    min(valid_referrals, 20) / 20 * 8   # max 8
    + min(dao_votes, 20) / 20 * 7       # max 7
)
```

- `valid_referrals` = gerçek, aktif referral sayısı
- `dao_votes` = son 30 gün DAO / validator katkısı

---

#### **E) EconomicScore (0–10)**

```python
stake_component = min(ncr_staked / 10_000, 1.0) * 6
usage_component = min(usage_volume / 2_000, 1.0) * 4

economic = stake_component + usage_component
```

- 10k NCR üstü stake → full 6 puan
- 2k NCR üstü 30-gün usage → full 4 puan

---

### **6.3 NovaScore Toplam Formülü**

```python
nova_score = activity + quality + ethics + contrib + economic
nova_score = round(min(nova_score, 100), 1)
```

---

### **6.4 NovaScore → Vatandaşlık Seviyesi**

| NovaScore | Seviye | Açıklama | Task Multiplier |
|-----------|--------|----------|-----------------|
| 0–39 | **Ghost** | İzleyici, sistemle yüzeysel temas. Görev ve withdraw limitli. | 0.5x |
| 40–59 | **Resident** | Normal citizen. Sıradan görev, sınırlı referral. | 1.0x |
| 60–79 | **Core Citizen** | Yüksek tavan, premium quest, daha iyi NCR çarpanı. | 1.2x |
| 80–89 | **Sovereign** | DAO görevleri, validator, yüksek güven limiti. | 1.4x |
| 90–100 | **Prime** | İç çekirdek. Beta feature'lar, yüksek stake, governance ağırlığı. | 1.5x |

### **6.5 Seviye Hakları ve Kısıtlamaları**

| Seviye | Günlük Withdraw | Validator | Referral |
|--------|----------------|-----------|----------|
| Ghost | 50 NCR | ❌ | ❌ |
| Resident | 200 NCR | ❌ | ✅ |
| Core Citizen | 500 NCR | ❌ | ✅ |
| Sovereign | 1000 NCR | ✅ | ✅ |
| Prime | 2000 NCR | ✅ | ✅ |

---

## **7. Adalet + NovaScore + NARE Entegrasyonu**

### **7.1 Adalet Modülü**
Ceza hesaplarken `nova_score`'u **merhamet katsayısı** olarak kullanır:
- Yüksek Nova → biraz daha hafif ceza

### **7.2 NARE (Quest Regülatörü)**
`nova_score` + `risk_score` + `streak`'ten **NareSignal** üretir:
- "bugün bu çocuğa kaç görev, ne sertlikte?" kararı

### **7.3 AbuseGuard**
RiskScore'ı yükselterek hem:
- **EthicsScore**'u yer (NovaScore düşer)
- **Önümüzdeki görev/ödül**leri düşürür

---

## **8. İtiraz Hakkı (Appeal Flow)**

AuroraOS **"polis devleti" değil, "adalet devleti"** olacak.

### **8.1 İtiraz Koşulları**
- `CP ≥ 25` ve yeni ceza almışsa → kullanıcıya `/appeal` linki göster.

### **8.2 İtiraz Süreci**
1. `/appeal` komutu ile başvuru
2. 1 kısa açıklama + 1 ekran görüntüsü/içerik referansı
3. Bazı durumlarda **5 NCR itiraz ücreti** (spam itirazı kesmek için)
4. Haksız ceza çıkarsa: **5 NCR iade + özür bonusu** (TrustBoost)

### **8.3 İtiraz Durumları**
| Durum | Açıklama |
|-------|----------|
| `pending` | İnceleme bekliyor |
| `approved` | İtiraz kabul, ceza kaldırıldı |
| `rejected` | İtiraz reddedildi, ceza geçerli |

---

## **9. Pydantic Model (API Schema)**

```python
from pydantic import BaseModel

class NovaScoreBreakdown(BaseModel):
    activity: float      # 0-25
    quality: float       # 0-25
    ethics: float        # 0-25
    contribution: float  # 0-15
    economic: float      # 0-10

class NovaScoreModel(BaseModel):
    user_id: str
    value: float           # 0–100
    level: str             # ghost/resident/core/sovereign/prime
    breakdown: NovaScoreBreakdown
    task_multiplier: float
    withdraw_limit_daily: float
    can_validate: bool
    can_refer: bool
```

---

## **10. Telegram Bot Entegrasyonu**

Bot: `@nasipquest_bot`

### **10.1 Komutlar**

| Komut | Açıklama |
|-------|----------|
| `/myscore` | NovaScore breakdown (Activity / Quality / Ethics / Contribution / Economic) |
| `/history` | Son 5 adalet olayı (hangi kural, kaç CP) |
| `/appeal <id>` | Adalet modülü itiraz biletini açar |
| `/rank` | Vatandaşlık ligi (gamification) |

---

## **11. Final Statement**

### **Adalet Modülü Garantileri:**

✔ **Otomatik ama adil**: Makine kararı + insan denetimi

✔ **Şeffaf ceza**: Her kararın arkasında açık kural

✔ **Geri dönüşüm**: Düzgün davranışla ceza silinir

✔ **Ekonomik denge**: Çakal ekonomiyi sömüremez

✔ **Vatandaş koruması**: Haksız cezaya itiraz hakkı

### **NovaScore Garantileri:**

✔ **Tek metrik**: Karmaşık davranışı tek sayıya sıkıştırır

✔ **5 bileşen**: Activity, Quality, Ethics, Contribution, Economic

✔ **Seviye sistemi**: Ghost → Prime arasında net hiyerarşi

✔ **Hak/kısıtlama**: Seviyeye göre withdraw, validator, referral hakları

✔ **Risk entegrasyonu**: AbuseGuard ile doğrudan bağlantı

---

*Document Version: 1.0*
*Last Updated: December 2025*
*Authority: BARON*
*System: AuroraOS Adalet Modülü v1.0 + NovaScore v1.0*

