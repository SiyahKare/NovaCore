# Changelog

Tüm önemli değişiklikler bu dosyada dokümante edilmiştir.

Format [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standardına uygundur ve bu proje [Semantic Versioning](https://semver.org/spec/v2.0.0.html) kullanır.

---

## [Unreleased]

### Planlanan

- Test coverage artırma (%80+)
- Production infrastructure (monitoring, backup, recovery)
- Payment gateway entegrasyonu (Stripe/PayPal)
- FlirtMarket MVP (matching, chat, profile)
- Mobile app (React Native)

---

## [0.6.0] - 2025-12-04

### Added

#### Security Framework
- **Security Documentation System**
  - Threat models (NovaCore, FlirtMarket)
  - Security checklists (Backend API, Telegram MiniApp, Infra)
  - Incident response playbook
  - Security policy (SECURITY.md)

- **GitHub PR Template**
  - Security checklist entegrasyonu
  - Threat model referans alanları
  - Kod kalitesi kontrolleri

#### Academy Module
- **Academy Progress Tracking**
  - `GET /api/v1/academy/progress` endpoint
  - `POST /api/v1/academy/modules/{module}/complete` endpoint
  - `useAcademyProgress` React hook
  - Module completion telemetry tracking

- **Academy Modules**
  - Constitution module (Anayasa)
  - NovaScore module (NovaScore sistemi)
  - Justice module (Aurora Justice)
  - DAO module (DAO Governance)

#### Documentation
- **NovaCore Stability Analysis**
  - FlirtMarket + OnlyVips risk değerlendirmesi
  - Production readiness analizi
  - Kullanılabilir modüller listesi

- **Roadmap**
  - 2025 Q1-Q4 planlaması
  - Production readiness hedefleri
  - FlirtMarket MVP planı

- **Documentation Organization**
  - Tüm dokümanlar `docs/` klasörüne taşındı
  - Security dokümantasyonu eklendi

### Changed

- **Cloudflare Deployment**
  - Cloudflare Tunnel entegrasyonu (`portal.siyahkare.com`, `api.siyahkare.com`)
  - CORS configuration güncellendi
  - Environment variables Cloudflare için optimize edildi

- **Telegram Integration**
  - Telegram OAuth entegrasyonu (domain verification)
  - Deep linking (`/panel` komutu ile otomatik login)
  - WebApp authentication iyileştirildi

- **Frontend**
  - ProtectedView component mesajları iyileştirildi ("Connect Citizen" vs "Become a Citizen")
  - Onboarding page Telegram OAuth desteği eklendi

### Fixed

- **CORS Issues**
  - Backend CORS configuration düzeltildi
  - Environment variable caching sorunu çözüldü (`@lru_cache` kaldırıldı)
  - Cloudflare subdomain'leri CORS'a eklendi

- **Configuration**
  - `app/core/config.py` - `@lru_cache` kaldırıldı (env değişiklikleri için)
  - `.env` dosyası Cloudflare URL'leri için güncellendi

---

## [0.5.0] - 2024-12-XX

### Added

#### Production-Ready Quest Engine
- **Quest System**
  - UserQuest model (quest assignment, completion tracking)
  - QuestFactory (günlük quest generation)
  - QuestService (quest business logic)
  - Quest submission pipeline (10-step process)

- **AI Scoring Service**
  - OpenAI entegrasyonu (gpt-4o-mini)
  - PRODUCTION/RESEARCH quest scoring
  - MODERATION/RITUAL auto-pass
  - Flags ve tags (nsfw_or_toxic, low_quality)

- **AbuseGuard Integration**
  - RiskScore calculation
  - Abuse detection (TOXIC_CONTENT, LOW_QUALITY_BURST)
  - Reward multipliers (risk-based)
  - Cooldown enforcement

- **Treasury Cap System**
  - Daily NCR limits
  - Damping multipliers
  - Economic sustainability

- **NCR Price Stabilization**
  - Coverage ratio calculation
  - Flow index tracking
  - EMA smoothing

#### Marketplace
- **Marketplace Core**
  - MarketplaceItem & MarketplacePurchase modelleri
  - MarketplaceService (business logic)
  - Quest → Marketplace Bridge (otomatik gönderim)
  - Revenue share (%70 creator, %30 treasury)

- **AI Scoring Integration**
  - AI Score 70+ → Marketplace'e gönder
  - Item type inference
  - Dynamic pricing

- **Telegram Bot Integration**
  - `/market` - TOP 10 ürün listesi
  - `💳 Satın al` - Inline button ile satın alma
  - `/buy <id>` - Text komutu ile satın alma
  - `/my_items` - Creator'ın kendi ürünleri
  - `/my_sales` - Satış istatistikleri

#### Aurora Contact
- **Telegram Dashboard**
  - 3-column layout
  - AI/Human hybrid chat
  - Telethon User Bot integration
  - ChatManager (Grok/GPT hybrid routing)

- **Business Intelligence**
  - Intent classification
  - Tool calling
  - Lead intelligence

#### Agency Pipeline
- **Creator → Agency Conversion**
  - ContentCurator model
  - CreatorAsset tracking
  - Revenue Share (20/40/40: Creator/Treasury/Agency)

#### Ombudsman Panel
- **HITL Quest Monitor**
  - RiskScore ≥ 6.0 quest review
  - Admin panel entegrasyonu
  - Case file management

#### NasipQuest Economy Dashboard
- **Economy Metrics**
  - NCR price tracking
  - Treasury health monitoring
  - Economic metrics visualization

---

## [0.4.0] - 2024-XX-XX

### Added

#### Internationalization (i18n)
- **Multi-language Support**
  - Türkçe (tr)
  - English (en)
  - Русский (ru)

- **next-intl Integration**
  - Locale-aware routing
  - Translation management
  - Language switching

#### NasipQuest Task Engine v3
- **Task System**
  - Task submission & reward system
  - Referral system
  - Event bonus system
  - Leaderboard & profile cards

---

## [0.3.0] - 2024-XX-XX

### Added

#### Dashboard v2: Devran-level Citizen State Console
- **Unified State Management**
  - `useCitizenState` hook
  - Real-time data integration

- **Aurora State Health Panel**
  - System health monitoring
  - Citizen state visualization

- **Citizen Timeline**
  - Activity tracking
  - Event history

- **Trust Factors**
  - Trust score visualization
  - Factor breakdown

- **Enhanced UI/UX**
  - Neon design elements
  - Glow effects
  - Depth perception

---

## [0.2.0] - 2024-XX-XX

### Added

#### Aurora Justice Stack v2.0
- **DAO-Controlled Policy**
  - On-chain governance
  - Policy versioning
  - Policy sync

- **3-Layer Architecture**
  - Chain Law (mutable)
  - Constitution (immutable)
  - Execution (runtime)

#### Frontend Ecosystem
- **Citizen Portal**
  - Next.js frontend
  - Component library
  - Shared hooks

- **Admin Panel**
  - Admin dashboard
  - User management
  - System monitoring

#### Web User Authentication
- **JWT Authentication**
  - Token-based auth
  - Refresh token support
  - Telegram integration

---

## [0.1.0] - 2024-XX-XX

### Added

#### Initial Release
- **Core Modules**
  - Identity & Authentication
  - Wallet & Ledger
  - Consent Management
  - Justice System

- **NovaScore**
  - Behavioral reputation score
  - CP (Ceza Puanı) integration
  - Trust calculation

- **Consent & Justice**
  - Consent flow
  - Justice engine
  - Ombudsman system

---

## [Unreleased] - Gelecek Özellikler

### Q1 2025
- Test coverage artırma (%80+)
- Production infrastructure (monitoring, backup, recovery)
- Error handling & resilience
- Security hardening
- Payment gateway entegrasyonu

### Q2 2025
- FlirtMarket MVP (matching, chat, profile)
- NSFW content moderation
- Telegram MiniApp
- GDPR/KVKK compliance

### Q3 2025
- Horizontal scaling
- Performance optimization
- Advanced matching (AI-powered)
- Analytics & A/B testing

### Q4 2025
- DAO integration (production-ready)
- Justice Engine production
- Mobile app (React Native)
- OnlyVips integration

---

## Değişiklik Türleri

- `Added` - Yeni özellikler
- `Changed` - Mevcut özelliklerde değişiklikler
- `Deprecated` - Yakında kaldırılacak özellikler
- `Removed` - Kaldırılan özellikler
- `Fixed` - Bug düzeltmeleri
- `Security` - Güvenlik düzeltmeleri

---

**Not:** Bu changelog, projenin başlangıcından itibaren önemli değişiklikleri içerir. Detaylı commit geçmişi için git log'a bakın.


