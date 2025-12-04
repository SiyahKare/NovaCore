# **SİYAHKARE – CITIZEN SYSTEM**

**Whitepaper v1.0 — Identity, Status & Income Framework**

---

## **1. Citizen Model: Kullanıcı Değil, Vatandaş**

SiyahKare, "user" kavramını bilerek reddeder.
Burada kimse "trafik" ya da "MAU" değildir.

> **SiyahKare'de herkes "Citizen" (Vatandaş) olarak konumlanır.**

Vatandaşlık sistemi üç eksen üzerine kuruludur:

1. **Level** → Üretim / katkı / emek seviyesi
2. **Rank** → Sosyal statü ve prestij katmanı
3. **Rights & Income** → Haklar ve kazanma kapasitesi

Bu üçlü, AI-ekonomi ile doğrudan bağlıdır.
Vatandaş = sadece görev yapan değil, **ekonomide payı olan aktör**.

---

## **2. Citizen Lifecycle (Vatandaş Yaşam Döngüsü)**

SiyahKare'de bir vatandaşın yolculuğu:

1. **Visitor** (Ziyaretçi)
2. **Citizen L0** (Kayıtlı ama aktif değil)
3. **Active Citizen (L1–L9)**
4. **Core Citizen (L10–L49)**
5. **Elite Citizen (L50–L89)**
6. **Sovereign Citizen (L90–L100)**

Bu lifecycle **Nasip Tasks**, GMV katkısı, sosyal etki ve stake davranışı üzerinden yönetilir.

---

## **3. Level Sistemi (L0–L100)**

Level = bir vatandaşın **ekosisteme yaptığı katkının kümülatif logaritmik ölçüsü**.
Kazandığın XP → Level'a dönüşür.

### **3.1 Level Aralıkları**

| Seviye Aralığı | Adı       | Tanım                                         |
| -------------- | --------- | --------------------------------------------- |
| L0             | Dormant   | Kayıtlı ama aktif değil                       |
| L1–L9          | Entry     | Sistemle tanışan, günlük görev yapan          |
| L10–L29        | Builder   | Düzenli katkı sağlayan, GMV üreten            |
| L30–L49        | Operator  | Davet eden, creator/miniapp destekleyen       |
| L50–L89        | Elite     | Ekosistemde ağırlığı olan, gelir odaklı       |
| L90–L100       | Sovereign | Devletin ekonomik omurgasına bağlı elit kesim |

---

### **3.2 XP → Level Formülü**

Level hesabı (bone-dry matematik):

```
Level = floor( log₁.₄(XP + 20) )
```

* Hızlı başlayan, sonra yavaşlayan bir eğri
* İlk 10 level kolay, sonrası "hak edilmiş seviye"

---

### **3.3 XP Kaynakları**

Vatandaş XP kazanır:

* **Nasip Tasks** (günlük/haftalık/aylık)
* **GMV katkısı** (harcama + referans + satış)
* **Streak (üst üste aktif günler)**
* **Creator / MiniApp katkısı**
* **Social Actions** (davet, paylaşım, community katkısı)

---

## **4. Rank Sistemi (Prestij Kademeleri)**

Level = sayısal seviye.
**Rank = sosyal kimlik.**

Rank, vatandaşa hem prestij hem bazı ayrıcalıklar sağlar.

### **4.1 Rank Kademeleri**

| Rank                      | Level Band (Öneri) | Vibe                               |
| ------------------------- | ------------------ | ---------------------------------- |
| **Bronze**                | L1–L9              | Yeni gelen, "çaba başlıyor"        |
| **Silver**                | L10–L24            | Düzenli emek veren                 |
| **Gold**                  | L25–L49            | Ekosisteme net katkı yapan         |
| **Platinum**              | L50–L74            | Çevresini de ekonomiyle tanıştıran |
| **Diamond**               | L75–L89            | Ekosistem lideri                   |
| **Legendary / Sovereign** | L90–L100           | Devletin üst elit tabakası         |

Rank sadece Level'a bağlı değildir.
Ayrıca:

* Nasip Bar istikrarı
* GMV katkısı
* Stake oranı
* Ceza geçmişi (fraud, abuse, afk)

gibi faktörler de ağırlık verir.

---

### **4.2 Rank Bonusları**

Rank, sadece vitrin değildir; direkt ekonomiye dokunur:

| Rank      | NCR Kazanç Çarpanı | Task Ödül Bonus | Priority                  |
| --------- | ------------------ | --------------- | ------------------------- |
| Bronze    | 1.00x              | –               | Normal kuyruğa            |
| Silver    | 1.05x              | +%5             | Normal                    |
| Gold      | 1.10x              | +%10            | Support önceliği          |
| Platinum  | 1.15x              | +%15            | Özel kampanya erişimi     |
| Diamond   | 1.20x              | +%20            | Whitelist, özel drop'lar  |
| Legendary | 1.25x              | +%25            | Governance, özel havuzlar |

Bu çarpanlar **DRM** ile birlikte çalışır:

```
Final_Reward = Base × DRM × Rank_Multiplier
```

---

## **5. Citizen Rights (Haklar)**

Governance bölümünde çerçevesi çizilen haklar, vatandaş katmanına indirgenir.

SiyahKare vatandaşı şu haklara sahiptir:

### **5.1 Economic Rights**

* Her vatandaşın **günlük kazanç fırsatı** hakkı vardır.
* Ödül mekanizmaları rastgele değil, formülsel ve öngörülebilirdir.
* Aynı işi yapan iki vatandaş, aynı ekonomik koşullarda **aynı ödülü** alır (level / rank farkı hariç).

### **5.2 Information Rights**

Vatandaş görebilir:

* Güncel DRM bandı
* Hangi moddayız? (Growth / Stabilization / Recovery)
* Kendi gelir istatistikleri
* Kendi Nasip Bar eğrisi
* Kendi GMV katkısı

### **5.3 Social Rights**

* Community kanallarına erişim
* Vatandaşlar arası trade & işbirliği
* Creator olarak yükselebilme hakkı

### **5.4 Exit Rights**

* NCR varlığını unstake etme (lock sürelerine saygı duyarak)
* Sistemden çekilme hakkı
* Hesap kapatma talebi

---

## **6. Citizen Obligations (Yükümlülükler)**

Hak varsa, yükümlülük de vardır.
Vatandaş:

### **1. Fraud yapmama**

* Bot, script, fake traffic yasaktır.
* Tespit edilirse: ceza, stake kesintisi, ban.

### **2. Ekosisteme zarar vermeme**

* Scam, phishing, dolandırıcılık yok.
* Başkasını sömürme odaklı davranış yasak.

### **3. Respect the System**

* Ekonomi = ortak alan.
* Hile yapan, herkesin gelirinden çalar.

### **4. Signal & Feedback**

* Hataları raporlamak
* Abuse'u bildirmek
* Yapıcı geri bildirim vermek → olumlu sinyal sayılır.

---

## **7. Nasip Bar: Davranış İstikrar Ölçüsü**

**Nasip Bar = Vatandaşın emek istikrarını ölçen içsel sayaç.**

* Skala: 0–100
* Günlük görev yaptıkça artar
* İnaktif oldukça düşer
* Çok agresif, spam davranışta "quality penalty" yer

### **7.1 Nasip Bar Etkileri**

| Aralık | Etki                                         |
| ------ | -------------------------------------------- |
| 0–20   | Ceza bölgesi: Ödüller -%30'a kadar düşebilir |
| 21–50  | Normal bölge: Standart kazanç                |
| 51–80  | Bonus bölge: Ödüller +%10'a kadar artar      |
| 81–100 | Nasip Mode: Ekstra bonuslar, gizli quest'ler |

### **7.2 Nasip Bar & Level/Ranks**

* Yüksek Level ama düşük Nasip Bar = "Eski ama pasif vatandaş"
* Orta Level ama yüksek Nasip Bar = "Yeni ama canavar çalışan"

AI bu farkı bilir ve ödülleri adil dağıtır.

---

## **8. Citizen Archetypes (Vatandaş Arketipleri)**

Ekosistemde davranış tiplerini anlamak için üç ana archetype kullanılır:

### **1) Worker Citizen (Task Odaklı)**

* En çok Nasip Tasks ile kazanır
* Günlük görev setlerini tamamlar
* Geliri: Task-to-earn + düşük stake + küçük GMV katkısı

### **2) Creator Citizen (Üreten)**

* Flirt / OnlyVips / MiniApps tarafında üretir
* GMV'yi doğrudan yükseltir
* Geliri: NCR + revenue share + bonus havuzları

### **3) Operator / Networker Citizen (Dağıtıcı)**

* İnsan getirir, trafik çeker, yayar
* Referral + network + community liderliği
* Geliri: Ref share + rank bonus + governance havuzları

Her vatandaş, zamanla bu üç arketipten birine veya hibritine evrilir.

---

## **9. Citizen Income Framework**

Whitepaper'ın Economy bölümündeki NCR modeliyle bağlantılı olarak, Citizen System şu gelir modelini sağlar:

```
Citizen_Monthly_Income = (Task_Income + Referral_Income + Creator_Share + Staking_Yield) × Rank_Multiplier × DRM_avg
```

### **9.1 Örnek: Level 10 – Gold Rank Vatandaşı**

* Günlük 8 görev → ~120 NCR
* Ay = 30 gün → 3.600 NCR
* Ortalama DRM = 1.05
* Rank Multiplier (Gold) = 1.10

```
Income = 3600 × 1.05 × 1.10 ≈ 4.158 NCR
```

> Mikro-ekonomik olarak:
> Bu kişi, sistemi düzenli kullandığında aylık anlamlı bir yan gelir elde eder.

---

## **10. Social Mobility (Sosyal Hareketlilik)**

SiyahKare, tasarım gereği "kast sistemi" kurmaz.
**Sosyal hareketlilik bilerek kolaylaştırılmıştır.**

### **10.1 Upward Mobility**

Aşağıdakiler, hızlı yükseliş için tasarlanmış:

* Yüksek Nasip Bar + streak serileri
* MiniApp / GMV katkısı
* Yüksek kaliteli invite
* Creator veya Operator rolüne evrilme

### **10.2 Downward Mobility**

Şu durumlarda "sosyal düşüş" yaşanır:

* Fraud / abuse / bot kullanımı
* Uzun süreli inaktivite
* Sürekli ekonomik zarar verici davranış

Sistem, vatandaşları **zorla yukarıda tutmaz**,
ama **hak edenin yukarı, bozanın aşağı inmesini** garanti eder.

---

## **11. Citizen Panel (Arayüz Tasarımı)**

Her vatandaşın göreceği ana panel:

* 📊 Level & Rank
* 💰 Son 7 gün NCR kazancı
* 📈 Nasip Bar grafiği
* 📦 Aktif görevler, biten görevler
* 🧮 Kişisel GMV katkısı
* 👥 Referans istatistikleri
* 🎖 Kazanılmış rozetler

Bu panel:

> "Ben kimim, ne kadar üretiyorum, ne kadar kazanıyorum, nereye gidiyorum?"
> sorularına cevap verir.

---

## **12. Citizen System – Governance ile Bağlantı**

Citizen System, Governance ve Economy bölümleriyle üçlü bir sacayağı oluşturur:

* Governance → **kural ve sınırları** belirler
* Economy → **para ve akışları** yönetir
* Citizen System → **kimin ne aldığı, ne yaptığı, nasıl yükseldiğini** belirler

Böylece:

> Vatandaş ≠ rastgele kullanıcı
> Vatandaş = Anayasal güvenceli, AI-ekonomi destekli, gelir üreten bir dijital kimlik

---

## **13. Citizen System Final Statement**

SiyahKare'nin Citizen System'i şunları sağlar:

* Kullanıcıyı "scroll eden tüketici" olmaktan çıkarır
* Vatandaşı "üreten, kazanan, statü sahibi" bir aktöre dönüştürür
* Gelir, statü ve haklar **matematiksel**, **AI-denetimli**, **anayasal korumalı** hale gelir
* Sosyal mobilite **mümkün**, sistem istismarı **zor** hale gelir

Bu yapı sayesinde:

> **"SiyahKare vatandaşı olmak" = sadece bir hesap açmak değil,
> bir dijital mikro-devlete dahil olmak demektir.**

---

*Document Version: 1.0*
*Last Updated: December 2024*
*Authority: BARON*
*System: Citizen Framework v1.0 (Level / Rank / Nasip Bar)*

