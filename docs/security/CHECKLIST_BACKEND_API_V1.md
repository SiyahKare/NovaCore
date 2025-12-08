# Backend API Security Checklist (NovaCore / CORE)

**Versiyon:** v1.0  
**Son Güncelleme:** 2025-12-04  
**Uygulama:** Her PR öncesi kontrol edilmeli

---

## 1. Auth & Identity

- [ ] Tüm state değiştirici endpoint'ler **auth zorunlu** (No open POST/PUT/DELETE).
- [ ] Auth için tek bir kaynak katman var (`/auth` middleware, decorator vs) – endpoint içinde `if user_id` kontrolü yok.
- [ ] JWT / session içinde **sadece ID + zorunlu claims** var, hassas veri (role listesi dışında) taşınmıyor.
- [ ] Token expiry mantıklı (access kısa, refresh uzun).
- [ ] Telegram auth (geldiğinde):
  - [ ] `initData` backend'de _signature verify_ ediliyor.
  - [ ] Sadece backend `Telegram Bot Token` ile doğruluyor, frontta hiçbir sır yok.

---

## 2. Authorization (Yetki)

- [ ] `user_id` her zaman **token'dan** geliyor, body/params'tan gelen ID sadece hedef obje için.
- [ ] "Kendi hesabım" aksiyonlarında: `where owner_id = current_user.id` filtresi zorunlu.
- [ ] Admin endpoint'leri:
  - [ ] Ayrı prefix: `/admin/*`
  - [ ] Ayrı role: `role = admin`
  - [ ] Loglanıyor (kim, ne zaman, ne yaptı).

---

## 3. Wallet & Ledger

- [ ] İşlem mantığı **tek bir "service/usecase" katmanında**; controller içinde balans hesaplanmıyor.
- [ ] Ledger **append-only**: UPDATE yok, sadece INSERT + soft revert.
- [ ] Tüm ekonomik işlemler:
  - [ ] idempotent (aynı request tekrar gelirse double charge yok).
  - [ ] tek transaction içinde DB commit.
- [ ] Negatif balance mümkün değil (constraint + kod kontrolü).
- [ ] "Promotional / bonus coin" işlemleri **flag** ile işaretli (audit için).

---

## 4. Input & Output

- [ ] Tüm public endpoint body/params'ları **schema validation**'dan geçiyor (pydantic / zod).
- [ ] Chat/message alanları:
  - [ ] max length sınırlı (örn: 2000 char).
  - [ ] HTML / script injection temizleniyor veya plain text olarak tutuluyor.
- [ ] Error message'lar stack trace, DB error, internal info sızdırmıyor.

---

## 5. Rate Limit & Abuse

- [ ] Auth'suz endpoint'ler için IP bazlı rate limit var.
- [ ] Auth'lu kritik endpoint'ler için user bazlı rate limit:
  - [ ] first-message send
  - [ ] offer gönderme
  - [ ] coin transfer
- [ ] Brute force'a açık hiçbir login endpoint'i yok (Telegram geldiğinde bile).

---

## 6. Logging & Audit

- [ ] Wallet / coin / premium işlemleri audit log'a yazılıyor:
  - [ ] `who`, `what`, `amount`, `reason`, `ip`, `user_agent`.
- [ ] Sensitive data (password, token, secrets) log'lanmıyor.
- [ ] Admin aksiyonları ayrı loglanıyor.

---

## 7. Secrets & Config

- [ ] DB URL, JWT secret, Telegram token, Stripe vs kesinlikle ENV'de – repo'da yok.
- [ ] Dev/prod config'leri ayrı `.env` dosyaları; hiçbir `.env` commit'lenmiyor.
- [ ] Config default değerleri güvenli (prod'da debug kapalı).

---

## 📝 Notlar

- Bu checklist her PR'da kontrol edilmeli.
- Kritik değişikliklerde (auth, wallet, admin) threat model'e referans verilmeli.
- Güvenlik açığı bulunursa: `SECURITY.md` dosyasındaki prosedürü takip et.


