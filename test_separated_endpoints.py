#!/usr/bin/env python3
"""
Test script for separated MP3 and MP4 endpoints
Bu script, ayrılmış MP3 ve MP4 endpoint'lerini test eder.
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        data = response.json()
        print(f"✅ Health check: {data['status']}")
        print(f"   FFmpeg available: {data['ffmpeg_available']}")
        print(f"   Moviepy available: {data['moviepy_available']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_search():
    """Test search functionality"""
    print("\n🔍 Testing search functionality...")
    try:
        # Test with a search query
        response = requests.post(f"{BASE_URL}/api/search", 
                               json={"query": "test video", "limit": 3})
        data = response.json()
        
        if data.get('success'):
            print(f"✅ Search successful: {data['total_results']} results found")
            for i, result in enumerate(data['results'][:2]):  # Show first 2 results
                print(f"   {i+1}. {result['title']}")
                print(f"      MP3 links: {len(result['download_links']['mp3'])} options")
                print(f"      MP4 links: {len(result['download_links']['mp4'])} options")
            return data['results'][0] if data['results'] else None
        else:
            print(f"❌ Search failed: {data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return None

def test_mp3_download(video_url):
    """Test MP3 download endpoint"""
    print(f"\n🎵 Testing MP3 download for: {video_url}")
    try:
        response = requests.post(f"{BASE_URL}/api/download/mp3", 
                               json={"video_url": video_url, "quality": "best"})
        data = response.json()
        
        if data.get('success'):
            download_id = data['download_id']
            print(f"✅ MP3 download started: {download_id}")
            return download_id
        else:
            print(f"❌ MP3 download failed: {data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ MP3 download test failed: {e}")
        return None

def test_audio_download(video_url):
    """Test audio download endpoint (without FFmpeg)"""
    print(f"\n🎵 Testing audio download (no FFmpeg) for: {video_url}")
    try:
        response = requests.post(f"{BASE_URL}/api/download/audio", 
                               json={"video_url": video_url})
        data = response.json()
        
        if data.get('success'):
            download_id = data['download_id']
            print(f"✅ Audio download started: {download_id}")
            return download_id
        else:
            print(f"❌ Audio download failed: {data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ Audio download test failed: {e}")
        return None

def test_mp4_download(video_url):
    """Test MP4 download endpoint"""
    print(f"\n🎬 Testing MP4 download for: {video_url}")
    try:
        response = requests.post(f"{BASE_URL}/api/download/mp4", 
                               json={"video_url": video_url, "quality": "720p"})
        data = response.json()
        
        if data.get('success'):
            download_id = data['download_id']
            print(f"✅ MP4 download started: {download_id}")
            return download_id
        else:
            print(f"❌ MP4 download failed: {data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ MP4 download test failed: {e}")
        return None

def test_download_status(download_id):
    """Test download status endpoint"""
    print(f"\n📊 Testing download status for: {download_id}")
    try:
        response = requests.get(f"{BASE_URL}/api/status/{download_id}")
        data = response.json()
        
        print(f"✅ Status: {data.get('status', 'Unknown')}")
        print(f"   Progress: {data.get('progress', 0)}%")
        print(f"   Message: {data.get('message', 'No message')}")
        return data
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        return None

def test_all_downloads():
    """Test listing all downloads"""
    print(f"\n📋 Testing all downloads list...")
    try:
        response = requests.get(f"{BASE_URL}/api/downloads")
        data = response.json()
        
        print(f"✅ Total downloads: {data.get('total', 0)}")
        for download in data.get('downloads', []):
            print(f"   - {download.get('download_id', 'Unknown')}: {download.get('status', 'Unknown')}")
        return data
    except Exception as e:
        print(f"❌ Downloads list failed: {e}")
        return None

def main():
    """Main test function"""
    print("🚀 Starting separated endpoints test...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Health check failed, stopping tests")
        return
    
    # Test search
    first_result = test_search()
    if not first_result:
        print("❌ Search failed, stopping tests")
        return
    
    video_url = first_result['video_url']
    print(f"\n📺 Using video: {first_result['title']}")
    
    # Test MP3 download
    mp3_id = test_mp3_download(video_url)
    if mp3_id:
        time.sleep(2)  # Wait a bit
        test_download_status(mp3_id)
    
    # Test audio download
    audio_id = test_audio_download(video_url)
    if audio_id:
        time.sleep(2)  # Wait a bit
        test_download_status(audio_id)
    
    # Test MP4 download
    mp4_id = test_mp4_download(video_url)
    if mp4_id:
        time.sleep(2)  # Wait a bit
        test_download_status(mp4_id)
    
    # Test all downloads
    test_all_downloads()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")
    print("\n📋 Summary:")
    print("   - MP3 endpoint: /api/download/mp3")
    print("   - Audio endpoint: /api/download/audio")
    print("   - MP4 endpoint: /api/download/mp4")
    print("   - Search endpoint: /api/search")
    print("   - Status endpoint: /api/status/:id")

if __name__ == "__main__":
    main() 