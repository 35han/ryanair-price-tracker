#!/usr/bin/env python3
"""
Minimal health check - if this doesn't output anything, Railway has a container problem
"""

import sys
import os

# Force output
sys.stdout = sys.stderr

print("=" * 70, flush=True)
print("🚀 HEALTH CHECK - This should always print", flush=True)
print("=" * 70, flush=True)

print(f"\n✅ Python version: {sys.version}", flush=True)
print(f"✅ Python path: {sys.executable}", flush=True)
print(f"✅ Working directory: {os.getcwd()}", flush=True)

print(f"\n📋 Environment variables:", flush=True)
print(f"   PYTHONUNBUFFERED: {os.getenv('PYTHONUNBUFFERED', 'NOT SET')}", flush=True)
print(f"   TELEGRAM_BOT_TOKEN: {'SET' if os.getenv('TELEGRAM_BOT_TOKEN') else 'NOT SET'}", flush=True)
print(f"   TELEGRAM_CHAT_ID: {'SET' if os.getenv('TELEGRAM_CHAT_ID') else 'NOT SET'}", flush=True)

print(f"\n📁 Files in /app:", flush=True)
try:
    for f in os.listdir('.'):
        if f.endswith('.py'):
            print(f"   ✅ {f}", flush=True)
except Exception as e:
    print(f"   ❌ Error listing files: {e}", flush=True)

print(f"\n🔧 Testing imports:", flush=True)

try:
    import config
    print(f"   ✅ config imported", flush=True)
except Exception as e:
    print(f"   ❌ config import failed: {e}", flush=True)
    sys.exit(1)

try:
    from database import create_database
    print(f"   ✅ database imported", flush=True)
except Exception as e:
    print(f"   ❌ database import failed: {e}", flush=True)
    sys.exit(1)

print("\n✅ HEALTH CHECK PASSED - All imports work", flush=True)
print("=" * 70 + "\n", flush=True)
