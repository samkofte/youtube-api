const express = require('express');
const { spawn } = require('child_process');
const cors = require('cors');

const app = express();
const PORT = 3000;

// CORS ayarları
app.use(cors());
app.use(express.json());

// Python API'yi başlat
console.log('Python API başlatılıyor...');
const pythonAPI = spawn('python', ['api_server.py']);

pythonAPI.stdout.on('data', (data) => {
    console.log(`Python: ${data}`);
});

pythonAPI.stderr.on('data', (data) => {
    console.log(`Python Error: ${data}`);
});

// Ana sayfa
app.get('/', (req, res) => {
    res.json({
        message: 'YouTube Downloader API - Node.js Gateway',
        python_api: 'http://localhost:5000',
        endpoints: {
            health: 'http://localhost:5000/api/health',
            search: 'http://localhost:5000/api/search',
            download: 'http://localhost:5000/api/download',
            status: 'http://localhost:5000/api/status/:id'
        }
    });
});

// Server'ı başlat
app.listen(PORT, () => {
    console.log(`Node.js Gateway: http://localhost:${PORT}`);
    console.log(`Python API: http://localhost:5000`);
    console.log('Çıkmak için Ctrl+C');
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('Server kapatılıyor...');
    pythonAPI.kill();
    process.exit(0);
}); 