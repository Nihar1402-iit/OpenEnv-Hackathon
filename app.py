#!/usr/bin/env python3
"""
FastAPI application entry point for Hugging Face Spaces.
This is the main app that Hugging Face Spaces will run.
"""

from app.main import app

if __name__ == "__main__":
    import uvicorn
    # HF Spaces uses port 7860 by default
    uvicorn.run(app, host="0.0.0.0", port=7860)
