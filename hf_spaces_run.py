#!/usr/bin/env python3
"""
HuggingFace Spaces runner script.
This script is used when deploying to HF Spaces.
It starts the FastAPI app with uvicorn on port 7860.
"""

import sys
import os
from pathlib import Path

# Ensure the app module can be imported
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point for HF Spaces."""
    import uvicorn
    from app.main import app
    
    print("🚀 Starting OpenEnv CRM Query Environment on port 7860...")
    print("📍 Binding to 0.0.0.0:7860")
    print("📚 API Documentation: http://localhost:7860/docs")
    print("🔍 ReDoc Documentation: http://localhost:7860/redoc")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=7860,
        log_level="info",
        access_log=True,
    )

if __name__ == "__main__":
    main()
