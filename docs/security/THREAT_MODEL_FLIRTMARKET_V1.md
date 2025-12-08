# FlirtMarket Threat Model v1

**Versiyon:** v1.0  
**Son Güncelleme:** 2025-12-04  
**Durum:** Aktif - Her kritik değişiklikte güncellenmeli

---

## 1. Varlıklar (Assets)

### Kritik Varlıklar

- **Kullanıcı profilleri** (fotoğraflar, bio, preferences)
- **Chat mesajları** (private messages, match conversations)
- **Match data** (kim kimi beğendi, match history)
- **Coin transactions** (Flirt Coin, premium coin, payment history)
- **Premium subscriptions** (VIP status, subscription data)
- **User location** (yakınlık bazlı matching için)

### Hassas Varlıklar

- **Payment data** (credit card last 4 digits, payment method)
- **Telegram user data** (telegram_id, username, profile picture)
- **Behavioral data** (swipe patterns, message frequency, engagement metrics)

---

## 2. Aktörler

### Normal Aktörler

- **Free user** (limited features, coin-based messaging)
- **Premium user** (VIP status, unlimited messaging)
- **Performer** (content creator, verified account)
- **Admin** (platform moderation, user management)

### Saldırgan Aktörler

- **Catfish / Fake profile** (sahte kimlik, fotoğraf çalma)
- **Harasser** (rahatsız edici mesajlar, spam)
- **Scammer** (finansal dolandırıcılık, fake payment)
- **Data harvester** (kullanıcı verisi toplama, scraping)

---

## 3. Ana Saldırı Yüzeyleri

### 3.1 Telegram MiniApp

- **WebApp initData** (Telegram authentication)
- **Frontend state** (client-side manipulation riski)
- **Real-time messaging** (WebSocket / polling)
- **Photo upload** (profile picture, chat images)

### 3.2 Matching & Discovery

- **Swipe API** (like/dislike endpoints)
- **Profile viewing** (photo viewing, bio reading)
- **Location-based matching** (proximity calculation)

### 3.3 Messaging System

- **First message** (coin cost, rate limiting)
- **Chat history** (message storage, retrieval)
- **Media sharing** (photo, video sharing)

### 3.4 Payment & Premium

- **Coin purchase** (payment gateway integration)
- **Premium subscription** (recurring payment)
- **Coin transfer** (user-to-user transfer)

---

## 4. Örnek Tehdit Senaryoları

### T1 – Fake Profile / Catfish

**Amaç:** Sahte kimlik ile kullanıcıları kandırmak, fotoğraf çalmak.

**Vektörler:**
- **Stolen photos**: Başkasının fotoğrafını kullanma
- **Fake identity**: Sahte isim, yaş, bio
- **Bot accounts**: Automated fake profiles

**Mitigation:**
- ✅ Photo verification (gelecekte: selfie verification)
- ✅ Telegram verified account requirement (premium için)
- ✅ Report system: Kullanıcılar fake profile rapor edebilir
- ✅ Admin moderation queue: Şüpheli profiller review ediliyor
- ✅ Behavioral analysis: Bot detection (swipe patterns, message patterns)

**Risk Seviyesi:** 🟡 **ORTA** (User trust, platform reputation)

---

### T2 – Harassment / Spam

**Amaç:** Kullanıcıları rahatsız etmek, spam mesaj göndermek.

**Vektörler:**
- **Unlimited messaging**: Rate limit bypass
- **Abusive content**: NSFW, toxic messages
- **Stalking**: Sürekli mesaj gönderme, takip etme

**Mitigation:**
- ✅ First message coin cost (3 FC) - spam engelleme
- ✅ Rate limit: User bazlı mesaj limiti (günlük/hourly)
- ✅ Block system: Kullanıcılar block edebilir
- ✅ Report system: Harassment rapor edilebilir
- ✅ AbuseGuard: RiskScore calculation, auto-ban (yüksek risk)
- ✅ Content moderation: AI + human review

**Risk Seviyesi:** 🟡 **ORTA** (User experience, legal risk)

---

### T3 – Payment Fraud

**Amaç:** Ödeme yapmadan coin kazanmak, fake payment ile premium almak.

**Vektörler:**
- **Payment gateway bypass**: Fake payment confirmation
- **Chargeback abuse**: Ödeme yapıp sonra iptal etme
- **Coin manipulation**: Backend'de coin balance manipulation (NovaCore T1)

**Mitigation:**
- ✅ Payment gateway webhook verification (signature check)
- ✅ Idempotency: Aynı payment request tekrar işlenmez
- ✅ Transaction logging: Tüm payment'lar audit log'da
- ✅ Chargeback handling: Chargeback durumunda coin geri alınır
- ✅ NovaCore wallet security (T1 mitigation'ları geçerli)

**Risk Seviyesi:** 🔴 **YÜKSEK** (Financial loss)

---

### T4 – Data Harvesting / Scraping

**Amaç:** Kullanıcı verilerini toplamak, profile fotoğraflarını çalmak.

**Vektörler:**
- **API scraping**: Automated API calls ile profile data toplama
- **Photo download**: Profile fotoğraflarını toplu indirme
- **Database dump**: Unauthorized DB access (NovaCore T3)

**Mitigation:**
- ✅ Rate limiting: IP ve user bazlı limit
- ✅ CAPTCHA: Şüpheli aktivite için CAPTCHA (gelecekte)
- ✅ Photo protection: Watermark, CDN protection
- ✅ API authentication: Tüm endpoint'ler auth gerektiriyor
- ✅ NovaCore data leakage protection (T3 mitigation'ları geçerli)

**Risk Seviyesi:** 🟡 **ORTA** (Privacy violation, legal risk)

---

### T5 – Location Privacy

**Amaç:** Kullanıcıların konumunu kötüye kullanmak, stalking.

**Vektörler:**
- **Exact location leak**: Tam koordinat sızıntısı
- **Location tracking**: Sürekli konum takibi
- **Proximity calculation abuse**: Yakınlık hesaplama ile konum tahmin

**Mitigation:**
- ✅ Approximate location: Sadece yaklaşık konum (city/district level)
- ✅ Location privacy settings: Kullanıcılar konum paylaşımını kapatabilir
- ✅ No exact coordinates: Tam koordinat saklanmıyor, sadece proximity hesaplanıyor
- ✅ Location data retention: Eski konum verileri siliniyor

**Risk Seviyesi:** 🟡 **ORTA** (Privacy violation, safety risk)

---

### T6 – Match Manipulation

**Amaç:** Matching algoritmasını manipüle edip istenmeyen kullanıcılarla eşleşmek.

**Vektörler:**
- **Swipe bot**: Automated swiping ile match sayısını artırma
- **Profile manipulation**: Fake preferences ile algoritmayı kandırma
- **Location spoofing**: Fake location ile farklı bölgeden match

**Mitigation:**
- ✅ Rate limiting: Swipe limiti (günlük/hourly)
- ✅ Behavioral analysis: Bot detection (swipe patterns)
- ✅ Location verification: Telegram location (gelecekte)
- ✅ Match quality score: Sadece kaliteli match'ler gösteriliyor

**Risk Seviyesi:** 🟢 **DÜŞÜK** (User experience)

---

## 5. Risk Matrisi

| Tehdit | Olasılık | Etki | Risk Seviyesi | Öncelik |
|--------|----------|------|---------------|---------|
| T1 - Fake Profile / Catfish | Yüksek | Orta | 🟡 ORTA | P1 |
| T2 - Harassment / Spam | Yüksek | Orta | 🟡 ORTA | P1 |
| T3 - Payment Fraud | Düşük | Yüksek | 🔴 YÜKSEK | P0 |
| T4 - Data Harvesting | Orta | Orta | 🟡 ORTA | P1 |
| T5 - Location Privacy | Düşük | Orta | 🟡 ORTA | P2 |
| T6 - Match Manipulation | Düşük | Düşük | 🟢 DÜŞÜK | P3 |

**Öncelik Seviyeleri:**
- **P0**: Kritik - Hemen ele alınmalı
- **P1**: Yüksek - Yakın zamanda ele alınmalı
- **P2**: Orta - Planlanmalı
- **P3**: Düşük - İleride ele alınabilir

---

## 6. FlirtMarket Özel Güvenlik Gereksinimleri

### NSFW Content Moderation

- ✅ AI scoring: Content quality ve NSFW detection
- ✅ Human review: Şüpheli içerikler admin queue'da
- ✅ Report system: Kullanıcılar içerik rapor edebilir
- ✅ Auto-ban: Yüksek risk içerik otomatik ban

### User Safety

- ✅ Block system: Kullanıcılar block edebilir
- ✅ Report system: Harassment rapor edilebilir
- ✅ Emergency contact: Acil durum desteği (gelecekte)
- ✅ Safety tips: Kullanıcılara güvenlik ipuçları (gelecekte)

### Payment Security

- ✅ PCI compliance: Payment data güvenli saklanıyor
- ✅ 3D Secure: Payment gateway 3D Secure desteği
- ✅ Refund policy: Açık refund politikası
- ✅ Chargeback handling: Chargeback durumunda otomatik işlem

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

- [NovaCore Threat Model](./THREAT_MODEL_NOVACORE_V1.md)
- [Telegram MiniApp Security](https://core.telegram.org/bots/webapps#security)
- [Dating App Security Best Practices](https://owasp.org/www-project-mobile-security/)


