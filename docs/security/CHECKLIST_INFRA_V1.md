# Infra / DevOps Security Checklist

**Versiyon:** v1.0  
**Son Güncelleme:** 2025-12-04  
**Uygulama:** Her deployment ve infra değişikliğinde kontrol edilmeli

---

## 1. Database & Network

- [ ] Prod DB'ye direkt public internetten erişim yok (sadece app / bastion).
- [ ] Database connection string'ler ENV'de, kod içinde hardcode yok.
- [ ] Database backup'ları otomatik ve test edilmiş (restore test edilmiş).
- [ ] Network security groups / firewall kuralları minimal (sadece gerekli portlar açık).

---

## 2. Access Control

- [ ] SSH key yönetimi: şifre yok, sadece key, mümkünse SSM.
- [ ] Admin panel erişimi IP whitelist veya VPN ile korumalı.
- [ ] Production environment'a erişim sınırlı (sadece gerekli kişiler).
- [ ] Service account'ları için least privilege prensibi uygulanmış.

---

## 3. CI/CD Pipeline

- [ ] CI pipeline'da:
  - [ ] secrets GH actions secrets'te, repo'da yok.
  - [ ] basic secrets scanning (gitleaks / trivy) var.
  - [ ] Dependency vulnerability scanning (Dependabot / Snyk) aktif.
- [ ] Production deployment manuel onay gerektiriyor (otomatik deploy yok).
- [ ] Rollback mekanizması test edilmiş.

---

## 4. Logging & Monitoring

- [ ] Log'lar merkezi (CloudWatch/ELK), ama PII minimum.
- [ ] Sensitive data (password, token, credit card) log'lanmıyor.
- [ ] Security event'leri (failed login, unauthorized access) alert ediliyor.
- [ ] Monitoring ve alerting kurulu (uptime, error rate, latency).

---

## 5. Secrets Management

- [ ] Tüm secrets (DB password, API keys, JWT secret) secrets manager'da (AWS Secrets Manager, HashiCorp Vault).
- [ ] Secrets rotation policy var (örn: 90 günde bir).
- [ ] `.env` dosyaları `.gitignore`'da ve commit'lenmiyor.
- [ ] `.env.example` dosyası var ama gerçek değerler yok.

---

## 6. Backup & Disaster Recovery

- [ ] Backup ve restore test edilmiş (DB snapshot'tan restore denenmiş).
- [ ] Backup retention policy var (örn: 30 gün).
- [ ] Disaster recovery planı dokümante edilmiş.
- [ ] RTO (Recovery Time Objective) ve RPO (Recovery Point Objective) tanımlı.

---

## 7. Container & Runtime Security

- [ ] Docker image'ları minimal base image kullanıyor (alpine, distroless).
- [ ] Container'lar non-root user ile çalışıyor.
- [ ] Runtime security scanning aktif (örn: Falco).
- [ ] Dependency'ler güncel ve vulnerability'siz.

---

## 8. Compliance & Audit

- [ ] GDPR / KVKK uyumlu (PII handling, right to deletion).
- [ ] Audit log'ları immutable (değiştirilemez).
- [ ] Access log'ları saklanıyor (kim, ne zaman, ne yaptı).
- [ ] Security incident response planı var.

---

## 📝 Notlar

- Bu checklist infra ve DevOps PR'ları için geçerlidir.
- Kritik değişikliklerde (network, access control, secrets) threat model'e referans verilmeli.
- Güvenlik açığı bulunursa: `SECURITY.md` dosyasındaki prosedürü takip et.


