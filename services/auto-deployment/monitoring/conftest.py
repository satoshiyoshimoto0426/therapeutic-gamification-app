"""
Pytest configuration for auto-deployment monitoring tests.
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

auto_deployment_dir = os.path.dirname(current_dir)
if auto_deployment_dir not in sys.path:
    sys.path.insert(0, auto_deployment_dir)
