#!/usr/bin/env python3
"""
Cloud API Test Script
Bu script, deploy edilen API'nin çalışıp çalışmadığını test eder.
"""

import requests
import json
import sys

def test_api(base_url):
    """Test API endpoints"""
    print(f"🔍 Testing API: {base_url}")
    print("=" * 50)
    
    # Test 1: Health Check
    print("1. Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']}")
            print(f"   FFmpeg: {data['ffmpeg_available']}")
            print(f"   Moviepy: {data['moviepy_available']}")
        else:
            print(f"❌ Health Check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check error: {e}")
        return False
    
    # Test 2: Search
    print("\n2. Testing Search...")
    try:
        response = requests.post(f"{base_url}/api/search", 
                               json={"query": "test video", "limit": 2},
                               timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"✅ Search: {data['total_results']} results found")
                if data['results']:
                    video = data['results'][0]
                    print(f"   First video: {video['title'][:50]}...")
                    print(f"   MP3 options: {len(video['download_links']['mp3'])}")
                    print(f"   MP4 options: {len(video['download_links']['mp4'])}")
                    return video['video_url']
            else:
                print(f"❌ Search failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Search error: {e}")
        return False
    
    return False

def test_download(base_url, video_url):
    """Test download functionality"""
    print(f"\n3. Testing Download (Audio - FFmpeg olmadan)...")
    try:
        response = requests.post(f"{base_url}/api/download/audio",
                               json={"video_url": video_url},
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                download_id = data['download_id']
                print(f"✅ Download started: {download_id}")
                
                # Test status
                print(f"\n4. Testing Download Status...")
                status_response = requests.get(f"{base_url}/api/status/{download_id}", timeout=10)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✅ Status: {status_data.get('status', 'Unknown')}")
                    print(f"   Progress: {status_data.get('progress', 0)}%")
                    print(f"   Message: {status_data.get('message', 'No message')}")
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                
                return True
            else:
                print(f"❌ Download failed: {data.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ Download failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Download error: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) < 2:
        print("Usage: python test_cloud_api.py <API_BASE_URL>")
        print("Example: python test_cloud_api.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("🚀 Cloud API Test Starting...")
    print(f"Target: {base_url}")
    print("=" * 60)
    
    # Test API
    video_url = test_api(base_url)
    if not video_url:
        print("\n❌ API test failed!")
        sys.exit(1)
    
    # Test download
    download_success = test_download(base_url, video_url)
    
    print("\n" + "=" * 60)
    if download_success:
        print("🎉 All tests passed! API is working correctly.")
    else:
        print("⚠️  API is working but download test failed.")
        print("   This might be due to FFmpeg not being available on the cloud platform.")
        print("   Try using the /api/download/audio endpoint instead of /api/download/mp3")
    
    print(f"\n📋 API Endpoints:")
    print(f"   Health: {base_url}/api/health")
    print(f"   Search: {base_url}/api/search?q=test")
    print(f"   Audio Download: {base_url}/api/download/audio?url=VIDEO_URL")
    print(f"   MP3 Download: {base_url}/api/download/mp3?url=VIDEO_URL")
    print(f"   MP4 Download: {base_url}/api/download/mp4?url=VIDEO_URL")

if __name__ == "__main__":
    main() 