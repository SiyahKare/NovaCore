# Docker Build Troubleshooting

## Frontend Build Donuyor

### Sorun: `npm ci` komutu çok uzun sürüyor veya donuyor

### Çözüm 1: Basitleştirilmiş Dockerfile Kullan

`Dockerfile.frontend.simple` dosyasını kullan:

```bash
# docker-compose.full.yml'de değiştir:
# dockerfile: Dockerfile.frontend
# yerine:
# dockerfile: Dockerfile.frontend.simple
```

### Çözüm 2: Build Cache Temizle

```bash
# Docker cache'i temizle
docker builder prune -a

# Sadece frontend'i rebuild et
docker compose -f docker-compose.full.yml build --no-cache novacore-frontend
```

### Çözüm 3: npm Timeout Ayarla

`.npmrc` dosyası oluştur:

```bash
cat > .npmrc <<EOF
fetch-timeout=600000
fetch-retries=5
fetch-retry-mintimeout=10000
fetch-retry-maxtimeout=60000
EOF
```

### Çözüm 4: Tek Tek Build Et

```bash
# Önce sadece backend
docker compose -f docker-compose.full.yml build novacore-api

# Sonra frontend
docker compose -f docker-compose.full.yml build novacore-frontend

# Son olarak bot
docker compose -f docker-compose.full.yml build nasipquest-bot
```

### Çözüm 5: npm Registry Değiştir

Eğer npm registry yavaşsa, daha hızlı bir mirror kullan:

```bash
# Dockerfile.frontend içinde:
RUN npm config set registry https://registry.npmmirror.com
```

### Çözüm 6: Disk Space Kontrolü

```bash
# Disk space kontrolü
df -h

# Docker disk kullanımı
docker system df

# Eski image'leri temizle
docker image prune -a
```

## Build Hızlandırma İpuçları

### 1. .dockerignore Kullan

`.dockerignore` dosyası build context'ini küçültür:

```dockerfile
node_modules
.git
.next
.env
```

### 2. Multi-stage Build Optimize Et

Sadece gerekli dosyaları kopyala:

```dockerfile
# Sadece package.json'ları kopyala
COPY package*.json ./
COPY apps/*/package.json ./apps/
COPY packages/*/package.json ./packages/
```

### 3. npm Cache Kullan

```dockerfile
# npm cache mount
RUN --mount=type=cache,target=/root/.npm \
    npm ci --legacy-peer-deps
```

### 4. Parallel Build

```bash
# Tüm servisleri paralel build et
docker compose -f docker-compose.full.yml build --parallel
```

## Hızlı Test

```bash
# Sadece syntax kontrolü
docker compose -f docker-compose.full.yml config

# Dry-run build (sadece Dockerfile kontrolü)
docker build --dry-run -f Dockerfile.frontend .

# Build progress göster
docker compose -f docker-compose.full.yml build --progress=plain
```

## EC2'de Build

EC2'de build yaparken:

```bash
# Memory limit kontrolü
free -h

# Swap ekle (eğer memory yetersizse)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Build timeout artır
export DOCKER_BUILDKIT=1
export BUILDKIT_STEP_LOG_MAX_SIZE=50000000
export BUILDKIT_STEP_LOG_MAX_SPEED=100000000

docker compose -f docker-compose.full.yml build
```

