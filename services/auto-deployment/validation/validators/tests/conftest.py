"""
Pytest configuration for auto-deployment validation tests.
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
validators_dir = os.path.dirname(current_dir)
validation_dir = os.path.dirname(validators_dir)
auto_deployment_dir = os.path.dirname(validation_dir)

if validators_dir not in sys.path:
    sys.path.insert(0, validators_dir)
if validation_dir not in sys.path:
    sys.path.insert(0, validation_dir)
if auto_deployment_dir not in sys.path:
    sys.path.insert(0, auto_deployment_dir)
