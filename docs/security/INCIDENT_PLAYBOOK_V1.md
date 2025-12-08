# Security Incident Response Playbook v1

**Versiyon:** v1.0  
**Son Güncelleme:** 2025-12-04  
**Durum:** Aktif - Her security incident'te kullanılmalı

---

## 🚨 Acil Durum Kontakları

### On-Call Rotation

- **Primary:** [Onur / Devran - Telegram: @onur / @devran]
- **Backup:** [Backup contact]
- **Escalation:** [Management contact]

### İletişim Kanalları

- **Telegram:** [Security channel]
- **Email:** security@siyahkare.com
- **Phone:** [Emergency phone]

---

## 📋 Incident Response Süreci

### 1. Tespit (Detection)

**Kaynaklar:**
- Monitoring alerts (error rate, unusual traffic)
- User reports (harassment, fraud, abuse)
- Security scanning tools (vulnerability scanners)
- Log analysis (suspicious patterns)

**İlk Adımlar:**
1. ✅ Incident'i kaydet (timestamp, source, description)
2. ✅ Severity belirle (Critical / High / Medium / Low)
3. ✅ On-call ekibi bilgilendir
4. ✅ İlk değerlendirmeyi yap (scope, impact)

---

### 2. Değerlendirme (Assessment)

**Severity Seviyeleri:**

#### 🔴 Critical (P0)
- **Örnekler:**
  - Database breach
  - Payment fraud (active)
  - Admin account compromise
  - DDoS attack (service down)
- **Response Time:** < 1 saat
- **Escalation:** Immediate

#### 🟡 High (P1)
- **Örnekler:**
  - User data leakage
  - Coin manipulation (active)
  - API abuse (high volume)
  - Security vulnerability (exploitable)
- **Response Time:** < 4 saat
- **Escalation:** Same day

#### 🟢 Medium (P2)
- **Örnekler:**
  - Spam / harassment (isolated)
  - Rate limit bypass (low impact)
  - Minor data exposure (non-sensitive)
- **Response Time:** < 24 saat
- **Escalation:** Next day

#### ⚪ Low (P3)
- **Örnekler:**
  - False positive alerts
  - Minor configuration issues
  - Non-exploitable vulnerabilities
- **Response Time:** < 1 hafta
- **Escalation:** Weekly review

---

### 3. Müdahale (Response)

#### 3.1 Containment (Yayılmayı Önleme)

**Acil Önlemler:**
- ✅ Etkilenen sistemleri izole et (disable endpoint, block IP)
- ✅ Etkilenen kullanıcı hesaplarını suspend et
- ✅ Database backup al (forensic analysis için)
- ✅ Log'ları topla ve koru (immutable)

**Örnek Komutlar:**
```bash
# IP block (Cloudflare / firewall)
# User suspend (admin panel)
# Endpoint disable (feature flag)
# Database backup (pg_dump)
```

#### 3.2 Eradication (Kökünü Kazıma)

**Adımlar:**
- ✅ Vulnerability'yi patch et
- ✅ Compromised account'ları temizle
- ✅ Malicious code'u kaldır
- ✅ Configuration'ı düzelt

**Örnekler:**
- SQL injection → Input validation ekle
- Coin manipulation → Wallet service'i güvenli hale getir
- Admin access → Role check'i düzelt

#### 3.3 Recovery (İyileştirme)

**Adımlar:**
- ✅ Sistemleri tekrar aktif et (gradual rollout)
- ✅ Monitoring'i artır (detection için)
- ✅ User notification (gerekirse)
- ✅ Post-incident review planla

---

### 4. Bildirim (Notification)

#### 4.1 İç Bildirim

**Kim:**
- Development team
- Operations team
- Management (Critical için)

**Ne Zaman:**
- Critical: Immediate
- High: Same day
- Medium: Next day
- Low: Weekly review

#### 4.2 Dış Bildirim

**GDPR / KVKK:**
- **Data breach** durumunda 72 saat içinde bildirim gerekli
- **Kullanıcılar** etkilenmişse bilgilendirme gerekli

**Payment Gateway:**
- **Payment fraud** durumunda payment provider bilgilendirilmeli

**Yasal:**
- **Criminal activity** durumunda yasal makamlara bildirim (gerekirse)

---

### 5. Post-Incident Review

#### 5.1 Incident Report

**İçerik:**
- ✅ Incident timeline (ne zaman, ne oldu)
- ✅ Root cause analysis (neden oldu)
- ✅ Impact assessment (kim etkilendi, ne kadar)
- ✅ Response actions (ne yapıldı)
- ✅ Lessons learned (ne öğrenildi)
- ✅ Action items (ne yapılacak)

**Template:**
```markdown
# Incident Report: [Title]

**Date:** YYYY-MM-DD
**Severity:** Critical / High / Medium / Low
**Status:** Resolved / Ongoing / Mitigated

## Timeline
- [Timestamp] - Detection
- [Timestamp] - Response started
- [Timestamp] - Containment
- [Timestamp] - Resolution

## Root Cause
[Description]

## Impact
- Users affected: [number]
- Data exposed: [type, amount]
- Financial impact: [if any]

## Response Actions
1. [Action 1]
2. [Action 2]

## Lessons Learned
- [Lesson 1]
- [Lesson 2]

## Action Items
- [ ] [Task 1] - Owner: [Name] - Due: [Date]
- [ ] [Task 2] - Owner: [Name] - Due: [Date]
```

#### 5.2 Action Items Tracking

**Örnekler:**
- [ ] Security patch uygula
- [ ] Monitoring rule ekle
- [ ] Documentation güncelle
- [ ] Training ver (team'e)
- [ ] Threat model güncelle

---

## 🔍 Senaryo Bazlı Playbook'lar

### Senaryo 1: Database Breach

**Tespit:**
- Unusual database access patterns
- User data leakage reports
- Database error logs

**Müdahale:**
1. ✅ Database connection'ları kes (emergency shutdown)
2. ✅ Backup al (forensic analysis)
3. ✅ Etkilenen kullanıcıları tespit et
4. ✅ Password reset zorunlu kıl (tüm kullanıcılar)
5. ✅ GDPR / KVKK bildirimi yap (72 saat içinde)

**Önleme:**
- Database access logging
- IP whitelist (production DB)
- Regular security audits

---

### Senaryo 2: Payment Fraud

**Tespit:**
- Unusual payment patterns
- Chargeback reports
- Coin balance anomalies

**Müdahale:**
1. ✅ Fraudulent transaction'ları iptal et
2. ✅ Etkilenen hesapları suspend et
3. ✅ Payment gateway'i bilgilendir
4. ✅ Coin balance'ları düzelt
5. ✅ User notification (gerekirse)

**Önleme:**
- Payment webhook verification
- Transaction monitoring
- Fraud detection rules

---

### Senaryo 3: DDoS Attack

**Tespit:**
- High traffic volume
- Service unavailability
- Error rate spike

**Müdahale:**
1. ✅ Cloudflare DDoS protection aktif
2. ✅ Rate limiting artır
3. ✅ IP blocking (attack source'ları)
4. ✅ Scaling (auto-scale if available)
5. ✅ Monitoring artır

**Önleme:**
- Cloudflare protection (always on)
- Rate limiting (proactive)
- Load balancing
- Auto-scaling

---

### Senaryo 4: Admin Account Compromise

**Tespit:**
- Unusual admin actions
- Admin log anomalies
- User reports (admin abuse)

**Müdahale:**
1. ✅ Compromised admin account'u disable et
2. ✅ Tüm admin session'ları invalidate et
3. ✅ Admin actions'ı review et (ne yapıldı?)
4. ✅ Affected data'yı restore et (backup'tan)
5. ✅ Password reset (tüm admin'ler)

**Önleme:**
- MFA (Multi-Factor Authentication)
- Admin action logging
- IP whitelist (admin panel)
- Regular access review

---

## 📊 Metrics & Monitoring

### Key Metrics

- **MTTR (Mean Time To Resolve):** < 4 saat (Critical)
- **MTTD (Mean Time To Detect):** < 1 saat (Critical)
- **Incident Count:** Monthly tracking
- **False Positive Rate:** < 10%

### Monitoring Tools

- **Error Tracking:** Sentry / Rollbar
- **Log Aggregation:** CloudWatch / ELK
- **Security Scanning:** Trivy / Snyk
- **DDoS Protection:** Cloudflare

---

## 🔄 Sürekli İyileştirme

### Quarterly Review

- ✅ Incident trend analysis
- ✅ Playbook effectiveness review
- ✅ Tool evaluation (yeni araçlar?)
- ✅ Training needs assessment

### Annual Review

- ✅ Full playbook revision
- ✅ Threat model update
- ✅ Security audit
- ✅ Compliance check (GDPR, PCI)

---

## 📚 Referanslar

- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [OWASP Incident Response](https://owasp.org/www-community/OWASP_Incident_Response)
- [GDPR Data Breach Notification](https://gdpr.eu/data-breach-notification/)


