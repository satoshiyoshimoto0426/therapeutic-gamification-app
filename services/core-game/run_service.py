#!/usr/bin/env python3
"""
Core Game Engine Service Runner
Starts the FastAPI service with proper configuration
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add shared modules to path
shared_path = Path(__file__).parent.parent.parent / "shared"
sys.path.append(str(shared_path))

def main():
    """Run the Core Game Engine service"""
    
    # Environment configuration
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8002"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    print(f"Starting Core Game Engine Service on {host}:{port}")
    print(f"Debug mode: {debug}")
    
    # Configure uvicorn
    config = {
        "app": "main:app",
        "host": host,
        "port": port,
        "reload": debug,
        "log_level": "debug" if debug else "info",
        "access_log": True
    }
    
    # Add SSL configuration for production
    if not debug:
        config.update({
            "workers": 4,
            "loop": "uvloop",
            "http": "httptools"
        })
    
    uvicorn.run(**config)

if __name__ == "__main__":
    main()