"""
Test package for auto-deployment reporting system.

This package contains comprehensive tests for all reporting components:
- DeploymentReporter: Main reporting coordinator
- ProgressTracker: Real-time progress tracking
- HistoryManager: Deployment history storage and retrieval
- ReportGenerator: Multi-format report generation
- Integration tests: End-to-end system testing
"""

# Test modules
from . import test_deployment_reporter
from . import test_progress_tracker
from . import test_history_manager
from . import test_report_generator
from . import test_reporting_integration

__all__ = [
    'test_deployment_reporter',
    'test_progress_tracker', 
    'test_history_manager',
    'test_report_generator',
    'test_reporting_integration'
]