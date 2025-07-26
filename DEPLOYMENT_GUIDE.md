# 🚀 Cloud Deployment Rehberi

Bu rehber, YouTube Downloader API'nizi Render.com, Heroku, Railway gibi cloud platformlarda nasıl deploy edeceğinizi açıklar.

## 📋 Seçenekler

### 1. **Sadece Python API (Önerilen)**
- Daha basit
- Daha az maliyet
- Daha hızlı

### 2. **Python API + Node.js Gateway**
- Daha karmaşık
- Daha fazla özellik
- Daha yüksek maliyet

## 🎯 Render.com Deployment

### Adım 1: GitHub'a Yükleyin
```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/username/youtube-downloader-api.git
git push -u origin main
```

### Adım 2: Render.com'da Servis Oluşturun

1. **Render.com'a gidin** ve hesap oluşturun
2. **"New Web Service"** tıklayın
3. **GitHub repository'nizi** bağlayın
4. **Ayarları yapılandırın:**

#### Python API için:
```
Name: youtube-downloader-api
Environment: Python 3
Build Command: pip install -r requirements.txt
Start Command: python api_server.py
```

#### Environment Variables:
```
PYTHON_VERSION=3.11.0
FLASK_ENV=production
DOWNLOAD_PATH=/tmp
```

### Adım 3: Deploy Edin
- **"Create Web Service"** tıklayın
- Deployment otomatik başlayacak
- 5-10 dakika sürebilir

## 🎯 Heroku Deployment

### Adım 1: Heroku CLI Kurulumu
```bash
# Heroku CLI'yi indirin: https://devcenter.heroku.com/articles/heroku-cli
heroku login
```

### Adım 2: Heroku App Oluşturun
```bash
heroku create your-app-name
git push heroku main
```

### Adım 3: Environment Variables
```bash
heroku config:set FLASK_ENV=production
heroku config:set DOWNLOAD_PATH=/tmp
```

## 🎯 Railway Deployment

### Adım 1: Railway'e Gidin
1. **railway.app** adresine gidin
2. **GitHub ile giriş yapın**
3. **"New Project"** tıklayın

### Adım 2: Repository Seçin
1. **GitHub repository'nizi** seçin
2. **"Deploy Now"** tıklayın

### Adım 3: Environment Variables
```
FLASK_ENV=production
DOWNLOAD_PATH=/tmp
```

## 🔧 Environment Variables

### Gerekli Variables:
```
FLASK_ENV=production
DOWNLOAD_PATH=/tmp
PORT=5000 (otomatik)
```

### Opsiyonel Variables:
```
PYTHON_API_URL=https://your-python-api.onrender.com (Node.js gateway için)
NODE_ENV=production (Node.js için)
```

## 📁 Dosya Yapısı

```
youtube-api-mp3/
├── api_server.py          # Ana Python API
├── server.js              # Node.js Gateway (opsiyonel)
├── requirements.txt       # Python dependencies
├── package.json           # Node.js dependencies
├── render.yaml           # Render.com config
├── Procfile              # Heroku config
├── runtime.txt           # Python version
└── README.md
```

## 🌐 API Kullanımı

### Deploy Edildikten Sonra:

#### Python API Direkt:
```
https://your-app-name.onrender.com/api/health
https://your-app-name.onrender.com/api/search?q=test
https://your-app-name.onrender.com/api/download/mp3?url=VIDEO_URL
```

#### Node.js Gateway ile:
```
https://your-gateway-app.onrender.com/api/health
https://your-gateway-app.onrender.com/api/search?q=test
https://your-gateway-app.onrender.com/api/download/mp3?url=VIDEO_URL
```

## ⚠️ Önemli Notlar

### 1. **FFmpeg Sorunu**
- Cloud platformlarda FFmpeg kurulu olmayabilir
- MP3 dönüşümü çalışmayabilir
- Audio endpoint'ini kullanın: `/api/download/audio`

### 2. **Dosya Sistemi**
- Cloud'da dosyalar geçici olarak saklanır
- İndirilen dosyalar kalıcı değildir
- Dosya paylaşımı için ek servis gerekir

### 3. **Rate Limiting**
- YouTube API limitleri olabilir
- Çok fazla istek göndermeyin
- Error handling ekleyin

### 4. **Maliyet**
- Render.com: Ücretsiz tier mevcut
- Heroku: Ücretli (ücretsiz tier kaldırıldı)
- Railway: Ücretsiz tier mevcut

## 🧪 Test Etme

### Deploy Sonrası Test:
```bash
# Health check
curl https://your-app-name.onrender.com/api/health

# Search test
curl "https://your-app-name.onrender.com/api/search?q=test%20video&limit=3"

# Download test (audio - FFmpeg olmadan)
curl "https://your-app-name.onrender.com/api/download/audio?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## 🔄 Güncelleme

### Kod Güncellemesi:
```bash
git add .
git commit -m "Update code"
git push origin main
# Cloud platform otomatik deploy edecek
```

### Environment Variables Güncellemesi:
- Cloud platform dashboard'undan güncelleyin
- Servisi yeniden başlatın

## 🆘 Sorun Giderme

### Yaygın Sorunlar:

1. **Build Hatası**
   - `requirements.txt` kontrol edin
   - Python version uyumluluğu

2. **Runtime Hatası**
   - Environment variables kontrol edin
   - Log'ları inceleyin

3. **API Çalışmıyor**
   - Health endpoint'ini test edin
   - CORS ayarlarını kontrol edin

4. **İndirme Çalışmıyor**
   - FFmpeg olmadan audio endpoint'ini kullanın
   - YouTube URL'ini kontrol edin

## 📞 Destek

Sorun yaşarsanız:
1. Cloud platform log'larını kontrol edin
2. Environment variables'ları kontrol edin
3. API health endpoint'ini test edin
4. GitHub issues açın 