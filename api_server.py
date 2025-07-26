#!/usr/bin/env python3
"""
YouTube MP3/MP4 İndirici - HTTP API Server
Bu API, YouTube videolarını indirmek için HTTP endpoint'leri sağlar.
MP3 ve MP4 indirme işlemleri ayrı endpoint'lerde yönetilir.
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import yt_dlp
import os
import threading
import time
import json
import tempfile
from werkzeug.utils import secure_filename
import uuid
import random

app = Flask(__name__)
CORS(app)  # Cross-origin requests için

# Global variables
downloads = {}  # Download status tracking
# Cloud deployment için geçici klasör kullan
download_path = os.environ.get('DOWNLOAD_PATH', os.path.expanduser("~/Downloads"))
if not os.path.exists(download_path):
    download_path = "/tmp"  # Cloud'da geçici klasör

# Simple HTML template for web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>YouTube Downloader API</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #e74c3c; text-align: center; }
        .section { margin: 30px 0; padding: 20px; border-radius: 8px; }
        .mp3-section { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
        .mp4-section { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; }
        .search-section { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; }
        .endpoint { background: rgba(255,255,255,0.1); padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #fff; }
        .method { font-weight: bold; color: #fff; }
        .url { font-family: monospace; background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 3px; color: #fff; }
        .description { color: rgba(255,255,255,0.9); margin-top: 5px; }
        .example { background: rgba(0,0,0,0.1); padding: 10px; border-radius: 5px; margin-top: 10px; font-family: monospace; font-size: 12px; color: #fff; }
        .status { text-align: center; padding: 20px; background: #d4edda; color: #155724; border-radius: 5px; margin: 20px 0; }
        .section-title { font-size: 24px; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 YouTube Downloader API</h1>
        
        <div class="status">
            ✅ API Server çalışıyor! Port: 5000
        </div>

        <div class="section search-section">
            <div class="section-title">🔍 Video Arama</div>
            
            <div class="endpoint">
                <div class="method">GET/POST</div>
                <div class="url">/api/search</div>
                <div class="description">Video arama (URL veya arama kelimesi) - Sayfalama destekli</div>
                <div class="example">
                    GET: curl "http://localhost:5000/api/search?q=test%20video&page=1&limit=5"<br>
                    POST: curl -X POST http://localhost:5000/api/search -H "Content-Type: application/json" -d '{"query": "test video", "page": 1, "limit": 5}'
                </div>
            </div>
        </div>

        <div class="section mp3-section">
            <div class="section-title">🎵 MP3 İndirme</div>
            
            <div class="endpoint">
                <div class="method">GET/POST</div>
                <div class="url">/api/download/mp3</div>
                <div class="description">MP3 İndirme başlat (kalite: best, high, medium, low, worst)</div>
                <div class="example">
                    GET: curl "http://localhost:5000/api/download/mp3?url=VIDEO_URL&quality=best"<br>
                    POST: curl -X POST http://localhost:5000/api/download/mp3 -H "Content-Type: application/json" -d '{"video_url": "URL", "quality": "best"}'
                </div>
            </div>

            <div class="endpoint">
                <div class="method">GET/POST</div>
                <div class="url">/api/download/audio</div>
                <div class="description">Audio İndirme (FFmpeg olmadan, orijinal format)</div>
                <div class="example">
                    GET: curl "http://localhost:5000/api/download/audio?url=VIDEO_URL"<br>
                    POST: curl -X POST http://localhost:5000/api/download/audio -H "Content-Type: application/json" -d '{"video_url": "URL"}'
                </div>
            </div>
        </div>

        <div class="section mp4-section">
            <div class="section-title">🎬 MP4 İndirme</div>
            
            <div class="endpoint">
                <div class="method">GET/POST</div>
                <div class="url">/api/download/mp4</div>
                <div class="description">MP4 İndirme başlat (kalite: best, 1080p, 720p, 480p, 360p)</div>
                <div class="example">
                    GET: curl "http://localhost:5000/api/download/mp4?url=VIDEO_URL&quality=720p"<br>
                    POST: curl -X POST http://localhost:5000/api/download/mp4 -H "Content-Type: application/json" -d '{"video_url": "URL", "quality": "720p"}'
                </div>
            </div>
        </div>

        <div class="section" style="background: #f8f9fa; color: #333;">
            <div class="section-title" style="color: #333;">🔧 Genel Endpoint'ler</div>
            
            <div class="endpoint" style="background: #e9ecef; color: #333;">
                <div class="method" style="color: #007bff;">GET</div>
                <div class="url" style="background: #fff; color: #333;">/api/health</div>
                <div class="description" style="color: #6c757d;">API sağlık kontrolü</div>
                <div class="example" style="background: #fff; color: #333;">curl http://localhost:5000/api/health</div>
            </div>

            <div class="endpoint" style="background: #e9ecef; color: #333;">
                <div class="method" style="color: #007bff;">GET/POST</div>
                <div class="url" style="background: #fff; color: #333;">/api/download</div>
                <div class="description" style="color: #6c757d;">İndirme başlat (eski format - geriye uyumluluk)</div>
                <div class="example" style="background: #fff; color: #333;">
                    GET: curl "http://localhost:5000/api/download?url=VIDEO_URL&format=mp4&quality=720p"<br>
                    POST: curl -X POST http://localhost:5000/api/download -H "Content-Type: application/json" -d '{"video_url": "URL", "format": "mp4", "quality": "720p"}'
                </div>
            </div>

            <div class="endpoint" style="background: #e9ecef; color: #333;">
                <div class="method" style="color: #007bff;">GET</div>
                <div class="url" style="background: #fff; color: #333;">/api/status/&lt;download_id&gt;</div>
                <div class="description" style="color: #6c757d;">İndirme durumu kontrolü</div>
                <div class="example" style="background: #fff; color: #333;">curl http://localhost:5000/api/status/DOWNLOAD_ID</div>
            </div>

            <div class="endpoint" style="background: #e9ecef; color: #333;">
                <div class="method" style="color: #007bff;">GET</div>
                <div class="url" style="background: #fff; color: #333;">/api/downloads</div>
                <div class="description" style="color: #6c757d;">Tüm indirmeleri listele</div>
                <div class="example" style="background: #fff; color: #333;">curl http://localhost:5000/api/downloads</div>
            </div>

            <div class="endpoint" style="background: #e9ecef; color: #333;">
                <div class="method" style="color: #007bff;">POST</div>
                <div class="url" style="background: #fff; color: #333;">/api/cancel/&lt;download_id&gt;</div>
                <div class="description" style="color: #6c757d;">İndirme iptal et</div>
                <div class="example" style="background: #fff; color: #333;">curl -X POST http://localhost:5000/api/cancel/DOWNLOAD_ID</div>
            </div>

            <div class="endpoint" style="background: #e9ecef; color: #333;">
                <div class="method" style="color: #007bff;">POST</div>
                <div class="url" style="background: #fff; color: #333;">/api/clear</div>
                <div class="description" style="color: #6c757d;">Tamamlanan indirmeleri temizle</div>
                <div class="example" style="background: #fff; color: #333;">curl -X POST http://localhost:5000/api/clear</div>
            </div>
        </div>

        <h2>🔗 Hızlı Test Linkleri</h2>
        <div class="section" style="background: #f8f9fa; color: #333;">
            <div class="endpoint" style="background: #e9ecef; color: #333;">
                <div class="method" style="color: #007bff;">GET</div>
                <div class="url" style="background: #fff; color: #333;">Hızlı Test</div>
                <div class="description" style="color: #6c757d;">Bu linkleri tarayıcınızda test edin:</div>
                <div class="example" style="background: #fff; color: #333;">
                    <a href="/api/health" target="_blank">🔍 Sağlık Kontrolü</a><br>
                    <a href="/api/search?q=test%20video&limit=5" target="_blank">🎵 Video Arama (5 sonuç)</a><br>
                    <a href="/api/download/mp3?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&quality=best" target="_blank">🎵 MP3 İndirme (320kbps)</a><br>
                    <a href="/api/download/audio?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ" target="_blank">🎵 Audio İndirme (FFmpeg olmadan)</a><br>
                    <a href="/api/download/mp4?url=https://www.youtube.com/watch?v=dQw4w9WgXcQ&quality=720p" target="_blank">🎬 MP4 İndirme</a><br>
                    <a href="/api/downloads" target="_blank">📋 Tüm İndirmeler</a>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


def download_with_retry(video_url, ydl_opts, max_retries=3):
    """Download with retry mechanism"""
    for attempt in range(max_retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
            return True
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(2, 5))  # Random delay
                continue
            else:
                raise e


def is_youtube_url(text):
    """Check if text is a YouTube URL"""
    import re
    youtube_patterns = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'(?:https?://)?(?:www\.)?youtu\.be/[\w-]+',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/[\w-]+'
    ]
    return any(re.match(pattern, text) for pattern in youtube_patterns)

def search_youtube(query, max_results=10):
    """Search YouTube for videos"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'default_search': f'ytsearch{max_results}',
            # Bot korumasını aşmak için
            'cookiefile': 'cookies.txt',  # YouTube cookies dosyası
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            results = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
            if results and 'entries' in results and results['entries']:
                return results['entries']
                
    except Exception as e:
        print(f"Arama hatası: {str(e)}")
        
    return []

def get_video_info(video_url):
    """Get video information"""
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'listformats': True,
            # Bot korumasını aşmak için
            'cookiefile': 'cookies.txt',  # YouTube cookies dosyası
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return info
            
    except Exception as e:
        print(f"Video bilgileri alınamadı: {str(e)}")
        return None

def get_available_qualities(info):
    """Get available quality options from video info"""
    try:
        formats = info.get('formats', [])
        quality_options = []
        
        # Extract video formats with resolution info
        for fmt in formats:
            if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                # Video with audio
                height = fmt.get('height', 0)
                if height:
                    quality_options.append(f"{height}p")
            elif fmt.get('vcodec') != 'none':
                # Video only
                height = fmt.get('height', 0)
                if height:
                    quality_options.append(f"{height}p (video only)")
        
        # Add audio-only option
        audio_formats = [fmt for fmt in formats if fmt.get('acodec') != 'none' and fmt.get('vcodec') == 'none']
        if audio_formats:
            quality_options.append("Audio only")
        
        # Add best/worst options and sort
        quality_options = ["best", "worst"] + sorted(list(set(quality_options)), 
                                                   key=lambda x: int(x.split('p')[0]) if 'p' in x else 0, reverse=True)
        
        return quality_options, formats
        
    except Exception as e:
        print(f"Kalite seçenekleri alınamadı: {str(e)}")
        return ["best", "worst", "720p", "480p", "360p"], []

def get_format_string_for_quality(quality, formats=None):
    """Get the appropriate format string for the selected quality"""
    try:
        if quality == "best":
            return 'best[ext=mp4]/best'
        elif quality == "worst":
            return 'worst[ext=mp4]/worst'
        elif quality == "Audio only":
            return 'bestaudio/best'
        elif "p" in quality:
            resolution = quality.split('p')[0]
            if resolution.isdigit():
                # HD indirme için daha basit ve güvenilir format string
                if int(resolution) >= 720:
                    # HD kaliteler için: önce video+audio, sonra video+bestaudio
                    return f'best[height>={resolution}][ext=mp4]/best[height>={resolution}]+bestaudio/best[height>={resolution}]/best'
                else:
                    # SD kaliteler için: basit format
                    return f'best[height={resolution}][ext=mp4]/best[height={resolution}]/best'
        return 'best[ext=mp4]/best'
    except Exception as e:
        print(f"Format string oluşturma hatası: {str(e)}")
        return 'best[ext=mp4]/best'

def progress_hook(d, download_id):
    """Progress hook for download updates"""
    if download_id in downloads:
        if d['status'] == 'downloading':
            try:
                downloaded = d.get('downloaded_bytes', 0)
                total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
                
                if total > 0:
                    progress = (downloaded / total) * 100
                    downloads[download_id]['progress'] = progress
                    
                speed = d.get('speed', 0)
                if speed:
                    speed_mb = speed / 1024 / 1024
                    downloads[download_id]['speed'] = f"{speed_mb:.1f} MB/s"
                    
                downloads[download_id]['status'] = 'downloading'
                downloads[download_id]['downloaded_bytes'] = downloaded
                downloads[download_id]['total_bytes'] = total
                    
            except Exception:
                pass
        elif d['status'] == 'finished':
            downloads[download_id]['progress'] = 100
            downloads[download_id]['status'] = 'finished'

def check_ffmpeg_available():
    """Check if FFmpeg is available"""
    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

def get_audio_format_info(file_path):
    """Get audio format information"""
    try:
        import mutagen
        audio = mutagen.File(file_path)
        if audio:
            return {
                'format': audio.mime[0].split('/')[-1].upper(),
                'duration': audio.info.length if hasattr(audio.info, 'length') else None,
                'bitrate': audio.info.bitrate if hasattr(audio.info, 'bitrate') else None
            }
    except:
        pass
    
    # Fallback info
    ext = file_path.split('.')[-1].upper()
    return {         
        'format': ext,
        'duration': None,
        'bitrate': None
    }

def get_video_format_info(file_path):
    """Get video format information"""
    # Check if moviepy is available
    try:
        import moviepy
    except ImportError:
        print("Moviepy not available for video info")
        # Fallback info
        ext = file_path.split('.')[-1].upper()
        return {
            'format': ext,
            'duration': None,
            'fps': None,
            'size': None,
            'width': None,
            'height': None
        }
    
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(file_path)
        return {
            'format': file_path.split('.')[-1].upper(),
            'duration': clip.duration,
            'fps': clip.fps,
            'size': f"{clip.w}x{clip.h}",
            'width': clip.w,
            'height': clip.h
        }
    except Exception as e:
        print(f"Video info error: {str(e)}")
        # Fallback info
        ext = file_path.split('.')[-1].upper()
        return {
            'format': ext,
            'duration': None,
            'fps': None,
            'size': None,
            'width': None,
            'height': None
        }

def convert_video_with_moviepy(input_file, output_file, quality='720p'):
    """Convert video using moviepy (no FFmpeg required)"""
    # Check if moviepy is available
    try:
        import moviepy
    except ImportError:
        print("Moviepy not available for video conversion")
        return False
    
    try:
        from moviepy.editor import VideoFileClip
        
        # Load video
        clip = VideoFileClip(input_file)
        
        # Set quality (resolution)
        quality_map = {
            '360p': (640, 360),
            '480p': (854, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '1440p': (2560, 1440),
            '2160p': (3840, 2160)
        }
        
        target_size = quality_map.get(quality, (1280, 720))
        
        # Resize if needed
        if clip.w > target_size[0] or clip.h > target_size[1]:
            clip = clip.resize(target_size)
        
        # Export as MP4
        clip.write_videofile(output_file, codec='libx264', audio_codec='aac')
        
        # Close clip
        clip.close()
        
        # Remove original file
        os.remove(input_file)
        
        return True
    except Exception as e:
        print(f"Moviepy conversion error: {str(e)}")
        return False

def download_video_api(video_url, format_type, quality, output_path, download_id):
    """Download video for API"""
    try:
        # Create output path if it doesn't exist
        os.makedirs(output_path, exist_ok=True)
        
        # Check FFmpeg availability
        ffmpeg_available = check_ffmpeg_available()
        
        # Configure yt-dlp options
        ydl_opts = {
            'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
            'progress_hooks': [lambda d: progress_hook(d, download_id)],
            # Bot korumasını aşmak için
            'cookiefile': 'cookies.txt',  # YouTube cookies dosyası
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        if format_type == "mp3" or format_type == "audio":
            # MP3 quality mapping
            mp3_quality_map = {
                'best': '320',
                'high': '256',
                'medium': '192',
                'low': '128',
                'worst': '96'
            }
            
            # Get audio quality
            audio_quality = mp3_quality_map.get(quality, '192')
            
            if format_type == "mp3":
                if ffmpeg_available:
                    # Use FFmpeg for MP3 conversion
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': audio_quality,
                        }],
                    })
                    format_display = f"MP3 {audio_quality}kbps (FFmpeg)"
                else:
                    # Download best audio without conversion
                    ydl_opts.update({
                        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                    })
                    format_display = f"Audio (En iyi kalite - MP3 dönüşümü için FFmpeg gerekli)"
                    downloads[download_id]['note'] = "FFmpeg kurulumu ile MP3 dönüşümü yapılabilir"
            else:  # audio format
                # FFmpeg olmadan audio indir
                ydl_opts.update({
                    'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                })
                format_display = f"Audio (FFmpeg olmadan)"
                
        else:  # mp4
            # HD indirme için basit ve güvenilir format string
            format_string = get_format_string_for_quality(quality)
            
            # FFmpeg yoksa daha basit format kullan
            if not ffmpeg_available and '+' in format_string:
                format_string = f'best[height>={quality.replace("p", "")}][ext=mp4]/best[height>={quality.replace("p", "")}]/best'
                format_display = f"Video {quality} (Basit Format)"
            else:
                format_display = f"Video {quality} (HD Format)"
            
            ydl_opts['format'] = format_string
        
        downloads[download_id]['status'] = 'starting'
        downloads[download_id]['message'] = f"İndirme başlatılıyor... Format: {format_display}"
        downloads[download_id]['ffmpeg_available'] = ffmpeg_available
        
        download_with_retry(video_url, ydl_opts)
        
        # Get file info after download
        try:
            for file in os.listdir(output_path):
                if file.endswith(('.m4a', '.webm', '.mp3', '.mp4', '.mkv')):
                    file_path = os.path.join(output_path, file)
                    file_size = os.path.getsize(file_path)
                    
                    downloads[download_id]['file_info'] = {
                        'filename': file,
                        'format': file.split('.')[-1].upper(),
                        'size_bytes': file_size,
                        'size_mb': f"{file_size / (1024*1024):.1f} MB"
                    }
                    break
        except Exception as e:
            downloads[download_id]['warning'] = f"Dosya bilgisi alınamadı: {str(e)}"
            
        downloads[download_id]['status'] = 'completed'
        downloads[download_id]['message'] = "İndirme başarıyla tamamlandı!"
        return True
        
    except Exception as e:
        downloads[download_id]['status'] = 'error'
        downloads[download_id]['message'] = f"İndirme hatası: {str(e)}"
        return False

@app.route('/', methods=['GET'])
def home():
    """Home page with API documentation"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    ffmpeg_available = check_ffmpeg_available()
    
    # Check if moviepy is available
    moviepy_available = False
    try:
        import moviepy
        moviepy_available = True
    except ImportError:
        pass
    
    return jsonify({
        'status': 'healthy',
        'message': 'YouTube Downloader API is running',
        'version': '1.0.0',
        'ffmpeg_available': ffmpeg_available,
        'moviepy_available': moviepy_available,
        'features': {
            'mp3_conversion': ffmpeg_available,
            'video_audio_merge': ffmpeg_available,
            'high_quality_downloads': moviepy_available or ffmpeg_available
        }
    })

@app.route('/api/search', methods=['GET', 'POST'])
def search_video():
    """Search for video by query or URL"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            query = request.args.get('q', '').strip()
            page = int(request.args.get('page', 1))
            limit = int(request.args.get('limit', 10))
        else:  # POST
            data = request.get_json()
            query = data.get('query', '').strip()
            page = data.get('page', 1)
            limit = data.get('limit', 10)
        
        if not query:
            return jsonify({'error': 'Query parameter is required. Use ?q=query for GET or {"query": "query"} for POST'}), 400
        
        # Determine if it's a URL or search query
        if is_youtube_url(query):
            # Single video URL
            video_url = query
            search_type = 'url'
            
            # Get video info
            info = get_video_info(video_url)
            if not info:
                return jsonify({'error': 'Video bilgileri alınamadı'}), 500
            
            # Get available qualities
            quality_options, formats = get_available_qualities(info)
            
            return jsonify({
                'success': True,
                'search_type': search_type,
                'total_results': 1,
                'page': 1,
                'limit': 1,
                'results': [{
                    'video_url': video_url,
                    'title': info.get('title', 'Bilinmiyor'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Bilinmiyor'),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'available_qualities': quality_options,
                    'formats_count': len(formats),
                    'download_links': {
                        'mp3': {
                            'best': f'/api/download/mp3?url={video_url}&quality=best',
                            'high': f'/api/download/mp3?url={video_url}&quality=high',
                            'medium': f'/api/download/mp3?url={video_url}&quality=medium',
                            'low': f'/api/download/mp3?url={video_url}&quality=low',
                            'audio_only': f'/api/download/audio?url={video_url}'
                        },
                        'mp4': {
                            'best': f'/api/download/mp4?url={video_url}&quality=best',
                            '1080p': f'/api/download/mp4?url={video_url}&quality=1080p',
                            '720p': f'/api/download/mp4?url={video_url}&quality=720p',
                            '480p': f'/api/download/mp4?url={video_url}&quality=480p',
                            '360p': f'/api/download/mp4?url={video_url}&quality=360p'
                        }
                    }
                }]
            })
        else:
            # Search query
            search_type = 'search'
            
            # Get search results
            search_results = search_youtube(query, max_results=limit)
            if not search_results:
                return jsonify({'error': 'Video bulunamadı'}), 404
            
            # Process each result
            processed_results = []
            for entry in search_results:
                if entry:
                    try:
                        # Get detailed info for each video
                        info = get_video_info(entry.get('url', ''))
                        if info:
                            quality_options, formats = get_available_qualities(info)
                            processed_results.append({
                                'video_url': entry.get('url', ''),
                                'title': info.get('title', 'Bilinmiyor'),
                                'duration': info.get('duration', 0),
                                'uploader': info.get('uploader', 'Bilinmiyor'),
                                'view_count': info.get('view_count', 0),
                                'thumbnail': info.get('thumbnail', ''),
                                'available_qualities': quality_options,
                                'formats_count': len(formats),
                                'download_links': {
                                    'mp3': {
                                        'best': f'/api/download/mp3?url={entry.get("url", "")}&quality=best',
                                        'high': f'/api/download/mp3?url={entry.get("url", "")}&quality=high',
                                        'medium': f'/api/download/mp3?url={entry.get("url", "")}&quality=medium',
                                        'low': f'/api/download/mp3?url={entry.get("url", "")}&quality=low',
                                        'audio_only': f'/api/download/audio?url={entry.get("url", "")}'
                                    },
                                    'mp4': {
                                        'best': f'/api/download/mp4?url={entry.get("url", "")}&quality=best',
                                        '1080p': f'/api/download/mp4?url={entry.get("url", "")}&quality=1080p',
                                        '720p': f'/api/download/mp4?url={entry.get("url", "")}&quality=720p',
                                        '480p': f'/api/download/mp4?url={entry.get("url", "")}&quality=480p',
                                        '360p': f'/api/download/mp4?url={entry.get("url", "")}&quality=360p'
                                    }
                                }
                            })
                    except Exception as e:
                        print(f"Video bilgileri alınamadı: {str(e)}")
                        continue
            
            return jsonify({
                'success': True,
                'search_type': search_type,
                'query': query,
                'total_results': len(processed_results),
                'page': page,
                'limit': limit,
                'results': processed_results
            })
        
    except Exception as e:
        return jsonify({'error': f'Search error: {str(e)}'}), 500

@app.route('/api/download/mp3', methods=['GET', 'POST'])
def start_mp3_download():
    """Start MP3 download"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            video_url = request.args.get('url', '').strip()
            quality = request.args.get('quality', 'best')
            custom_path = request.args.get('path', download_path)
        else:  # POST
            data = request.get_json()
            video_url = data.get('video_url', '').strip()
            quality = data.get('quality', 'best')
            custom_path = data.get('output_path', download_path)
        
        if not video_url:
            return jsonify({
                'error': 'Video URL is required. Use ?url=VIDEO_URL for GET or {"video_url": "URL"} for POST'
            }), 400
        
        # Generate unique download ID
        download_id = str(uuid.uuid4())
        
        # Initialize download status
        downloads[download_id] = {
            'status': 'queued',
            'progress': 0,
            'speed': '0 MB/s',
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'message': 'MP3 İndirme kuyruğa alındı',
            'video_url': video_url,
            'format': 'mp3',
            'quality': quality,
            'output_path': custom_path,
            'start_time': time.time()
        }
        
        # Start download in background thread
        thread = threading.Thread(
            target=download_video_api,
            args=(video_url, 'mp3', quality, custom_path, download_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': 'MP3 İndirme başlatıldı',
            'format': 'mp3',
            'ffmpeg_required': True,
            'status_url': f'/api/status/{download_id}',
            'download_url': f'/api/status/{download_id}'
        })
        
    except Exception as e:
        return jsonify({'error': f'MP3 Download error: {str(e)}'}), 500

@app.route('/api/download/audio', methods=['GET', 'POST'])
def start_audio_download():
    """Start audio download (without FFmpeg conversion)"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            video_url = request.args.get('url', '').strip()
            custom_path = request.args.get('path', download_path)
        else:  # POST
            data = request.get_json()
            video_url = data.get('video_url', '').strip()
            custom_path = data.get('output_path', download_path)
        
        if not video_url:
            return jsonify({
                'error': 'Video URL is required. Use ?url=VIDEO_URL for GET or {"video_url": "URL"} for POST'
            }), 400
        
        # Generate unique download ID
        download_id = str(uuid.uuid4())
        
        # Initialize download status
        downloads[download_id] = {
            'status': 'queued',
            'progress': 0,
            'speed': '0 MB/s',
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'message': 'Audio İndirme kuyruğa alındı',
            'video_url': video_url,
            'format': 'audio',
            'quality': 'best',
            'output_path': custom_path,
            'start_time': time.time()
        }
        
        # Start download in background thread
        thread = threading.Thread(
            target=download_video_api,
            args=(video_url, 'audio', 'best', custom_path, download_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': 'Audio İndirme başlatıldı (FFmpeg olmadan)',
            'format': 'audio',
            'ffmpeg_required': False,
            'status_url': f'/api/status/{download_id}',
            'download_url': f'/api/status/{download_id}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Audio Download error: {str(e)}'}), 500

@app.route('/api/download/mp4', methods=['GET', 'POST'])
def start_mp4_download():
    """Start MP4 download"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            video_url = request.args.get('url', '').strip()
            quality = request.args.get('quality', 'best')
            custom_path = request.args.get('path', download_path)
        else:  # POST
            data = request.get_json()
            video_url = data.get('video_url', '').strip()
            quality = data.get('quality', 'best')
            custom_path = data.get('output_path', download_path)
        
        if not video_url:
            return jsonify({
                'error': 'Video URL is required. Use ?url=VIDEO_URL for GET or {"video_url": "URL"} for POST'
            }), 400
        
        # Generate unique download ID
        download_id = str(uuid.uuid4())
        
        # Initialize download status
        downloads[download_id] = {
            'status': 'queued',
            'progress': 0,
            'speed': '0 MB/s',
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'message': 'MP4 İndirme kuyruğa alındı',
            'video_url': video_url,
            'format': 'mp4',
            'quality': quality,
            'output_path': custom_path,
            'start_time': time.time()
        }
        
        # Start download in background thread
        thread = threading.Thread(
            target=download_video_api,
            args=(video_url, 'mp4', quality, custom_path, download_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': 'MP4 İndirme başlatıldı',
            'format': 'mp4',
            'status_url': f'/api/status/{download_id}',
            'download_url': f'/api/status/{download_id}'
        })
        
    except Exception as e:
        return jsonify({'error': f'MP4 Download error: {str(e)}'}), 500

# Keep the old endpoint for backward compatibility
@app.route('/api/download', methods=['GET', 'POST'])
def start_download():
    """Start a download (backward compatibility)"""
    try:
        # Handle both GET and POST requests
        if request.method == 'GET':
            video_url = request.args.get('url', '').strip()
            format_type = request.args.get('format', 'mp4')  # mp3 or mp4
            quality = request.args.get('quality', 'best')
            custom_path = request.args.get('path', download_path)
        else:  # POST
            data = request.get_json()
            video_url = data.get('video_url', '').strip()
            format_type = data.get('format', 'mp4')  # mp3 or mp4
            quality = data.get('quality', 'best')
            custom_path = data.get('output_path', download_path)
        
        if not video_url:
            return jsonify({
                'error': 'Video URL is required. Use ?url=VIDEO_URL for GET or {"video_url": "URL"} for POST'
            }), 400
        
        # Generate unique download ID
        download_id = str(uuid.uuid4())
        
        # Initialize download status
        downloads[download_id] = {
            'status': 'queued',
            'progress': 0,
            'speed': '0 MB/s',
            'downloaded_bytes': 0,
            'total_bytes': 0,
            'message': f'{format_type.upper()} İndirme kuyruğa alındı',
            'video_url': video_url,
            'format': format_type,
            'quality': quality,
            'output_path': custom_path,
            'start_time': time.time()
        }
        
        # Start download in background thread
        thread = threading.Thread(
            target=download_video_api,
            args=(video_url, format_type, quality, custom_path, download_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': f'{format_type.upper()} İndirme başlatıldı',
            'format': format_type,
            'status_url': f'/api/status/{download_id}',
            'download_url': f'/api/status/{download_id}'
        })
        
    except Exception as e:
        return jsonify({'error': f'Download error: {str(e)}'}), 500

@app.route('/api/status/<download_id>', methods=['GET'])
def get_download_status(download_id):
    """Get download status"""
    if download_id not in downloads:
        return jsonify({'error': 'Download ID not found'}), 404
    
    download_info = downloads[download_id].copy()
    
    # Calculate elapsed time
    if 'start_time' in download_info:
        elapsed = time.time() - download_info['start_time']
        download_info['elapsed_time'] = f"{elapsed:.1f} seconds"
    
    return jsonify(download_info)

@app.route('/api/downloads', methods=['GET'])
def list_downloads():
    """List all downloads"""
    download_list = []
    for download_id, info in downloads.items():
        download_info = info.copy()
        download_info['download_id'] = download_id
        
        # Calculate elapsed time
        if 'start_time' in download_info:
            elapsed = time.time() - download_info['start_time']
            download_info['elapsed_time'] = f"{elapsed:.1f} seconds"
        
        download_list.append(download_info)
    
    return jsonify({
        'downloads': download_list,
        'total': len(download_list)
    })

@app.route('/api/cancel/<download_id>', methods=['GET', 'POST'])
def cancel_download(download_id):
    """Cancel a download"""
    if download_id not in downloads:
        return jsonify({'error': 'Download ID not found'}), 404
    
    downloads[download_id]['status'] = 'cancelled'
    downloads[download_id]['message'] = 'İndirme iptal edildi'
    
    return jsonify({
        'success': True,
        'message': 'İndirme iptal edildi'
    })

@app.route('/api/delete/<download_id>', methods=['GET', 'POST'])
def delete_download(download_id):
    """Delete a specific download from history"""
    if download_id not in downloads:
        return jsonify({'error': 'Download ID not found'}), 404
    
    # Remove the download from history
    del downloads[download_id]
    
    return jsonify({
        'success': True,
        'message': 'İndirme geçmişten silindi'
    })

@app.route('/api/clear', methods=['GET', 'POST'])
def clear_downloads():
    """Clear completed downloads"""
    global downloads
    
    # Keep only active downloads
    active_downloads = {}
    for download_id, info in downloads.items():
        if info['status'] in ['queued', 'starting', 'downloading']:
            active_downloads[download_id] = info
    
    downloads = active_downloads
    
    return jsonify({
        'success': True,
        'message': 'Tamamlanan indirmeler temizlendi',
        'remaining_downloads': len(downloads)
    })

@app.route('/api/clear/all', methods=['GET', 'POST'])
def clear_all_downloads():
    """Clear all downloads (including active ones)"""
    global downloads
    
    downloads = {}
    
    return jsonify({
        'success': True,
        'message': 'Tüm indirmeler temizlendi'
    })

if __name__ == '__main__':
    print("YouTube MP3/MP4 İndirici - HTTP API Server")
    print("=" * 50)
    print(f"API Server başlatılıyor...")
    print(f"İndirme klasörü: {download_path}")
    print(f"Web Arayüzü: http://localhost:5000")
    print(f"API Endpoint'leri:")
    print(f"  GET  / - Web arayüzü ve dokümantasyon")
    print(f"  GET  /api/health - Sağlık kontrolü")
    print(f"  GET/POST /api/search - Video arama")
    print(f"  POST /api/download - İndirme başlat")
    print(f"  GET  /api/status/<id> - İndirme durumu")
    print(f"  GET  /api/downloads - Tüm indirmeler")
    print(f"  POST /api/cancel/<id> - İndirme iptal")
    print(f"  POST /api/clear - Tamamlananları temizle")
    print("=" * 50)
    
    # JSON response'ları güzel formatla
    app.config['JSON_AS_ASCII'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    
    # Cloud deployment için port ayarı
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(host='0.0.0.0', port=port, debug=debug, threaded=True) 