import os
import sys

# Add this service directory to the front of sys.path
# This ensures that 'from main import' resolves to this service's main.py
sys.path.insert(0, os.path.dirname(__file__))
