"""
Rollback trigger system for automatic and manual rollback initiation.

This module implements both automatic rollback triggers based on failure
detection and manual rollback triggers for operator-initiated rollbacks.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

try:
    from .failure_detector import FailureDetector, FailureEvent, FailureType
    from ..exceptions import RollbackError
except ImportError:
    # テスト実行時の代替インポート
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from rollback.failure_detector import FailureDetector, FailureEvent, FailureType
    from exceptions import RollbackError


class RollbackReason(Enum):
    """Reasons for triggering rollback."""
    AUTOMATIC_HEALTH_FAILURE = "automatic_health_failure"
    AUTOMATIC_PERFORMANCE_DEGRADATION = "automatic_performance_degradation"
    AUTOMATIC_ERROR_SPIKE = "automatic_error_spike"
    AUTOMATIC_RESOURCE_EXHAUSTION = "automatic_resource_exhaustion"
    MANUAL_OPERATOR_REQUEST = "manual_operator_request"
    MANUAL_EMERGENCY = "manual_emergency"
    MANUAL_SCHEDULED = "manual_scheduled"


@dataclass
class RollbackTriggerConfig:
    """Configuration for rollback triggers."""
    enabled: bool = True
    cooldown_minutes: int = 10
    max_rollbacks_per_hour: int = 3
    require_confirmation: bool = False
    notification_channels: List[str] = None


@dataclass
class RollbackRequest:
    """Represents a rollback request."""
    trigger_id: str
    reason: RollbackReason
    timestamp: datetime
    severity: str
    message: str
    failure_events: List[FailureEvent]
    metadata: Dict[str, Any]
    operator_id: Optional[str] = None
    confirmation_required: bool = False


class RollbackTrigger(ABC):
    """Abstract base class for rollback triggers."""
    
    def __init__(self, config: RollbackTriggerConfig):
        """Initialize rollback trigger."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.rollback_history: List[RollbackRequest] = []
        self._callbacks: List[Callable[[RollbackRequest], None]] = []
    
    def add_callback(self, callback: Callable[[RollbackRequest], None]) -> None:
        """Add callback for rollback trigger events."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[RollbackRequest], None]) -> None:
        """Remove callback for rollback trigger events."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    async def _trigger_rollback(self, request: RollbackRequest) -> None:
        """Trigger rollback and notify callbacks."""
        if not self.config.enabled:
            self.logger.info(f"Rollback trigger disabled, ignoring request: {request.trigger_id}")
            return
        
        # Check cooldown period
        if not self._check_cooldown():
            self.logger.warning(f"Rollback trigger in cooldown period, ignoring request: {request.trigger_id}")
            return
        
        # Check rate limiting
        if not self._check_rate_limit():
            self.logger.warning(f"Rollback rate limit exceeded, ignoring request: {request.trigger_id}")
            return
        
        # Record rollback request
        self.rollback_history.append(request)
        
        self.logger.info(f"Triggering rollback: {request.reason.value} - {request.message}")
        
        # Notify all callbacks
        for callback in self._callbacks:
            try:
                await callback(request)
            except Exception as e:
                self.logger.error(f"Error in rollback callback: {e}")
    
    def _check_cooldown(self) -> bool:
        """Check if cooldown period has passed since last rollback."""
        if not self.rollback_history:
            return True
        
        last_rollback = max(self.rollback_history, key=lambda r: r.timestamp)
        cooldown_end = last_rollback.timestamp + timedelta(minutes=self.config.cooldown_minutes)
        
        return datetime.now() >= cooldown_end
    
    def _check_rate_limit(self) -> bool:
        """Check if rollback rate limit is exceeded."""
        one_hour_ago = datetime.now() - timedelta(hours=1)
        recent_rollbacks = [
            r for r in self.rollback_history
            if r.timestamp >= one_hour_ago
        ]
        
        return len(recent_rollbacks) < self.config.max_rollbacks_per_hour
    
    @abstractmethod
    async def start(self) -> None:
        """Start the rollback trigger."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the rollback trigger."""
        pass


class AutomaticRollbackTrigger(RollbackTrigger):
    """
    Automatic rollback trigger based on failure detection.
    
    This trigger monitors failure events and automatically initiates
    rollback when certain conditions are met.
    """
    
    def __init__(self, 
                 failure_detector: FailureDetector,
                 config: RollbackTriggerConfig):
        """
        Initialize automatic rollback trigger.
        
        Args:
            failure_detector: Failure detection system
            config: Trigger configuration
        """
        super().__init__(config)
        self.failure_detector = failure_detector
        self.monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Automatic trigger conditions
        self.trigger_conditions = {
            FailureType.HEALTH_CHECK_FAILURE: {
                "min_failures": 3,
                "time_window_minutes": 5,
                "severity_threshold": "warning"
            },
            FailureType.PERFORMANCE_DEGRADATION: {
                "min_failures": 2,
                "time_window_minutes": 10,
                "severity_threshold": "critical"
            },
            FailureType.ERROR_RATE_SPIKE: {
                "min_failures": 2,
                "time_window_minutes": 5,
                "severity_threshold": "warning"
            },
            FailureType.RESOURCE_EXHAUSTION: {
                "min_failures": 1,
                "time_window_minutes": 5,
                "severity_threshold": "critical"
            }
        }
    
    async def start(self) -> None:
        """Start automatic rollback monitoring."""
        if self.monitoring_active:
            self.logger.warning("Automatic rollback trigger already active")
            return
        
        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Started automatic rollback trigger")
    
    async def stop(self) -> None:
        """Stop automatic rollback monitoring."""
        self.monitoring_active = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped automatic rollback trigger")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for automatic rollback detection."""
        try:
            while self.monitoring_active:
                await self._check_rollback_conditions()
                await asyncio.sleep(30)  # Check every 30 seconds
        except asyncio.CancelledError:
            self.logger.info("Automatic rollback monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in automatic rollback monitoring loop: {e}")
            raise RollbackError(f"Automatic rollback monitoring failed: {e}")
    
    async def _check_rollback_conditions(self) -> None:
        """Check if automatic rollback should be triggered."""
        for failure_type, condition in self.trigger_conditions.items():
            try:
                if await self._should_trigger_rollback(failure_type, condition):
                    await self._create_automatic_rollback_request(failure_type, condition)
            except Exception as e:
                self.logger.error(f"Error checking rollback condition for {failure_type}: {e}")
    
    async def _should_trigger_rollback(self, failure_type: FailureType, condition: Dict[str, Any]) -> bool:
        """Check if rollback should be triggered for a specific failure type."""
        # Get recent failures of this type
        time_window = timedelta(minutes=condition["time_window_minutes"])
        cutoff_time = datetime.now() - time_window
        
        recent_failures = [
            failure for failure in self.failure_detector.failure_history
            if (failure.failure_type == failure_type and 
                failure.timestamp >= cutoff_time and
                self._meets_severity_threshold(failure.severity, condition["severity_threshold"]))
        ]
        
        return len(recent_failures) >= condition["min_failures"]
    
    def _meets_severity_threshold(self, actual_severity: str, threshold_severity: str) -> bool:
        """Check if actual severity meets the threshold."""
        severity_levels = {"info": 0, "warning": 1, "critical": 2}
        actual_level = severity_levels.get(actual_severity, 0)
        threshold_level = severity_levels.get(threshold_severity, 1)
        return actual_level >= threshold_level
    
    async def _create_automatic_rollback_request(self, failure_type: FailureType, condition: Dict[str, Any]) -> None:
        """Create and trigger automatic rollback request."""
        # Get relevant failure events
        time_window = timedelta(minutes=condition["time_window_minutes"])
        cutoff_time = datetime.now() - time_window
        
        failure_events = [
            failure for failure in self.failure_detector.failure_history
            if (failure.failure_type == failure_type and 
                failure.timestamp >= cutoff_time)
        ]
        
        # Map failure type to rollback reason
        reason_mapping = {
            FailureType.HEALTH_CHECK_FAILURE: RollbackReason.AUTOMATIC_HEALTH_FAILURE,
            FailureType.PERFORMANCE_DEGRADATION: RollbackReason.AUTOMATIC_PERFORMANCE_DEGRADATION,
            FailureType.ERROR_RATE_SPIKE: RollbackReason.AUTOMATIC_ERROR_SPIKE,
            FailureType.RESOURCE_EXHAUSTION: RollbackReason.AUTOMATIC_RESOURCE_EXHAUSTION
        }
        
        reason = reason_mapping.get(failure_type, RollbackReason.AUTOMATIC_HEALTH_FAILURE)
        
        # Determine severity
        has_critical = any(f.severity == "critical" for f in failure_events)
        severity = "critical" if has_critical else "warning"
        
        request = RollbackRequest(
            trigger_id=f"auto_{failure_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            reason=reason,
            timestamp=datetime.now(),
            severity=severity,
            message=f"Automatic rollback triggered due to {failure_type.value}: {len(failure_events)} failures in {condition['time_window_minutes']} minutes",
            failure_events=failure_events,
            metadata={
                "failure_type": failure_type.value,
                "condition": condition,
                "failure_count": len(failure_events)
            },
            confirmation_required=self.config.require_confirmation
        )
        
        await self._trigger_rollback(request)


class ManualRollbackTrigger(RollbackTrigger):
    """
    Manual rollback trigger for operator-initiated rollbacks.
    
    This trigger provides interfaces for operators to manually
    initiate rollbacks when needed.
    """
    
    def __init__(self, config: RollbackTriggerConfig):
        """Initialize manual rollback trigger."""
        super().__init__(config)
        self.active = False
    
    async def start(self) -> None:
        """Start manual rollback trigger."""
        self.active = True
        self.logger.info("Started manual rollback trigger")
    
    async def stop(self) -> None:
        """Stop manual rollback trigger."""
        self.active = False
        self.logger.info("Stopped manual rollback trigger")
    
    async def trigger_rollback(self, 
                             reason: str,
                             operator_id: str,
                             severity: str = "warning",
                             emergency: bool = False,
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Manually trigger rollback.
        
        Args:
            reason: Reason for rollback
            operator_id: ID of operator requesting rollback
            severity: Severity level (info, warning, critical)
            emergency: Whether this is an emergency rollback
            metadata: Additional metadata
            
        Returns:
            Rollback request ID
        """
        if not self.active:
            raise RollbackError("Manual rollback trigger is not active")
        
        # Determine rollback reason type
        rollback_reason = (RollbackReason.MANUAL_EMERGENCY if emergency 
                          else RollbackReason.MANUAL_OPERATOR_REQUEST)
        
        request = RollbackRequest(
            trigger_id=f"manual_{operator_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            reason=rollback_reason,
            timestamp=datetime.now(),
            severity=severity,
            message=f"Manual rollback requested by {operator_id}: {reason}",
            failure_events=[],
            metadata=metadata or {},
            operator_id=operator_id,
            confirmation_required=self.config.require_confirmation and not emergency
        )
        
        await self._trigger_rollback(request)
        return request.trigger_id
    
    async def trigger_scheduled_rollback(self,
                                       reason: str,
                                       operator_id: str,
                                       scheduled_time: datetime,
                                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Schedule a rollback for a specific time.
        
        Args:
            reason: Reason for rollback
            operator_id: ID of operator scheduling rollback
            scheduled_time: When to execute rollback
            metadata: Additional metadata
            
        Returns:
            Rollback request ID
        """
        if not self.active:
            raise RollbackError("Manual rollback trigger is not active")
        
        request = RollbackRequest(
            trigger_id=f"scheduled_{operator_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            reason=RollbackReason.MANUAL_SCHEDULED,
            timestamp=scheduled_time,
            severity="info",
            message=f"Scheduled rollback by {operator_id}: {reason}",
            failure_events=[],
            metadata={
                **(metadata or {}),
                "scheduled_time": scheduled_time.isoformat(),
                "created_time": datetime.now().isoformat()
            },
            operator_id=operator_id,
            confirmation_required=self.config.require_confirmation
        )
        
        # For scheduled rollbacks, we might want to implement a scheduler
        # For now, we'll trigger immediately if the time has passed
        if scheduled_time <= datetime.now():
            await self._trigger_rollback(request)
        else:
            self.logger.info(f"Scheduled rollback for {scheduled_time}: {request.trigger_id}")
            # In a real implementation, you'd schedule this with a task scheduler
        
        return request.trigger_id
    
    def get_rollback_status(self) -> Dict[str, Any]:
        """Get status of manual rollback trigger."""
        recent_rollbacks = [
            r for r in self.rollback_history
            if r.timestamp >= datetime.now() - timedelta(hours=24)
        ]
        
        return {
            "active": self.active,
            "config": {
                "enabled": self.config.enabled,
                "cooldown_minutes": self.config.cooldown_minutes,
                "max_rollbacks_per_hour": self.config.max_rollbacks_per_hour,
                "require_confirmation": self.config.require_confirmation
            },
            "recent_rollbacks": len(recent_rollbacks),
            "can_rollback": self._check_cooldown() and self._check_rate_limit(),
            "last_rollback": (max(self.rollback_history, key=lambda r: r.timestamp).timestamp.isoformat() 
                             if self.rollback_history else None)
        }