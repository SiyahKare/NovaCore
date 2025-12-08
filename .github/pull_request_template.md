# Pull Request

## 📋 Checklist

### Güvenlik

- [ ] [Backend API Security Checklist](./docs/security/CHECKLIST_BACKEND_API_V1.md) uygulandı mı? (Backend değişiklikleri için)
- [ ] [Telegram MiniApp Security Checklist](./docs/security/CHECKLIST_TELEGRAM_MINIAPP_V1.md) uygulandı mı? (Frontend/MiniApp değişiklikleri için)
- [ ] [Infra Security Checklist](./docs/security/CHECKLIST_INFRA_V1.md) uygulandı mı? (Infra/DevOps değişiklikleri için)
- [ ] Threat model'e referans verildi mi? (Kritik değişiklikler için)
  - [ ] [NovaCore Threat Model](./docs/security/THREAT_MODEL_NOVACORE_V1.md)
  - [ ] [FlirtMarket Threat Model](./docs/security/THREAT_MODEL_FLIRTMARKET_V1.md)

### Kod Kalitesi

- [ ] Kod lint'ten geçti mi? (`ruff check`, `eslint`)
- [ ] Type checking başarılı mı? (`mypy`, `tsc`)
- [ ] Test'ler yazıldı mı ve geçiyor mu?
- [ ] Documentation güncellendi mi? (gerekirse)

### Değişiklikler

- [ ] Breaking change var mı? (Varsa migration guide eklendi mi?)
- [ ] Environment variable değişikliği var mı? (`.env.example` güncellendi mi?)
- [ ] Database migration var mı? (Migration dosyası eklendi mi?)

---

## 📝 Açıklama

<!-- PR'ın amacını ve yapılan değişiklikleri açıklayın -->

### Ne Değişti?

<!-- Kısa özet -->

### Neden?

<!-- Problem / ihtiyaç -->

### Nasıl Test Edildi?

<!-- Test adımları, test senaryoları -->

### Screenshots (UI değişiklikleri için)

<!-- Görsel değişiklikler varsa ekleyin -->

---

## 🔗 İlgili Issue'lar

<!-- Closes #123, Related to #456 -->

---

## ⚠️ Breaking Changes

<!-- Varsa açıklayın -->

---

## 📚 Referanslar

<!-- Threat model, design doc, vs -->

---

## 👀 Review Notları

<!-- Reviewer'lar için özel notlar -->


