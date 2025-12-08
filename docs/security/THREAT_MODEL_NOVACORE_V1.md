# NovaCore Threat Model v1

**Versiyon:** v1.0  
**Son Güncelleme:** 2025-12-04  
**Durum:** Aktif - Her kritik değişiklikte güncellenmeli

---

## 1. Varlıklar (Assets)

### Kritik Varlıklar

- **Kullanıcı kimliği** (identity, Telegram link, email)
- **Wallet bakiyeleri** (NCR, Flirt Coin, premium coin)
- **Ledger kayıtları** (tüm ekonomik geçmiş, transaction history)
- **Chat mesajları** (kişisel içerik, private messages)
- **Admin panelindeki kontrol aksiyonları** (user ban, coin adjustment, policy changes)
- **User data** (profile, preferences, behavioral data)

### Hassas Varlıklar

- **API keys** (Telegram Bot Token, OpenAI API Key, payment gateway keys)
- **Database credentials** (connection strings, passwords)
- **JWT secrets** (token signing keys)
- **Log files** (potansiyel PII içerebilir)

---

## 2. Aktörler

### Normal Aktörler

- **Normal kullanıcı** (free account, limited permissions)
- **Premium kullanıcı** (paid account, extended features)
- **Performer / Operator** (content creator, agency operator)
- **Admin / Internal staff** (full system access)

### Saldırgan Aktörler

- **Kendi hesabı ile gelen saldırgan** (insider user, account takeover)
- **Dışarıdan istek atan attacker** (no auth, brute force)
- **Yetkili ama kötü niyetli admin** (privileged insider threat)
- **Automated bot / script** (spam, abuse, DDoS)

---

## 3. Ana Saldırı Yüzeyleri

### 3.1 Public API (HTTP)

- **REST endpoints** (`/api/v1/*`)
- **GraphQL** (eğer varsa)
- **WebSocket** (real-time features)
- **Rate limiting bypass** riski
- **Input validation bypass** riski

### 3.2 Telegram WebApp Giriş Noktası

- **Telegram initData** signature verification
- **Frontend → Backend** communication
- **Client-side state manipulation** riski
- **XSS** (Cross-Site Scripting) riski

### 3.3 Admin Paneli

- **Admin endpoints** (`/admin/*`)
- **Role-based access control** (RBAC)
- **Audit logging**
- **Privilege escalation** riski

### 3.4 CI/CD + Deploy Pipeline

- **GitHub Actions** / CI secrets
- **Docker image** security
- **Deployment scripts**
- **Supply chain attack** riski

### 3.5 3rd Party Servisler

- **Payment gateway** (Stripe, PayPal)
- **Telegram Bot API**
- **OpenAI API** (AI scoring)
- **Cloudflare Tunnel** (network dependency)
- **External API compromise** riski

---

## 4. Örnek Tehdit Senaryoları

### T1 – Coin / Wallet Manipülasyonu

**Amaç:** Kendine sınırsız coin yazdırmak veya başkasının bakiyesini çalmak.

**Vektörler:**
- **ID spoof**: Başka `user_id` ile işlem gönderme
- **Double spend**: Aynı request'i spam'leyip race condition arama
- **Negative balance bypass**: Constraint bypass ile negatif bakiye oluşturma
- **Ledger manipulation**: Direct DB access ile ledger kayıtlarını değiştirme

**Mitigation:**
- ✅ Tüm wallet işlemleri tek service + transaction (atomicity)
- ✅ `owner_id = current_user` enforce (authorization)
- ✅ Idempotency key (örn: `request_id`) ile duplicate prevention
- ✅ Database constraint: `CHECK (balance >= 0)`
- ✅ Ledger append-only: UPDATE yok, sadece INSERT + soft revert
- ✅ Audit logging: Tüm wallet işlemleri log'lanıyor

**Risk Seviyesi:** 🔴 **YÜKSEK** (Finansal kayıp)

---

### T2 – Unauthorized Admin Access

**Amaç:** Admin API'lerine sızıp tüm sistemi yönetmek.

**Vektörler:**
- **Admin flag manipulation**: Client-side admin flag'ine müdahale
- **Weak auth**: Token theft, leaked admin secret
- **Privilege escalation**: Normal user'dan admin'e yükseltme
- **Session hijacking**: JWT token çalınması

**Mitigation:**
- ✅ Admin role server-side + separate endpoint (`/admin/*`)
- ✅ Admin actions full audit log (kim, ne zaman, ne yaptı)
- ✅ JWT token expiry (kısa access token, uzun refresh token)
- ✅ IP whitelist / VPN requirement (production admin panel)
- ✅ Multi-factor authentication (MFA) - gelecekte eklenebilir

**Risk Seviyesi:** 🔴 **YÜKSEK** (Sistem kontrolü kaybı)

---

### T3 – Kullanıcı Verisi Sızıntısı

**Amaç:** Chat logları, özel bilgiler, fotoğraflar, PII (Personally Identifiable Information).

**Vektörler:**
- **Hatalı SQL filtreleri**: Başkasının verisini çekmek (`WHERE user_id = ...` eksik)
- **Backup / log yanlış konfig**: PII içeren log'lar public erişilebilir
- **API response leakage**: Başka kullanıcının verisi response'ta dönüyor
- **Database dump**: Unauthorized DB backup erişimi

**Mitigation:**
- ✅ Her sorguda `where user_id = current_user` filtresi zorunlu
- ✅ Log'larda PII minimum (sadece user_id, timestamp)
- ✅ Backup erişimi sınırlı (sadece authorized personnel)
- ✅ API response validation (sadece authorized data dönüyor)
- ✅ GDPR / KVKK uyumlu (right to deletion, data portability)

**Risk Seviyesi:** 🟡 **ORTA** (Privacy violation, legal risk)

---

### T4 – Abuse / Harassment

**Amaç:** Kadın kullanıcıları rahatsız etmek, spam, platform kötüye kullanımı.

**Vektörler:**
- **Free account spam**: Sınırsız ilk mesaj gönderme
- **Yeni hesap spam**: Multiple account creation
- **Automated bot**: Script ile otomatik mesaj gönderme
- **Report abuse**: False report ile masum kullanıcıları banlatma

**Mitigation:**
- ✅ First message coin cost (3 FC) - spam engelleme
- ✅ Rate limit: User bazlı mesaj limiti
- ✅ AbuseGuard: RiskScore calculation, cooldown enforcement
- ✅ Report + block sistemi: Kullanıcılar rapor edebilir
- ✅ Admin moderasyon queue: Şüpheli içerikler review ediliyor
- ✅ Account verification: Telegram verified account requirement (gelecekte)

**Risk Seviyesi:** 🟡 **ORTA** (User experience, platform reputation)

---

### T5 – API Rate Limit Bypass

**Amaç:** Rate limit'i bypass edip sistem kaynaklarını tüketmek (DDoS).

**Vektörler:**
- **IP rotation**: Farklı IP'lerden istek gönderme
- **Distributed attack**: Multiple source'dan koordineli saldırı
- **Authentication bypass**: Auth gerektirmeyen endpoint'lere spam
- **Slowloris attack**: Yavaş isteklerle connection pool'u tüketme

**Mitigation:**
- ✅ IP bazlı rate limit (auth'suz endpoint'ler)
- ✅ User bazlı rate limit (auth'lu endpoint'ler)
- ✅ Cloudflare protection (DDoS mitigation)
- ✅ Connection timeout: Yavaş istekler kesiliyor
- ✅ Circuit breaker: Yüksek error rate'te endpoint kapanıyor

**Risk Seviyesi:** 🟡 **ORTA** (Availability, performance)

---

### T6 – Input Validation Bypass

**Amaç:** SQL injection, XSS, command injection ile sistem kontrolü.

**Vektörler:**
- **SQL injection**: Raw SQL query'lerde user input kullanımı
- **XSS**: Frontend'de user input'un sanitize edilmemesi
- **Command injection**: System command'lerinde user input kullanımı
- **Path traversal**: File system'e unauthorized erişim

**Mitigation:**
- ✅ Pydantic schema validation (backend)
- ✅ Zod schema validation (frontend)
- ✅ SQLModel / ORM kullanımı (SQL injection koruması)
- ✅ HTML sanitization (XSS koruması)
- ✅ Input length limits (DoS koruması)
- ✅ File upload validation (path traversal koruması)

**Risk Seviyesi:** 🔴 **YÜKSEK** (System compromise)

---

### T7 – Telegram Auth Bypass

**Amaç:** Telegram WebApp authentication'ı bypass edip başka kullanıcı olarak giriş yapmak.

**Vektörler:**
- **initData signature bypass**: Signature verification eksik/hatalı
- **Token replay**: Eski token'ı tekrar kullanma
- **Man-in-the-middle**: initData'yı intercept edip değiştirme
- **Client-side manipulation**: Frontend'de user_id değiştirme

**Mitigation:**
- ✅ Backend'de `initData` signature verify (Telegram Bot Token ile)
- ✅ JWT token expiry (token süresi dolunca geçersiz)
- ✅ HTTPS only (MITM koruması)
- ✅ Frontend'de kritik değerler backend'ten alınıyor (client-side manipulation koruması)

**Risk Seviyesi:** 🔴 **YÜKSEK** (Account takeover)

---

## 5. Risk Matrisi

| Tehdit | Olasılık | Etki | Risk Seviyesi | Öncelik |
|--------|----------|------|---------------|---------|
| T1 - Coin/Wallet Manipülasyonu | Yüksek | Yüksek | 🔴 YÜKSEK | P0 |
| T2 - Unauthorized Admin Access | Düşük | Çok Yüksek | 🔴 YÜKSEK | P0 |
| T3 - Kullanıcı Verisi Sızıntısı | Orta | Orta | 🟡 ORTA | P1 |
| T4 - Abuse / Harassment | Yüksek | Düşük | 🟡 ORTA | P1 |
| T5 - API Rate Limit Bypass | Orta | Orta | 🟡 ORTA | P1 |
| T6 - Input Validation Bypass | Düşük | Çok Yüksek | 🔴 YÜKSEK | P0 |
| T7 - Telegram Auth Bypass | Düşük | Çok Yüksek | 🔴 YÜKSEK | P0 |

**Öncelik Seviyeleri:**
- **P0**: Kritik - Hemen ele alınmalı
- **P1**: Yüksek - Yakın zamanda ele alınmalı
- **P2**: Orta - Planlanmalı
- **P3**: Düşük - İleride ele alınabilir

---

## 6. Güvenlik Kontrol Noktaları

### Code Review Checklist

- [ ] Threat model'e referans verildi mi?
- [ ] Security checklist uygulandı mı?
- [ ] Test coverage yeterli mi? (özellikle security-critical kod)
- [ ] Error handling güvenli mi? (stack trace sızdırmıyor mu?)

### Deployment Checklist

- [ ] Secrets ENV'de mi? (hardcode yok mu?)
- [ ] Database migration güvenli mi? (data loss riski var mı?)
- [ ] Rate limiting aktif mi?
- [ ] Monitoring ve alerting kurulu mu?

---

## 7. Güncelleme Süreci

Bu threat model:

- **Her kritik değişiklikte** gözden geçirilmeli
- **Yeni tehdit keşfedildiğinde** güncellenmeli
- **Yılda en az bir kez** tam review edilmeli
- **Security incident sonrası** mutlaka güncellenmeli

**Son Güncelleme:** 2025-12-04  
**Sonraki Review:** 2026-03-04

---

## 📚 Referanslar

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [Telegram Bot API Security](https://core.telegram.org/bots/api#security)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/advanced/security/)


