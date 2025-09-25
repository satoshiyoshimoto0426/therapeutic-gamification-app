"""
Rollback integration system demonstration.

This script demonstrates how to use the integrated rollback system
including automatic and manual rollback capabilities.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

try:
    from .rollback_manager import RollbackManager, RollbackManagerConfig
    from .rollback_executor import RollbackConfig, RollbackStrategy
    from .rollback_triggers import RollbackTriggerConfig
    from .failure_detector import FailureDetector, FailureCondition, FailureType
    from ..deployment.cloud_run.traffic_manager import TrafficManager
    from ..deployment.cloud_run.revision_manager import RevisionManager
    from ..monitoring.health_check import HealthCheckFramework
    from ..monitoring.performance_monitor import PerformanceMonitor
    from ..notification.notification_manager import NotificationManager
except ImportError:
    # テスト実行時の代替インポート
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
    from rollback.rollback_manager import RollbackManager, RollbackManagerConfig
    from rollback.rollback_executor import RollbackConfig, RollbackStrategy
    from rollback.rollback_triggers import RollbackTriggerConfig
    from rollback.failure_detector import FailureDetector, FailureCondition, FailureType
    from deployment.cloud_run.traffic_manager import TrafficManager
    from deployment.cloud_run.revision_manager import RevisionManager
    from monitoring.health_check import HealthCheckFramework
    from monitoring.performance_monitor import PerformanceMonitor
    from notification.notification_manager import NotificationManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockTrafficManager:
    """Mock traffic manager for demonstration."""
    
    def __init__(self):
        self.current_traffic = {"service-v2": 100}
        self.rollback_count = 0
    
    async def rollback_traffic(self, service_name: str, target_revision: str):
        """Mock traffic rollback."""
        logger.info(f"Rolling back traffic for {service_name} to {target_revision}")
        self.rollback_count += 1
        self.current_traffic = {target_revision: 100}
        
        from ..deployment.cloud_run.traffic_manager import TrafficUpdateResult
        return TrafficUpdateResult(
            success=True,
            service_name=service_name,
            traffic_splits=[],
            error_message=None
        )
    
    def get_current_traffic(self, service_name: str) -> Dict[str, int]:
        """Get current traffic distribution."""
        return self.current_traffic


class MockRevisionManager:
    """Mock revision manager for demonstration."""
    
    async def get_revision_history(self, service_name: str, limit: int = 10):
        """Mock revision history."""
        from ..deployment.cloud_run.revision_manager import RevisionInfo
        return [
            RevisionInfo(name="service-v2", status="READY", created_at=datetime.now()),
            RevisionInfo(name="service-v1", status="READY", created_at=datetime.now() - timedelta(hours=1)),
            RevisionInfo(name="service-v0", status="READY", created_at=datetime.now() - timedelta(hours=2))
        ]
    
    async def get_current_revision(self, service_name: str) -> str:
        """Get current revision."""
        return "service-v2"


class MockHealthCheckFramework:
    """Mock health check framework for demonstration."""
    
    def __init__(self):
        self.health_status = True
        self.check_count = 0
    
    async def run_health_checks(self):
        """Mock health checks."""
        self.check_count += 1
        
        # Simulate health check results
        from ..monitoring.health_check import HealthCheckResult
        return [
            HealthCheckResult(
                endpoint="/health",
                timestamp=datetime.now(),
                status_code=200 if self.health_status else 500,
                response_time_ms=100,
                success=self.health_status,
                error_message=None if self.health_status else "Service unhealthy"
            )
        ]
    
    async def get_health_history(self, start_time: datetime, end_time: datetime):
        """Mock health history."""
        return await self.run_health_checks()
    
    def set_health_status(self, healthy: bool):
        """Set health status for testing."""
        self.health_status = healthy


class MockPerformanceMonitor:
    """Mock performance monitor for demonstration."""
    
    def __init__(self):
        self.response_time = 150
        self.error_rate = 0.01
        self.cpu_usage = 50
        self.memory_usage = 60
    
    async def get_metrics_history(self, start_time: datetime, end_time: datetime):
        """Mock metrics history."""
        from ..monitoring.performance_monitor import PerformanceMetric
        return [
            PerformanceMetric(
                timestamp=datetime.now(),
                response_time_ms=self.response_time,
                request_count=1000,
                error_count=int(1000 * self.error_rate),
                resource_utilization={
                    "cpu_percent": self.cpu_usage,
                    "memory_percent": self.memory_usage
                }
            )
        ]
    
    async def get_current_metrics(self):
        """Mock current metrics."""
        metrics = await self.get_metrics_history(datetime.now(), datetime.now())
        return metrics[0] if metrics else None
    
    def set_performance_degradation(self, response_time: float, error_rate: float):
        """Set performance degradation for testing."""
        self.response_time = response_time
        self.error_rate = error_rate


class MockNotificationManager:
    """Mock notification manager for demonstration."""
    
    def __init__(self):
        self.notifications = []
    
    async def send_notification(self, channel: str, message: str, severity: str = "info"):
        """Mock notification sending."""
        notification = {
            "channel": channel,
            "message": message,
            "severity": severity,
            "timestamp": datetime.now()
        }
        self.notifications.append(notification)
        logger.info(f"Notification sent to {channel}: {message}")


async def demonstrate_rollback_system():
    """Demonstrate the integrated rollback system."""
    logger.info("Starting rollback system demonstration...")
    
    # Create mock components
    traffic_manager = MockTrafficManager()
    revision_manager = MockRevisionManager()
    health_check_manager = MockHealthCheckFramework()
    performance_monitor = MockPerformanceMonitor()
    notification_manager = MockNotificationManager()
    
    # Configure rollback system
    rollback_config = RollbackConfig(
        strategy=RollbackStrategy.IMMEDIATE,
        verification_timeout_seconds=30,
        health_check_timeout_seconds=15
    )
    
    auto_trigger_config = RollbackTriggerConfig(
        enabled=True,
        cooldown_minutes=1,  # Short cooldown for demo
        max_rollbacks_per_hour=5
    )
    
    manual_trigger_config = RollbackTriggerConfig(
        enabled=True,
        require_confirmation=False  # No confirmation for demo
    )
    
    manager_config = RollbackManagerConfig(
        service_name="demo-service",
        environment="demo",
        auto_rollback_enabled=True,
        manual_rollback_enabled=True,
        failure_detection_enabled=True,
        rollback_config=rollback_config,
        auto_trigger_config=auto_trigger_config,
        manual_trigger_config=manual_trigger_config,
        monitoring_interval_seconds=5  # Fast monitoring for demo
    )
    
    # Create rollback manager
    rollback_manager = RollbackManager(
        traffic_manager=traffic_manager,
        revision_manager=revision_manager,
        health_check_manager=health_check_manager,
        performance_monitor=performance_monitor,
        notification_manager=notification_manager,
        config=manager_config
    )
    
    try:
        # Start rollback system
        logger.info("Starting rollback management system...")
        await rollback_manager.start()
        
        # Display initial status
        status = rollback_manager.get_status()
        logger.info(f"Rollback manager status: {status['status']}")
        logger.info(f"Components active: {status['components']}")
        
        # Demonstrate manual rollback
        logger.info("\n=== Demonstrating Manual Rollback ===")
        rollback_id = await rollback_manager.trigger_manual_rollback(
            reason="Demonstration of manual rollback",
            operator_id="demo-operator",
            severity="warning"
        )
        
        if rollback_id:
            logger.info(f"Manual rollback triggered: {rollback_id}")
            
            # Wait for rollback to complete
            await asyncio.sleep(3)
            
            # Check rollback results
            recent_rollbacks = rollback_manager.get_recent_rollbacks(5)
            if recent_rollbacks:
                latest_rollback = recent_rollbacks[0]
                logger.info(f"Latest rollback status: {latest_rollback.status.value}")
                logger.info(f"Rollback success: {latest_rollback.success}")
        
        # Demonstrate automatic rollback trigger
        logger.info("\n=== Demonstrating Automatic Rollback ===")
        
        # Simulate health check failure
        logger.info("Simulating health check failures...")
        health_check_manager.set_health_status(False)
        
        # Add failure events to trigger automatic rollback
        from .failure_detector import FailureEvent
        failure_event = FailureEvent(
            failure_type=FailureType.HEALTH_CHECK_FAILURE,
            timestamp=datetime.now(),
            severity="critical",
            message="Simulated health check failure",
            metrics={"success_rate": 0.3},
            threshold_breached=0.8,
            actual_value=0.3
        )
        
        # Add multiple failures to trigger automatic rollback
        for i in range(3):
            rollback_manager.failure_detector.failure_history.append(failure_event)
        
        # Wait for automatic trigger to detect and process
        logger.info("Waiting for automatic rollback detection...")
        await asyncio.sleep(10)
        
        # Check if automatic rollback was triggered
        recent_rollbacks = rollback_manager.get_recent_rollbacks(10)
        auto_rollbacks = [r for r in recent_rollbacks if "auto_" in r.rollback_id]
        
        if auto_rollbacks:
            logger.info(f"Automatic rollback triggered: {auto_rollbacks[0].rollback_id}")
        else:
            logger.info("No automatic rollback triggered (may need more time or conditions)")
        
        # Demonstrate performance degradation detection
        logger.info("\n=== Demonstrating Performance Degradation Detection ===")
        
        # Simulate performance issues
        performance_monitor.set_performance_degradation(
            response_time=3000,  # 3 seconds
            error_rate=0.15      # 15% error rate
        )
        
        # Add performance failure events
        perf_failure = FailureEvent(
            failure_type=FailureType.PERFORMANCE_DEGRADATION,
            timestamp=datetime.now(),
            severity="critical",
            message="Simulated performance degradation",
            metrics={"avg_response_time": 3000},
            threshold_breached=2000,
            actual_value=3000
        )
        
        rollback_manager.failure_detector.failure_history.append(perf_failure)
        rollback_manager.failure_detector.failure_history.append(perf_failure)
        
        await asyncio.sleep(5)
        
        # Display system status
        logger.info("\n=== System Status ===")
        status = rollback_manager.get_status()
        logger.info(f"Total rollbacks: {status['statistics']['total_rollbacks']}")
        logger.info(f"Successful rollbacks: {status['statistics']['successful_rollbacks']}")
        logger.info(f"Failed rollbacks: {status['statistics']['failed_rollbacks']}")
        logger.info(f"Success rate: {status['statistics']['success_rate']:.1f}%")
        
        # Display recent failures
        recent_failures = rollback_manager.get_recent_failures(30)
        logger.info(f"Recent failures: {len(recent_failures)}")
        
        for failure in recent_failures[-3:]:  # Show last 3 failures
            logger.info(f"  - {failure.failure_type.value}: {failure.message}")
        
        # Display notifications
        logger.info(f"\nNotifications sent: {len(notification_manager.notifications)}")
        for notification in notification_manager.notifications[-3:]:  # Show last 3
            logger.info(f"  - {notification['channel']}: {notification['message'][:50]}...")
        
        # Demonstrate rollback history
        logger.info("\n=== Rollback History ===")
        all_rollbacks = rollback_manager.get_recent_rollbacks(20)
        for rollback in all_rollbacks:
            logger.info(
                f"  - {rollback.rollback_id}: {rollback.status.value} "
                f"({rollback.target.target_revision})"
            )
        
        logger.info("\n=== Demonstration Complete ===")
        logger.info("The rollback system has successfully demonstrated:")
        logger.info("1. Manual rollback triggering")
        logger.info("2. Automatic failure detection")
        logger.info("3. Performance monitoring")
        logger.info("4. Notification system")
        logger.info("5. Status monitoring and reporting")
    
    finally:
        # Stop rollback system
        logger.info("Stopping rollback management system...")
        await rollback_manager.stop()
        logger.info("Rollback system demonstration completed.")


async def demonstrate_rollback_strategies():
    """Demonstrate different rollback strategies."""
    logger.info("\n=== Demonstrating Rollback Strategies ===")
    
    # Create mock components
    traffic_manager = MockTrafficManager()
    revision_manager = MockRevisionManager()
    health_check_manager = MockHealthCheckFramework()
    performance_monitor = MockPerformanceMonitor()
    notification_manager = MockNotificationManager()
    
    strategies = [
        RollbackStrategy.IMMEDIATE,
        RollbackStrategy.GRADUAL,
        RollbackStrategy.BLUE_GREEN
    ]
    
    for strategy in strategies:
        logger.info(f"\nTesting {strategy.value} rollback strategy...")
        
        # Configure rollback with specific strategy
        rollback_config = RollbackConfig(
            strategy=strategy,
            gradual_rollback_steps=3,
            gradual_rollback_interval_seconds=1
        )
        
        manager_config = RollbackManagerConfig(
            service_name=f"demo-service-{strategy.value}",
            environment="demo",
            rollback_config=rollback_config,
            auto_rollback_enabled=False,  # Only manual for this demo
            manual_rollback_enabled=True,
            failure_detection_enabled=False
        )
        
        rollback_manager = RollbackManager(
            traffic_manager=traffic_manager,
            revision_manager=revision_manager,
            health_check_manager=health_check_manager,
            performance_monitor=performance_monitor,
            notification_manager=notification_manager,
            config=manager_config
        )
        
        try:
            await rollback_manager.start()
            
            # Trigger rollback with this strategy
            rollback_id = await rollback_manager.trigger_manual_rollback(
                reason=f"Testing {strategy.value} strategy",
                operator_id="demo-operator"
            )
            
            if rollback_id:
                logger.info(f"Rollback {rollback_id} triggered with {strategy.value} strategy")
                
                # Wait for completion
                await asyncio.sleep(5)
                
                # Check results
                recent_rollbacks = rollback_manager.get_recent_rollbacks(1)
                if recent_rollbacks:
                    result = recent_rollbacks[0]
                    logger.info(f"Strategy {strategy.value} result: {result.status.value}")
        
        finally:
            await rollback_manager.stop()


if __name__ == "__main__":
    async def main():
        """Main demonstration function."""
        try:
            await demonstrate_rollback_system()
            await demonstrate_rollback_strategies()
        except KeyboardInterrupt:
            logger.info("Demonstration interrupted by user")
        except Exception as e:
            logger.error(f"Demonstration error: {e}")
            raise
    
    # Run demonstration
    asyncio.run(main())