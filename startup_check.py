#!/usr/bin/env python3
"""
Startup check script to verify the app can be imported and run.
Used for debugging HF Spaces deployment issues.
"""

import sys
import os
from pathlib import Path

print("=" * 80)
print("🔍 STARTUP CHECK FOR HF SPACES DEPLOYMENT")
print("=" * 80 + "\n")

# Check 1: Python version
print(f"1. Python Version: {sys.version}")
print(f"   ✅ OK\n")

# Check 2: Current directory
print(f"2. Current Directory: {os.getcwd()}")
print(f"   Working files: {list(Path('.').glob('*.py'))[:5]}\n")

# Check 3: Import FastAPI
print("3. Checking FastAPI import...")
try:
    import fastapi
    print(f"   ✅ FastAPI {fastapi.__version__} imported\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    sys.exit(1)

# Check 4: Import uvicorn
print("4. Checking uvicorn import...")
try:
    import uvicorn
    print(f"   ✅ uvicorn imported\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    sys.exit(1)

# Check 5: Import app module
print("5. Checking app module import...")
try:
    from app.main import app
    print(f"   ✅ app.main.app imported successfully")
    print(f"   App: {app}\n")
except Exception as e:
    print(f"   ❌ Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check 6: Verify app routes
print("6. Checking app routes...")
try:
    routes = [route.path for route in app.routes]
    print(f"   Routes found: {len(routes)}")
    for route in routes[:10]:
        print(f"     • {route}")
    print(f"   ✅ Routes OK\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    sys.exit(1)

# Check 7: Test health check endpoint
print("7. Testing health check endpoint...")
try:
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/health")
    print(f"   Response status: {response.status_code}")
    print(f"   Response body: {response.json()}")
    if response.status_code == 200:
        print(f"   ✅ Health check OK\n")
    else:
        print(f"   ⚠️ Health check returned {response.status_code}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 80)
print("✅ ALL STARTUP CHECKS PASSED")
print("=" * 80)
print("\n✨ App is ready to be deployed on HF Spaces!")
print("   Command: python -m uvicorn app.main:app --host 0.0.0.0 --port 7860\n")
