"""
Failure detection algorithms for rollback management.

This module implements various failure detection algorithms to identify
when a deployment has failed and rollback should be triggered.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    from ..monitoring.health_check import HealthCheckFramework
    from ..monitoring.performance_monitor import PerformanceMonitor
    from ..exceptions import RollbackError
except ImportError:
    # テスト実行時の代替インポート
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from monitoring.health_check import HealthCheckFramework
    from monitoring.performance_monitor import PerformanceMonitor
    from exceptions import RollbackError


class FailureType(Enum):
    """Types of failures that can trigger rollback."""
    HEALTH_CHECK_FAILURE = "health_check_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    ERROR_RATE_SPIKE = "error_rate_spike"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    TIMEOUT = "timeout"
    CUSTOM = "custom"


@dataclass
class FailureCondition:
    """Configuration for failure detection conditions."""
    failure_type: FailureType
    threshold: float
    duration_seconds: int
    enabled: bool = True
    description: str = ""


@dataclass
class FailureEvent:
    """Represents a detected failure event."""
    failure_type: FailureType
    timestamp: datetime
    severity: str
    message: str
    metrics: Dict[str, Any]
    threshold_breached: float
    actual_value: float


class FailureDetector:
    """
    Detects deployment failures using various algorithms and metrics.
    
    This class monitors deployment health and performance to identify
    failure conditions that should trigger automatic rollback.
    """
    
    def __init__(self, 
                 health_check_manager: HealthCheckFramework,
                 performance_monitor: PerformanceMonitor,
                 failure_conditions: Optional[List[FailureCondition]] = None):
        """
        Initialize failure detector.
        
        Args:
            health_check_manager: Health check monitoring system
            performance_monitor: Performance monitoring system
            failure_conditions: Custom failure detection conditions
        """
        self.health_check_manager = health_check_manager
        self.performance_monitor = performance_monitor
        self.logger = logging.getLogger(__name__)
        
        # Default failure conditions
        self.failure_conditions = failure_conditions or self._get_default_conditions()
        
        # Tracking state
        self.failure_history: List[FailureEvent] = []
        self.monitoring_active = False
        self._monitoring_task: Optional[asyncio.Task] = None
    
    def _get_default_conditions(self) -> List[FailureCondition]:
        """Get default failure detection conditions."""
        return [
            FailureCondition(
                failure_type=FailureType.HEALTH_CHECK_FAILURE,
                threshold=0.8,  # 80% success rate
                duration_seconds=60,
                description="Health check success rate below threshold"
            ),
            FailureCondition(
                failure_type=FailureType.PERFORMANCE_DEGRADATION,
                threshold=2000.0,  # 2 seconds response time
                duration_seconds=120,
                description="Average response time above threshold"
            ),
            FailureCondition(
                failure_type=FailureType.ERROR_RATE_SPIKE,
                threshold=0.05,  # 5% error rate
                duration_seconds=60,
                description="Error rate above threshold"
            ),
            FailureCondition(
                failure_type=FailureType.RESOURCE_EXHAUSTION,
                threshold=0.9,  # 90% resource utilization
                duration_seconds=300,
                description="Resource utilization above threshold"
            )
        ]
    
    async def start_monitoring(self) -> None:
        """Start continuous failure monitoring."""
        if self.monitoring_active:
            self.logger.warning("Failure monitoring already active")
            return
        
        self.monitoring_active = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info("Started failure detection monitoring")
    
    async def stop_monitoring(self) -> None:
        """Stop failure monitoring."""
        self.monitoring_active = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("Stopped failure detection monitoring")
    
    async def _monitoring_loop(self) -> None:
        """Main monitoring loop for failure detection."""
        try:
            while self.monitoring_active:
                await self._check_all_conditions()
                await asyncio.sleep(30)  # Check every 30 seconds
        except asyncio.CancelledError:
            self.logger.info("Monitoring loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in monitoring loop: {e}")
            raise RollbackError(f"Failure detection monitoring failed: {e}")
    
    async def _check_all_conditions(self) -> None:
        """Check all configured failure conditions."""
        for condition in self.failure_conditions:
            if not condition.enabled:
                continue
            
            try:
                failure_event = await self._check_condition(condition)
                if failure_event:
                    self.failure_history.append(failure_event)
                    self.logger.warning(
                        f"Failure detected: {failure_event.failure_type.value} - "
                        f"{failure_event.message}"
                    )
            except Exception as e:
                self.logger.error(f"Error checking condition {condition.failure_type}: {e}")
    
    async def _check_condition(self, condition: FailureCondition) -> Optional[FailureEvent]:
        """Check a specific failure condition."""
        if condition.failure_type == FailureType.HEALTH_CHECK_FAILURE:
            return await self._check_health_failure(condition)
        elif condition.failure_type == FailureType.PERFORMANCE_DEGRADATION:
            return await self._check_performance_degradation(condition)
        elif condition.failure_type == FailureType.ERROR_RATE_SPIKE:
            return await self._check_error_rate_spike(condition)
        elif condition.failure_type == FailureType.RESOURCE_EXHAUSTION:
            return await self._check_resource_exhaustion(condition)
        else:
            self.logger.warning(f"Unknown failure type: {condition.failure_type}")
            return None
    
    async def _check_health_failure(self, condition: FailureCondition) -> Optional[FailureEvent]:
        """Check for health check failures."""
        try:
            # Get recent health check results
            end_time = datetime.now()
            start_time = end_time - timedelta(seconds=condition.duration_seconds)
            
            health_results = await self.health_check_manager.get_health_history(
                start_time=start_time,
                end_time=end_time
            )
            
            if not health_results:
                return None
            
            # Calculate success rate
            total_checks = len(health_results)
            successful_checks = sum(1 for result in health_results if result.success)
            success_rate = successful_checks / total_checks
            
            if success_rate < condition.threshold:
                return FailureEvent(
                    failure_type=condition.failure_type,
                    timestamp=datetime.now(),
                    severity="critical" if success_rate < 0.5 else "warning",
                    message=f"Health check success rate {success_rate:.2%} below threshold {condition.threshold:.2%}",
                    metrics={"success_rate": success_rate, "total_checks": total_checks},
                    threshold_breached=condition.threshold,
                    actual_value=success_rate
                )
        except Exception as e:
            self.logger.error(f"Error checking health failure: {e}")
        
        return None
    
    async def _check_performance_degradation(self, condition: FailureCondition) -> Optional[FailureEvent]:
        """Check for performance degradation."""
        try:
            # Get recent performance metrics
            end_time = datetime.now()
            start_time = end_time - timedelta(seconds=condition.duration_seconds)
            
            metrics = await self.performance_monitor.get_metrics_history(
                start_time=start_time,
                end_time=end_time
            )
            
            if not metrics:
                return None
            
            # Calculate average response time
            response_times = [m.response_time_ms for m in metrics if m.response_time_ms is not None]
            if not response_times:
                return None
            
            avg_response_time = sum(response_times) / len(response_times)
            
            if avg_response_time > condition.threshold:
                return FailureEvent(
                    failure_type=condition.failure_type,
                    timestamp=datetime.now(),
                    severity="critical" if avg_response_time > condition.threshold * 2 else "warning",
                    message=f"Average response time {avg_response_time:.0f}ms above threshold {condition.threshold:.0f}ms",
                    metrics={"avg_response_time": avg_response_time, "sample_count": len(response_times)},
                    threshold_breached=condition.threshold,
                    actual_value=avg_response_time
                )
        except Exception as e:
            self.logger.error(f"Error checking performance degradation: {e}")
        
        return None
    
    async def _check_error_rate_spike(self, condition: FailureCondition) -> Optional[FailureEvent]:
        """Check for error rate spikes."""
        try:
            # Get recent error metrics
            end_time = datetime.now()
            start_time = end_time - timedelta(seconds=condition.duration_seconds)
            
            metrics = await self.performance_monitor.get_metrics_history(
                start_time=start_time,
                end_time=end_time
            )
            
            if not metrics:
                return None
            
            # Calculate error rate
            total_requests = sum(m.request_count for m in metrics if m.request_count is not None)
            error_requests = sum(m.error_count for m in metrics if m.error_count is not None)
            
            if total_requests == 0:
                return None
            
            error_rate = error_requests / total_requests
            
            if error_rate > condition.threshold:
                return FailureEvent(
                    failure_type=condition.failure_type,
                    timestamp=datetime.now(),
                    severity="critical" if error_rate > condition.threshold * 2 else "warning",
                    message=f"Error rate {error_rate:.2%} above threshold {condition.threshold:.2%}",
                    metrics={"error_rate": error_rate, "total_requests": total_requests, "error_requests": error_requests},
                    threshold_breached=condition.threshold,
                    actual_value=error_rate
                )
        except Exception as e:
            self.logger.error(f"Error checking error rate spike: {e}")
        
        return None
    
    async def _check_resource_exhaustion(self, condition: FailureCondition) -> Optional[FailureEvent]:
        """Check for resource exhaustion."""
        try:
            # Get current resource utilization
            metrics = await self.performance_monitor.get_current_metrics()
            
            if not metrics or not metrics.resource_utilization:
                return None
            
            # Check CPU and memory utilization
            cpu_usage = metrics.resource_utilization.get('cpu_percent', 0)
            memory_usage = metrics.resource_utilization.get('memory_percent', 0)
            
            max_usage = max(cpu_usage, memory_usage) / 100.0  # Convert to decimal
            
            if max_usage > condition.threshold:
                resource_type = "CPU" if cpu_usage > memory_usage else "Memory"
                return FailureEvent(
                    failure_type=condition.failure_type,
                    timestamp=datetime.now(),
                    severity="critical" if max_usage > 0.95 else "warning",
                    message=f"{resource_type} utilization {max_usage:.1%} above threshold {condition.threshold:.1%}",
                    metrics={"cpu_usage": cpu_usage, "memory_usage": memory_usage, "max_usage": max_usage},
                    threshold_breached=condition.threshold,
                    actual_value=max_usage
                )
        except Exception as e:
            self.logger.error(f"Error checking resource exhaustion: {e}")
        
        return None
    
    def get_recent_failures(self, minutes: int = 10) -> List[FailureEvent]:
        """Get recent failure events."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        return [
            failure for failure in self.failure_history
            if failure.timestamp >= cutoff_time
        ]
    
    def has_critical_failures(self, minutes: int = 5) -> bool:
        """Check if there are recent critical failures."""
        recent_failures = self.get_recent_failures(minutes)
        return any(failure.severity == "critical" for failure in recent_failures)
    
    def get_failure_summary(self) -> Dict[str, Any]:
        """Get summary of failure detection status."""
        recent_failures = self.get_recent_failures(30)  # Last 30 minutes
        
        failure_counts = {}
        for failure in recent_failures:
            failure_type = failure.failure_type.value
            failure_counts[failure_type] = failure_counts.get(failure_type, 0) + 1
        
        return {
            "monitoring_active": self.monitoring_active,
            "total_conditions": len(self.failure_conditions),
            "enabled_conditions": len([c for c in self.failure_conditions if c.enabled]),
            "recent_failures": len(recent_failures),
            "failure_counts": failure_counts,
            "has_critical_failures": self.has_critical_failures(),
            "last_check": datetime.now().isoformat()
        }