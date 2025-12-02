# EC2 Kurulum Hızlı Düzeltme

## 🔴 Python 3.11 Bulunamıyor Hatası

Ubuntu 22.04'te Python 3.11 varsayılan olarak yok. Şu adımları takip et:

### Adım 1: DeadSnakes PPA Ekle

```bash
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
```

### Adım 2: Python 3.11 Kur

```bash
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
```

### Adım 3: Python 3.11'i Kontrol Et

```bash
python3.11 --version
# Python 3.11.x çıktısı görmelisin
```

### Adım 4: Script'i Yeniden Çalıştır

```bash
cd ~/NovaCore
./scripts/ec2-setup.sh
```

## 🔄 Alternatif: Mevcut Python Versiyonunu Kullan

Eğer Python 3.11 kurmak istemiyorsan, mevcut Python versiyonunu kullanabilirsin:

```bash
# Mevcut Python versiyonunu kontrol et
python3 --version

# Eğer Python 3.10 veya üzeri ise, script'i düzenle:
# python3.11 yerine python3 kullan
```

## 📝 Manuel Kurulum (Script Olmadan)

Eğer script çalışmıyorsa, adım adım manuel kurulum:

```bash
# 1. Sistem güncellemesi
sudo apt-get update
sudo apt-get upgrade -y

# 2. Temel paketler
sudo apt-get install -y curl wget git build-essential software-properties-common

# 3. Python 3.11
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip

# 4. PostgreSQL
sudo apt-get install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 5. Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 6. Database oluştur
sudo -u postgres psql <<EOF
CREATE USER novacore WITH PASSWORD 'GÜÇLÜ_ŞİFRE_BURAYA';
CREATE DATABASE novacore OWNER novacore;
GRANT ALL PRIVILEGES ON DATABASE novacore TO novacore;
\q
EOF

# 7. Projeyi klonla (eğer yoksa)
cd /opt
sudo mkdir -p novacore
sudo chown $USER:$USER novacore
cd novacore
git clone https://github.com/YOUR_USERNAME/NovaCore.git
cd NovaCore

# 8. Python environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .

# 9. Node.js dependencies
npm install

# 10. Environment variables
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

# 11. Database migration
alembic upgrade head

# 12. Frontend build
cd apps/citizen-portal
npm run build
cd ../..

# 13. Cloudflare Tunnel
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o /tmp/cloudflared.deb
sudo dpkg -i /tmp/cloudflared.deb
./scripts/setup-cloudflare-tunnel.sh
```

## ✅ Kontrol

```bash
# Python versiyonu
python3.11 --version

# Node.js versiyonu
node --version

# PostgreSQL durumu
sudo systemctl status postgresql

# Database bağlantısı
psql -U novacore -d novacore -h localhost
```

