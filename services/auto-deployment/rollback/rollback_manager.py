"""
Rollback management system that integrates triggers and execution.

This module provides a unified interface for rollback management,
coordinating between trigger detection and rollback execution.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

try:
    from .rollback_triggers import (
        RollbackTrigger, AutomaticRollbackTrigger, ManualRollbackTrigger,
        RollbackRequest, RollbackTriggerConfig
    )
    from .rollback_executor import (
        RollbackExecutor, RollbackConfig, RollbackTarget, RollbackResult,
        RollbackStatus, RollbackStrategy
    )
    from .failure_detector import FailureDetector
    from ..deployment.cloud_run.traffic_manager import TrafficManager
    from ..deployment.cloud_run.revision_manager import RevisionManager
    from ..monitoring.health_check import HealthCheckFramework
    from ..monitoring.performance_monitor import PerformanceMonitor
    from ..notification.notification_manager import NotificationManager
    from ..exceptions import RollbackError
except ImportError:
    # テスト実行時の代替インポート
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from rollback.rollback_triggers import (
        RollbackTrigger, AutomaticRollbackTrigger, ManualRollbackTrigger,
        RollbackRequest, RollbackTriggerConfig
    )
    from rollback.rollback_executor import (
        RollbackExecutor, RollbackConfig, RollbackTarget, RollbackResult,
        RollbackStatus, RollbackStrategy
    )
    from rollback.failure_detector import FailureDetector
    from deployment.cloud_run.traffic_manager import TrafficManager
    from deployment.cloud_run.revision_manager import RevisionManager
    from monitoring.health_check import HealthCheckFramework
    from monitoring.performance_monitor import PerformanceMonitor
    from notification.notification_manager import NotificationManager
    from exceptions import RollbackError


class RollbackManagerStatus(Enum):
    """Status of rollback manager."""
    STOPPED = "stopped"
    STARTING = "starting"
    ACTIVE = "active"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class RollbackManagerConfig:
    """Configuration for rollback manager."""
    auto_rollback_enabled: bool = True
    manual_rollback_enabled: bool = True
    failure_detection_enabled: bool = True
    notification_enabled: bool = True
    
    # Trigger configurations
    auto_trigger_config: Optional[RollbackTriggerConfig] = None
    manual_trigger_config: Optional[RollbackTriggerConfig] = None
    
    # Execution configuration
    rollback_config: Optional[RollbackConfig] = None
    
    # Service configuration
    service_name: str = ""
    environment: str = "production"
    
    # Monitoring intervals
    monitoring_interval_seconds: int = 30
    health_check_interval_seconds: int = 60


class RollbackManager:
    """
    Unified rollback management system.
    
    This class integrates failure detection, rollback triggers, and rollback execution
    to provide a comprehensive automated rollback solution.
    """
    
    def __init__(self,
                 traffic_manager: TrafficManager,
                 revision_manager: RevisionManager,
                 health_check_manager: HealthCheckFramework,
                 performance_monitor: PerformanceMonitor,
                 notification_manager: NotificationManager,
                 config: Optional[RollbackManagerConfig] = None):
        """
        Initialize rollback manager.
        
        Args:
            traffic_manager: Traffic management system
            revision_manager: Revision management system
            health_check_manager: Health check monitoring
            performance_monitor: Performance monitoring
            notification_manager: Notification system
            config: Rollback manager configuration
        """
        self.config = config or RollbackManagerConfig()
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.traffic_manager = traffic_manager
        self.revision_manager = revision_manager
        self.health_check_manager = health_check_manager
        self.performance_monitor = performance_monitor
        self.notification_manager = notification_manager
        
        # Initialize failure detector
        self.failure_detector = FailureDetector(
            health_check_manager=health_check_manager,
            performance_monitor=performance_monitor
        )
        
        # Initialize rollback executor
        rollback_config = self.config.rollback_config or RollbackConfig()
        self.rollback_executor = RollbackExecutor(
            traffic_manager=traffic_manager,
            revision_manager=revision_manager,
            health_check_manager=health_check_manager,
            performance_monitor=performance_monitor,
            notification_manager=notification_manager,
            config=rollback_config
        )
        
        # Initialize triggers
        self.automatic_trigger: Optional[AutomaticRollbackTrigger] = None
        self.manual_trigger: Optional[ManualRollbackTrigger] = None
        
        if self.config.auto_rollback_enabled:
            auto_config = self.config.auto_trigger_config or RollbackTriggerConfig()
            self.automatic_trigger = AutomaticRollbackTrigger(
                failure_detector=self.failure_detector,
                config=auto_config
            )
            self.automatic_trigger.add_callback(self._handle_rollback_request)
        
        if self.config.manual_rollback_enabled:
            manual_config = self.config.manual_trigger_config or RollbackTriggerConfig()
            self.manual_trigger = ManualRollbackTrigger(config=manual_config)
            self.manual_trigger.add_callback(self._handle_rollback_request)
        
        # Manager state
        self.status = RollbackManagerStatus.STOPPED
        self._management_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Statistics and tracking
        self.start_time: Optional[datetime] = None
        self.total_rollbacks = 0
        self.successful_rollbacks = 0
        self.failed_rollbacks = 0
    
    async def start(self) -> None:
        """Start the rollback management system."""
        if self.status != RollbackManagerStatus.STOPPED:
            self.logger.warning(f"Rollback manager already running with status: {self.status}")
            return
        
        try:
            self.status = RollbackManagerStatus.STARTING
            self.start_time = datetime.now()
            
            self.logger.info("Starting rollback management system...")
            
            # Start failure detection
            if self.config.failure_detection_enabled:
                await self.failure_detector.start_monitoring()
                self.logger.info("Failure detection started")
            
            # Start automatic trigger
            if self.automatic_trigger:
                await self.automatic_trigger.start()
                self.logger.info("Automatic rollback trigger started")
            
            # Start manual trigger
            if self.manual_trigger:
                await self.manual_trigger.start()
                self.logger.info("Manual rollback trigger started")
            
            # Start management loop
            self._management_task = asyncio.create_task(self._management_loop())
            
            self.status = RollbackManagerStatus.ACTIVE
            self.logger.info("Rollback management system started successfully")
            
            # Send startup notification
            if self.config.notification_enabled:
                await self._send_status_notification("started")
        
        except Exception as e:
            self.status = RollbackManagerStatus.ERROR
            self.logger.error(f"Failed to start rollback management system: {e}")
            await self._cleanup()
            raise RollbackError(f"Failed to start rollback manager: {e}")
    
    async def stop(self) -> None:
        """Stop the rollback management system."""
        if self.status == RollbackManagerStatus.STOPPED:
            self.logger.info("Rollback manager already stopped")
            return
        
        try:
            self.status = RollbackManagerStatus.STOPPING
            self.logger.info("Stopping rollback management system...")
            
            # Signal shutdown
            self._shutdown_event.set()
            
            # Stop management loop
            if self._management_task:
                self._management_task.cancel()
                try:
                    await self._management_task
                except asyncio.CancelledError:
                    pass
            
            await self._cleanup()
            
            self.status = RollbackManagerStatus.STOPPED
            self.logger.info("Rollback management system stopped")
            
            # Send shutdown notification
            if self.config.notification_enabled:
                await self._send_status_notification("stopped")
        
        except Exception as e:
            self.status = RollbackManagerStatus.ERROR
            self.logger.error(f"Error stopping rollback management system: {e}")
            raise RollbackError(f"Failed to stop rollback manager: {e}")
    
    async def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            # Stop triggers
            if self.automatic_trigger:
                await self.automatic_trigger.stop()
            
            if self.manual_trigger:
                await self.manual_trigger.stop()
            
            # Stop failure detection
            if self.config.failure_detection_enabled:
                await self.failure_detector.stop_monitoring()
        
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    async def _management_loop(self) -> None:
        """Main management loop."""
        try:
            while not self._shutdown_event.is_set():
                await self._perform_management_tasks()
                
                try:
                    await asyncio.wait_for(
                        self._shutdown_event.wait(),
                        timeout=self.config.monitoring_interval_seconds
                    )
                    break  # Shutdown requested
                except asyncio.TimeoutError:
                    continue  # Continue monitoring
        
        except asyncio.CancelledError:
            self.logger.info("Management loop cancelled")
        except Exception as e:
            self.logger.error(f"Error in management loop: {e}")
            self.status = RollbackManagerStatus.ERROR
    
    async def _perform_management_tasks(self) -> None:
        """Perform periodic management tasks."""
        try:
            # Check system health
            await self._check_system_health()
            
            # Clean up old data
            await self._cleanup_old_data()
            
            # Update statistics
            await self._update_statistics()
        
        except Exception as e:
            self.logger.error(f"Error in management tasks: {e}")
    
    async def _check_system_health(self) -> None:
        """Check overall system health."""
        try:
            # Check if all components are healthy
            components_status = {
                "failure_detector": self.failure_detector.monitoring_active,
                "automatic_trigger": self.automatic_trigger.monitoring_active if self.automatic_trigger else True,
                "manual_trigger": self.manual_trigger.active if self.manual_trigger else True,
                "rollback_executor": True  # Executor is stateless
            }
            
            unhealthy_components = [
                name for name, healthy in components_status.items()
                if not healthy
            ]
            
            if unhealthy_components:
                self.logger.warning(f"Unhealthy components detected: {unhealthy_components}")
                
                # Attempt to restart unhealthy components
                await self._restart_unhealthy_components(unhealthy_components)
        
        except Exception as e:
            self.logger.error(f"Error checking system health: {e}")
    
    async def _restart_unhealthy_components(self, components: List[str]) -> None:
        """Restart unhealthy components."""
        for component in components:
            try:
                if component == "failure_detector" and not self.failure_detector.monitoring_active:
                    self.logger.info("Restarting failure detector")
                    await self.failure_detector.start_monitoring()
                
                elif component == "automatic_trigger" and self.automatic_trigger:
                    self.logger.info("Restarting automatic trigger")
                    await self.automatic_trigger.stop()
                    await self.automatic_trigger.start()
                
                elif component == "manual_trigger" and self.manual_trigger:
                    self.logger.info("Restarting manual trigger")
                    await self.manual_trigger.stop()
                    await self.manual_trigger.start()
            
            except Exception as e:
                self.logger.error(f"Failed to restart component {component}: {e}")
    
    async def _cleanup_old_data(self) -> None:
        """Clean up old data to prevent memory leaks."""
        try:
            # Clean up old failure events (keep last 1000)
            if len(self.failure_detector.failure_history) > 1000:
                self.failure_detector.failure_history = self.failure_detector.failure_history[-1000:]
            
            # Clean up old rollback history (keep last 100)
            if len(self.rollback_executor.rollback_history) > 100:
                self.rollback_executor.rollback_history = self.rollback_executor.rollback_history[-100:]
        
        except Exception as e:
            self.logger.error(f"Error cleaning up old data: {e}")
    
    async def _update_statistics(self) -> None:
        """Update rollback statistics."""
        try:
            # Update rollback counts
            completed_rollbacks = [
                r for r in self.rollback_executor.rollback_history
                if r.status == RollbackStatus.COMPLETED
            ]
            failed_rollbacks = [
                r for r in self.rollback_executor.rollback_history
                if r.status == RollbackStatus.FAILED
            ]
            
            self.total_rollbacks = len(self.rollback_executor.rollback_history)
            self.successful_rollbacks = len(completed_rollbacks)
            self.failed_rollbacks = len(failed_rollbacks)
        
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    async def _handle_rollback_request(self, request: RollbackRequest) -> None:
        """Handle rollback request from triggers."""
        try:
            self.logger.info(f"Processing rollback request: {request.trigger_id}")
            
            # Determine target revision for rollback
            target_revision = await self._determine_rollback_target()
            
            if not target_revision:
                self.logger.error("Could not determine rollback target revision")
                return
            
            # Create rollback target
            target = RollbackTarget(
                service_name=self.config.service_name,
                target_revision=target_revision,
                environment=self.config.environment
            )
            
            # Execute rollback
            result = await self.rollback_executor.execute_rollback(request, target)
            
            # Log result
            if result.success:
                self.logger.info(f"Rollback completed successfully: {result.rollback_id}")
            else:
                self.logger.error(f"Rollback failed: {result.rollback_id} - {result.error_message}")
        
        except Exception as e:
            self.logger.error(f"Error handling rollback request: {e}")
    
    async def _determine_rollback_target(self) -> Optional[str]:
        """Determine the target revision for rollback."""
        try:
            # Get revision history
            revisions = await self.revision_manager.get_revision_history(
                service_name=self.config.service_name,
                limit=10
            )
            
            if len(revisions) < 2:
                self.logger.warning("Not enough revisions available for rollback")
                return None
            
            # Get current revision
            current_revision = await self.revision_manager.get_current_revision(
                service_name=self.config.service_name
            )
            
            # Find the previous stable revision
            for revision in revisions:
                if revision.name != current_revision and revision.status == "READY":
                    return revision.name
            
            self.logger.warning("No stable previous revision found for rollback")
            return None
        
        except Exception as e:
            self.logger.error(f"Error determining rollback target: {e}")
            return None
    
    async def _send_status_notification(self, status: str) -> None:
        """Send status notification."""
        try:
            message = f"Rollback Manager {status}\n"
            message += f"Service: {self.config.service_name}\n"
            message += f"Environment: {self.config.environment}\n"
            message += f"Time: {datetime.now().isoformat()}\n"
            
            await self.notification_manager.send_notification(
                channel="system",
                message=message,
                severity="info"
            )
        except Exception as e:
            self.logger.error(f"Error sending status notification: {e}")
    
    # Public API methods
    
    async def trigger_manual_rollback(self,
                                    reason: str,
                                    operator_id: str,
                                    severity: str = "warning",
                                    emergency: bool = False) -> Optional[str]:
        """
        Trigger manual rollback.
        
        Args:
            reason: Reason for rollback
            operator_id: ID of operator requesting rollback
            severity: Severity level
            emergency: Whether this is an emergency rollback
            
        Returns:
            Rollback request ID if successful, None otherwise
        """
        if not self.manual_trigger:
            self.logger.error("Manual rollback trigger not available")
            return None
        
        try:
            return await self.manual_trigger.trigger_rollback(
                reason=reason,
                operator_id=operator_id,
                severity=severity,
                emergency=emergency
            )
        except Exception as e:
            self.logger.error(f"Error triggering manual rollback: {e}")
            return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of rollback manager."""
        uptime = None
        if self.start_time:
            uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "status": self.status.value,
            "uptime_seconds": uptime,
            "config": {
                "auto_rollback_enabled": self.config.auto_rollback_enabled,
                "manual_rollback_enabled": self.config.manual_rollback_enabled,
                "failure_detection_enabled": self.config.failure_detection_enabled,
                "service_name": self.config.service_name,
                "environment": self.config.environment
            },
            "statistics": {
                "total_rollbacks": self.total_rollbacks,
                "successful_rollbacks": self.successful_rollbacks,
                "failed_rollbacks": self.failed_rollbacks,
                "success_rate": (self.successful_rollbacks / self.total_rollbacks * 100) if self.total_rollbacks > 0 else 0
            },
            "components": {
                "failure_detector": {
                    "active": self.failure_detector.monitoring_active,
                    "recent_failures": len(self.failure_detector.get_recent_failures())
                },
                "automatic_trigger": {
                    "active": self.automatic_trigger.monitoring_active if self.automatic_trigger else False,
                    "enabled": self.config.auto_rollback_enabled
                },
                "manual_trigger": {
                    "active": self.manual_trigger.active if self.manual_trigger else False,
                    "enabled": self.config.manual_rollback_enabled
                },
                "rollback_executor": {
                    "active_rollbacks": len(self.rollback_executor.get_active_rollbacks()),
                    "recent_rollbacks": len(self.rollback_executor.get_rollback_history(10))
                }
            }
        }
    
    def get_recent_rollbacks(self, limit: int = 10) -> List[RollbackResult]:
        """Get recent rollback results."""
        return self.rollback_executor.get_rollback_history(limit)
    
    def get_active_rollbacks(self) -> List[RollbackResult]:
        """Get currently active rollbacks."""
        return self.rollback_executor.get_active_rollbacks()
    
    def get_recent_failures(self, minutes: int = 30) -> List:
        """Get recent failure events."""
        return self.failure_detector.get_recent_failures(minutes)