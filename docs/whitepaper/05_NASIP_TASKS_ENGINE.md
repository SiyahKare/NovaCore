# **SİYAHKARE – NASIP TASKS ENGINE**

**Whitepaper v1.0 — Task-to-Earn Monetary Engine**

---

## **1. Amaç: "Nasip = Çaba → Kazanç" Motoru**

Nasip Tasks Engine, SiyahKare ekonomisinin **birincil gelir üretim makinesidir**.

* Vatandaş için:
  → "Günlük somut çaba → ölçülebilir NCR geliri"
* Devlet için:
  → "GMV, büyüme, retention ve veri toplama motoru"
* Ekonomi için:
  → "Token dağıtımının kontrollü, adil ve hedefli yapılması"

> **Nasip Tasks Engine = Emek → Gelir → GMV → Veri Döngüsü.**

---

## **2. Tasarım İlkeleri**

1. **Çabasız kazanç yok**
   → Tüm NCR ödülleri bir davranışa bağlanır.

2. **Ekonomik dengeden kopuk task yok**
   → Ödül seviyeleri, AI-ekonomi (DRM, Fiscal AI, Neural Governor) ile entegre.

3. **Kısa vadeli pump yok**
   → Task yapısı spekülatif değil, üretim odaklı.

4. **Türkiye gerçeğine uygun**
   → 5–10 dakika / gün → mikro gelir → sadakat.

5. **Anti-exploit**
   → Bot, script, spam davranış; sistem tasarımında doğrudan cezalıdır.

---

## **3. Task Kategorileri (Core Taxonomy)**

Tüm görevler beş ana ligde toplanır:

### **3.1 Growth Tasks (Büyüme Görevleri)**

Ekosistemi genişleten görevler.

Örnekler:

* Davet linki ile yeni citizen getirme
* MiniApp paylaşımı
* Sosyal medya (IG/TikTok) görevleri
* Flirt / OnlyVips profil paylaşımı
* Referral aktivasyonu

**Hedef:** kullanıcı + GMV büyümesi
**Ödül:** yüksek XP, orta NCR

---

### **3.2 Engagement Tasks (Bağlılık Görevleri)**

Vatandaşı sistemde tutan "ritüel" görevler.

Örnekler:

* Günlük check-in
* Citizen panelini açma
* Nasip Bar skoru görme
* En az 1 MiniApp tamamlama
* Creator içeriği izleme

**Hedef:** retention
**Ödül:** yüksek XP, düşük NCR

---

### **3.3 GMV Tasks (Gelir Üreten Görevler)**

Doğrudan **harcama → GMV** üreten görevler.

Örnekler:

* Premium mesaj atma
* PPV (pay-per-view) içerik açma
* Boost / premium özellik satın alma
* Creator shop üzerinden alışveriş
* AI servislerine ödeme yapma

**Hedef:** GMV & fee & burn
**Ödül:** orta XP, yüksek NCR

---

### **3.4 Creator Tasks (Üreten Taraf Görevleri)**

Creator ve MiniApp sahiplerini merkeze alır.

Örnekler:

* Yeni içerik yükleme
* PPV paket oluşturma
* AI avatar prompt'u set etme
* Günlük/haftalık yayın hedeflerini tamamlama
* MiniApp'e yeni özellik ekleme veya veri aktarma

**Hedef:** supply tarafı → içerik/servis hacmi
**Ödül:** yüksek NCR + yüksek XP

---

### **3.5 Prestige Tasks (Statü Görevleri)**

Level, rank, rozet, streak gibi soyut değerleri besler.

Örnekler:

* 7 gün üst üste aktif kal
* Profilini tamamla / güncelle
* Belli bir GMV hedefini aş
* Belirli bir rank'a ulaş
* Özel event / sezon görevleri

**Hedef:** uzun vadeli bağlılık & statü ekonomisi
**Ödül:** XP + küçük NCR + görsel prestij

---

## **4. Task Şeması (Makine Dostu Tanım)**

Tüm görevler aşağıdaki şemaya göre tanımlanır:

```json
{
  "task_id": "GROWTH_INVITE_01",
  "category": "growth",
  "title": "1 Yeni Vatandaş Davet Et",
  "description": "Kişisel davet linkinle 1 yeni citizen getir.",
  "difficulty": 3,
  "ecosystem_impact": 4,
  "effort": 2,
  "base_rewards": {
    "ncr": 15,
    "xp": 0
  },
  "limits": {
    "max_per_day": 5,
    "cooldown_hours": 24
  },
  "constraints": {
    "requires_level": 1,
    "max_level": null
  },
  "tracking": {
    "event": "invite_accepted",
    "min_quality_score": 0.4
  }
}
```

---

## **5. XP Sistemi (v1.0)**

XP, vatandaşın **çaba ve etki** skorudur.
XP formülü:

```
XP = D × E × C
```

* **D (Difficulty)**: Görevin zorluğu (1–5)
* **E (Ecosystem Impact)**: Ekosisteme fayda katsayısı (1–4)
* **C (User Effort)**: Kullanıcı açısından emek düzeyi (1–3)

Örnek:

* 3 zorluk
* 4 etki
* 2 çaba

```
XP = 3 × 4 × 2 = 24
```

Bu XP, Citizen System'de tanımlanan **Level** formülüne akar.

---

## **6. NCR Ödül Sistemi (v1.0 → v1.4 Entegrasyon)**

Temel NCR ödül formülü:

```
NCR_task = NCR_base × DRM × Rank_Multiplier × NasipBar_Multiplier
```

Nerede:

* **NCR_base** → Task'ın kendi taban ödülü
* **DRM** → Dynamic Reward Multiplier (0.5–1.5, ekonomi moduna göre)
* **Rank_Multiplier** → Citizen rank'ine göre (Bronze 1.0x → Legendary 1.25x)
* **NasipBar_Multiplier** → Nasip bar aralığına göre (~0.7–1.2)

### **6.1 Nasip Bar Çarpanı**

| Nasip Bar | Çarpan              |
| --------- | ------------------- |
| 0–20      | 0.7x (ceza bölgesi) |
| 21–50     | 1.0x (nötr)         |
| 51–80     | 1.1x (bonus)        |
| 81–100    | 1.2x (Nasip Mode)   |

---

## **7. Günlük / Haftalık / Aylık Görev Setleri**

### **7.1 Günlük Görev Paketi (Daily Loop)**

Playtime: 5–15 dakika.
Amaç:

* Günlük login
* Ekonomiye hafif katkı
* Nasip Bar stabilizasyonu

Örnek günlük set:

| Görev                    | Kategori       | Ödül (base NCR) |
| ------------------------ | -------------- | --------------- |
| Check-in yap             | engagement     | 5 NCR           |
| 1 içerik izle            | engagement     | 5 NCR           |
| 1 MiniApp kullan         | engagement/gmv | 10 NCR          |
| 1 arkadaşına link gönder | growth         | 10 NCR          |
| Citizen paneline bak     | engagement     | 3 NCR           |

---

### **7.2 Haftalık Quest Paketi**

Amaç: "gerçek emek" → anlamlı mikro gelir.

Örnek:

* 5 yeni invite → 60 NCR + 100 XP
* 7 gün üst üste en az 1 görev → 50 NCR + 80 XP
* 10 premium mesaj / işlem → 70 NCR + 120 XP
* 3 PPV içerik aç → 40 NCR + 70 XP

Haftalık toplam potansiyel:
**≈ 150–300 NCR + kayda değer XP**

---

### **7.3 Aylık Master Quest'ler**

Büyük ödüller, sadık vatandaş içindir.

Örnek aylık quest:

* 20 invite
* 30 MiniApp tamamla
* 15 GMV üreten aksiyon
* 100+ günlük görev tamamla

Ödül:
**300–500 NCR + özel rozet + rank boost + gizli görev açılışları**

---

## **8. Dynamic Yield Balancer Entegrasyonu (v1.1)**

v1.1 ile Nasip Tasks Engine, **ekonominin durumuna göre otomatik ayarlanan bir yield** sistemine dönüşür.

DRM'in çekirdek fikri:

```
DRM = f(GMV_momentum, Active_Users, Stake_ratio, NasipBar_health, Economy_Stress)
```

* Ekonomi şişerse → **DRM düşer** (ödüller azalır)
* Ekonomi zayıflarsa → **DRM artar** (ödüller yükselir)

Bu, reward sistemini:

* ne çok cömert,
* ne de çok cimri

bırakmadan **otomatik denge** sağlar.

Detay formüller Economy bölümünde tanımlıdır; burada sadece **bağlantı** önemlidir:

> **Nasip Tasks Engine, kendi kendine değil, ekonomi beyniyle birlikte çalışır.**

---

## **9. ML Adaptive Yield (v1.2) & Predictive AI (v1.3)**

v1.2 ve v1.3 seviyesinde:

* Görev ödülleri
* DRM seviyeleri
* Kategori ağırlıkları (growth vs engagement vs gmv)

artık **ML modelleri** tarafından ayarlanır.

### **9.1 Öğrenen Görev Ekonomisi**

Model, şunları sürekli analiz eder:

* Hangi görevler GMV getiriyor?
* Hangi görevler retention sağlıyor?
* Hangi görevler bot'a açık?
* Hangi vatandaş tipi hangi görevleri seviyor?

Sonuç:

* Kullanılmayan görevler ağırlık kaybeder
* Aşırı kullanılan / abuse riski olan görevler optimize edilir
* GMV'yi büyüten görevler daha cazip hale gelir

### **9.2 3 Haftalık Tahmin Entegrasyonu (v1.3)**

Predictive AI (v1.3):

* 21 gün sonra GMV, DAU, churn, stake trendini tahmin eder
* Eğer 3 hafta sonra GMV düşüş riski varsa:
  → bugünden growth ve GMV görevlerinin ödülünü yükseltir
* Eğer 3 hafta sonra emission şişiyorsa:
  → bugünden daha düşük NCR base'ler ve DRM uygular

Nasip Tasks Engine =
**sadece bugüne değil, geleceğe göre çalışan ekonomik planlayıcı.**

---

## **10. Fiscal AI & Vergi / Sübvansiyon Etkisi (v1.4)**

Görev ödülleri, Fiscal AI tarafından da "net gelir" olarak yeniden şekillenir.

Örnek:

* High earner citizen → küçük oranda rake/stopaj
* Low-level citizen → +% bonus sübvansiyon
* Yeni citizen → onboarding bonusu
* Comeback citizen → geri dönüş bonusu

Sonuç:
**Zengin daha da zengin olsun diye değil, ekonomide alt taban da kazansın diye tasarlanmış bir task ekonomisi.**

---

## **11. Anti-Exploit & Güvenlik Katmanı**

Nasip Tasks Engine, abuse engellemek için tasarlanmış güvenlik önlemlerine sahiptir.

### **11.1 Düşen Getiri (Diminishing Returns)**

* Günlük 10+ aynı tip task → ödül kademeli olarak düşer.
* Spam yapan, farm mantığına kayan davranış → ekonomik olarak anlamsızlaşır.

### **11.2 Quality Score**

Her task:

* "Tamamlandı" + "kalite sinyali" ile değerlendirilir.

Örneğin:

* Davet edilen hesap → 0 dakika sonra terk etmişse
* Premium mesaj → SPAM olarak işaretlendiyse

Bu görevlerin **NCR ödülü kırpılır**, XP'si düşürülür.

### **11.3 Behavioral Fingerprinting**

* Aşırı hızlı tıklama
* Tekrarlayan pattern
* Tek cihazdan onlarca hesap
  → Bot riski olarak işaretlenir.

Ceza:

* NCR silme
* Rank düşürme
* Nasip Bar çakma
* Gerekirse ban

---

## **12. Görev Yaşam Döngüsü (Devlet Perspektifi)**

### **1. Design**

* Ekonomik hedef belirlenir (growth / gmv / retention)
* Task tipi tanımlanır
* Base XP & NCR belirlenir

### **2. Simulate**

* Yield, DRM, Fiscal AI ile "simulate" edilir
* Aşırı ödül veya bug riski varsa düzeltilir

### **3. Deploy**

* Production'a alınır
* Vatandaş panelinde görünür

### **4. Monitor**

* Kullanım istatistikleri
* GMV etkisi
* Abuse sinyalleri

### **5. Adapt**

* ML modelleri görevi yeniden ağırlıklandırır
* Gerekirse ödüller güncellenir
* Gerekirse emekliye ayrılır veya yeni varyantı gelir

---

## **13. Örnek Görev Paketi – L10 Citizen İçin**

Bir **L10 Gold Citizen** için tipik bir gün:

* 5 günlük görev →
  ≈ 60–100 NCR
* 2 growth görevi →
  ≈ 30–50 NCR
* 1 GMV görevi (küçük harcama) →
  ≈ 20–40 NCR (NCR + on-chain fayda)

Toplam:
**≈ 110–190 NCR / gün (DRM & rank & Nasip Bar'a göre)**

Bu, Economy & Citizen bölümleriyle birleşince,
**aylık anlamlı bir yan gelir** oluşturur.

---

## **14. Version Roadmap (Nasip Tasks Engine)**

| Version | Feature |
|---------|---------|
| **v1.0** | Core Task Taxonomy + XP/NCR formülleri |
| **v1.1** | Dynamic Yield Balancer (DRM) entegrasyonu |
| **v1.2** | ML Adaptive Yield (kendi kendine öğrenen ödül sistemi) |
| **v1.3** | Predictive Economic AI (3-week forecast) |
| **v1.4** | Autonomous Fiscal AI (vergi + sübvansiyon entegrasyonu) |
| **v2.0+** | Neural Governor & Cognitive Constitution ile tam entegrasyon |

---

## **15. Final Statement – Nasip Tasks Engine**

Nasip Tasks Engine:

* Kullanıcıyı **görev yapan köle** değil,
  **gelir üreten vatandaş** yapar.
* Ekonomiyi **pump & dump oyuncağı** değil,
  **AI tarafından dengelenen mikro-devlet bütçesi** haline getirir.
* Davranışı **tesadüfi** değil,
  **ölçülebilir, yönlendirilebilir ve ödüllendirilebilir** kılar.

> **SiyahKare'de "Nasip" bir bahane değil,
> matematiksel olarak işletilen bir motor haline gelir.**

---

*Document Version: 1.0*
*Last Updated: December 2024*
*Authority: BARON*
*Engine: Nasip Tasks Engine v1.4 (ML & Fiscal AI integrated)*

