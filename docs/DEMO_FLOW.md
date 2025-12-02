# Aurora Citizen Pitch Demo Flow (v1)

Bu doküman, AuroraOS'u birine **10–15 dakikada** anlatırken kullanacağın canlı demo akışıdır.  
Amaç: "Bu sadece app değil, gerçekten çalışan bir **dijital devlet protokolü**" hissini net vermek.

---

## 0. Setup (Demo Öncesi)

**Tek gereksinim:**

- Backend açık:

  ```bash
  uvicorn app.main:app --reload
  ```

* Postgres + migration'lar tamam (activate_aurora_state.sh zaten hallediyor)

* Citizen Portal çalışıyor:

  ```bash
  cd apps/citizen-portal
  npm run dev
  ```

**Tarayıcıda aç:**

* Citizen Portal: `http://localhost:3000`
* Gerekirse Admin Panel: `http://localhost:3000/admin/aurora`

---

## 1. 5 Dakikalık "Hızlı State Pitch"

> Kullanıcı yorgun, süren kısıtlı. "Bu ne?" sorusuna net cevap.

### Adım 1 — Landing (Home)

* Git: `/`

* Cümle (kısa):

  > "Aurora bir uygulama değil; üç katmanlı bir dijital devlet motoru.
  > Vatandaşın verisini, skorunu ve cezasını **anayasaya bağlı** yönetiyor."

* Hero'daki "How it works" 3 bullet'a dokun:

  * Veri egemenliği
  * NovaScore & CP
  * DAO policy

---

### Adım 2 — Manifesto & Mimarî (`/about`)

* Git: `/about`

Anlatım iskeleti:

1. **Hero cümlesi:**

   > "Burası Aurora'nın manifestosu. Yani fikrin hukuki ve teknik omurgası."

2. Soldaki 3 katman kartını oku:

   * Katman 1: Anayasa & Veri Egemenliği
   * Katman 2: NovaScore & Justice Engine
   * Katman 3: DAO & Policy

3. Sağdaki paneli göster:

   * NovaScoreCard (gerçek veriye bağlıysa: "bak bu senin canlı durumun")
   * RegimeBadge → "Vatandaşın hangi rejimde olduğunu gösteriyor."
   * PolicyBreakdown:

     > "Ceza ağırlıkları, decay, threshold'lar **DAO'nun kontrolünde**. Hard-code yok."

4. "How Aurora Works" 4-step grid:

   * Onboarding & kimlik
   * Consent & PLA
   * NovaScore & CP
   * Enforcement & DAO

**Burada amaç:**

"Her şey endpoint + ledger + hukuk katmanına bağlı" duygusunu vermek.

---

### Adım 3 — Demo (`/demo`)

* Git: `/demo`

Burada tek cümle ile sahne:

> "Şimdi sana aynı sistemi, 3 farklı vatandaşın gözüyle göstereceğim."

Sol panelden sırasıyla geçir:

1. **Clean Citizen**

   * Rejim: NORMAL, CP ≈ 0
   * NovaScore yüksek.
   * Allowed/blocked listelerini göster:

     > "Bak burada hiçbir aksiyon bloklanmıyor."

2. **Probation Citizen**

   * Rejim: PROBATION
   * Açıklama:

     > "Bu vatandaş birkaç ihlal yapmış. Hâlâ sistemde, ama spotlight altında."
   * Allowed/blocked listesi:

     * "Messaging var ama riskli."
     * "Bazı yüksek riskli işlemler kısılmış."

3. **Lockdown Citizen**

   * Rejim: LOCKDOWN, CP yüksek
   * DemoActionButton'lara dikkat çek:

     * Send Message → Ghost/disabled
     * Withdraw → Ghost/disabled
   * Cümle:

     > "Bu profilde butonlar sadece görsel değil; backend de aynı aksiyonları 403 ile tokatlıyor."

**Pitch note alanını oku:**

> "Bu sayfa Aurora'yı ilk defa görene şunu göstermek için:
> Bu sadece puanlama değil; ceza, veri, politika ve UI hepsi aynı protokolün parçası."

Burada kısa dur, soruları al.

---

## 2. 15 Dakikalık "Deep Dive Devlet Motoru" Demo

> Karşındaki kişi developer / founder / regulator kafasında → Derine in.

### 2.1. Consent & Constitution (Academy + Backend)

1. Git: `/academy/modules/constitution`

   * RecallRequest component'ini göster:

     > "Vatandaş, verisini sistemden geri çektirdiğinde, NovaScore'daki confidence düşüyor; bu hukuki hakkı teknik bir prosedüre bağlıyoruz."

2. Terminal (isteğe bağlı):

   * `app/consent/router.py`
   * `ConsentRecord`, `UserPrivacyProfile` göster:

     * `/consent/session`
     * `/consent/clauses`
     * `/consent/redline`
     * `/consent/sign`

   Cümle:

   > "İmza attığın an, bu tabloya immutable kayıt düşüyor.
   > Her NovaScore çağrısında önce bu profile bakıyoruz → policy-aware skor."

---

### 2.2. NovaScore & CP (Dashboard + Justice)

1. Git: `/dashboard`

   * RegimeBanner + RegimeMessage:

     > "Ekran temasının bile rejime bağlı olduğu bir UX devleti bu."

2. Eğer istersen:

   * `/admin/aurora/stats` → CP ortalamaları, regime dağılımı
   * `/admin/aurora/violations` → real-time violation stream

3. **Dev pitch:**

   > "Violation → CP → Regime → Enforcement zinciri tamamen loglanıyor.
   > Aynı zamanda DAO kontrollü policy ile simüle edilebilir halde."

---

### 2.3. DAO & Policy Governance

1. Git: `/admin/aurora/policy` (veya policy view neyse)

   * Policy breakdown UI:

     > "Bu ekrandaki parametreler, on-chain AuroraPolicyConfig kontratından geliyor / gelecek.
     > Bizim backend sadece bunu cacheleyip uyguluyor."

2. Terminal (isteğe bağlı):

   * `contracts/AuroraPolicyConfig.sol`
   * `app/justice/policy_service.py`
   * `scripts/simulate_aurora_policies.py`

   Cümle:

   > "Policy değiştirmek istediğinde önce bu script ile 1000 vatandaş üzerinde simüle ediyorsun,
   > sonra DAO proposal açıyorsun, oylama geçerse sync script ile backend'e indiriyorsun."

---

## 3. Demo Konuşma İskeleti (Kısa Versiyon)

Standart 2–3 dakikalık elevator pitch:

1. **Opening:**

   > "Aurora, AI çağında kurulmuş bir dijital devlet protokolü.
   > Verini, skorunu ve cezanı **anayasaya bağlı**, şeffaf ve DAO kontrollü yönetiyor."

2. **Göster: `/about`**

   > "Burada üç katmanlı yapıyı görüyorsun: Consent & Anayasa, NovaScore & Adalet, DAO & Policy."

3. **Göster: `/demo`**

   > "Aynı sistemi üç vatandaş üzerinden simüle ediyoruz: temiz, risk altı, kilitli.
   > UI, backend ve policy hepsi aynı rejime göre davranıyor."

4. **Kapat:**

   > "Fark şu: Aurora bir feature set değil, kendi anayasası olan küçük bir devlet motoru.
   > Sen istersen FlirtMarket'e, istersen başka bir sosyal/finansal ağa bunu embed edebilirsin."

---

## 4. Notlar / Püf Noktaları

* Çok teknik birine → `/admin/aurora` ve `scripts/simulate_aurora_policies.py` göster.

* Daha soyut düşünen birine → `/demo` ve `/academy` yeter, backend'e inmene gerek yok.

* Lockdown demoda mutlaka şunu söyle:

  > "Burada gördüğün her kısıtlama; verisi, violation log'u, CP'si ve policy parametresiyle desteklenmiş gerçek bir karar."

---

## 5. Checklist (Demo Öncesi)

* [ ] Backend up (`uvicorn app.main:app --reload`)
* [ ] DB + migration tamam (`alembic upgrade head`)
* [ ] `activate_aurora_state.sh` en az bir kere çalıştı
* [ ] Citizen Portal `npm run dev`
* [ ] `/about` + `/demo` sorunsuz açılıyor
* [ ] Admin kullanıcı ile login olabiliyorsun (gerekirse)

---

Aurora Citizen Pitch Kit v1 bu akışla **sahnede, Zoom'da, kahve masasında** direkt kullanılabilir.

