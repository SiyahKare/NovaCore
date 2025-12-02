# Recall (Veri Geri Çekme) İşlem Akışı

## Mevcut Durum

### 1. Recall Talebi Oluşturma
- **Endpoint:** `POST /api/v1/consent/recall`
- **İşlem:**
  - Kullanıcı recall talebi oluşturur (FULL_EXCLUDE veya ANONYMIZE)
  - `UserPrivacyProfile` tablosunda:
    - `recall_mode` set edilir
    - `recall_requested_at` timestamp kaydedilir
    - `recall_completed_at` = `None` (henüz tamamlanmadı)
    - `state` = `"REQUESTED"`

### 2. Recall Durumu Kontrolü
- **Endpoint:** `GET /api/v1/consent/recall/status`
- **Durumlar:**
  - `NONE`: Recall talebi yok
  - `REQUESTED`: Talebi oluşturuldu, işleniyor
  - `IN_PROGRESS`: İşlem devam ediyor (şu an kullanılmıyor)
  - `COMPLETED`: İşlem tamamlandı (`recall_completed_at` set edildi)

### 3. NovaScore Etkisi
- Recall talebi varsa, NovaScore explanation'ına uyarı mesajı ekleniyor
- Confidence düşebilir (veri kapsamı azaldığı için)

## Eksik Olan İşlemler (TODO)

Backend'te `request_recall` fonksiyonunda şu hook'lar TODO olarak bırakılmış:

```python
# Burada senin gerçek pipeline hook'ların devreye girecek:
# - feature_store.delete_user_features(user_id)
# - training_log.mark_user_events_for_exclusion(user_id)
# Şimdilik sadece TODO olarak bırakıyoruz.
```

### Gerekli İşlemler:

1. **Feature Store Temizleme:**
   - Kullanıcının feature'larını silmek veya anonimleştirmek
   - `feature_store.delete_user_features(user_id)` veya
   - `feature_store.anonymize_user_features(user_id)`

2. **Training Log İşaretleme:**
   - Gelecekteki eğitimlerde bu kullanıcının verilerini exclude etmek
   - `training_log.mark_user_events_for_exclusion(user_id)`

3. **Background Job:**
   - Recall talebi oluşturulduktan sonra bir background job başlatılmalı
   - Bu job:
     - Feature store'dan verileri siler/anonimleştirir
     - Training pipeline'ına exclusion flag'i ekler
     - İşlem tamamlandığında `recall_completed_at` set eder
     - `state` = `"COMPLETED"` yapar

4. **48 Saat SLA:**
   - Aurora, recall talebini 48 saat içinde işlemekle yükümlü
   - Bu süre içinde işlem tamamlanmalı

## Önerilen İmplementasyon

### Seçenek 1: Background Job (Celery/Redis)
```python
# app/consent/tasks.py
from celery import shared_task

@shared_task
def process_recall_request(user_id: str, recall_mode: str):
    """
    Recall talebini işle:
    1. Feature store'dan verileri sil/anonimleştir
    2. Training log'ları işaretle
    3. recall_completed_at set et
    """
    # Implementation
    pass
```

### Seçenek 2: Async Background Task (FastAPI BackgroundTasks)
```python
from fastapi import BackgroundTasks

async def request_recall(
    body: RecallRequest,
    background_tasks: BackgroundTasks,
    ...
):
    # Recall talebini kaydet
    result = await service.request_recall(current_user_id, body)
    
    # Background task başlat
    background_tasks.add_task(
        process_recall_request,
        user_id=current_user_id,
        recall_mode=body.mode
    )
    
    return result
```

### Seçenek 3: Event-Driven (Kafka/RabbitMQ)
- Recall talebi bir event olarak publish edilir
- Consumer service işlemi yapar
- Tamamlandığında callback ile `recall_completed_at` set edilir

## Şu Anki Durum

- ✅ Recall talebi oluşturulabiliyor
- ✅ Recall durumu kontrol edilebiliyor
- ✅ NovaScore'da recall durumu gösteriliyor
- ✅ **Recall işlemi otomatik olarak tamamlanıyor** (Background task ile)
- ✅ **recall_completed_at otomatik set ediliyor**
- ⚠️ Feature store temizleme hook'ları hazır (TODO: gerçek entegrasyon)
- ⚠️ Training pipeline exclusion hook'ları hazır (TODO: gerçek entegrasyon)

## İmplementasyon Detayları

### Background Task Sistemi
- **FastAPI BackgroundTasks** kullanılıyor
- `POST /api/v1/consent/recall` endpoint'i çağrıldığında:
  1. Recall talebi DB'ye kaydedilir (`state = "REQUESTED"`)
  2. Background task başlatılır (`process_recall_request`)
  3. Task arka planda çalışır:
     - Feature store temizleme (TODO: gerçek entegrasyon)
     - Training log exclusion (TODO: gerçek entegrasyon)
     - `recall_completed_at` set edilir
     - `state = "COMPLETED"` olur

### Frontend Polling
- Recall talebi oluşturulduğunda, frontend her 5 saniyede bir durumu kontrol eder
- `recall_completed_at` set edildiğinde otomatik olarak UI güncellenir

## Sonraki Adımlar

1. ✅ Background job sistemi kuruldu (FastAPI BackgroundTasks)
2. ⚠️ Feature store entegrasyonu yapılmalı (hook'lar hazır, gerçek servis entegrasyonu gerekli)
3. ⚠️ Training pipeline exclusion mekanizması eklenmeli (hook'lar hazır, gerçek servis entegrasyonu gerekli)
4. ⚠️ 48 saat SLA monitoring eklenmeli
5. ⚠️ Admin panel'de recall taleplerini görüntüleme ve manuel tamamlama özelliği eklenmeli

