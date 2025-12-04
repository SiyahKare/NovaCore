# NovaCore Academy v1 - Eğitim & Growth Motoru

## 🎓 Overview

NovaCore Academy, vatandaşların SiyahKare / Aurora Justice sistemini anlaması için interaktif eğitim platformu.

## 📚 Modüller

### 1. Constitution (Core · Zorunlu)
**Route:** `/academy/modules/constitution`

**İçerik:**
- Veri egemenliği prensipleri
- Kırmızı Hat veriler
- Recall hakkı
- Ombudsman temyiz

**Component'ler:**
- `RecallRequest` - Gerçek recall formu

### 2. NovaScore & CP (Core · Zorunlu)
**Route:** `/academy/modules/novascore`

**İçerik:**
- NovaScore bileşenleri (ECO, REL, SOC, ID, CON)
- CP (Ceza Puanı) sistemi
- Regime seviyeleri
- Skor hesaplama mantığı

**Component'ler:**
- `NovaScoreCard` - Örnek skor gösterimi
- `RegimeBadge` - Tüm regime seviyeleri

### 3. Justice Engine (Advanced)
**Route:** `/academy/modules/justice`

**İçerik:**
- Violation kategorileri
- CP hesaplama
- Decay mekanizması
- Enforcement matrix
- Regime seviyeleri

**Component'ler:**
- `RegimeBadge` - Regime görselleştirme

### 4. DAO & Policy (Advanced)
**Route:** `/academy/modules/dao`

**İçerik:**
- DAO governance süreci
- Policy parametreleri
- On-chain → Backend sync
- 3-Layer Architecture

**Component'ler:**
- `PolicyBreakdown` - Gerçek policy gösterimi
- `usePolicy` hook - API entegrasyonu

## 🎯 Kullanım

### Navigation
Academy link'i nav'da görünür:
- `/academy` - Overview
- `/academy/modules/{slug}` - Modül sayfaları

### Next/Previous Navigation
Her modül sayfasında:
- ← Academy ana sayfaya dön
- Sonraki ders → (sıralı gezinme)

## 🚀 Gelecek Özellikler

- [ ] Progress tracking (hangi modüller tamamlandı)
- [ ] Badge sistemi (modül tamamlama rozetleri)
- [ ] Quiz/Test (öğrenme kontrolü)
- [ ] Personalized recommendations (NovaScore'a göre)
- [ ] Interactive simulations
- [ ] Video content
- [ ] Community discussions

## 📊 Growth Metrics

Academy, growth motoru olarak:
- **Adoption:** Yeni vatandaşlar sistemi anlıyor
- **Engagement:** Eğitim tamamlama oranı
- **Retention:** Eğitim sonrası aktif kullanım
- **Advocacy:** Eğitilmiş vatandaşlar topluluk büyütüyor

## 🔗 Entegrasyon

- **Dashboard:** Eğitim önerileri gösterilebilir
- **Onboarding:** İlk modül onboarding'e entegre edilebilir
- **Justice:** CP yüksekse ilgili modül önerilebilir
- **Consent:** Constitution modülü consent flow'a bağlanabilir

