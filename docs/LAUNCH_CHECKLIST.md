# 🚀 Launch Checklist - Cohort-1 Hazırlık

**Tarih:** 2025-12-04  
**Versiyon:** V1.0  
**Hedef:** 5-15 kişilik kontrollü test grubu için hazırlık

---

## ✅ Tamamlanan Özellikler

- ✅ Quest Submission Pipeline
- ✅ AI Scoring Service V1
- ✅ Marketplace Core
- ✅ Telegram Bot Komutları
- ✅ Content Delivery
- ✅ Launch Pack Copy'leri
- ✅ Onboarding Mesajı
- ✅ Marketplace Seed Script

---

## 📋 Launch Öncesi Checklist

### 1. Backend Hazırlık

- [ ] Backend çalışıyor mu? (`uvicorn app.main:app --reload`)
- [ ] Database migration'ları çalıştırıldı mı?
- [ ] OpenAI API key set edildi mi? (`OPENAI_API_KEY`)
- [ ] Telegram Bridge Token set edildi mi? (`TELEGRAM_BRIDGE_TOKEN`)
- [ ] Treasury User ID set edildi mi? (`NCR_TREASURY_USER_ID`)

### 2. Telegram Bot Hazırlık

- [ ] Bot token set edildi mi? (`TELEGRAM_BOT_TOKEN`)
- [ ] Bot çalışıyor mu? (`python -m nasipquest_bot.main`)
- [ ] `/start` komutu onboarding mesajını gösteriyor mu?
- [ ] `/görevler` komutu quest'leri gösteriyor mu?
- [ ] Text yakalama handler çalışıyor mu?

### 3. Marketplace Seed

- [ ] Seed script çalıştırıldı mı? (`python scripts/seed_marketplace_launch.py`)
- [ ] 20-30 ACTIVE item oluşturuldu mu?
- [ ] `/market` komutu item'leri gösteriyor mu?
- [ ] Demo creator user'ları var mı? (ID: 1, 2, 3)

### 4. Test Kullanıcıları

- [ ] 5-10 test kullanıcısı belirlendi mi?
- [ ] Onlara davet mesajı gönderildi mi?
- [ ] Cohort-1 Telegram grubu oluşturuldu mu? (opsiyonel)

### 5. Metrik Takip

- [ ] Metrik takip sistemi hazır mı?
- [ ] Günlük metrikler toplanacak mı?
- [ ] Post-mortem için geri bildirim formu hazır mı?

---

## 🎯 İlk 3 Gün Planı

### Gün 1

**Sabah:**
- [ ] Backend ve bot çalışıyor mu kontrol et
- [ ] Marketplace seed çalıştır
- [ ] Test kullanıcılarına davet mesajı gönder

**Akşam:**
- [ ] Metrikleri kontrol et:
  - Kaç kişi `/tasks` gördü?
  - Kaç proof geldi?
  - AI score dağılımı?
  - AbuseGuard risk artışı var mı?

### Gün 2

**Sabah:**
- [ ] Gün 1 metriklerini gözden geçir
- [ ] Sorun varsa düzelt
- [ ] Günlük hatırlatma mesajı gönder (opsiyonel)

**Akşam:**
- [ ] Metrikleri kontrol et
- [ ] Kullanıcı geri bildirimlerini topla

### Gün 3

**Sabah:**
- [ ] Gün 2 metriklerini gözden geçir
- [ ] Sorun varsa düzelt
- [ ] Günlük hatırlatma mesajı gönder (opsiyonel)

**Akşam:**
- [ ] Metrikleri kontrol et
- [ ] Kullanıcı geri bildirimlerini topla

---

## 📊 Günlük Metrikler (Akşam Kontrolü)

### Engagement

- [ ] `/tasks` kullanan kişi sayısı: [X]
- [ ] En az 1 proof gönderen kişi sayısı: [Y]
- [ ] Ortalama proof sayısı: [Z]

### Quality

- [ ] Ortalama AI score: [A]
- [ ] 70+ oranı: [%]
- [ ] Marketplace'e gönderilen item sayısı: [B]

### Economy

- [ ] Toplam mint edilen NCR: [C]
- [ ] Marketplace harcaması: [D]
- [ ] Treasury'ye giren NCR: [E]

### Risk

- [ ] Ortalama RiskScore değişimi: [F]
- [ ] TOXIC_CONTENT event: [G]
- [ ] LOW_QUALITY_BURST event: [H]

---

## 🔧 Hızlı Komutlar

### Backend Başlat

```bash
cd /Users/onur/code/DeltaNova_System/NovaCore
uvicorn app.main:app --reload
```

### Bot Başlat

```bash
cd /Users/onur/code/DeltaNova_System/NovaCore
python -m nasipquest_bot.main
```

### Marketplace Seed

```bash
cd /Users/onur/code/DeltaNova_System/NovaCore
python scripts/seed_marketplace_launch.py
```

### Database Kontrol

```bash
# Quest'leri kontrol et
psql -d novacore -c "SELECT COUNT(*) FROM user_quests WHERE status = 'assigned';"

# Marketplace item'leri kontrol et
psql -d novacore -c "SELECT COUNT(*) FROM marketplace_items WHERE status = 'active';"

# Proof'ları kontrol et
psql -d novacore -c "SELECT COUNT(*) FROM quest_proofs;"
```

---

## 📝 Post-Mortem Soruları (1 Hafta Sonra)

### 1. Nerede Tıkanıyor?

- Görevler çok mu zor?
- Sistem yavaş mı?
- Anlaşılmayan bir şey var mı?

### 2. Hangi Görevleri Seviyorsun / Sarmıyor?

- MONEY görevleri nasıl?
- SKILL görevleri nasıl?
- INTEGRITY görevleri nasıl?

### 3. Marketplace'ten Gerçekten "İşe Yarar Şey" Satın Alıyor musun?

- Hangi ürünleri aldın?
- İşe yaradı mı?
- Fiyatlar uygun mu?

### 4. Genel Görüşlerin?

- Sistem çalışıyor mu?
- Abuse var mı?
- İyileştirme önerilerin?

---

## 🚨 Acil Durum Planı

### Sorun: Backend Çöküyor

1. Log'lara bak (`tail -f logs/app.log`)
2. Database connection kontrol et
3. Gerekirse backend'i restart et

### Sorun: Bot Çalışmıyor

1. Bot token kontrol et
2. Bridge token kontrol et
3. Backend'e bağlanabiliyor mu kontrol et

### Sorun: Marketplace Boş

1. Seed script'i tekrar çalıştır
2. Item'lerin status'ünü kontrol et
3. Creator user'ları kontrol et

### Sorun: Kullanıcılar Quest Göremiyor

1. Quest factory çalışıyor mu kontrol et
2. Database'de quest kayıtları var mı kontrol et
3. Bot handler'ları kontrol et

---

## 📚 Dokümantasyon

- `docs/LAUNCH_PACK_COPY.md` - Görev copy'leri
- `docs/ONBOARDING_MESSAGE.md` - Onboarding mesajı
- `docs/COHORT1_MESSAGE_TEMPLATE.md` - Cohort-1 mesaj şablonları
- `docs/FIRST_3_DAYS_QUEST_SCRIPT.md` - İlk 3 günlük quest script'i
- `app/marketplace/seed_launch.py` - Marketplace seed script

---

**Launch Checklist V1.0 - Hazır!** 🚀

**Sonraki Adım:** Backend ve bot'u başlat, marketplace seed çalıştır, test kullanıcılarına davet gönder!

