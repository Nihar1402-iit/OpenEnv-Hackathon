#!/usr/bin/env python3
"""
FastAPI application entry point for Hugging Face Spaces.
This is the main app that HuggingFace Spaces will import and run.
"""

import sys
import os
from pathlib import Path

# Ensure app module can be imported
sys.path.insert(0, str(Path(__file__).parent))

# Import the FastAPI app from app.main
from app.main import app

# Export the app for HF Spaces to discover
__all__ = ['app']

# This is the entry point that HF Spaces looks for when it imports this file
if __name__ == "__main__":
    import uvicorn
    # HF Spaces uses port 7860 by default
    uvicorn.run(app, host="0.0.0.0", port=7860)
if __name__ == "__main__":
    import uvicorn
    # HF Spaces uses port 7860 by default
    uvicorn.run(app, host="0.0.0.0", port=7860)
