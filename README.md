# 🎵 YouTube Downloader API

YouTube videolarını MP3 ve MP4 formatlarında indirmek için geliştirilmiş HTTP API servisi.

## 🚀 Özellikler

- **🔍 Video Arama**: URL veya arama kelimesi ile video bulma
- **🎵 MP3 İndirme**: FFmpeg ile yüksek kaliteli MP3 dönüşümü
- **🎵 Audio İndirme**: FFmpeg olmadan orijinal audio formatında indirme
- **🎬 MP4 İndirme**: Çeşitli kalitelerde video indirme
- **📊 İndirme Takibi**: Gerçek zamanlı ilerleme ve durum kontrolü
- **🌐 Web Arayüzü**: Kullanıcı dostu API dokümantasyonu

## 📋 API Endpoint'leri

### 🔍 Video Arama
```
GET/POST /api/search
```

### 🎵 MP3 İndirme
```
GET/POST /api/download/mp3
```

### 🎵 Audio İndirme (FFmpeg olmadan)
```
GET/POST /api/download/audio
```

### 🎬 MP4 İndirme
```
GET/POST /api/download/mp4
```

### 📊 Durum Kontrolü
```
GET /api/status/<download_id>
```

## 🛠️ Kurulum

### Gereksinimler
- Python 3.8+
- FFmpeg (MP3 dönüşümü için, opsiyonel)

### Adım 1: Repository'yi Klonlayın
```bash
git clone https://github.com/samkofte/youtube-api.git
cd youtube-api
```

### Adım 2: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 3: API'yi Başlatın
```bash
python api_server.py
```

API http://localhost:5000 adresinde çalışmaya başlayacak.

## 🎯 Kullanım Örnekleri

### Video Arama
```bash
curl "http://localhost:5000/api/search?q=test%20video&limit=5"
```

### MP3 İndirme
```bash
curl "http://localhost:5000/api/download/mp3?url=VIDEO_URL&quality=best"
```

### Audio İndirme (FFmpeg olmadan)
```bash
curl "http://localhost:5000/api/download/audio?url=VIDEO_URL"
```

### MP4 İndirme
```bash
curl "http://localhost:5000/api/download/mp4?url=VIDEO_URL&quality=720p"
```

## 🌐 Web Arayüzü

API'nin web arayüzüne erişmek için:
```
http://localhost:5000
```

Bu sayfada tüm endpoint'lerin dokümantasyonu ve test linkleri bulunur.

## 🚀 Cloud Deployment

Bu API'yi Render.com, Heroku, Railway gibi cloud platformlarda deploy edebilirsiniz.

Detaylı deployment rehberi için: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

### Hızlı Deployment (Render.com)
1. Bu repository'yi GitHub'a fork edin
2. render.com'a gidin ve "New Web Service" tıklayın
3. GitHub repository'nizi seçin
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `python api_server.py`
6. "Create Web Service" tıklayın

## 🧪 Test Etme

### Local Test
```bash
python test_separated_endpoints.py
```

### Cloud Test
```bash
python test_cloud_api.py https://your-app-name.onrender.com
```

## 📁 Proje Yapısı

```
youtube-api/
├── api_server.py              # Ana Python API
├── server.js                  # Node.js Gateway (opsiyonel)
├── requirements.txt           # Python bağımlılıkları
├── package.json              # Node.js bağımlılıkları
├── test_separated_endpoints.py # Local test script
├── test_cloud_api.py         # Cloud test script
├── DEPLOYMENT_GUIDE.md       # Deployment rehberi
└── README.md                 # Bu dosya
```

## 🔧 Konfigürasyon

### Environment Variables
- `PORT`: API port (varsayılan: 5000)
- `DOWNLOAD_PATH`: İndirme klasörü (varsayılan: ~/Downloads)
- `FLASK_ENV`: Flask environment (development/production)

### FFmpeg Kurulumu
MP3 dönüşümü için FFmpeg gereklidir:

#### Windows
1. https://ffmpeg.org/download.html adresinden indirin
2. C:\ffmpeg klasörüne çıkartın
3. Sistem PATH'ine ekleyin

#### macOS
```bash
brew install ffmpeg
```

#### Linux
```bash
sudo apt update
sudo apt install ffmpeg
```

## 📊 API Response Örnekleri

### Arama Sonucu
```json
{
  "success": true,
  "total_results": 3,
  "results": [
    {
      "video_url": "https://www.youtube.com/watch?v=...",
      "title": "Video Başlığı",
      "duration": 180,
      "uploader": "Kanal Adı",
      "download_links": {
        "mp3": {
          "best": "/api/download/mp3?url=...&quality=best",
          "high": "/api/download/mp3?url=...&quality=high"
        },
        "mp4": {
          "720p": "/api/download/mp4?url=...&quality=720p",
          "1080p": "/api/download/mp4?url=...&quality=1080p"
        }
      }
    }
  ]
}
```

### İndirme Başlatma
```json
{
  "success": true,
  "download_id": "uuid-string",
  "message": "MP3 İndirme başlatıldı",
  "status_url": "/api/status/uuid-string"
}
```

## ⚠️ Önemli Notlar

1. **FFmpeg**: MP3 dönüşümü için FFmpeg gereklidir
2. **Rate Limiting**: YouTube API limitlerine dikkat edin
3. **Dosya Sistemi**: Cloud'da dosyalar geçici olarak saklanır
4. **Güvenlik**: Production'da güvenlik önlemleri alın

## 🤝 Katkıda Bulunma

1. Bu repository'yi fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına bakın.

## 📞 İletişim

- **GitHub**: [@samkofte](https://github.com/samkofte)
- **Repository**: https://github.com/samkofte/youtube-api

## 🙏 Teşekkürler

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube indirme kütüphanesi
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [FFmpeg](https://ffmpeg.org/) - Media dönüştürme

---

⭐ Bu projeyi beğendiyseniz yıldız vermeyi unutmayın! 