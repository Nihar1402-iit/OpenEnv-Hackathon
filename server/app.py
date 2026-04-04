#!/usr/bin/env python3
"""
FastAPI application entry point for OpenEnv CRM Query Environment
Serves the environment for HuggingFace Spaces and other deployment modes
"""

import os
import sys
import uvicorn
from pathlib import Path

# Add parent directory to path to import app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


def main():
    """Main entry point for the server"""
    # Get configuration from environment or use defaults
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "7860"))
    
    # For HuggingFace Spaces, use port 7860
    if os.getenv("SPACE_ID"):
        port = 7860
    
    # Run uvicorn server
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
    )


if __name__ == "__main__":
    main()
