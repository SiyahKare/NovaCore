# NovaCore Scripts

## Cloudflare Tunnel Scripts

### `setup_cloudflare_tunnel.sh`
Cloudflare Tunnel otomatik kurulum script'i.

**Kullanım:**
```bash
chmod +x scripts/setup_cloudflare_tunnel.sh
./scripts/setup_cloudflare_tunnel.sh
```

**Yapılanlar:**
- Tunnel oluşturur (`novacore-siyahkare`)
- Config dosyası oluşturur (`~/.cloudflared/config.yml`)
- DNS route'ları oluşturur
- Systemd service oluşturur (Linux)
- Tunnel'ı başlatır

**Gereksinimler:**
- Cloudflare Account ID
- Cloudflare API Token
- `cloudflared` kurulu
- `jq` kurulu

### `start_cloudflared_tunnel.sh`
Cloudflare Tunnel'ı manuel başlatma script'i.

**Kullanım:**
```bash
chmod +x scripts/start_cloudflared_tunnel.sh
./scripts/start_cloudflared_tunnel.sh
```

## Marketplace Seed Scripts

### `seed_marketplace_launch.py`
Marketplace'i launch için seed item'larıyla doldurur.

**Kullanım:**
```bash
python scripts/seed_marketplace_launch.py
```

## Diğer Scripts

Tüm script'ler `scripts/` dizininde bulunur.

