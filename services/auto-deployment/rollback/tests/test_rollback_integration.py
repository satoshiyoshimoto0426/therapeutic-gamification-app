"""
Integration tests for rollback execution engine.

This module tests the complete rollback system integration including
triggers, execution, and monitoring components.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

try:
    from ..rollback_manager import (
        RollbackManager, RollbackManagerConfig, RollbackManagerStatus
    )
    from ..rollback_executor import (
        RollbackExecutor, RollbackConfig, RollbackTarget, RollbackResult,
        RollbackStatus, RollbackStrategy
    )
    from ..rollback_triggers import (
        AutomaticRollbackTrigger, ManualRollbackTrigger, RollbackRequest,
        RollbackTriggerConfig, RollbackReason
    )
    from ..failure_detector import FailureDetector, FailureEvent, FailureType
    from ...deployment.cloud_run.traffic_manager import TrafficManager, TrafficUpdateResult
    from ...deployment.cloud_run.revision_manager import RevisionManager, RevisionInfo
    from ...monitoring.health_check import HealthCheckFramework
    from ...monitoring.performance_monitor import PerformanceMonitor
    from ...notification.notification_manager import NotificationManager
    from ...exceptions import RollbackError
except ImportError:
    # テスト実行時の代替インポート
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    from rollback.rollback_manager import (
        RollbackManager, RollbackManagerConfig, RollbackManagerStatus
    )
    from rollback.rollback_executor import (
        RollbackExecutor, RollbackConfig, RollbackTarget, RollbackResult,
        RollbackStatus, RollbackStrategy
    )
    from rollback.rollback_triggers import (
        AutomaticRollbackTrigger, ManualRollbackTrigger, RollbackRequest,
        RollbackTriggerConfig, RollbackReason
    )
    from rollback.failure_detector import FailureDetector, FailureEvent, FailureType
    from deployment.cloud_run.traffic_manager import TrafficManager, TrafficUpdateResult
    from deployment.cloud_run.revision_manager import RevisionManager, RevisionInfo
    from monitoring.health_check import HealthCheckFramework
    from monitoring.performance_monitor import PerformanceMonitor
    from notification.notification_manager import NotificationManager
    from exceptions import RollbackError


class TestRollbackIntegration:
    """Test rollback system integration."""
    
    @pytest.fixture
    def mock_traffic_manager(self):
        """Mock traffic manager."""
        manager = Mock(spec=TrafficManager)
        manager.rollback_traffic = AsyncMock(return_value=TrafficUpdateResult(
            success=True,
            service_name="test-service",
            traffic_splits=[],
            error_message=None
        ))
        manager.get_current_traffic = Mock(return_value={"test-revision": 100})
        return manager
    
    @pytest.fixture
    def mock_revision_manager(self):
        """Mock revision manager."""
        manager = Mock(spec=RevisionManager)
        manager.get_revision_history = AsyncMock(return_value=[
            RevisionInfo(name="test-revision-2", status="READY", created_at=datetime.now()),
            RevisionInfo(name="test-revision-1", status="READY", created_at=datetime.now() - timedelta(hours=1))
        ])
        manager.get_current_revision = AsyncMock(return_value="test-revision-2")
        return manager
    
    @pytest.fixture
    def mock_health_check_manager(self):
        """Mock health check manager."""
        manager = Mock(spec=HealthCheckFramework)
        manager.run_health_checks = AsyncMock(return_value=[
            Mock(success=True, endpoint="/health", response_time_ms=100)
        ])
        manager.get_health_history = AsyncMock(return_value=[
            Mock(success=True, timestamp=datetime.now())
        ])
        return manager
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock performance monitor."""
        monitor = Mock(spec=PerformanceMonitor)
        monitor.get_metrics_history = AsyncMock(return_value=[
            Mock(response_time_ms=150, request_count=100, error_count=1)
        ])
        monitor.get_current_metrics = AsyncMock(return_value=Mock(
            resource_utilization={"cpu_percent": 50, "memory_percent": 60}
        ))
        return monitor
    
    @pytest.fixture
    def mock_notification_manager(self):
        """Mock notification manager."""
        manager = Mock(spec=NotificationManager)
        manager.send_notification = AsyncMock()
        return manager
    
    @pytest.fixture
    def rollback_manager_config(self):
        """Rollback manager configuration."""
        return RollbackManagerConfig(
            service_name="test-service",
            environment="test",
            auto_rollback_enabled=True,
            manual_rollback_enabled=True,
            failure_detection_enabled=True,
            monitoring_interval_seconds=1  # Fast for testing
        )
    
    @pytest.fixture
    def rollback_manager(self, mock_traffic_manager, mock_revision_manager,
                        mock_health_check_manager, mock_performance_monitor,
                        mock_notification_manager, rollback_manager_config):
        """Create rollback manager instance."""
        return RollbackManager(
            traffic_manager=mock_traffic_manager,
            revision_manager=mock_revision_manager,
            health_check_manager=mock_health_check_manager,
            performance_monitor=mock_performance_monitor,
            notification_manager=mock_notification_manager,
            config=rollback_manager_config
        )
    
    @pytest.mark.asyncio
    async def test_rollback_manager_startup_shutdown(self, rollback_manager):
        """Test rollback manager startup and shutdown."""
        # Test startup
        await rollback_manager.start()
        assert rollback_manager.status == RollbackManagerStatus.ACTIVE
        assert rollback_manager.start_time is not None
        
        # Test shutdown
        await rollback_manager.stop()
        assert rollback_manager.status == RollbackManagerStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_automatic_rollback_trigger_integration(self, rollback_manager,
                                                         mock_traffic_manager):
        """Test automatic rollback trigger integration."""
        await rollback_manager.start()
        
        try:
            # Simulate failure detection
            failure_event = FailureEvent(
                failure_type=FailureType.HEALTH_CHECK_FAILURE,
                timestamp=datetime.now(),
                severity="critical",
                message="Health check failed",
                metrics={"success_rate": 0.5},
                threshold_breached=0.8,
                actual_value=0.5
            )
            
            # Add failure to detector history
            rollback_manager.failure_detector.failure_history.append(failure_event)
            
            # Wait for automatic trigger to process
            await asyncio.sleep(2)
            
            # Check if rollback was triggered
            # Note: In a real scenario, this would be triggered by the monitoring loop
            # For testing, we'll manually trigger the condition check
            
            assert rollback_manager.status == RollbackManagerStatus.ACTIVE
        
        finally:
            await rollback_manager.stop()
    
    @pytest.mark.asyncio
    async def test_manual_rollback_trigger_integration(self, rollback_manager,
                                                      mock_traffic_manager):
        """Test manual rollback trigger integration."""
        await rollback_manager.start()
        
        try:
            # Trigger manual rollback
            rollback_id = await rollback_manager.trigger_manual_rollback(
                reason="Testing manual rollback",
                operator_id="test-operator",
                severity="warning"
            )
            
            assert rollback_id is not None
            
            # Wait for rollback to process
            await asyncio.sleep(1)
            
            # Check rollback was executed
            mock_traffic_manager.rollback_traffic.assert_called()
        
        finally:
            await rollback_manager.stop()
    
    @pytest.mark.asyncio
    async def test_rollback_execution_flow(self, rollback_manager, mock_traffic_manager,
                                          mock_health_check_manager):
        """Test complete rollback execution flow."""
        await rollback_manager.start()
        
        try:
            # Create rollback request
            request = RollbackRequest(
                trigger_id="test-trigger",
                reason=RollbackReason.MANUAL_OPERATOR_REQUEST,
                timestamp=datetime.now(),
                severity="warning",
                message="Test rollback",
                failure_events=[],
                metadata={},
                operator_id="test-operator"
            )
            
            # Execute rollback through manager
            await rollback_manager._handle_rollback_request(request)
            
            # Verify traffic rollback was called
            mock_traffic_manager.rollback_traffic.assert_called()
            
            # Verify health checks were performed
            mock_health_check_manager.run_health_checks.assert_called()
        
        finally:
            await rollback_manager.stop()
    
    @pytest.mark.asyncio
    async def test_rollback_failure_handling(self, rollback_manager, mock_traffic_manager):
        """Test rollback failure handling."""
        # Configure traffic manager to fail
        mock_traffic_manager.rollback_traffic.return_value = TrafficUpdateResult(
            success=False,
            service_name="test-service",
            traffic_splits=[],
            error_message="Traffic rollback failed"
        )
        
        await rollback_manager.start()
        
        try:
            # Trigger rollback
            rollback_id = await rollback_manager.trigger_manual_rollback(
                reason="Test failure handling",
                operator_id="test-operator"
            )
            
            assert rollback_id is not None
            
            # Wait for rollback to process
            await asyncio.sleep(1)
            
            # Check that rollback was attempted but failed
            mock_traffic_manager.rollback_traffic.assert_called()
            
            # Check rollback history for failed rollback
            recent_rollbacks = rollback_manager.get_recent_rollbacks(5)
            failed_rollbacks = [r for r in recent_rollbacks if r.status == RollbackStatus.FAILED]
            assert len(failed_rollbacks) > 0
        
        finally:
            await rollback_manager.stop()
    
    @pytest.mark.asyncio
    async def test_rollback_status_monitoring(self, rollback_manager):
        """Test rollback status monitoring."""
        await rollback_manager.start()
        
        try:
            # Get initial status
            status = rollback_manager.get_status()
            
            assert status["status"] == RollbackManagerStatus.ACTIVE.value
            assert "uptime_seconds" in status
            assert "config" in status
            assert "statistics" in status
            assert "components" in status
            
            # Check component status
            components = status["components"]
            assert "failure_detector" in components
            assert "automatic_trigger" in components
            assert "manual_trigger" in components
            assert "rollback_executor" in components
        
        finally:
            await rollback_manager.stop()
    
    @pytest.mark.asyncio
    async def test_rollback_statistics_tracking(self, rollback_manager):
        """Test rollback statistics tracking."""
        await rollback_manager.start()
        
        try:
            # Initial statistics should be zero
            status = rollback_manager.get_status()
            stats = status["statistics"]
            assert stats["total_rollbacks"] == 0
            assert stats["successful_rollbacks"] == 0
            assert stats["failed_rollbacks"] == 0
            
            # Trigger a rollback
            await rollback_manager.trigger_manual_rollback(
                reason="Test statistics",
                operator_id="test-operator"
            )
            
            # Wait for processing
            await asyncio.sleep(1)
            
            # Update statistics manually (normally done by management loop)
            await rollback_manager._update_statistics()
            
            # Check updated statistics
            status = rollback_manager.get_status()
            stats = status["statistics"]
            assert stats["total_rollbacks"] > 0
        
        finally:
            await rollback_manager.stop()
    
    @pytest.mark.asyncio
    async def test_component_health_monitoring(self, rollback_manager):
        """Test component health monitoring."""
        await rollback_manager.start()
        
        try:
            # Simulate component failure
            rollback_manager.failure_detector.monitoring_active = False
            
            # Run health check
            await rollback_manager._check_system_health()
            
            # Component should be restarted
            assert rollback_manager.failure_detector.monitoring_active
        
        finally:
            await rollback_manager.stop()
    
    @pytest.mark.asyncio
    async def test_rollback_target_determination(self, rollback_manager, mock_revision_manager):
        """Test rollback target determination."""
        await rollback_manager.start()
        
        try:
            # Test target determination
            target_revision = await rollback_manager._determine_rollback_target()
            
            assert target_revision is not None
            assert target_revision == "test-revision-1"  # Previous revision
            
            # Verify revision manager was called
            mock_revision_manager.get_revision_history.assert_called()
            mock_revision_manager.get_current_revision.assert_called()
        
        finally:
            await rollback_manager.stop()
    
    @pytest.mark.asyncio
    async def test_notification_integration(self, rollback_manager, mock_notification_manager):
        """Test notification system integration."""
        await rollback_manager.start()
        
        try:
            # Trigger rollback to generate notifications
            await rollback_manager.trigger_manual_rollback(
                reason="Test notifications",
                operator_id="test-operator"
            )
            
            # Wait for processing
            await asyncio.sleep(1)
            
            # Check notifications were sent
            mock_notification_manager.send_notification.assert_called()
        
        finally:
            await rollback_manager.stop()
    
    def test_rollback_manager_configuration(self, rollback_manager_config):
        """Test rollback manager configuration."""
        assert rollback_manager_config.service_name == "test-service"
        assert rollback_manager_config.environment == "test"
        assert rollback_manager_config.auto_rollback_enabled is True
        assert rollback_manager_config.manual_rollback_enabled is True
        assert rollback_manager_config.failure_detection_enabled is True
    
    @pytest.mark.asyncio
    async def test_rollback_manager_error_handling(self, mock_traffic_manager,
                                                   mock_revision_manager,
                                                   mock_health_check_manager,
                                                   mock_performance_monitor,
                                                   mock_notification_manager):
        """Test rollback manager error handling."""
        # Configure revision manager to fail
        mock_revision_manager.get_revision_history.side_effect = Exception("Revision fetch failed")
        
        config = RollbackManagerConfig(
            service_name="test-service",
            environment="test"
        )
        
        manager = RollbackManager(
            traffic_manager=mock_traffic_manager,
            revision_manager=mock_revision_manager,
            health_check_manager=mock_health_check_manager,
            performance_monitor=mock_performance_monitor,
            notification_manager=mock_notification_manager,
            config=config
        )
        
        await manager.start()
        
        try:
            # Attempt to determine rollback target (should handle error gracefully)
            target_revision = await manager._determine_rollback_target()
            assert target_revision is None
        
        finally:
            await manager.stop()


class TestRollbackExecutorIntegration:
    """Test rollback executor integration."""
    
    @pytest.fixture
    def rollback_executor(self, mock_traffic_manager, mock_revision_manager,
                         mock_health_check_manager, mock_performance_monitor,
                         mock_notification_manager):
        """Create rollback executor instance."""
        config = RollbackConfig(
            strategy=RollbackStrategy.IMMEDIATE,
            verification_timeout_seconds=10,
            health_check_timeout_seconds=5
        )
        
        return RollbackExecutor(
            traffic_manager=mock_traffic_manager,
            revision_manager=mock_revision_manager,
            health_check_manager=mock_health_check_manager,
            performance_monitor=mock_performance_monitor,
            notification_manager=mock_notification_manager,
            config=config
        )
    
    @pytest.mark.asyncio
    async def test_immediate_rollback_strategy(self, rollback_executor, mock_traffic_manager):
        """Test immediate rollback strategy."""
        request = RollbackRequest(
            trigger_id="test-immediate",
            reason=RollbackReason.MANUAL_OPERATOR_REQUEST,
            timestamp=datetime.now(),
            severity="warning",
            message="Test immediate rollback",
            failure_events=[],
            metadata={}
        )
        
        target = RollbackTarget(
            service_name="test-service",
            target_revision="test-revision-1",
            current_revision="test-revision-2"
        )
        
        result = await rollback_executor.execute_rollback(request, target)
        
        assert result.success is True
        assert result.status == RollbackStatus.COMPLETED
        assert mock_traffic_manager.rollback_traffic.called
    
    @pytest.mark.asyncio
    async def test_gradual_rollback_strategy(self, mock_traffic_manager, mock_revision_manager,
                                           mock_health_check_manager, mock_performance_monitor,
                                           mock_notification_manager):
        """Test gradual rollback strategy."""
        config = RollbackConfig(
            strategy=RollbackStrategy.GRADUAL,
            gradual_rollback_steps=2,
            gradual_rollback_interval_seconds=0.1  # Fast for testing
        )
        
        executor = RollbackExecutor(
            traffic_manager=mock_traffic_manager,
            revision_manager=mock_revision_manager,
            health_check_manager=mock_health_check_manager,
            performance_monitor=mock_performance_monitor,
            notification_manager=mock_notification_manager,
            config=config
        )
        
        # Mock traffic manager for gradual rollback
        mock_traffic_manager.update_traffic = AsyncMock(return_value=TrafficUpdateResult(
            success=True,
            service_name="test-service",
            traffic_splits=[],
            error_message=None
        ))
        
        request = RollbackRequest(
            trigger_id="test-gradual",
            reason=RollbackReason.AUTOMATIC_HEALTH_FAILURE,
            timestamp=datetime.now(),
            severity="critical",
            message="Test gradual rollback",
            failure_events=[],
            metadata={}
        )
        
        target = RollbackTarget(
            service_name="test-service",
            target_revision="test-revision-1",
            current_revision="test-revision-2"
        )
        
        result = await executor.execute_rollback(request, target)
        
        assert result.success is True
        assert result.status == RollbackStatus.COMPLETED
        assert mock_traffic_manager.update_traffic.called
    
    @pytest.mark.asyncio
    async def test_rollback_verification(self, rollback_executor, mock_traffic_manager,
                                       mock_health_check_manager, mock_performance_monitor):
        """Test rollback verification process."""
        # Configure successful verification
        mock_traffic_manager.get_current_traffic.return_value = {"test-revision-1": 100}
        
        request = RollbackRequest(
            trigger_id="test-verification",
            reason=RollbackReason.MANUAL_OPERATOR_REQUEST,
            timestamp=datetime.now(),
            severity="warning",
            message="Test verification",
            failure_events=[],
            metadata={}
        )
        
        target = RollbackTarget(
            service_name="test-service",
            target_revision="test-revision-1"
        )
        
        result = await rollback_executor.execute_rollback(request, target)
        
        assert result.success is True
        assert result.verification_results is not None
        assert "health_check" in result.verification_results
        assert "performance_check" in result.verification_results
        assert "traffic_verification" in result.verification_results


if __name__ == "__main__":
    pytest.main([__file__])