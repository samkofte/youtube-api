# YouTube Downloader API - Ayrılmış Endpoint'ler

Bu API, YouTube videolarını indirmek için ayrılmış MP3 ve MP4 endpoint'leri sağlar.

## 🚀 Özellikler

### 🔍 Video Arama
- **Endpoint**: `/api/search`
- **Metod**: GET/POST
- **Açıklama**: Video arama (URL veya arama kelimesi) - Sayfalama destekli
- **Kullanım**:
  ```bash
  # GET ile arama
  curl "http://localhost:5000/api/search?q=test%20video&page=1&limit=5"
  
  # POST ile arama
  curl -X POST http://localhost:5000/api/search \
    -H "Content-Type: application/json" \
    -d '{"query": "test video", "page": 1, "limit": 5}'
  ```

### 🎵 MP3 İndirme
- **Endpoint**: `/api/download/mp3`
- **Metod**: GET/POST
- **Açıklama**: MP3 İndirme başlat (kalite: best, high, medium, low, worst)
- **Gereksinim**: FFmpeg (MP3 dönüşümü için)
- **Kullanım**:
  ```bash
  # GET ile MP3 indirme
  curl "http://localhost:5000/api/download/mp3?url=VIDEO_URL&quality=best"
  
  # POST ile MP3 indirme
  curl -X POST http://localhost:5000/api/download/mp3 \
    -H "Content-Type: application/json" \
    -d '{"video_url": "URL", "quality": "best"}'
  ```

### 🎵 Audio İndirme (FFmpeg olmadan)
- **Endpoint**: `/api/download/audio`
- **Metod**: GET/POST
- **Açıklama**: Audio İndirme (FFmpeg olmadan, orijinal format)
- **Gereksinim**: FFmpeg gerekmez
- **Kullanım**:
  ```bash
  # GET ile audio indirme
  curl "http://localhost:5000/api/download/audio?url=VIDEO_URL"
  
  # POST ile audio indirme
  curl -X POST http://localhost:5000/api/download/audio \
    -H "Content-Type: application/json" \
    -d '{"video_url": "URL"}'
  ```

### 🎬 MP4 İndirme
- **Endpoint**: `/api/download/mp4`
- **Metod**: GET/POST
- **Açıklama**: MP4 İndirme başlat (kalite: best, 1080p, 720p, 480p, 360p)
- **Kullanım**:
  ```bash
  # GET ile MP4 indirme
  curl "http://localhost:5000/api/download/mp4?url=VIDEO_URL&quality=720p"
  
  # POST ile MP4 indirme
  curl -X POST http://localhost:5000/api/download/mp4 \
    -H "Content-Type: application/json" \
    -d '{"video_url": "URL", "quality": "720p"}'
  ```

## 📋 Arama Sonuçları Yapısı

Arama sonuçları artık ayrılmış download link'leri içerir:

```json
{
  "success": true,
  "results": [
    {
      "video_url": "https://www.youtube.com/watch?v=...",
      "title": "Video Başlığı",
      "duration": 180,
      "uploader": "Kanal Adı",
      "view_count": 1000,
      "thumbnail": "https://...",
      "available_qualities": ["best", "720p", "480p", "360p"],
      "formats_count": 15,
      "download_links": {
        "mp3": {
          "best": "/api/download/mp3?url=...&quality=best",
          "high": "/api/download/mp3?url=...&quality=high",
          "medium": "/api/download/mp3?url=...&quality=medium",
          "low": "/api/download/mp3?url=...&quality=low",
          "audio_only": "/api/download/audio?url=..."
        },
        "mp4": {
          "best": "/api/download/mp4?url=...&quality=best",
          "1080p": "/api/download/mp4?url=...&quality=1080p",
          "720p": "/api/download/mp4?url=...&quality=720p",
          "480p": "/api/download/mp4?url=...&quality=480p",
          "360p": "/api/download/mp4?url=...&quality=360p"
        }
      }
    }
  ]
}
```

## 🔧 Genel Endpoint'ler

### Sağlık Kontrolü
- **Endpoint**: `/api/health`
- **Metod**: GET
- **Açıklama**: API sağlık kontrolü ve özellik durumu

### İndirme Durumu
- **Endpoint**: `/api/status/<download_id>`
- **Metod**: GET
- **Açıklama**: İndirme durumu kontrolü

### Tüm İndirmeler
- **Endpoint**: `/api/downloads`
- **Metod**: GET
- **Açıklama**: Tüm indirmeleri listele

### İndirme İptal
- **Endpoint**: `/api/cancel/<download_id>`
- **Metod**: POST
- **Açıklama**: İndirme iptal et

### Temizleme
- **Endpoint**: `/api/clear`
- **Metod**: POST
- **Açıklama**: Tamamlanan indirmeleri temizle

## 🧪 Test Etme

Test script'ini çalıştırmak için:

```bash
python test_separated_endpoints.py
```

Bu script:
1. Health check yapar
2. Video arama test eder
3. MP3 indirme test eder
4. Audio indirme test eder
5. MP4 indirme test eder
6. İndirme durumlarını kontrol eder

## 🎯 Kullanım Örnekleri

### Python ile Kullanım

```python
import requests

# Video ara
response = requests.post('http://localhost:5000/api/search', 
                        json={'query': 'test video'})
video_data = response.json()

if video_data['success']:
    video = video_data['results'][0]
    
    # MP3 indirme
    mp3_response = requests.post('http://localhost:5000/api/download/mp3',
                                json={
                                    'video_url': video['video_url'],
                                    'quality': 'best'
                                })
    mp3_id = mp3_response.json()['download_id']
    
    # MP4 indirme
    mp4_response = requests.post('http://localhost:5000/api/download/mp4',
                                json={
                                    'video_url': video['video_url'],
                                    'quality': '720p'
                                })
    mp4_id = mp4_response.json()['download_id']
    
    # Durum kontrolü
    status = requests.get(f'http://localhost:5000/api/status/{mp3_id}').json()
    print(f"MP3 Progress: {status['progress']}%")
```

### JavaScript ile Kullanım

```javascript
// Video ara
fetch('http://localhost:5000/api/search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({query: 'test video'})
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        const video = data.results[0];
        
        // MP3 indirme
        return fetch('http://localhost:5000/api/download/mp3', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                video_url: video.video_url,
                quality: 'best'
            })
        });
    }
})
.then(response => response.json())
.then(data => {
    console.log('MP3 Download ID:', data.download_id);
});
```

## 🔗 Hızlı Test Linkleri

Tarayıcınızda test edebileceğiniz linkler:

- 🔍 [Sağlık Kontrolü](http://localhost:5000/api/health)
- 🎵 [Video Arama](http://localhost:5000/api/search?q=test%20video&limit=5)
- 🎵 [MP3 İndirme](http://localhost:5000/api/download/mp3?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&quality=best)
- 🎵 [Audio İndirme](http://localhost:5000/api/download/audio?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ)
- 🎬 [MP4 İndirme](http://localhost:5000/api/download/mp4?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&quality=720p)
- 📋 [Tüm İndirmeler](http://localhost:5000/api/downloads)

## 📝 Notlar

1. **MP3 İndirme**: FFmpeg gereklidir, yoksa audio indirme kullanın
2. **Audio İndirme**: FFmpeg olmadan orijinal audio formatında indirir
3. **MP4 İndirme**: Video+audio birleştirme için FFmpeg kullanır
4. **Geriye Uyumluluk**: Eski `/api/download` endpoint'i hala çalışır
5. **Arama Sonuçları**: Artık MP3 ve MP4 link'leri ayrı kategorilerde

## 🚀 Başlatma

```bash
# Python API'yi başlat
python api_server.py

# Node.js Gateway'i başlat (opsiyonel)
node server.js
```

API'ler şu adreslerde çalışır:
- Python API: http://localhost:5000
- Node.js Gateway: http://localhost:3000 