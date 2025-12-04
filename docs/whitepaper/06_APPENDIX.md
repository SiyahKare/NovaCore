# **SİYAHKARE – APPENDIX**

**Whitepaper v1.0 — Technical, Mathematical & AI Appendix**

---

## 1. Matematiksel Formüller Özeti

Bu bölüm, diğer tüm whitepaper bölümlerinde geçen çekirdek formülleri tek yerde toplar.

---

### 1.1 Level Formülü (Citizen System)

Citizen Level, kümülatif XP'ye göre logaritmik hesaplanır:

```
Level = floor( log₁.₄(XP + 20) )
```

* Küçük XP artışlarında hızlı level up
* İlerleyen safhalarda yavaşlayan, emek gerektiren eğri

---

### 1.2 XP Hesabı (Nasip Tasks Engine)

Her görev için:

```
XP = D × E × C
```

* **D**: Difficulty (1–5)
* **E**: Ecosystem Impact (1–4)
* **C**: User Effort (1–3)

---

### 1.3 NCR Görev Ödülü

Tek bir task için NCR ödülü:

```
NCR_task = NCR_base × DRM × Rank_Multiplier × NasipBar_Multiplier
```

* **NCR_base**: Göreve atanmış taban ödül
* **DRM**: Dynamic Reward Multiplier (0.5–1.5)
* **Rank_Multiplier**: Rank bazlı çarpan (1.0–1.25)
* **NasipBar_Multiplier**: Nasip aralığına göre (0.7–1.2)

---

### 1.4 Citizen Aylık Gelir Formülü

```
Citizen_Monthly_Income = (Task_Income + Referral_Income + Creator_Share + Staking_Yield) × Rank_Multiplier × DRM_avg
```

---

### 1.5 Emission Formülü (Economy)

```
Daily_Emission = Base_Rate × GMV_Factor × Activity_Multiplier × Stability_Coefficient
```

Önerilen:

* `Base_Rate = 0.0005 × Circ_Supply` (0.05%)
* `GMV_Factor = log(Daily_GMV / Target_GMV)` (normalize edilerek kullanılır)
* `Activity_Multiplier = DAU / Expected_DAU`
* `Stability_Coefficient = 1 / Price_Volatility_Index`

**Constitutional caps:**

* Günlük: ≤ circ supply'in %0.5'i
* Haftalık: ≤ %2
* Aylık: ≤ %5

---

### 1.6 Burn Formülü

```
Daily_Burn = Σ(Fees × 0.30)
           + Σ(Premium_Payments × 0.50)
           + Σ(GMV_Rake × 0.20)
           + Σ(CP_Penalties × 1.00)
           + Protocol_Scheduled_Burn
```

**Hedef:**

```
Daily_Burn ≈ Daily_Emission ± 5%
```

---

### 1.7 Sink Efficiency

```
Sink_Efficiency = (Locked_NCR / Circulating_NCR) × 100
```

* Hedef: %40–%60
* < %30 → çok likit (gevşek ekonomi)
* > %70 → illikidite riski

---

### 1.8 DRM (Dynamic Reward Multiplier)

Basitleştirilmiş form:

```
DRM = clamp(1.5 × Raw_Score, 0.5, 1.5)

Raw_Score = 0.35 × GMV_Score 
          + 0.25 × Activity_Score 
          + 0.25 × Treasury_Score 
          + 0.15 × Sentiment_Score
```

Tüm skorlar 0–1 normalize edilir.

---

### 1.9 Neural Governor Amaç Fonksiyonu

```
min(
    ω₁ × |GMV - GMV_target| +
    ω₂ × |Stake - Stake_target| +
    ω₃ × Churn +
    ω₄ × Emission_Risk +
    ω₅ × Social_Equity
)
```

Ağırlıklar (ω_i) governance tarafından config'den ayarlanır.

---

## 2. Değişken & Parametre Sözlüğü (Glossary)

Bu bölüm, whitepaper boyunca geçen sembolleri ve metrikleri toparlar.

---

### 2.1 Ekonomik Değişkenler

| Sembol / Ad                | Tanım                                                      |
| -------------------------- | ---------------------------------------------------------- |
| **NCR**                    | NovaCoin Real, devletin para birimi                        |
| **Circ_Supply**            | Dolaşımdaki NCR miktarı                                    |
| **Max_Supply**             | AI kontrollü üst sınır; sabit değil, parametrik            |
| **Daily_Emission**         | O gün üretilen NCR miktarı                                 |
| **Daily_Burn**             | O gün yakılan NCR miktarı                                  |
| **GMV**                    | Gross Merchandise Value – ekosistem içi toplam işlem hacmi |
| **Daily_GMV**              | Günlük GMV                                                 |
| **Target_GMV**             | AI hedeflediği referans GMV bandı                          |
| **DAU**                    | Daily Active Users (aktif citizen)                         |
| **MAU**                    | Monthly Active Users                                       |
| **Stake**                  | Stake edilmiş NCR toplamı                                  |
| **Stake_Ratio**            | Stake / Circ_Supply                                        |
| **Treasury**               | Devlet kasasındaki NCR rezervi                             |
| **Price**                  | NCR dış piyasadaki fiyatı (USD referans)                   |
| **Price_Volatility_Index** | 24–72 saatlik volatilite skoru                             |
| **Churn**                  | Belirli periyotta sistemi bırakan citizen oranı            |

---

### 2.2 Citizen & Görev Değişkenleri

| Ad                      | Tanım                                 |
| ----------------------- | ------------------------------------- |
| **XP**                  | Citizen deneyim puanı                 |
| **Level**               | XP'ye göre hesaplanan seviye (0–100)  |
| **Rank**                | Bronze–Legendary sosyal statü katmanı |
| **Nasip Bar**           | 0–100 arası istikrar / emek barı      |
| **Task_Income**         | Görevlerden gelen NCR geliri          |
| **Referral_Income**     | Davet/referral kaynaklı NCR           |
| **Creator_Share**       | Creator olarak kazanılan NCR          |
| **Staking_Yield**       | Stake getirisi                        |
| **DRM**                 | Dynamic Reward Multiplier             |
| **Rank_Multiplier**     | Rank bazlı kazanç çarpanı             |
| **NasipBar_Multiplier** | Nasip Bar'a göre kazanç çarpanı       |
| **Quality_Score**       | Görevin/aktifliğin kalite metriği     |
| **Streak**              | Kesintisiz aktif gün sayısı           |

---

### 2.3 AI & Governance Parametreleri

| Parametre                 | Tanım                                                                  |
| ------------------------- | ---------------------------------------------------------------------- |
| **ω1..ω5**                | Neural Governor amaç fonksiyonu ağırlıkları                            |
| **Mode**                  | Governance çalışma modu: full_autonomy / limited_policy / observe_only |
| **Economic_Mode**         | Crisis / Contraction / Equilibrium / Growth / Boom                     |
| **DRM_Band**              | O anki DRM aralığı (örn. 0.9–1.1)                                      |
| **Tax_Rate_High/Mid/Low** | Fiscal AI'nin gelir grubuna göre vergi oranları                        |
| **Subsidy_Rate**          | Low-level citizen sübvansiyon oranı                                    |
| **Stimulus_Flag**         | Ekonomik teşvik paketinin aktiflik bayrağı                             |
| **Emergency_Flag**        | Meltdown protokolünün tetiklenme bayrağı                               |

---

## 3. AI Modelleri & Motorlar – Teknik Özet

Bu bölüm, SiyahKare'nin "AI Council" bileşenlerini teknik seviyede özetler.

---

### 3.1 Yield Balancer AI

**Rol:** Para politikası – ödüller & emisyon dengesi.

**Input:**
* Daily_GMV, GMV_momentum
* DAU / MAU
* Stake_Ratio
* Treasury seviyesi
* Price, Volatility
* DRM geçmişi

**Output:**
* Günlük DRM bandı
* NCR_base scale faktörleri
* Emission önerileri (Governor'a sinyal)

**Cadence:** Saatlik + günlük

**Failure Mode Riski:**
* Gereğinden yüksek DRM → enflasyon, emission patlaması
* Gereğinden düşük DRM → citizen geliri düşer, churn artar

**Safeguard:** DRM 0.5–1.5 clamp + Constitutional Guard.

---

### 3.2 Predictive Economic AI (v1.3)

**Rol:** 3 haftalık ekonomik hava durumu tahmini.

**Input:**
* Son 90 gün: GMV, DAU, Churn, Stake, Price
* Task completion dağılımı
* MiniApp kullanım metrikleri

**Output:**
* 21 günlük forecast: GMV, DAU, Churn, Emission_Risk
* Risk kategorisi: Low / Medium / High
* Politika tavsiyeleri: "growth push", "cooldown", "stabilize"

**Cadence:** 1–2 günde bir

**Risk:** Yanlış forecast → gereksiz fazla/az teşvik

**Mitigation:** Governor, forecast sinyalini tek kaynak almaz; real-time verilerle harmanlar.

---

### 3.3 Fiscal AI (Treasury Engine)

**Rol:** Vergi, sübvansiyon, stimulus.

**Input:**
* Income dağılımı (citizen bazlı)
* GMV metrikleri
* Low-level citizen gelir durumu
* Treasury rezerv seviyesi

**Output:**
* Tax_Rate tablosu
* Subsidy_Rate tablosu
* Stimulus paketleri (kampanya, bonus)
* Redistribution_Pool planı

**Cadence:** Günlük + haftalık

**Risk:** Aşırı vergi → büyüme yavaşlar, moral kaybı

**Mitigation:** Vergi / sübvansiyon oranlarına anayasal limitler (%0–5 bandı, vb).

---

### 3.4 Neural Governor (Economy Executive)

**Rol:** Ekonomik yürütme + makro karar alma.

**Input:**
* Yield Balancer çıktıları
* Fiscal AI çıktıları
* Predictive AI forecast'leri
* Anlık ekonomi ve citizen metrikleri

**Output:**
* Reward, tax, subsidy, sink, emission ayarları
* Economic_Mode seçimi

**Cadence:** 4 saatte bir ana karar döngüsü

**Policy Engine:** Deep RL + policy gradient + rule-based filters

**Safeguard:**
* Constitutional Guard + Economic Guard + Human Override.

---

### 3.5 Economic Guard (Judicial AI)

**Rol:** Yargı / fren sistemi.

**Input:**
* Governor'ın önerdiği aksiyonlar
* Risk metrikleri: Emission/Burn oranı, Treasury coverage, Price crash, GMV drop, Churn spike

**Output:**
* "Allow, Modify, Reject" kararları
* Emergency_Flag tetikleme
* Mode switch önerisi (full → limited → observe)

**Cadence:** Governor ile senkron + kritik event tetiklenince

**Yetki:**
* Aşırı risk tespitinde policy range'i daraltır
* En uç durumda governance'i observe-only moduna zorlayabilir.

---

## 4. Risk & Safeguard Matrisi

"Bu sistem nereden patlar?" sorusunun net tablosu.

---

### 4.1 Risk Sınıfları

| Kategori       | Örnek Risk                                           |
| -------------- | ---------------------------------------------------- |
| **Ekonomik**   | Emission patlaması, fiyat çöküşü, Treasury boşalması |
| **Teknik**     | Model hatası, veri tutarsızlığı, API downtime        |
| **Governance** | Aşırı AI otonomisi, insan override eksikliği         |
| **Sosyal**     | Abuse, organize exploit, vatandaş güven kaybı        |

---

### 4.2 Ekonomik Riskler

**1. Over-Emission / Enflasyon**

* Sebep: Hatalı DRM, agresif teşvik
* Sonuç: NCR değeri erir, vatandaş geliri reel anlamda düşer
* Savunma:
  * Emission caps (gün/hafta/ay)
  * Economic Guard kontrolü
  * Emergency mode: Emission stop + burn artışı

**2. Under-Reward / Gelir Çöküşü**

* Sebep: Fazla sıkı DPR/DRM, korkak politika
* Sonuç: Citizen churn, ekosistem aktifliği düşer
* Savunma:
  * Minimum NCR/day garantisi
  * Low-level subsidies
  * Stimulus paketleri (Retention & GMV push)

**3. Treasury Risk**

* Sebep: Kontrolsüz buyback / gereksiz market müdahalesi
* Savunma:
  * Haftalık max %5 kullanım
  * Fiyat bandına bağlı **katı** kurallar (sadece <0.70 / >1.50 gibi)
  * Intervention log'larının public olması

---

### 4.3 Teknik Riskler

* **Model Drift** → Geçmiş veriye aşırı overfit, gerçek zamanlı şartlara uyumsuzluk
  * Çözüm: Periodik retrain + manuel sanity check

* **Data Quality Issues** → Eksik veya bozuk event'ler
  * Çözüm: Validation pipeline, anomaly detection (örneğin GMV = 0 ama DAU = yüksek ise alarm)

* **Infra Failure (API/DB)**
  * Çözüm:
    * Fallback: "Safe static policy mode"
    * Ödüller = conservative defaults
    * Emission & tax = sabit, AI devre dışı

---

### 4.4 Governance Riskleri

* **AI Overreach** → Model, vatandaşı ezmeye başlarsa
  * Çözüm:
    * Constitutional caps
    * Economic Guard veto
    * President override

* **Human Abuse** → President taraflı suistimal
  * Çözüm (politik, teknik değil ama not edilmeli):
    * On-chain governance log
    * Vatandaşların sistemden exit hakkı
    * Güven = veri + şeffaflık

---

### 4.5 Sosyal & Abuse Riskleri

* Çok hesap açıp farm yapanlar
* Bot'la görev kasanlar
* Creator/performer tarafının istismar girişimleri

**Savunma:**

* Quality Score
* Diminishing Returns
* Behavioral fingerprinting
* Ceza havuzu:
  * NCR yakımı
  * Rank/Level/Bar cezası
  * Gerekirse kalıcı uzaklaştırma

---

## 5. Implementation Notları (Dev Tarafı için)

Bu bölüm, gerçek sistem kurulumuna niyetlenenler için "zihin haritası".

---

### 5.1 Config & Parametre Dosyaları

Önerilen yapı:

```bash
config/
  economy.yml           # emission, burn, sinks, DRM limits
  governance.yml        # modes, override rules, ω ağırlıkları
  citizens.yml          # level bands, rank çarpanları, haklar
  tasks.yml             # task şemaları, kategori ağırlıkları
  fiscal.yml            # vergi, sübvansiyon, stimulus setleri
  risk_limits.yml       # meltdown eşikleri, uyarı bantları
```

Bu yapıyı, gerçek NovaCore repo'suna direkt uyarlayabilirsin.

---

### 5.2 Simulation Modu

Gerçek deployment'tan önce:

* **Offline Simulator**:
  * 30/60/90 günlük senaryolar
  * Farklı adoption hızları
  * Farklı emission ve GMV pattern'leri

* Çıktılar:
  * NCR fiyat baskısı
  * Treasury tüketimi
  * Citizen gelir dağılımı
  * Gini coefficient (income inequality metriği)

Amaç:
**"Teoride güzel duruyor" değil, "simülasyonda da patlamıyor" demek.**

---

### 5.3 Güvenli Varsayılanlar (Safe Defaults)

* DRM default = 1.0
* Emission default = konservatif (0.03–0.05% / gün)
* Yeni kullanıcı için NCR bonusu = düşük ama motive edici
* Treasury intervention = kapalı, sadece manual onayla açılan mod
* Task sayısı = az ama net (fazla karmaşık başlatma)

---

## 6. Versiyonlama & Parametre Yönetimi

Bu sistem yaşayan bir organizma.
Şu kurallar, uzun vadede oyunu bozmazsın diye:

---

### 6.1 Parametre Versiyonlama

Her büyük değişiklik:

* `ECONOMY_MODEL_VERSION`
* `TASK_ENGINE_VERSION`
* `GOVERNANCE_VERSION`

olarak loglanmalı.

Örn:

```json
{
  "economy_model_version": "1.4",
  "governance_version": "2.1",
  "tasks_engine_version": "1.4",
  "last_change_tx": "on-chain log id"
}
```

---

### 6.2 Breaking Change Kuralları

Şunlar **breaking** sayılır:

* Reward seviyelerinde >%30 tek seferde değişiklik
* Vergi / sübvansiyon bandının değiştirilmesi
* Treasury kullanım kurallarının gevşetilmesi
* Citizen haklarına dokunan her şey

Bu tip değişiklikler:

* "Ekonomik reform" olarak isimlendirilmeli
* Gerekçe + risk analizi + forecast ile birlikte yayınlanmalı
* Mümkünse testnet / shadow mode'da denenmeli

---

### 6.3 Human-In-The-Loop Prensibi

Ne kadar AI olursa olsun:

* Kritik kararlar = AI + insan birlikte
* "Körlemesine otonomi" yok
* President.BARON en azından:
  * Meltdown/economy mode switch
  * Büyük vergi/sübvansiyon değişiklikleri
  * Treasury kullanımları
  
  üzerinde onay mercii olarak kalır.

---

## 7. Appendix Final Statement

Bu ek bölüm:

* Tüm formülleri
* Değişkenleri
* AI motorlarını
* Risk matrisini
* Uygulama notlarını

**tek yerde** toplar.

Bundan sonrası artık "ben hayal ettim" alanı değil:

> **Matematik + makine + anayasa** alanı.

SiyahKare, bu ekle birlikte:

* Whitepaper'ı tamamlanmış,
* Governance / Economy / Citizen / Tasks / Appendix'i netleşmiş,
* AI-first MicroNation tasarımını bitirmiş bir **devlet taslağı**.

---

*Document Version: 1.0*
*Last Updated: December 2024*
*Authority: BARON*
*Appendix: Technical & Mathematical Reference*

