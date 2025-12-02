# GitHub Repository Kurulumu

## 📋 Adımlar

### 1. GitHub'da Repository Oluştur

1. [GitHub](https://github.com) → New Repository
2. Repository adı: `NovaCore` (veya istediğin isim)
3. Description: "Aurora State Network - Core Backend Infrastructure"
4. **Public** veya **Private** seç
5. **Initialize with README** seçme (zaten var)
6. **Create repository**

### 2. Local Repository'yi GitHub'a Bağla

```bash
cd /Users/onur/code/DeltaNova_System/NovaCore

# Remote ekle (YOUR_USERNAME'i değiştir)
git remote add origin https://github.com/YOUR_USERNAME/NovaCore.git

# veya SSH kullanıyorsan
git remote add origin git@github.com:YOUR_USERNAME/NovaCore.git

# Branch'i main yap
git branch -M main

# Push et
git push -u origin main
```

### 3. GitHub Token (Eğer Gerekirse)

Eğer 2FA aktifse veya private repo ise:

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. **Generate new token**
3. Scopes: `repo` seç
4. Token'ı kopyala
5. Push sırasında password yerine token kullan

### 4. EC2 Script'lerini Güncelle

EC2 kurulum script'inde repository URL'ini güncelle:

```bash
# scripts/ec2-setup.sh dosyasında
# YOUR_USERNAME ve REPO_NAME'i değiştir
```

## ✅ Kontrol

```bash
# Remote'ları kontrol et
git remote -v

# Son commit'leri gör
git log --oneline -5
```

## 🔄 Güncelleme

```bash
# Değişiklikleri ekle
git add -A

# Commit et
git commit -m "Commit mesajı"

# Push et
git push origin main
```

