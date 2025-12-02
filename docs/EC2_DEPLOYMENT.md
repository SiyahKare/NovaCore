# EC2 Deployment Guide

NovaCore'u Amazon EC2 üzerine kurulum rehberi.

## 📋 Gereksinimler

- Amazon EC2 instance (Ubuntu 22.04 LTS önerilir)
- Minimum: t3.medium (2 vCPU, 4 GB RAM)
- Önerilen: t3.large (2 vCPU, 8 GB RAM)
- Security Group: SSH (22), HTTP (80), HTTPS (443) açık olmalı
- Elastic IP (opsiyonel ama önerilir)

## 🚀 Hızlı Kurulum

### 1. EC2 Instance Oluştur

1. AWS Console → EC2 → Launch Instance
2. **AMI**: Ubuntu Server 22.04 LTS
3. **Instance Type**: t3.medium veya daha büyük
4. **Key Pair**: Yeni oluştur veya mevcut olanı seç
5. **Security Group**: 
   - SSH (22) - My IP
   - HTTP (80) - 0.0.0.0/0
   - HTTPS (443) - 0.0.0.0/0
6. **Storage**: 20 GB minimum
7. Launch Instance

### 2. EC2'ye Bağlan

```bash
# SSH ile bağlan
ssh -i your-key.pem ubuntu@YOUR_EC2_IP

# veya Elastic IP kullanıyorsan
ssh -i your-key.pem ubuntu@YOUR_ELASTIC_IP
```

### 3. Otomatik Kurulum

```bash
# GitHub'dan script'i indir ve çalıştır
curl -fsSL https://raw.githubusercontent.com/YOUR_USERNAME/NovaCore/main/scripts/ec2-setup.sh | bash

# veya manuel olarak
git clone https://github.com/YOUR_USERNAME/NovaCore.git
cd NovaCore
chmod +x scripts/ec2-setup.sh
./scripts/ec2-setup.sh
```

### 4. Manuel Kurulum (Adım Adım)

#### Adım 1: Sistem Güncellemesi

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

#### Adım 2: Temel Paketler

```bash
sudo apt-get install -y \
    curl wget git build-essential \
    python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib \
    nodejs npm \
    ufw htop vim
```

#### Adım 3: Node.js LTS

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs
```

#### Adım 4: PostgreSQL Yapılandırması

```bash
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Database oluştur
sudo -u postgres psql <<EOF
CREATE USER novacore WITH PASSWORD 'GÜÇLÜ_ŞİFRE_BURAYA';
CREATE DATABASE novacore OWNER novacore;
GRANT ALL PRIVILEGES ON DATABASE novacore TO novacore;
\q
EOF
```

#### Adım 5: Projeyi Klonla

```bash
cd /opt
sudo mkdir -p novacore
sudo chown $USER:$USER novacore
cd novacore
git clone https://github.com/YOUR_USERNAME/NovaCore.git
cd NovaCore
```

#### Adım 6: Python Environment

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

#### Adım 7: Node.js Dependencies

```bash
npm install
```

#### Adım 8: Environment Variables

```bash
# Backend .env
cat > .env <<EOF
ENV=prod
DATABASE_URL=postgresql+asyncpg://novacore:GÜÇLÜ_ŞİFRE_BURAYA@localhost:5432/novacore
DATABASE_URL_SYNC=postgresql://novacore:GÜÇLÜ_ŞİFRE_BURAYA@localhost:5432/novacore
JWT_SECRET=$(openssl rand -hex 32)
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=10080
NCR_TREASURY_USER_ID=1
CORS_ORIGINS=https://novacore.siyahkare.com,https://api.novacore.siyahkare.com
LOG_LEVEL=INFO
EOF

# Frontend .env.local
cat > apps/citizen-portal/.env.local <<EOF
NEXT_PUBLIC_AURORA_API_URL=https://api.novacore.siyahkare.com/api/v1
NEXT_PUBLIC_AURORA_ENV=production
EOF
```

#### Adım 9: Database Migration

```bash
alembic upgrade head
```

#### Adım 10: Cloudflare Tunnel

```bash
# Cloudflare Tunnel kur
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb
sudo dpkg -i /tmp/cloudflared.deb

# Tunnel yapılandır
./scripts/setup-cloudflare-tunnel.sh
```

#### Adım 11: Production Build

```bash
cd apps/citizen-portal
npm run build
cd ../..
```

#### Adım 12: Systemd Services

Otomatik kurulum script'i service'leri oluşturur. Manuel oluşturmak için:

```bash
# Backend service
sudo tee /etc/systemd/system/novacore-backend.service > /dev/null <<EOF
[Unit]
Description=NovaCore Backend API
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/novacore/NovaCore
Environment="PATH=/opt/novacore/.venv/bin"
ExecStart=/opt/novacore/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Frontend service
sudo tee /etc/systemd/system/novacore-frontend.service > /dev/null <<EOF
[Unit]
Description=NovaCore Frontend
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/novacore/NovaCore/apps/citizen-portal
Environment="PATH=/usr/bin:/usr/local/bin"
ExecStart=/usr/bin/npm run start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Cloudflare Tunnel service
sudo tee /etc/systemd/system/novacore-cloudflared.service > /dev/null <<EOF
[Unit]
Description=Cloudflare Tunnel for NovaCore
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/opt/novacore/NovaCore
ExecStart=/usr/local/bin/cloudflared tunnel --config /opt/novacore/NovaCore/cloudflare-tunnel.yml run novacore-tunnel
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Service'leri aktif et
sudo systemctl daemon-reload
sudo systemctl enable novacore-backend
sudo systemctl enable novacore-frontend
sudo systemctl enable novacore-cloudflared

sudo systemctl start novacore-backend
sudo systemctl start novacore-frontend
sudo systemctl start novacore-cloudflared
```

#### Adım 13: Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable
```

## 🔧 Yönetim

### Service Durumları

```bash
# Tüm service'lerin durumu
sudo systemctl status novacore-backend
sudo systemctl status novacore-frontend
sudo systemctl status novacore-cloudflared

# Service'leri yeniden başlat
sudo systemctl restart novacore-backend
sudo systemctl restart novacore-frontend
sudo systemctl restart novacore-cloudflared

# Service'leri durdur
sudo systemctl stop novacore-backend
sudo systemctl stop novacore-frontend
sudo systemctl stop novacore-cloudflared
```

### Loglar

```bash
# Backend logları
sudo journalctl -u novacore-backend -f

# Frontend logları
sudo journalctl -u novacore-frontend -f

# Cloudflare Tunnel logları
sudo journalctl -u novacore-cloudflared -f

# Tüm loglar
sudo journalctl -u novacore-* -f
```

### Güncelleme

```bash
cd /opt/novacore/NovaCore
git pull origin main

# Backend güncellemesi
source .venv/bin/activate
pip install -e .
alembic upgrade head
sudo systemctl restart novacore-backend

# Frontend güncellemesi
cd apps/citizen-portal
npm install
npm run build
sudo systemctl restart novacore-frontend
```

## 🔒 Güvenlik

### 1. SSH Key Authentication

```bash
# Password authentication'ı kapat
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
```

### 2. Fail2Ban

```bash
sudo apt-get install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Automatic Security Updates

```bash
sudo apt-get install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 4. Database Backup

```bash
# Cron job ekle
crontab -e

# Her gün saat 02:00'de backup al
0 2 * * * pg_dump -U novacore novacore > /opt/novacore/backups/novacore_$(date +\%Y\%m\%d).sql
```

## 📊 Monitoring

### System Resources

```bash
# CPU ve Memory kullanımı
htop

# Disk kullanımı
df -h

# Network trafiği
sudo iftop
```

### Application Health

```bash
# Backend health check
curl http://localhost:8000/health

# Frontend health check
curl http://localhost:3000
```

## 🐛 Troubleshooting

### Service Başlamıyor

```bash
# Logları kontrol et
sudo journalctl -u novacore-backend -n 50

# Manuel başlatmayı dene
cd /opt/novacore/NovaCore
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database Bağlantı Hatası

```bash
# PostgreSQL durumu
sudo systemctl status postgresql

# Connection test
psql -U novacore -d novacore -h localhost
```

### Port Kullanımda

```bash
# Hangi process port'u kullanıyor?
sudo lsof -i :8000
sudo lsof -i :3000

# Process'i öldür
sudo kill -9 PID
```

## 💰 Maliyet Optimizasyonu

- **Reserved Instances**: Uzun vadeli kullanım için %30-50 tasarruf
- **Spot Instances**: Test/Dev için %70-90 tasarruf
- **Elastic IP**: Kullanılmıyorsa ücret alınır, dikkatli ol
- **EBS Storage**: Gereksiz snapshot'ları sil

## 📚 Kaynaklar

- [EC2 Documentation](https://docs.aws.amazon.com/ec2/)
- [Ubuntu Server Guide](https://ubuntu.com/server/docs)
- [Systemd Service Management](https://www.freedesktop.org/software/systemd/man/systemd.service.html)

