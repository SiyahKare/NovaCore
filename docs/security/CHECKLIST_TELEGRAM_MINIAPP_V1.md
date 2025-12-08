# FlirtMarket – Telegram MiniApp Security Checklist

**Versiyon:** v1.0  
**Son Güncelleme:** 2025-12-04  
**Uygulama:** Her PR öncesi kontrol edilmeli

---

## 1. WebApp Init & Auth

- [ ] Miniapp sadece Telegram WebApp context'te kritik aksiyonlara izin veriyor (dev ortamı hariç).
- [ ] `initData` backend'e forward edilip signature verify ediliyor.
- [ ] Frontend, `user_id` / `telegram_id` gibi kritik değerleri sadece backend'ten JSON olarak alıyor.

---

## 2. Navigation & State

- [ ] Kullanıcı login değilken `/app/*` rotalarına giremiyor (guard / redirect).
- [ ] Onboarding tamamlanmadan Discover/Chats'e geçilemiyor (flag).

---

## 3. Coin UI Mantığı

- [ ] İlk mesaj butonları (Mesaj gönder / Sohbet başlat) her zaman:
  - [ ] "3 FC" cost bilgisini gösteriyor.
  - [ ] Backend'ten gelen gerçek balance'a göre enable/disable.
- [ ] "Coin'in yetersiz" modali, state ile uyumlu (fake gösterge yok).

---

## 4. Input & Abuse

- [ ] Mesaj input'ları:
  - [ ] max karakter sınırı
  - [ ] basic profanity / spam guard ileride backend'de.
- [ ] Client tarafında hiçbir "gizli admin", "gizli feature flag" tamamen güvene alınmıyor (server side tekrar check).

---

## 5. Premium / Her Zaman Aktif Profiller

- [ ] UI'da AI/BOT kelimesi geçmiyor.
- [ ] İnsan kullanıcıyı dürten hiçbir otomasyon "kandırıcı" değil (no dark pattern).

---

## 📝 Notlar

- Bu checklist FlirtMarket Telegram MiniApp PR'ları için geçerlidir.
- Kritik değişikliklerde (auth, coin logic, premium features) threat model'e referans verilmeli.
- Güvenlik açığı bulunursa: `SECURITY.md` dosyasındaki prosedürü takip et.


