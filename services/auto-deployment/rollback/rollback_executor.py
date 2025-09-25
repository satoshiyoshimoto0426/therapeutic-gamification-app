"""
Rollback execution engine for automated deployment rollbacks.

This module implements the core rollback execution logic, including
traffic rollback procedures and rollback verification systems.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

try:
    from .rollback_triggers import RollbackRequest, RollbackReason
    from ..deployment.cloud_run.traffic_manager import TrafficManager, TrafficUpdateResult
    from ..deployment.cloud_run.revision_manager import RevisionManager, RevisionInfo
    from ..monitoring.health_check import HealthCheckFramework
    from ..monitoring.performance_monitor import PerformanceMonitor
    from ..notification.notification_manager import NotificationManager
    from ..exceptions import RollbackError
except ImportError:
    # テスト実行時の代替インポート
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from rollback.rollback_triggers import RollbackRequest, RollbackReason
    from deployment.cloud_run.traffic_manager import TrafficManager, TrafficUpdateResult
    from deployment.cloud_run.revision_manager import RevisionManager, RevisionInfo
    from monitoring.health_check import HealthCheckFramework
    from monitoring.performance_monitor import PerformanceMonitor
    from notification.notification_manager import NotificationManager
    from exceptions import RollbackError


class RollbackStatus(Enum):
    """Status of rollback execution."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RollbackStrategy(Enum):
    """Rollback execution strategies."""
    IMMEDIATE = "immediate"  # Immediate traffic switch
    GRADUAL = "gradual"     # Gradual traffic shift
    BLUE_GREEN = "blue_green"  # Blue-green rollback


@dataclass
class RollbackConfig:
    """Configuration for rollback execution."""
    strategy: RollbackStrategy = RollbackStrategy.IMMEDIATE
    verification_timeout_seconds: int = 300
    health_check_timeout_seconds: int = 120
    gradual_rollback_steps: int = 3
    gradual_rollback_interval_seconds: int = 60
    max_retry_attempts: int = 3
    notification_enabled: bool = True


@dataclass
class RollbackTarget:
    """Target configuration for rollback."""
    service_name: str
    target_revision: str
    current_revision: Optional[str] = None
    environment: str = "production"


@dataclass
class RollbackResult:
    """Result of rollback execution."""
    success: bool
    rollback_id: str
    status: RollbackStatus
    target: RollbackTarget
    start_time: datetime
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    verification_results: Dict[str, Any] = None
    traffic_results: List[TrafficUpdateResult] = None


class RollbackExecutor:
    """
    Core rollback execution engine.
    
    Handles the execution of rollback procedures including traffic management,
    verification, and notification.
    """
    
    def __init__(self,
                 traffic_manager: TrafficManager,
                 revision_manager: RevisionManager,
                 health_check_manager: HealthCheckFramework,
                 performance_monitor: PerformanceMonitor,
                 notification_manager: NotificationManager,
                 config: Optional[RollbackConfig] = None):
        """
        Initialize rollback executor.
        
        Args:
            traffic_manager: Traffic management system
            revision_manager: Revision management system
            health_check_manager: Health check monitoring
            performance_monitor: Performance monitoring
            notification_manager: Notification system
            config: Rollback configuration
        """
        self.traffic_manager = traffic_manager
        self.revision_manager = revision_manager
        self.health_check_manager = health_check_manager
        self.performance_monitor = performance_monitor
        self.notification_manager = notification_manager
        self.config = config or RollbackConfig()
        self.logger = logging.getLogger(__name__)
        
        # Execution tracking
        self.active_rollbacks: Dict[str, RollbackResult] = {}
        self.rollback_history: List[RollbackResult] = []
        
        # Callbacks for rollback events
        self._callbacks: Dict[str, List[Callable]] = {
            'start': [],
            'progress': [],
            'complete': [],
            'failed': []
        }
    
    def add_callback(self, event: str, callback: Callable) -> None:
        """Add callback for rollback events."""
        if event in self._callbacks:
            self._callbacks[event].append(callback)
    
    async def execute_rollback(self, request: RollbackRequest, target: RollbackTarget) -> RollbackResult:
        """
        Execute rollback based on rollback request.
        
        Args:
            request: Rollback request with trigger information
            target: Rollback target configuration
            
        Returns:
            RollbackResult with execution status
        """
        rollback_id = f"rollback_{request.trigger_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        result = RollbackResult(
            success=False,
            rollback_id=rollback_id,
            status=RollbackStatus.PENDING,
            target=target,
            start_time=datetime.now(),
            traffic_results=[]
        )
        
        self.active_rollbacks[rollback_id] = result
        
        try:
            self.logger.info(f"Starting rollback execution: {rollback_id}")
            await self._notify_callbacks('start', result)
            
            # Send initial notification
            if self.config.notification_enabled:
                await self._send_rollback_notification(
                    "started", result, request
                )
            
            # Update status to in progress
            result.status = RollbackStatus.IN_PROGRESS
            await self._notify_callbacks('progress', result)
            
            # Execute rollback based on strategy
            if self.config.strategy == RollbackStrategy.IMMEDIATE:
                success = await self._execute_immediate_rollback(result)
            elif self.config.strategy == RollbackStrategy.GRADUAL:
                success = await self._execute_gradual_rollback(result)
            elif self.config.strategy == RollbackStrategy.BLUE_GREEN:
                success = await self._execute_blue_green_rollback(result)
            else:
                raise RollbackError(f"Unknown rollback strategy: {self.config.strategy}")
            
            if success:
                # Verify rollback success
                verification_success = await self._verify_rollback(result)
                
                if verification_success:
                    result.success = True
                    result.status = RollbackStatus.COMPLETED
                    result.end_time = datetime.now()
                    
                    self.logger.info(f"Rollback completed successfully: {rollback_id}")
                    await self._notify_callbacks('complete', result)
                    
                    if self.config.notification_enabled:
                        await self._send_rollback_notification(
                            "completed", result, request
                        )
                else:
                    result.status = RollbackStatus.FAILED
                    result.error_message = "Rollback verification failed"
                    
                    self.logger.error(f"Rollback verification failed: {rollback_id}")
                    await self._notify_callbacks('failed', result)
                    
                    if self.config.notification_enabled:
                        await self._send_rollback_notification(
                            "failed", result, request
                        )
            else:
                result.status = RollbackStatus.FAILED
                result.error_message = "Rollback execution failed"
                
                self.logger.error(f"Rollback execution failed: {rollback_id}")
                await self._notify_callbacks('failed', result)
                
                if self.config.notification_enabled:
                    await self._send_rollback_notification(
                        "failed", result, request
                    )
        
        except Exception as e:
            result.status = RollbackStatus.FAILED
            result.error_message = str(e)
            result.end_time = datetime.now()
            
            self.logger.error(f"Rollback execution error: {rollback_id} - {e}")
            await self._notify_callbacks('failed', result)
            
            if self.config.notification_enabled:
                await self._send_rollback_notification(
                    "failed", result, request
                )
        
        finally:
            # Move from active to history
            if rollback_id in self.active_rollbacks:
                del self.active_rollbacks[rollback_id]
            self.rollback_history.append(result)
            
            # Keep only recent history (last 100 rollbacks)
            if len(self.rollback_history) > 100:
                self.rollback_history = self.rollback_history[-100:]
        
        return result
    
    async def _execute_immediate_rollback(self, result: RollbackResult) -> bool:
        """
        Execute immediate rollback strategy.
        
        Args:
            result: Rollback result to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Executing immediate rollback for service: {result.target.service_name}")
            
            # Switch all traffic to target revision immediately
            traffic_result = self.traffic_manager.rollback_traffic(
                service_name=result.target.service_name,
                target_revision=result.target.target_revision
            )
            
            result.traffic_results.append(traffic_result)
            
            if traffic_result.success:
                self.logger.info(f"Traffic rollback successful for service: {result.target.service_name}")
                return True
            else:
                self.logger.error(f"Traffic rollback failed: {traffic_result.error_message}")
                result.error_message = f"Traffic rollback failed: {traffic_result.error_message}"
                return False
        
        except Exception as e:
            self.logger.error(f"Error in immediate rollback: {e}")
            result.error_message = f"Immediate rollback error: {e}"
            return False
    
    async def _execute_gradual_rollback(self, result: RollbackResult) -> bool:
        """
        Execute gradual rollback strategy.
        
        Args:
            result: Rollback result to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Executing gradual rollback for service: {result.target.service_name}")
            
            steps = self.config.gradual_rollback_steps
            interval = self.config.gradual_rollback_interval_seconds
            
            # Calculate traffic percentages for each step
            step_percentages = []
            for i in range(1, steps + 1):
                percentage = int((i / steps) * 100)
                step_percentages.append(percentage)
            
            # Execute gradual traffic shift
            for i, target_percentage in enumerate(step_percentages):
                current_percentage = 100 - target_percentage
                
                self.logger.info(
                    f"Gradual rollback step {i + 1}/{steps}: "
                    f"{target_percentage}% to target revision"
                )
                
                # Create traffic splits
                from ..deployment.cloud_run.traffic_manager import TrafficSplit
                traffic_splits = []
                
                if target_percentage > 0:
                    traffic_splits.append(TrafficSplit(
                        revision_name=result.target.target_revision,
                        percentage=target_percentage,
                        tag="rollback"
                    ))
                
                if current_percentage > 0 and result.target.current_revision:
                    traffic_splits.append(TrafficSplit(
                        revision_name=result.target.current_revision,
                        percentage=current_percentage,
                        tag="current"
                    ))
                
                # Update traffic
                traffic_result = self.traffic_manager.update_traffic(
                    service_name=result.target.service_name,
                    traffic_splits=traffic_splits
                )
                
                result.traffic_results.append(traffic_result)
                
                if not traffic_result.success:
                    self.logger.error(f"Gradual rollback step {i + 1} failed: {traffic_result.error_message}")
                    result.error_message = f"Gradual rollback step {i + 1} failed: {traffic_result.error_message}"
                    return False
                
                # Wait before next step (except for last step)
                if i < len(step_percentages) - 1:
                    await asyncio.sleep(interval)
                
                # Quick health check after each step
                if not await self._quick_health_check(result.target.service_name):
                    self.logger.error(f"Health check failed after gradual rollback step {i + 1}")
                    result.error_message = f"Health check failed after gradual rollback step {i + 1}"
                    return False
            
            self.logger.info(f"Gradual rollback completed for service: {result.target.service_name}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error in gradual rollback: {e}")
            result.error_message = f"Gradual rollback error: {e}"
            return False
    
    async def _execute_blue_green_rollback(self, result: RollbackResult) -> bool:
        """
        Execute blue-green rollback strategy.
        
        Args:
            result: Rollback result to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info(f"Executing blue-green rollback for service: {result.target.service_name}")
            
            # In blue-green rollback, we switch traffic from green (current) to blue (target)
            traffic_result = self.traffic_manager.execute_blue_green_deployment(
                service_name=result.target.service_name,
                blue_revision=result.target.target_revision,
                green_revision=result.target.current_revision or "",
                switch_to_green=False  # Switch back to blue (target revision)
            )
            
            result.traffic_results.append(traffic_result)
            
            if traffic_result.success:
                self.logger.info(f"Blue-green rollback successful for service: {result.target.service_name}")
                return True
            else:
                self.logger.error(f"Blue-green rollback failed: {traffic_result.error_message}")
                result.error_message = f"Blue-green rollback failed: {traffic_result.error_message}"
                return False
        
        except Exception as e:
            self.logger.error(f"Error in blue-green rollback: {e}")
            result.error_message = f"Blue-green rollback error: {e}"
            return False
    
    async def _verify_rollback(self, result: RollbackResult) -> bool:
        """
        Verify rollback success through health checks and performance monitoring.
        
        Args:
            result: Rollback result to update
            
        Returns:
            True if verification successful, False otherwise
        """
        try:
            self.logger.info(f"Verifying rollback for service: {result.target.service_name}")
            
            verification_results = {
                "health_check": False,
                "performance_check": False,
                "traffic_verification": False
            }
            
            # Verify traffic allocation
            current_traffic = self.traffic_manager.get_current_traffic(result.target.service_name)
            target_traffic_percentage = current_traffic.get(result.target.target_revision, 0)
            
            if target_traffic_percentage >= 90:  # Allow for small rounding differences
                verification_results["traffic_verification"] = True
                self.logger.info(f"Traffic verification passed: {target_traffic_percentage}% to target revision")
            else:
                self.logger.warning(f"Traffic verification failed: only {target_traffic_percentage}% to target revision")
            
            # Health check verification
            health_check_success = await self._verify_health_checks(result.target.service_name)
            verification_results["health_check"] = health_check_success
            
            # Performance verification
            performance_check_success = await self._verify_performance(result.target.service_name)
            verification_results["performance_check"] = performance_check_success
            
            result.verification_results = verification_results
            
            # Overall verification success
            overall_success = all(verification_results.values())
            
            if overall_success:
                self.logger.info(f"Rollback verification successful for service: {result.target.service_name}")
            else:
                failed_checks = [k for k, v in verification_results.items() if not v]
                self.logger.error(f"Rollback verification failed for service: {result.target.service_name}. Failed checks: {failed_checks}")
            
            return overall_success
        
        except Exception as e:
            self.logger.error(f"Error in rollback verification: {e}")
            result.error_message = f"Rollback verification error: {e}"
            return False
    
    async def _verify_health_checks(self, service_name: str) -> bool:
        """Verify health checks after rollback."""
        try:
            # Wait a bit for the service to stabilize
            await asyncio.sleep(30)
            
            # Run health checks for the specified timeout
            timeout = self.config.health_check_timeout_seconds
            start_time = datetime.now()
            
            while (datetime.now() - start_time).total_seconds() < timeout:
                health_results = await self.health_check_manager.run_health_checks()
                
                if health_results:
                    # Check if all health checks are passing
                    all_healthy = all(result.success for result in health_results)
                    if all_healthy:
                        self.logger.info("Health check verification passed")
                        return True
                
                # Wait before next check
                await asyncio.sleep(10)
            
            self.logger.warning("Health check verification timed out")
            return False
        
        except Exception as e:
            self.logger.error(f"Error in health check verification: {e}")
            return False
    
    async def _verify_performance(self, service_name: str) -> bool:
        """Verify performance metrics after rollback."""
        try:
            # Wait for performance metrics to stabilize
            await asyncio.sleep(60)
            
            # Get recent performance metrics
            end_time = datetime.now()
            start_time = end_time - timedelta(minutes=5)
            
            metrics = await self.performance_monitor.get_metrics_history(
                start_time=start_time,
                end_time=end_time
            )
            
            if not metrics:
                self.logger.warning("No performance metrics available for verification")
                return True  # Assume success if no metrics available
            
            # Check response time
            response_times = [m.response_time_ms for m in metrics if m.response_time_ms is not None]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                if avg_response_time > 5000:  # 5 seconds threshold
                    self.logger.warning(f"Performance verification failed: high response time {avg_response_time}ms")
                    return False
            
            # Check error rate
            total_requests = sum(m.request_count for m in metrics if m.request_count is not None)
            error_requests = sum(m.error_count for m in metrics if m.error_count is not None)
            
            if total_requests > 0:
                error_rate = error_requests / total_requests
                if error_rate > 0.1:  # 10% error rate threshold
                    self.logger.warning(f"Performance verification failed: high error rate {error_rate:.2%}")
                    return False
            
            self.logger.info("Performance verification passed")
            return True
        
        except Exception as e:
            self.logger.error(f"Error in performance verification: {e}")
            return False
    
    async def _quick_health_check(self, service_name: str) -> bool:
        """Perform a quick health check."""
        try:
            health_results = await self.health_check_manager.run_health_checks()
            return all(result.success for result in health_results) if health_results else True
        except Exception as e:
            self.logger.error(f"Quick health check error: {e}")
            return False
    
    async def _send_rollback_notification(self, status: str, result: RollbackResult, request: RollbackRequest) -> None:
        """Send rollback notification."""
        try:
            message = f"Rollback {status}: {result.rollback_id}\n"
            message += f"Service: {result.target.service_name}\n"
            message += f"Target Revision: {result.target.target_revision}\n"
            message += f"Reason: {request.reason.value}\n"
            
            if result.error_message:
                message += f"Error: {result.error_message}\n"
            
            await self.notification_manager.send_notification(
                channel="rollback",
                message=message,
                severity=request.severity
            )
        except Exception as e:
            self.logger.error(f"Error sending rollback notification: {e}")
    
    async def _notify_callbacks(self, event: str, result: RollbackResult) -> None:
        """Notify registered callbacks."""
        for callback in self._callbacks.get(event, []):
            try:
                await callback(result)
            except Exception as e:
                self.logger.error(f"Error in rollback callback: {e}")
    
    def get_rollback_status(self, rollback_id: str) -> Optional[RollbackResult]:
        """Get status of a specific rollback."""
        # Check active rollbacks first
        if rollback_id in self.active_rollbacks:
            return self.active_rollbacks[rollback_id]
        
        # Check history
        for result in self.rollback_history:
            if result.rollback_id == rollback_id:
                return result
        
        return None
    
    def get_active_rollbacks(self) -> List[RollbackResult]:
        """Get all currently active rollbacks."""
        return list(self.active_rollbacks.values())
    
    def get_rollback_history(self, limit: int = 50) -> List[RollbackResult]:
        """Get rollback history."""
        return self.rollback_history[-limit:] if limit > 0 else self.rollback_history
    
    async def cancel_rollback(self, rollback_id: str) -> bool:
        """
        Cancel an active rollback.
        
        Args:
            rollback_id: ID of rollback to cancel
            
        Returns:
            True if cancelled successfully, False otherwise
        """
        if rollback_id not in self.active_rollbacks:
            self.logger.warning(f"Rollback {rollback_id} not found in active rollbacks")
            return False
        
        try:
            result = self.active_rollbacks[rollback_id]
            result.status = RollbackStatus.CANCELLED
            result.end_time = datetime.now()
            
            # Move to history
            del self.active_rollbacks[rollback_id]
            self.rollback_history.append(result)
            
            self.logger.info(f"Rollback cancelled: {rollback_id}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error cancelling rollback {rollback_id}: {e}")
            return False