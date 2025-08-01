#!/usr/bin/env python3
"""
Debug script to check available routes in the FastAPI app
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import app

def list_routes():
    """List all available routes in the FastAPI app"""
    print("Available routes in Task Management API:")
    print("=" * 50)
    
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            methods = ', '.join(route.methods)
            print(f"{methods:10} {route.path}")
    
    print("=" * 50)

if __name__ == "__main__":
    list_routes()