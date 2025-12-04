# **SİYAHKARE – ECONOMY & NCR TOKENOMICS**

**Whitepaper v1.0 — Monetary Architecture**

---

## **1. NCR: Devletin Para Birimi**

**NCR (NovaCoin Real)** SiyahKare mikro-devletinin resmi para birimidir.

NCR:
- Bir meme coin **değildir**
- Bir spekülatif varlık **değildir**  
- Bir "utility token" **değildir**

NCR:
> **Otonom bir ekonomik sistemin işlemsel kan dolaşımıdır.**

### **NCR'nin Üç Temel Fonksiyonu**

| Fonksiyon | Açıklama |
|-----------|----------|
| **Medium of Exchange** | Ekosistem içi tüm işlemlerin birimi |
| **Store of Value** | Vatandaşın birikimi ve stake mekanizması |
| **Unit of Account** | GMV, vergi, ödül hesaplamalarının temeli |

---

## **2. Token Economics Overview**

### **2.1 Supply Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                    NCR SUPPLY MODEL                      │
├─────────────────────────────────────────────────────────┤
│  Initial Supply:         100,000,000 NCR                │
│  Max Supply:             DYNAMIC (AI-controlled)        │
│  Emission Rate:          Variable (0.1% - 2% monthly)   │
│  Burn Rate:              Variable (matches emission)    │
│  Target Equilibrium:     Net-zero inflation             │
└─────────────────────────────────────────────────────────┘
```

### **2.2 Allocation Matrix**

| Pool | Allocation | Purpose |
|------|------------|---------|
| **Treasury Reserve** | 30% | Ekonomik stabilizasyon, kriz fonu |
| **Reward Pool** | 40% | Task ödülleri, XP bonusları |
| **Liquidity Pool** | 15% | DEX likiditesi, fiyat desteği |
| **Team & Development** | 10% | Geliştirme, operasyon |
| **Community Grants** | 5% | Creator teşvikleri, hackathon |

---

## **3. Emission Mechanics (Token Üretimi)**

NCR emisyonu **sabit değildir**. AI tarafından dinamik olarak kontrol edilir.

### **3.1 Emission Formula**

```
Daily_Emission = Base_Rate × GMV_Factor × Activity_Multiplier × Stability_Coefficient

Nerede:
- Base_Rate = 0.05% of circulating supply
- GMV_Factor = log(daily_gmv / target_gmv)
- Activity_Multiplier = active_users / expected_users
- Stability_Coefficient = 1 / price_volatility_index
```

### **3.2 Emission Triggers**

| Durum | AI Tepkisi |
|-------|------------|
| GMV artıyor + Kullanıcı artıyor | Emisyon ↑ (max +15%) |
| GMV düşüyor + Kullanıcı sabit | Emisyon ↓ (min -10%) |
| Fiyat çok düşük | Emisyon STOP + Burn aktif |
| Fiyat çok yüksek | Emisyon ↑ + Sink aktivasyonu |

### **3.3 Emission Caps (Anayasal Limit)**

```
Günlük Maksimum Emisyon: Dolaşımdaki arzın %0.5'i
Haftalık Maksimum Emisyon: Dolaşımdaki arzın %2'si
Aylık Maksimum Emisyon: Dolaşımdaki arzın %5'i
```

> **Constitutional Lock:** Bu limitler AI tarafından aşılamaz.

---

## **4. Burn Mechanics (Token Yakımı)**

NCR ekonomisinde **burn = vergi + sink + fee** üçlüsüdür.

### **4.1 Burn Sources**

```
┌─────────────────────────────────────────────────────────┐
│                    BURN CHANNELS                         │
├─────────────────────────────────────────────────────────┤
│  1. Transaction Fee Burn      → %30 of all fees         │
│  2. Premium Feature Burn      → %50 of premium payments │
│  3. Marketplace Commission    → %20 of GMV rake         │
│  4. Penalty Burn              → %100 of CP penalties    │
│  5. Voluntary Burn            → Citizen sacrifice pool  │
│  6. Scheduled Protocol Burn   → Quarterly treasury burn │
└─────────────────────────────────────────────────────────┘
```

### **4.2 Burn Formula**

```
Daily_Burn = Σ(Transaction_Fees × 0.30) 
           + Σ(Premium_Payments × 0.50)
           + Σ(GMV_Rake × 0.20)
           + Σ(CP_Penalties × 1.00)
           + Protocol_Scheduled_Burn
```

### **4.3 Equilibrium Target**

```
Target: Daily_Burn ≈ Daily_Emission ± 5%

Eğer Burn > Emission × 1.20 → Deflasyonist mod (nadir)
Eğer Burn < Emission × 0.80 → Emisyon azaltılır
```

---

## **5. GMV Sinks (Değer Tutma Mekanizmaları)**

GMV Sink = NCR'nin ekonomiden "çıkış noktası" değil, "tutulma noktası"dır.

### **5.1 Primary Sinks**

| Sink | Mechanism | Lock Period |
|------|-----------|-------------|
| **Staking Pool** | APY karşılığı NCR kilitleme | 7-90 gün |
| **Creator Boost** | Görünürlük için NCR harcama | Instant burn |
| **Premium Membership** | Aylık NCR subscription | 30 gün |
| **MiniApp Activation** | App açmak için NCR yatırma | 90 gün |
| **Governance Stake** | Oy hakkı için NCR kilitleme | 180 gün |
| **Insurance Pool** | Risk koruma için NCR | Flexible |

### **5.2 Sink Efficiency Formula**

```
Sink_Efficiency = (Locked_NCR / Circulating_NCR) × 100

Target Efficiency: 40-60%
Warning Zone: < 30% (too liquid)
Danger Zone: > 70% (illiquidity risk)
```

---

## **6. Task-to-Earn Economy**

SiyahKare'nin temel ekonomik motoru **Nasip Tasks**'tır.

### **6.1 Reward Architecture**

```
Task_Reward = Base_NCR × Level_Multiplier × Streak_Bonus × Economic_Factor

Nerede:
- Base_NCR = Task difficulty rating (1-100 NCR)
- Level_Multiplier = 1 + (user_level × 0.05)
- Streak_Bonus = 1 + (consecutive_days × 0.02) [max 1.5]
- Economic_Factor = DRM_coefficient (0.5 - 1.5)
```

### **6.2 Daily Reward Distribution**

```
┌─────────────────────────────────────────────────────────┐
│              DAILY REWARD POOL DISTRIBUTION              │
├─────────────────────────────────────────────────────────┤
│  Task Completion Rewards     │  60%                     │
│  Referral Bonuses            │  10%                     │
│  Creator Earnings            │  15%                     │
│  Staking Rewards             │  10%                     │
│  Random Bonus Pool           │  5%                      │
└─────────────────────────────────────────────────────────┘
```

### **6.3 Anti-Exploit Mechanisms**

| Mechanism | Description |
|-----------|-------------|
| **Diminishing Returns** | Günlük 10+ task sonrası ödül %50 düşer |
| **Quality Score** | Düşük kalite = düşük ödül |
| **Cooldown Period** | Aynı task tipi 4 saat cooldown |
| **Behavioral Analysis** | Bot/script tespiti → ban |

---

## **7. Dynamic Yield System (DRM Integration)**

### **7.1 Dynamic Reward Multiplier (DRM)**

DRM, ekonominin "nabzı"dır.

```
DRM = f(GMV_health, User_activity, Treasury_balance, Market_sentiment)

DRM Range: 0.5x — 1.5x
Default: 1.0x
```

### **7.2 DRM Calculation**

```python
def calculate_drm():
    gmv_score = normalize(current_gmv / target_gmv)           # 0-1
    activity_score = normalize(dau / expected_dau)            # 0-1
    treasury_score = normalize(treasury / min_treasury)       # 0-1
    sentiment_score = normalize(price_7d_change)              # 0-1
    
    raw_drm = (gmv_score * 0.35 + 
               activity_score * 0.25 + 
               treasury_score * 0.25 + 
               sentiment_score * 0.15)
    
    return clamp(raw_drm * 1.5, 0.5, 1.5)
```

### **7.3 DRM Impact Matrix**

| DRM Value | Economic State | AI Response |
|-----------|----------------|-------------|
| 0.5 - 0.7 | **Crisis** | Burn artır, emission durdur |
| 0.7 - 0.9 | **Contraction** | Sübvansiyon aktif, sink azalt |
| 0.9 - 1.1 | **Equilibrium** | Normal operasyon |
| 1.1 - 1.3 | **Growth** | Emission artır, yeni sink aç |
| 1.3 - 1.5 | **Boom** | Vergi artır, aşırı ısınmayı önle |

---

## **8. Fiscal AI Impact**

Fiscal AI, ekonomiyi "adil" tutan motordur.

### **8.1 Fiscal Policies**

```
┌─────────────────────────────────────────────────────────┐
│                  FISCAL AI TOOLKIT                       │
├─────────────────────────────────────────────────────────┤
│  PROGRESSIVE TAXATION                                    │
│    └─ High earners: %5 rake                             │
│    └─ Mid earners: %3 rake                              │
│    └─ Low earners: %1 rake                              │
├─────────────────────────────────────────────────────────┤
│  SUBSIDY SYSTEM                                          │
│    └─ New user bonus: +50 NCR first week                │
│    └─ Low-level boost: +20% rewards (Level 1-5)         │
│    └─ Comeback bonus: +30% after 7-day absence          │
├─────────────────────────────────────────────────────────┤
│  STIMULUS TRIGGERS                                       │
│    └─ GMV drop > 20%: Emergency reward boost            │
│    └─ User churn > 15%: Retention campaign active       │
│    └─ Creator exodus: Creator grant program             │
└─────────────────────────────────────────────────────────┘
```

### **8.2 Redistribution Formula**

```
Redistribution_Pool = Σ(High_Earner_Tax) × 0.70

Distribution:
  - 50% → Low-level user subsidies
  - 30% → New user onboarding bonuses
  - 20% → Creator growth fund
```

---

## **9. Price Stability Band**

NCR fiyatı **tamamen serbest piyasa değildir**.

### **9.1 Stability Mechanism**

```
Target Price Band: $0.80 — $1.20 (soft peg)
Emergency Band: $0.50 — $2.00 (hard limits)
```

### **9.2 Intervention Triggers**

| Price Zone | AI Action |
|------------|-----------|
| **< $0.50** | Treasury buyback + Emission stop |
| **$0.50 - $0.80** | Burn artır + Sink teşviki |
| **$0.80 - $1.20** | Normal operasyon |
| **$1.20 - $2.00** | Emission artır + Sell pressure |
| **> $2.00** | Emergency emission + Warning |

### **9.3 Treasury Reserve Usage**

```
Treasury Intervention Rules:
1. Max 5% of treasury per week for price support
2. Buyback only when price < $0.70 for 48h
3. Sell only when price > $1.50 for 48h
4. All interventions logged and public
```

---

## **10. Citizen Income Simulation**

### **10.1 Expected Daily Earnings by Level**

| Level | Daily Tasks | Base Earnings | With DRM 1.0 | With DRM 1.3 |
|-------|-------------|---------------|--------------|--------------|
| 1 | 5 | 50 NCR | 50 NCR | 65 NCR |
| 5 | 8 | 120 NCR | 120 NCR | 156 NCR |
| 10 | 10 | 200 NCR | 200 NCR | 260 NCR |
| 20 | 12 | 350 NCR | 350 NCR | 455 NCR |
| 50 | 15 | 600 NCR | 600 NCR | 780 NCR |
| 100 | 20 | 1000 NCR | 1000 NCR | 1300 NCR |

### **10.2 Monthly Income Projection**

```
Monthly_Income = Daily_Base × 30 × Avg_DRM × Streak_Bonus × (1 - Tax_Rate)

Level 10 Örnek:
= 200 × 30 × 1.0 × 1.15 × 0.97
= 6,693 NCR/month
≈ $6,693 (at $1.00 peg)
```

### **10.3 Income Distribution Curve**

```
┌─────────────────────────────────────────────────────────┐
│  CITIZEN INCOME DISTRIBUTION (Monthly, NCR)              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Top 1%:    ████████████████████████████  15,000+       │
│  Top 10%:   ████████████████████          8,000-15,000  │
│  Top 25%:   ████████████████              5,000-8,000   │
│  Median:    ████████████                  3,000-5,000   │
│  Bottom 25%: ████████                     1,500-3,000   │
│  Bottom 10%: ████                         500-1,500     │
│                                                          │
│  Gini Coefficient Target: 0.35 (moderate inequality)    │
└─────────────────────────────────────────────────────────┘
```

---

## **11. NCR Monetary Cycle**

### **11.1 Complete Flow Diagram**

```
                         ┌──────────────────┐
                         │   TREASURY       │
                         │   RESERVE        │
                         └────────┬─────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              │                   │                   │
              ▼                   ▼                   ▼
       ┌──────────┐        ┌──────────┐        ┌──────────┐
       │ EMISSION │        │ BUYBACK  │        │ STIMULUS │
       │  POOL    │        │  FUND    │        │  FUND    │
       └────┬─────┘        └──────────┘        └────┬─────┘
            │                                       │
            ▼                                       ▼
     ┌─────────────┐                        ┌─────────────┐
     │   REWARD    │                        │  SUBSIDY    │
     │    POOL     │                        │   POOL      │
     └──────┬──────┘                        └──────┬──────┘
            │                                      │
            └──────────────┬───────────────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │  CITIZENS   │
                    │  (Earners)  │
                    └──────┬──────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │  SPEND   │  │  STAKE   │  │   HOLD   │
      │ (GMV)    │  │  (Lock)  │  │ (Wallet) │
      └────┬─────┘  └────┬─────┘  └──────────┘
           │             │
           ▼             ▼
      ┌──────────┐  ┌──────────┐
      │   BURN   │  │  SINK    │
      │  (Exit)  │  │  (Lock)  │
      └────┬─────┘  └────┬─────┘
           │             │
           └──────┬──────┘
                  │
                  ▼
           ┌─────────────┐
           │  DEFLATION  │
           │  PRESSURE   │
           └─────────────┘
```

### **11.2 Cycle Health Metrics**

| Metric | Healthy Range | Warning | Critical |
|--------|---------------|---------|----------|
| **Velocity** | 2-4x/month | < 1.5x | < 1x |
| **Sink Ratio** | 40-60% | > 70% | > 80% |
| **Emission/Burn** | 0.9 - 1.1 | > 1.3 | > 1.5 |
| **Treasury Coverage** | > 120% | < 100% | < 80% |

---

## **12. Economic Emergency Protocols**

### **12.1 Meltdown Prevention**

```
MELTDOWN DETECTION CRITERIA:
- Price drops > 40% in 24h
- Treasury coverage < 50%
- DAU drops > 50% in 7 days
- Emission/Burn ratio > 2.0

EMERGENCY RESPONSE:
1. HALT all emissions immediately
2. ACTIVATE treasury buyback (max 20%)
3. PAUSE new user subsidies
4. ENABLE emergency burn (double fees)
5. ALERT President for manual override
```

### **12.2 Recovery Protocol**

```
RECOVERY PHASES:
Phase 1 (Stabilization): Price within emergency band
Phase 2 (Normalization): Emission/burn ratio < 1.2
Phase 3 (Growth): Resume normal operations
Phase 4 (Expansion): Re-enable full features
```

---

## **13. Economic Guarantees**

SiyahKare ekonomisi şunları **anayasal olarak garanti eder**:

### ✔ **Fiyat Tabanı**
NCR asla $0.30'un altına düşmez (treasury müdahalesi)

### ✔ **Kazanç Hakkı**
Her vatandaş günde minimum 10 NCR kazanabilir

### ✔ **Öngörülebilirlik**
Ödül değişiklikleri max ±20%/gün

### ✔ **Şeffaflık**
Tüm ekonomik kararlar publik ve açıklanmış

### ✔ **Adillik**
Aynı iş = Aynı ödül (level farkı hariç)

### ✔ **Çıkış Hakkı**
Unstake ve withdraw her zaman mümkün (cooldown dahilinde)

---

## **14. Tokenomics Summary**

```
┌─────────────────────────────────────────────────────────┐
│              NCR TOKENOMICS AT A GLANCE                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Token Name:        NovaCoin Real (NCR)                 │
│  Type:              AI-Managed State Currency           │
│  Target Price:      $1.00 ± 20%                         │
│  Supply Model:      Dynamic Equilibrium                  │
│  Emission Control:  Yield Balancer AI                   │
│  Burn Control:      Multi-channel automatic             │
│  Governance:        Cognitive Governance System         │
│  Stability:         Treasury-backed soft peg            │
│                                                          │
│  Primary Use Cases:                                      │
│    • Task Rewards                                        │
│    • Marketplace Transactions                            │
│    • Staking & Governance                               │
│    • Premium Features                                    │
│    • Creator Monetization                               │
│                                                          │
│  Economic Philosophy:                                    │
│    "Sustainable growth over speculative pump"           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## **15. Economy Section Final Statement**

NCR tokenomics, SiyahKare'nin ekonomik omurgasıdır.

Bu sistem:
- Spekülatif değil, **üretken**
- Volatil değil, **stabil**
- Merkeziyetçi değil, **AI-otonom**
- Adaletsiz değil, **redistribütif**

NCR:
> **"AI tarafından yönetilen, anayasal sınırlarla korunan, vatandaş odaklı dijital devlet parası."**

Bu ekonomi modeli:
- Web3'ün chaos'unu
- Geleneksel finans'ın katılığını
- Ve merkez bankalarının yavaşlığını

reddeder.

Yerine:
> **Otonom, adaptif, adil bir ekonomik sistem** koyar.

---

*Document Version: 1.0*  
*Last Updated: December 2024*  
*Authority: BARON*  
*Economic Model: Cognitive Economic System v1.4*

