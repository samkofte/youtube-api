# 🍪 YouTube Cookies Alma Rehberi

YouTube bot korumasını aşmak için cookies dosyası oluşturmanız gerekiyor.

## 🔧 Yöntem 1: Browser Extension (Önerilen)

### Chrome/Firefox için:
1. **"Get cookies.txt"** extension'ını yükleyin
2. YouTube'a gidin ve giriş yapın
3. Extension'ı çalıştırın
4. `cookies.txt` dosyasını indirin
5. Proje klasörüne koyun

## 🔧 Yöntem 2: Manuel Olarak

### Adım 1: YouTube'a Giriş Yapın
1. Chrome'da YouTube'a gidin
2. Google hesabınızla giriş yapın

### Adım 2: Developer Tools Açın
1. F12 tuşuna basın
2. "Application" sekmesine gidin
3. Sol tarafta "Cookies" > "https://www.youtube.com" seçin

### Adım 3: Cookies'i Export Edin
1. Tüm cookies'leri seçin
2. Sağ tık > "Copy" > "Copy as cURL"
3. Bir metin editöründe açın
4. Netscape formatına çevirin

## 🔧 Yöntem 3: Otomatik Script

```bash
# Python script ile cookies alma
pip install browser-cookie3
```

```python
import browser_cookie3
import http.cookiejar

# Chrome'dan cookies al
cookies = browser_cookie3.chrome(domain_name='.youtube.com')

# Netscape formatında kaydet
with open('cookies.txt', 'w') as f:
    f.write('# Netscape HTTP Cookie File\n')
    for cookie in cookies:
        f.write(f'{cookie.domain}\tTRUE\t{cookie.path}\t'
                f'{"TRUE" if cookie.secure else "FALSE"}\t{cookie.expires}\t'
                f'{cookie.name}\t{cookie.value}\n')
```

## 📁 Dosya Yapısı

```
youtube-api-mp3/
├── api_server.py
├── cookies.txt          # ← Bu dosyayı ekleyin
├── requirements.txt
└── ...
```

## ⚠️ Önemli Notlar

1. **Güvenlik**: cookies.txt dosyasını GitHub'a yüklemeyin
2. **Güncelleme**: Cookies'ler sürekli güncellenir
3. **Kişisel**: Sadece kendi hesabınızın cookies'ini kullanın

## 🚀 Test Etme

Cookies dosyasını ekledikten sonra:

```bash
# API'yi yeniden başlatın
python api_server.py

# Test edin
curl "http://localhost:5000/api/search?q=test%20video&limit=3"
```

## 🔄 Alternatif Çözüm

Eğer cookies çalışmazsa, API'yi şu şekilde güncelleyin:

```python
# api_server.py'de
ydl_opts = {
    # ... diğer ayarlar
    'extractor_args': {
        'youtube': {
            'skip': ['dash', 'live'],
        }
    }
}
``` 