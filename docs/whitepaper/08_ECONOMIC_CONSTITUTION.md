# **SİYAHKARE NCR EKONOMİ ANAYASASI v1.0**

**Whitepaper v1.0 — Economic Constitution**

---

## **Madde 1 – Resmî Dijital Para Birimi**

### 1.1. NCR Tanımı

SiyahKare Devleti'nin tek resmî dijital para birimi **NCR (Nasip Credit)**'dir.

### 1.2. NCR Kullanım Alanı

Tüm görev ödülleri, market ödemeleri, stake havuzları ve devlet içi transferler **yalnızca NCR** cinsinden hesaplanır.

### 1.3. Vatandaşlık Ölçüsü

"Gerçek vatandaşlık seviyesi", sahip olunan parayla değil; **kazanılmış NCR + NovaScore** kombinasyonuyla ölçülür.

```
Citizen_Value = f(Earned_NCR, NovaScore)
```

---

## **Madde 2 – Emek İlkesi (Fundamental Law)**

### 2.1. Emek Temelli Basım

NCR, **yalnızca emek karşılığında** basılabilir.

### 2.2. Emek Tanımı

Emek; sistem tarafından tanımlanmış **görevlerin (Quest)** kurallara uygun biçimde tamamlanmasıyla ölçülür.

### 2.3. Temel Kural

> **"Emek yoksa, NCR de yoktur."**

### 2.4. Geçersiz Kazanç

Referral, exploit, hile veya sahte aktiviteyle üretilen her NCR, **geçersiz** sayılır ve geri alınır.

### 2.5. Otomatik Uygulama

AbuseGuard tarafından "emeksiz kazanç" tespit edilen tüm işlemler, **otomatik iptal + ceza** sürecine girer.

---

## **Madde 3 – NCR Kazanma Mekanizması**

### 3.1. Base Ödül

Her görev bir **BaseNCR** değeri ile tanımlanır.

### 3.2. Final Ödül Formülü

Vatandaşın alacağı fiili ödül:

```
NCR_final = BaseNCR × RewardMultiplier(user)
```

### 3.3. RewardMultiplier Bileşenleri

`RewardMultiplier(user)` aşağıdaki sinyallerden türetilir:

| Sinyal | Ağırlık | Açıklama |
|--------|---------|----------|
| **StreakFactor** | 1.0-1.3 | Üst üste aktif gün sayısı |
| **SiyahScoreFactor** | 0.7-1.2 | İş kalitesi (AI değerlendirme) |
| **RiskFactor** | 0.0-1.0 | Ahlak/abuse riski (düşük risk = yüksek) |
| **NovaFactor** | 0.5-1.5 | Vatandaşlık seviyesi çarpanı |

### 3.4. Detaylı Formül

```python
def compute_reward_multiplier(user: UserContext) -> float:
    # Streak Factor (1.0 - 1.3)
    streak_factor = 1.0 + min(user.streak_days, 30) / 100.0
    
    # SiyahScore Factor (0.7 - 1.2)
    siyah_factor = 0.7 + (user.siyah_score_avg / 100.0) * 0.5
    
    # Risk Factor (0.0 - 1.0): Düşük risk = yüksek çarpan
    risk_factor = max(0.0, 1.0 - user.risk_score / 10.0)
    
    # Nova Factor (0.5 - 1.5): Vatandaşlık seviyesine göre
    nova_factor = CITIZEN_LEVEL_MULTIPLIERS[user.citizen_level]
    
    # Final multiplier
    multiplier = streak_factor * siyah_factor * risk_factor * nova_factor
    
    # Clamp to reasonable bounds
    return max(0.1, min(2.0, multiplier))
```

### 3.5. Adalet Prensibi

Böylece **ahlaklı, istikrarlı ve kaliteli** vatandaşlar aynı görevi yaparak **daha fazla NCR** kazanır.

---

## **Madde 4 – NCR Harcama Alanları**

### 4.1. Birincil Kullanım (Tier 1)

Kazanılan NCR, öncelikle:

| Alan | Açıklama |
|------|----------|
| **Market** | Ürün/hizmet satın alma |
| **Sosyal Upgrade** | Avatar, profil, rol yükseltme |
| **Premium Erişim** | Eğitim, mentorluk, özel oda |

### 4.2. İkincil Kullanım (Tier 2)

| Alan | Açıklama |
|------|----------|
| **Stake Havuzları** | Kilitleme ile pasif getiri (Treasury'den yeniden dağıtım) |
| **DAO Ağırlığı** | Yönetim oylamalarında söz hakkı |
| **Whitelist/Event** | Özel etkinliklerde öncelik |

**ÖNEMLİ:** Stake ödülleri, yeni NCR basımıyla değil; Treasury'deki mevcut NCR havuzunun yeniden dağıtımıyla ödenir. Bu, "Emek yoksa mint yok" ilkesini korur.

### 4.3. Off-Ramp (Fiat Çıkış)

Fiat'a çıkış (off-ramp) varsa, bu işlem her zaman **fee + burn** ile çalışır:

```
NCR_withdrawn = NCR_requested × (1 - off_ramp_fee)
NCR_burned = NCR_requested × off_ramp_fee × burn_ratio
```

---

## **Madde 5 – Enflasyon Kontrolü ve Burn**

### 5.1. Emisyon Limitleri

Toplam **NCR emisyonu**, günlük/haftalık limitler ve görev bütçeleriyle sınırlıdır:

| Limit Türü | Değer | Açıklama |
|------------|-------|----------|
| `daily_emission_cap` | Dinamik | DRM ile kontrol |
| `weekly_emission_cap` | Dinamik | Makro ekonomi dengesi |
| `task_pool_budget` | Sabit/Periyodik | Görev havuzu bütçesi |

### 5.2. Burn Mekanizması

Market ve off-ramp işlemlerinde, her işlemden alınan **fee'nin bir kısmı yakılır (burn)**:

```
NCR_burn = α × Fee_collected

# Örnek:
# Fee = %5
# Burn ratio (α) = 0.5
# 100 NCR işlem → 5 NCR fee → 2.5 NCR burn
```

### 5.3. Ekonomik Denge

| Giriş (Mint) | Çıkış (Burn/Freeze) |
|--------------|---------------------|
| Emek (Görev Ödülleri) | Market Fee Burn |
| Stake Ödülleri | Off-Ramp Fee Burn |
| Referral Bonusu | Ceza/Geri Alma |
| | Inactivity Freeze |

### 5.4. Terk Edilmiş Bakiyeler

Uzun süre kullanılamayan, terk edilmiş bakiyeler belirli kurallar dahilinde **Hazinede pasif varlık** olarak işaretlenir; rastgele dağılmaz.

```python
# Inactivity kuralı
if user.last_activity_days > INACTIVITY_THRESHOLD:
    user.balance_status = "FROZEN"
    treasury.add_frozen_balance(user.id, user.ncr_balance)
```

---

## **Madde 6 – Emek Dışı Kazancın Geçersizliği**

### 6.1. Geçersiz Kazanç Türleri

Aşağıdaki yollarla üretilen NCR **hükümsüzdür**:

| Tip | Açıklama | Kod |
|-----|----------|-----|
| **Bot/Script Spam** | Otomatik görev tamamlama | `FRAUD_BOT` |
| **Multi-Account** | Sybil saldırısı | `FRAUD_SYBIL` |
| **Exploit/Bug** | Sistem açığı kullanımı | `FRAUD_EXPLOIT` |
| **Plagiarism** | Başka kullanıcının çıktısını kopyalama | `FRAUD_COPY` |

### 6.2. Uygulanan Yaptırımlar

Bu durumlarda:

```python
def handle_fraud(user_id: str, fraud_type: str, amount: float):
    # 1. NCR geri alınır/yakılır
    clawback_ncr(user_id, amount)
    
    # 2. RiskScore yükselir
    increase_risk_score(user_id, FRAUD_RISK_DELTAS[fraud_type])
    
    # 3. Ceza uygulanır
    apply_sanction(user_id, fraud_type)
    
    # 4. Log tutulur (şeffaflık)
    log_fraud_event(user_id, fraud_type, amount)
```

### 6.3. Ceza Matrisi

| Fraud Tipi | NCR Geri Alma | Risk Delta | Ek Ceza |
|------------|---------------|------------|---------|
| `FRAUD_BOT` | %100 | +3.0 | 7 gün cooldown |
| `FRAUD_SYBIL` | %100 | +5.0 | Tüm hesaplar freeze |
| `FRAUD_EXPLOIT` | %100 | +5.0 | Kalıcı ban (inceleme ile) |
| `FRAUD_COPY` | %100 | +2.0 | 3 gün cooldown |

---

## **Madde 7 – Vatandaşın Hakkı**

### 7.1. Tasarruf Hakkı

Her vatandaş, **kendi emeğiyle kazandığı NCR üzerinde tam tasarruf hakkına** sahiptir.

### 7.2. Şeffaflık Zorunluluğu

Sistem, açık ve anlaşılır bir şekilde göstermek **zorundadır**:

| Bilgi | Endpoint | Açıklama |
|-------|----------|----------|
| Görev Kazancı | `/wallet/history` | Hangi görevden kaç NCR |
| Ceza/Fee/Burn | `/wallet/deductions` | Ne kaybedildiği ve sebebi |
| NovaScore | `/nova-score/me` | Güncel vatandaşlık skoru |
| RiskScore | `/justice/risk/me` | Güncel risk skoru |

### 7.3. İtiraz Hakkı

Vatandaş, haksız bulduğu her işleme itiraz edebilir:

```
POST /justice/appeals
{
    "type": "clawback" | "sanction" | "burn",
    "transaction_id": "...",
    "reason": "..."
}
```

---

## **Madde 8 – Ekonomik Garanti**

### 8.1. Sistemin Taahhütleri

SiyahKare ekonomisi şunları **garanti eder**:

✔ **Emek = Kazanç**: Çalışan kazanır, çalışmayan kazanamaz

✔ **Şeffaf Kurallar**: Tüm formüller açık ve denetlenebilir

✔ **Adil Dağılım**: Ahlaklı vatandaş daha çok kazanır

✔ **Enflasyon Kontrolü**: Burn + Limit ile değer koruması

✔ **Tasarruf Güvenliği**: Haksız el koyma yok

### 8.2. Sistemin Yapamayacakları

SiyahKare ekonomisi şunları **yapamaz**:

✖ Sebepsiz NCR yaratma (emeksiz basım)

✖ Keyfi bakiye silme (şeffaf kural olmadan)

✖ Gizli fee uygulama (tüm kesintiler görünür)

✖ Vatandaşı bilgilendirmeden kural değiştirme

---

## **Madde 9 – Ekonomik Modlar**

### 9.1. Normal Mod

Standart ekonomi kuralları geçerli.

### 9.2. Growth Mod

Yeni vatandaş kazanımı için:
- Onboarding bonusları aktif
- Referral ödülleri yüksek
- Emission limitleri genişletilmiş

### 9.3. Stabilization Mod

Enflasyon riski varsa:
- DRM düşürülür (ödüller azalır)
- Burn oranı artırılır
- Stake teşvikleri yükseltilir

### 9.4. Recovery Mod

Ekonomik kriz durumunda:
- Acil burn aktivasyonu
- Emission durdurma
- Hazine müdahalesi

---

## **Madde 10 – Ekonomi Yönetimi**

### 10.1. Yetkili Organlar

| Organ | Yetki |
|-------|-------|
| **Neural Governor** | Günlük/haftalık emission |
| **Fiscal AI** | Vergi/sübvansiyon dengesi |
| **Yield Balancer** | Stake ödülleri |
| **Economic Guard** | Anayasal kontrol |
| **President (BARON)** | Override & veto |

### 10.2. Karar Alma Süreci

```
1. AI Önerisi → Neural Governor
2. Risk Analizi → Economic Guard
3. Anayasa Kontrolü → Constitution Check
4. Uygulama / Override → President
```

---

## **Final Statement**

Bu Ekonomi Anayasası, SiyahKare'nin ekonomik temelini oluşturur:

> **NCR = Emek + Güven + Katkı**

Emeksiz kazanç yok. Kuralsız ceza yok. Şeffaflıksız işlem yok.

Bu prensiplerle SiyahKare:
- **Sürdürülebilir** bir mikro-ekonomi
- **Adil** bir dağıtım sistemi
- **Güvenilir** bir değer deposu

olarak konumlanır.

---

*Document Version: 1.0*
*Last Updated: December 2025*
*Authority: BARON*
*System: NCR Economic Constitution v1.0*

