# Security Documentation

**Versiyon:** v1.0  
**Son Güncelleme:** 2025-12-04

---

## 📚 Dokümantasyon Yapısı

Bu klasör NovaCore ve FlirtMarket projelerinin güvenlik dokümantasyonunu içerir.

### Threat Models (Tehdit Modelleri)

- **[THREAT_MODEL_NOVACORE_V1.md](./THREAT_MODEL_NOVACORE_V1.md)**
  - NovaCore backend API için threat model
  - Varlıklar, aktörler, saldırı yüzeyleri
  - Örnek tehdit senaryoları ve mitigation'lar

- **[THREAT_MODEL_FLIRTMARKET_V1.md](./THREAT_MODEL_FLIRTMARKET_V1.md)**
  - FlirtMarket Telegram MiniApp için threat model
  - FlirtMarket'e özel tehditler (fake profile, harassment, payment fraud)

### Security Checklists (Güvenlik Kontrol Listeleri)

- **[CHECKLIST_BACKEND_API_V1.md](./CHECKLIST_BACKEND_API_V1.md)**
  - Backend API PR'ları için security checklist
  - Auth, authorization, wallet, input validation, rate limiting

- **[CHECKLIST_TELEGRAM_MINIAPP_V1.md](./CHECKLIST_TELEGRAM_MINIAPP_V1.md)**
  - Telegram MiniApp PR'ları için security checklist
  - WebApp init, navigation, coin UI, input abuse

- **[CHECKLIST_INFRA_V1.md](./CHECKLIST_INFRA_V1.md)**
  - Infra/DevOps değişiklikleri için security checklist
  - Database, network, CI/CD, secrets management

### Incident Response (Olay Müdahale)

- **[INCIDENT_PLAYBOOK_V1.md](./INCIDENT_PLAYBOOK_V1.md)**
  - Security incident response süreci
  - Senaryo bazlı playbook'lar (database breach, payment fraud, DDoS)
  - Post-incident review süreci

---

## 🚀 Kullanım

### PR Öncesi

1. **İlgili checklist'i aç:**
   - Backend değişikliği → `CHECKLIST_BACKEND_API_V1.md`
   - Frontend/MiniApp değişikliği → `CHECKLIST_TELEGRAM_MINIAPP_V1.md`
   - Infra değişikliği → `CHECKLIST_INFRA_V1.md`

2. **Checklist'i uygula:**
   - Her maddeyi kontrol et
   - Eksikler varsa tamamla

3. **PR template'i kullan:**
   - `.github/pull_request_template.md` dosyasını kullan
   - Security checklist'i işaretle

### Kritik Değişikliklerde

- **Threat model'e referans ver:**
  - Kritik değişikliklerde (auth, wallet, admin) threat model'e referans ekle
  - Yeni tehdit keşfedildiyse threat model'i güncelle

### Security Incident Durumunda

- **Incident playbook'u takip et:**
  - `INCIDENT_PLAYBOOK_V1.md` dosyasındaki adımları izle
  - Severity'ye göre response timeline'ı takip et

---

## 🔄 Güncelleme Süreci

### Threat Models

- **Her kritik değişiklikte** gözden geçirilmeli
- **Yeni tehdit keşfedildiğinde** güncellenmeli
- **Yılda en az bir kez** tam review edilmeli

### Checklists

- **Her PR'da** kullanılmalı
- **Yeni güvenlik gereksinimi** eklendiğinde güncellenmeli
- **Quarterly review** yapılmalı

### Incident Playbook

- **Her incident sonrası** gözden geçirilmeli
- **Yeni senaryo** keşfedildiğinde eklenmeli
- **Yıllık tam review** yapılmalı

---

## 📞 İletişim

**Güvenlik Soruları:** security@siyahkare.com  
**Security Policy:** [../../SECURITY.md](../../SECURITY.md)

---

## 📚 Referanslar

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**Son Güncelleme:** 2025-12-04


