# 📅 İlk 3 Günlük Quest Script'i

**Tarih:** 2025-12-04  
**Versiyon:** V1.0  
**Hedef:** İlk 3 gün için özel quest dağılımı

---

## 🎯 Genel Mantık

**İlk 3 gün:**
- Tek seferlik görevler (`swamp_story_v1`, `nasip_oath_v1`) öncelikli
- Basit görevler öncelikli (karmaşık görevler sonra)
- Her gün 3 slot (MONEY, SKILL, INTEGRITY)

---

## 📋 Gün 1 Quest Seti

### MONEY Slot
- **Quest:** `daily_income_snapshot`
- **Neden:** En basit görev, kullanıcıyı sisteme alıştırır
- **Copy:** "Bugün cebine giren/çıkan parayı tek cümle yaz."

### SKILL Slot
- **Quest:** `daily_micro_content`
- **Neden:** İçerik üretimi, marketplace'e gidebilir
- **Copy:** "Nasip / Rızık / Gerçek temalı 1 cümle söz yaz."

### INTEGRITY Slot
- **Quest:** `nasip_oath_v1` (tek seferlik)
- **Neden:** İlk gün yemin, sistemin ciddiyetini gösterir
- **Copy:** "Bu oyundan ne beklediğini 2 cümleyle yaz."

**Beklenen Sonuç:**
- Kullanıcı 3 görevi görür
- En az 1-2 görevi tamamlar
- Sistemin nasıl çalıştığını anlar

---

## 📋 Gün 2 Quest Seti

### MONEY Slot
- **Quest:** `micro_value_action`
- **Neden:** İkinci gün biraz daha karmaşık
- **Copy:** "Bugün başkasına yaptığın küçük iyiliği yaz."

### SKILL Slot
- **Quest:** `skill_xp_log`
- **Neden:** Öğrenme odaklı görev
- **Copy:** "Bugün 1 skill için yaptığın en küçük hareket neydi?"

### INTEGRITY Slot
- **Quest:** `swamp_story_v1` (tek seferlik)
- **Neden:** İkinci gün daha derin bir görev
- **Copy:** "Seni ezen en ağır anı 3-5 cümle yaz."

**Beklenen Sonuç:**
- Kullanıcı tek seferlik görevleri tamamlar
- Daha derin içerik üretir
- Sistemin kalite filtresini görür

---

## 📋 Gün 3 Quest Seti

### MONEY Slot
- **Quest:** `daily_income_snapshot` veya `micro_value_action`
- **Neden:** Rutin görevler, günlük alışkanlık oluşturur
- **Copy:** (Gün 1 veya Gün 2'deki copy)

### SKILL Slot
- **Quest:** `daily_micro_content` veya `skill_xp_log`
- **Neden:** Rutin görevler, içerik üretimi devam eder
- **Copy:** (Gün 1 veya Gün 2'deki copy)

### INTEGRITY Slot
- **Quest:** `trusted_friend_refer`
- **Neden:** Tek seferlik görevler tamamlandı, rutin görevler başlar
- **Copy:** "En güvendiğin 1 kişinin adını yaz."

**Beklenen Sonuç:**
- Kullanıcı rutin görevlere alışır
- Günlük alışkanlık oluşur
- Sistemin sürdürülebilirliğini görür

---

## 🔄 Quest Factory Entegrasyonu

**Gün 1:**
```python
quests = QuestFactory.generate_for_user(
    user_id=user_id,
    use_mvp_pack=True,
    completed_one_time_quests=[],  # Henüz hiçbir tek seferlik tamamlanmadı
)

# Beklenen:
# MONEY → daily_income_snapshot
# SKILL → daily_micro_content
# INTEGRITY → nasip_oath_v1 (tek seferlik, öncelikli)
```

**Gün 2:**
```python
quests = QuestFactory.generate_for_user(
    user_id=user_id,
    use_mvp_pack=True,
    completed_one_time_quests=["nasip_oath_v1"],  # Gün 1'de tamamlandı
)

# Beklenen:
# MONEY → micro_value_action
# SKILL → skill_xp_log
# INTEGRITY → swamp_story_v1 (tek seferlik, öncelikli)
```

**Gün 3:**
```python
quests = QuestFactory.generate_for_user(
    user_id=user_id,
    use_mvp_pack=True,
    completed_one_time_quests=["nasip_oath_v1", "swamp_story_v1"],  # İkisi de tamamlandı
)

# Beklenen:
# MONEY → daily_income_snapshot veya micro_value_action (random)
# SKILL → daily_micro_content veya skill_xp_log (random)
# INTEGRITY → trusted_friend_refer (tek seferlikler bitti)
```

---

## 📊 Beklenen Metrikler

### Gün 1
- **Engagement:** %80+ `/tasks` görüntüleme
- **Completion:** %60+ en az 1 görev tamamlama
- **Quality:** Ortalama AI score 65-75

### Gün 2
- **Engagement:** %70+ `/tasks` görüntüleme
- **Completion:** %50+ en az 1 görev tamamlama
- **Quality:** Ortalama AI score 70-80 (tek seferlik görevler daha derin)

### Gün 3
- **Engagement:** %60+ `/tasks` görüntüleme
- **Completion:** %40+ en az 1 görev tamamlama
- **Quality:** Ortalama AI score 65-75 (rutin görevler)

---

## 🎯 Sonraki Adımlar

**Gün 4+ için:**
- Rutin görevler devam eder
- Tek seferlik görevler tamamlandı
- Marketplace'e gönderilen içerikler görünür
- Kullanıcılar `/market` komutunu kullanır

---

**İlk 3 Günlük Quest Script'i V1.0 - Hazır!** 🚀

