# Security Policy

**Versiyon:** v1.0  
**Son Güncelleme:** 2025-12-04

---

## 🛡️ Güvenlik Raporlama

NovaCore ve FlirtMarket projelerinde güvenlik açığı bulduysanız, lütfen **sorumlu açığa çıkarma** (responsible disclosure) prensibini takip edin.

### Güvenlik Açığı Bildirimi

**Email:** security@siyahkare.com  
**PGP Key:** [PGP key link - gelecekte eklenecek]

**Lütfen şunları dahil edin:**
- Açığın açıklaması
- Etkilenen sistem/endpoint
- Reproduction steps (mümkünse)
- Potansiyel impact
- Önerilen fix (varsa)

### Response Timeline

- **İlk yanıt:** 48 saat içinde
- **Değerlendirme:** 7 gün içinde
- **Fix timeline:** Severity'ye göre (Critical: < 7 gün, High: < 30 gün)

### Güvenlik Açığı Ödülleri

Şu anda **bug bounty program** aktif değil, ancak gelecekte eklenebilir.

---

## 🔒 Güvenlik Süreçleri

### Code Review

Tüm kod değişiklikleri security checklist'lerden geçmelidir:

- [Backend API Security Checklist](./docs/security/CHECKLIST_BACKEND_API_V1.md)
- [Telegram MiniApp Security Checklist](./docs/security/CHECKLIST_TELEGRAM_MINIAPP_V1.md)
- [Infra Security Checklist](./docs/security/CHECKLIST_INFRA_V1.md)

### Threat Modeling

Kritik değişikliklerde threat model'e referans verilmelidir:

- [NovaCore Threat Model](./docs/security/THREAT_MODEL_NOVACORE_V1.md)
- [FlirtMarket Threat Model](./docs/security/THREAT_MODEL_FLIRTMARKET_V1.md)

### Incident Response

Security incident durumunda:

- [Security Incident Response Playbook](./docs/security/INCIDENT_PLAYBOOK_V1.md) takip edilmelidir.

---

## 🔐 Güvenlik Kontrol Noktaları

### Pre-Deployment

- [ ] Security checklist uygulandı mı?
- [ ] Threat model güncellendi mi? (kritik değişiklikler için)
- [ ] Dependency vulnerabilities taranmış mı?
- [ ] Secrets scanning yapılmış mı?
- [ ] Code review tamamlandı mı?

### Post-Deployment

- [ ] Monitoring aktif mi?
- [ ] Alerting kurulu mu?
- [ ] Log aggregation çalışıyor mu?
- [ ] Backup alındı mı?

---

## 📋 Güvenlik Dokümantasyonu

Tüm güvenlik dokümantasyonu `docs/security/` klasöründe bulunur:

- **Threat Models:** Sistem tehdit analizi
- **Security Checklists:** PR öncesi kontrol listeleri
- **Incident Playbook:** Security incident response süreci

---

## 🔄 Güvenlik Güncellemeleri

### Dependency Updates

- **Kritik güvenlik yamaları:** Hemen uygulanır
- **Yüksek öncelikli:** 7 gün içinde
- **Orta öncelikli:** 30 gün içinde

### Security Audits

- **Yıllık:** Full security audit
- **Çeyreklik:** Dependency vulnerability scan
- **Aylık:** Security configuration review

---

## 📞 İletişim

**Güvenlik Soruları:** security@siyahkare.com  
**Acil Durum:** [Emergency contact - Telegram]

---

## 📜 Lisans ve Yasal

Bu güvenlik politikası [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) lisansı altındadır.

---

**Son Güncelleme:** 2025-12-04


