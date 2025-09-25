"""
Rollback management system for auto-deployment.

This module provides comprehensive rollback capabilities including:
- Failure detection algorithms
- Automatic rollback triggers
- Manual rollback interfaces
- Rollback execution and monitoring
"""

from .failure_detector import (
    FailureDetector, 
    FailureType, 
    FailureCondition, 
    FailureEvent
)
from .rollback_triggers import (
    AutomaticRollbackTrigger, 
    ManualRollbackTrigger,
    RollbackTriggerConfig,
    RollbackRequest,
    RollbackReason
)

__all__ = [
    'FailureDetector',
    'FailureType',
    'FailureCondition', 
    'FailureEvent',
    'AutomaticRollbackTrigger', 
    'ManualRollbackTrigger',
    'RollbackTriggerConfig',
    'RollbackRequest',
    'RollbackReason'
]