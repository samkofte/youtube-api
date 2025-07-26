#!/usr/bin/env python3
"""
Simple test to check imports
"""

try:
    import flask
    print("✅ Flask imported successfully")
except ImportError as e:
    print(f"❌ Flask import error: {e}")

try:
    import yt_dlp
    print("✅ yt-dlp imported successfully")
except ImportError as e:
    print(f"❌ yt-dlp import error: {e}")

try:
    import os
    print("✅ os imported successfully")
except ImportError as e:
    print(f"❌ os import error: {e}")

try:
    import threading
    print("✅ threading imported successfully")
except ImportError as e:
    print(f"❌ threading import error: {e}")

try:
    import time
    print("✅ time imported successfully")
except ImportError as e:
    print(f"❌ time import error: {e}")

try:
    import json
    print("✅ json imported successfully")
except ImportError as e:
    print(f"❌ json import error: {e}")

try:
    import tempfile
    print("✅ tempfile imported successfully")
except ImportError as e:
    print(f"❌ tempfile import error: {e}")

try:
    from werkzeug.utils import secure_filename
    print("✅ werkzeug imported successfully")
except ImportError as e:
    print(f"❌ werkzeug import error: {e}")

try:
    import uuid
    print("✅ uuid imported successfully")
except ImportError as e:
    print(f"❌ uuid import error: {e}")

print("\n🎉 All imports successful!") 