# 🎯 NasipQuest Onboarding Mesajı

**Tarih:** 2025-12-04  
**Versiyon:** V1.0  
**Ton:** Burak/Karanlık Mentor - Tok, samimi, gerçekçi

---

## 📱 `/start` Komutu Mesajı

### Ekran 1: Hoş Geldin

```
✨ Hoş geldin, vatandaş.

Bu sistem seni sömürmek için değil, seni eski sistemden kurtarmak için var.

NasipQuest = Görev yap → NCR kazan → Marketplace'te sat → Gerçek iş.

Eski sistem: Sen çalış, patron kazansın.
Yeni sistem: Sen üret, sen kazan.

Hazırsan devam et.
```

### Ekran 2: Nasıl Çalışır?

```
📋 Nasıl Çalışır?

1️⃣ Her gün 3 görev gelir:
   • 💸 MONEY (Para/İş)
   • 🧠 SKILL (Öğrenme/Üretim)
   • 🧭 INTEGRITY (Dürüstlük/Şeffaflık)

2️⃣ Görevleri tamamla → NCR + XP kazan

3️⃣ Kaliteli içerik üret → Marketplace'e düşer

4️⃣ KOBİ'ler senin içeriğini satın alır → Sen kazanırsın

5️⃣ Treasury şişer → Sistem büyür

Basit. Gerçek.
```

### Ekran 3: İlk Adım

```
🚀 İlk Adım

Şimdi `/görevler` yaz ve bugünkü görevlerini gör.

Her görev 1-2 dakika sürer.
Dürüst ol, gerçek ol.

Başla: /görevler
```

---

## 📝 Tam Mesaj (Tek Parça)

```
✨ Hoş geldin, vatandaş.

Bu sistem seni sömürmek için değil, seni eski sistemden kurtarmak için var.

NasipQuest = Görev yap → NCR kazan → Marketplace'te sat → Gerçek iş.

Eski sistem: Sen çalış, patron kazansın.
Yeni sistem: Sen üret, sen kazan.

---

📋 Nasıl Çalışır?

1️⃣ Her gün 3 görev gelir:
   • 💸 MONEY (Para/İş)
   • 🧠 SKILL (Öğrenme/Üretim)
   • 🧭 INTEGRITY (Dürüstlük/Şeffaflık)

2️⃣ Görevleri tamamla → NCR + XP kazan

3️⃣ Kaliteli içerik üret → Marketplace'e düşer

4️⃣ KOBİ'ler senin içeriğini satın alır → Sen kazanırsın

5️⃣ Treasury şişer → Sistem büyür

Basit. Gerçek.

---

🚀 İlk Adım

Şimdi `/görevler` yaz ve bugünkü görevlerini gör.

Her görev 1-2 dakika sürer.
Dürüst ol, gerçek ol.

Başla: /görevler
```

---

## 🎨 Ton ve Stil

**Prensipler:**
- ✅ Tok ve samimi
- ✅ Gerçekçi, vaat vermiyor
- ✅ Kısa ve net
- ✅ Burak/Karanlık Mentor vibe
- ✅ "Eski sistem vs yeni sistem" karşılaştırması
- ✅ Dürüstlük vurgusu

**Kaçınılacaklar:**
- ❌ "Çok para kazanacaksın" gibi abartılı vaatler
- ❌ Teknik jargon
- ❌ Uzun açıklamalar
- ❌ "Kolay para" mesajı

---

## 🔄 Kullanım

**Telegram Bot Handler:**
```python
@router.message(CommandStart())
async def cmd_start(message: Message):
    telegram_user_id = message.from_user.id
    
    # NovaCore'a link et
    result = await api_client.link_user(...)
    
    if result.get("success"):
        # Onboarding mesajını gönder
        await message.answer(ONBOARDING_MESSAGE, parse_mode="Markdown")
    else:
        await message.answer("❌ Bağlantı hatası. Lütfen tekrar dene.")
```

**Mesaj Sabitleri:**
```python
ONBOARDING_MESSAGE = """
✨ Hoş geldin, vatandaş.

Bu sistem seni sömürmek için değil, seni eski sistemden kurtarmak için var.

NasipQuest = Görev yap → NCR kazan → Marketplace'te sat → Gerçek iş.

Eski sistem: Sen çalış, patron kazansın.
Yeni sistem: Sen üret, sen kazan.

---

📋 Nasıl Çalışır?

1️⃣ Her gün 3 görev gelir:
   • 💸 MONEY (Para/İş)
   • 🧠 SKILL (Öğrenme/Üretim)
   • 🧭 INTEGRITY (Dürüstlük/Şeffaflık)

2️⃣ Görevleri tamamla → NCR + XP kazan

3️⃣ Kaliteli içerik üret → Marketplace'e düşer

4️⃣ KOBİ'ler senin içeriğini satın alır → Sen kazanırsın

5️⃣ Treasury şişer → Sistem büyür

Basit. Gerçek.

---

🚀 İlk Adım

Şimdi `/görevler` yaz ve bugünkü görevlerini gör.

Her görev 1-2 dakika sürer.
Dürüst ol, gerçek ol.

Başla: /görevler
"""
```

---

**Onboarding V1.0 - Hazır!** 🚀

