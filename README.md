# NovaCore - Aurora State Network Kernel

**NovaCore** is the core backend infrastructure for the Aurora State Network, a decentralized governance and justice system built on blockchain principles.

## 🏗️ Architecture

NovaCore consists of:

- **Backend API** (FastAPI) - Core services and endpoints
- **Citizen Portal** (Next.js) - Web interface for citizens
- **Telegram Bridge** - Bot integration layer
- **Shared Packages** - UI components and hooks

## 🚀 Quick Start

### Local Development

```bash
# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Frontend
cd apps/citizen-portal
npm run dev
```

### Production Deployment

See [EC2 Deployment Guide](./docs/EC2_DEPLOYMENT.md) for EC2 setup, or [Cloudflare Tunnel Setup](./docs/CLOUDFLARE_TUNNEL_SETUP.md) for Cloudflare Tunnel deployment.

## 📚 Documentation

- [EC2 Deployment](./docs/EC2_DEPLOYMENT.md)
- [Cloudflare Tunnel Setup](./docs/CLOUDFLARE_TUNNEL_SETUP.md)
- [Telegram Bridge](./docs/TELEGRAM_BRIDGE.md)
- [Bot Setup](./docs/BOT_KURULUM.md)

## 🔧 Tech Stack

- **Backend**: FastAPI, SQLModel, PostgreSQL, Alembic
- **Frontend**: Next.js 14, React, TypeScript, Tailwind CSS
- **Infrastructure**: Cloudflare Tunnel, Systemd, Docker (optional)

## 📝 License

[Your License Here]
