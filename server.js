const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// CORS ayarları
app.use(cors());
app.use(express.json());

// Python API process'i
let pythonProcess = null;

// Python API'yi başlat (sadece local development için)
function startPythonAPI() {
    console.log('Python API başlatılıyor... (sadece local development)');
    
    // Cloud'da Python API ayrı servis olarak çalışacak
    if (process.env.NODE_ENV === 'production') {
        console.log('Production modunda Python API ayrı servis olarak çalışıyor');
        return;
    }
    
    pythonProcess = spawn('python', ['api_server.py'], {
        stdio: ['pipe', 'pipe', 'pipe']
    });

    pythonProcess.stdout.on('data', (data) => {
        console.log(`Python API: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.log(`Python API Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python API kapandı, kod: ${code}`);
        // 5 saniye sonra yeniden başlat
        setTimeout(startPythonAPI, 5000);
    });

    pythonProcess.on('error', (error) => {
        console.log(`Python API hatası: ${error}`);
    });
}

// Ana endpoint'ler
app.get('/', (req, res) => {
    res.json({
        message: 'YouTube Downloader API - Node.js Gateway',
        python_api: 'http://localhost:5000',
        endpoints: {
            health: '/api/health',
            search: '/api/search',
            mp3_download: '/api/download/mp3',
            audio_download: '/api/download/audio',
            mp4_download: '/api/download/mp4',
            download: '/api/download', // Eski format - geriye uyumluluk
            status: '/api/status/:id',
            downloads: '/api/downloads',
            cancel: '/api/cancel/:id',
            clear: '/api/clear'
        },
        features: {
            'mp3_conversion': 'FFmpeg ile MP3 dönüşümü',
            'audio_download': 'FFmpeg olmadan audio indirme',
            'mp4_download': 'Video indirme (çeşitli kaliteler)',
            'search': 'Video arama ve URL ile indirme'
        }
    });
});

// Python API'ye proxy
app.all('/api/*', async (req, res) => {
    try {
        // Cloud'da Python API URL'ini environment variable'dan al
        const pythonApiUrl = process.env.PYTHON_API_URL || 'http://localhost:5000';
        const pythonUrl = `${pythonApiUrl}${req.path}`;
        
        const response = await fetch(pythonUrl, {
            method: req.method,
            headers: {
                'Content-Type': 'application/json',
                ...req.headers
            },
            body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
        });

        const data = await response.json();
        res.json(data);
    } catch (error) {
        res.status(500).json({
            error: 'Python API bağlantı hatası',
            message: error.message
        });
    }
});

// Python API'yi yeniden başlat
app.post('/restart-python', (req, res) => {
    if (pythonProcess) {
        pythonProcess.kill();
    }
    startPythonAPI();
    res.json({ message: 'Python API yeniden başlatılıyor...' });
});

// Server'ı başlat
app.listen(PORT, () => {
    console.log(`Node.js Gateway başlatıldı: http://localhost:${PORT}`);
    console.log(`Python API: http://localhost:5000`);
    console.log(`\n📋 Endpoint'ler:`);
    console.log(`  🔍 /api/search - Video arama`);
    console.log(`  🎵 /api/download/mp3 - MP3 indirme`);
    console.log(`  🎵 /api/download/audio - Audio indirme (FFmpeg olmadan)`);
    console.log(`  🎬 /api/download/mp4 - MP4 indirme`);
    console.log(`  📊 /api/status/:id - İndirme durumu`);
    console.log(`  📋 /api/downloads - Tüm indirmeler`);
    console.log(`  ❌ /api/cancel/:id - İndirme iptal`);
    console.log(`  🧹 /api/clear - Tamamlananları temizle`);
    
    // Python API'yi başlat
    startPythonAPI();
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Server kapatılıyor...');
    if (pythonProcess) {
        pythonProcess.kill();
    }
    process.exit(0);
}); 