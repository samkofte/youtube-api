#!/usr/bin/env python3
"""
Quick Fix for YouTube Bot Protection
Bu script, YouTube bot korumasını aşmak için alternatif yöntemler sağlar.
"""

import requests
import json
import time
import random

def test_youtube_access():
    """Test YouTube access with different methods"""
    print("🔍 Testing YouTube access methods...")
    
    # Method 1: Direct URL test
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"✅ Direct access: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Direct access failed: {e}")
        return False

def create_test_cookies():
    """Create a basic test cookies file"""
    print("🍪 Creating test cookies file...")
    
    cookies_content = """# Netscape HTTP Cookie File
# This is a test cookies file for YouTube API
.youtube.com	TRUE	/	FALSE	1735689600	VISITOR_INFO1_LIVE	random_string
.youtube.com	TRUE	/	FALSE	1735689600	LOGIN_INFO	random_string
.youtube.com	TRUE	/	FALSE	1735689600	SID	random_string
.youtube.com	TRUE	/	FALSE	1735689600	HSID	random_string
.youtube.com	TRUE	/	FALSE	1735689600	SSID	random_string
.youtube.com	TRUE	/	FALSE	1735689600	APISID	random_string
.youtube.com	TRUE	/	FALSE	1735689600	SAPISID	random_string
"""
    
    try:
        with open('cookies.txt', 'w') as f:
            f.write(cookies_content)
        print("✅ Test cookies file created: cookies.txt")
        return True
    except Exception as e:
        print(f"❌ Failed to create cookies file: {e}")
        return False

def update_api_with_retry():
    """Update API with retry mechanism"""
    print("🔄 Updating API with retry mechanism...")
    
    # Read current api_server.py
    try:
        with open('api_server.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add retry mechanism
        retry_code = '''
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
'''
        
        # Replace the download section
        if 'with yt_dlp.YoutubeDL(ydl_opts) as ydl:' in content:
            content = content.replace(
                'with yt_dlp.YoutubeDL(ydl_opts) as ydl:\n            ydl.download([video_url])',
                'download_with_retry(video_url, ydl_opts)'
            )
            
            # Add the retry function at the top
            if 'def download_with_retry' not in content:
                content = content.replace(
                    'import uuid',
                    'import uuid\nimport random'
                )
                content = content.replace(
                    'def is_youtube_url(text):',
                    retry_code + '\n\ndef is_youtube_url(text):'
                )
        
        # Write updated content
        with open('api_server.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ API updated with retry mechanism")
        return True
        
    except Exception as e:
        print(f"❌ Failed to update API: {e}")
        return False

def main():
    """Main function"""
    print("🚀 YouTube Bot Protection Quick Fix")
    print("=" * 40)
    
    # Test 1: Direct access
    test_youtube_access()
    
    # Test 2: Create cookies
    create_test_cookies()
    
    # Test 3: Update API
    update_api_with_retry()
    
    print("\n" + "=" * 40)
    print("✅ Quick fix completed!")
    print("\n📋 Next steps:")
    print("1. Restart your API: python api_server.py")
    print("2. Test search: curl 'http://localhost:5000/api/search?q=test&limit=3'")
    print("3. If still failing, get real cookies from browser")
    print("\n🍪 For real cookies:")
    print("- Install 'Get cookies.txt' browser extension")
    print("- Go to YouTube and login")
    print("- Export cookies to cookies.txt")

if __name__ == "__main__":
    main() 