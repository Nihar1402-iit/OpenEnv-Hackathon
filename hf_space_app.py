#!/usr/bin/env python3
"""
Hugging Face Spaces compatible FastAPI app for OpenEnv CRM Query Environment.
This app runs the FastAPI server on the port assigned by HF Spaces.
"""

import os
import subprocess
import sys

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = os.getenv("PORT", "8000")
    
    # Run the FastAPI app
    subprocess.run([
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", port
    ])
