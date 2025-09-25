"""
Tests for rollback execution engine.

Tests the core rollback execution logic, traffic rollback procedures,
and rollback verification systems.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch, MagicMock

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from rollback.rollback_executor import (
    RollbackExecutor, RollbackConfig, RollbackTarget, RollbackResult,
    RollbackStatus, RollbackStrategy
)
from rollback.rollback_triggers import RollbackRequest, RollbackReason
from deployment.cloud_run.traffic_manager import TrafficUpdateResult


class TestRollbackExecutor:
    """Test cases for RollbackExecutor."""
    
    @pytest.fixture
    def mock_traffic_manager(self):
        """Mock traffic manager."""
        mock = Mock()
        mock.rollback_traffic = Mock(return_value=TrafficUpdateResult(
            success=True,
            current_traffic={"test-revision": 100}
        ))
        mock.get_current_traffic = Mock(return_value={"test-revision": 100})
        mock.update_traffic = Mock(return_value=TrafficUpdateResult(
            success=True,
            current_traffic={"test-revision": 50, "current-revision": 50}
        ))
        mock.execute_blue_green_deployment = Mock(return_value=TrafficUpdateResult(
            success=True,
            current_traffic={"test-revision": 100}
        ))
        return mock
    
    @pytest.fixture
    def mock_revision_manager(self):
        """Mock revision manager."""
        return Mock()
    
    @pytest.fixture
    def mock_health_check_manager(self):
        """Mock health check manager."""
        mock = Mock()
        mock.run_health_checks = AsyncMock(return_value=[
            Mock(success=True, endpoint="/health"),
            Mock(success=True, endpoint="/api/health")
        ])
        mock.get_health_history = AsyncMock(return_value=[
            Mock(success=True),
            Mock(success=True)
        ])
        return mock
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock performance monitor."""
        mock = Mock()
        mock.get_metrics_history = AsyncMock(return_value=[
            Mock(response_time_ms=100, request_count=100, error_count=1),
            Mock(response_time_ms=150, request_count=100, error_count=2)
        ])
        return mock
    
    @pytest.fixture
    def mock_notification_manager(self):
        """Mock notification manager."""
        mock = Mock()
        mock.send_notification = AsyncMock()
        return mock
    
    @pytest.fixture
    def rollback_executor(self, mock_traffic_manager, mock_revision_manager,
                         mock_health_check_manager, mock_performance_monitor,
                         mock_notification_manager):
        """Create rollback executor with mocked dependencies."""
        config = RollbackConfig(
            strategy=RollbackStrategy.IMMEDIATE,
            verification_timeout_seconds=60,
            health_check_timeout_seconds=30
        )
        
        return RollbackExecutor(
            traffic_manager=mock_traffic_manager,
            revision_manager=mock_revision_manager,
            health_check_manager=mock_health_check_manager,
            performance_monitor=mock_performance_monitor,
            notification_manager=mock_notification_manager,
            config=config
        )
    
    @pytest.fixture
    def sample_rollback_request(self):
        """Create sample rollback request."""
        return RollbackRequest(
            trigger_id="test_trigger_123",
            reason=RollbackReason.AUTOMATIC_HEALTH_FAILURE,
            timestamp=datetime.now(),
            severity="critical",
            message="Health check failure detected",
            failure_events=[],
            metadata={"test": "data"}
        )
    
    @pytest.fixture
    def sample_rollback_target(self):
        """Create sample rollback target."""
        return RollbackTarget(
            service_name="test-service",
            target_revision="stable-revision-123",
            current_revision="current-revision-456",
            environment="production"
        )
    
    @pytest.mark.asyncio
    async def test_execute_immediate_rollback_success(self, rollback_executor,
                                                    sample_rollback_request,
                                                    sample_rollback_target):
        """Test successful immediate rollback execution."""
        result = await rollback_executor.execute_rollback(
            sample_rollback_request, sample_rollback_target
        )
        
        assert result.success is True
        assert result.status == RollbackStatus.COMPLETED
        assert result.target == sample_rollback_target
        assert result.end_time is not None
        assert len(result.traffic_results) == 1
        assert result.traffic_results[0].success is True
        
        # Verify traffic manager was called
        rollback_executor.traffic_manager.rollback_traffic.assert_called_once_with(
            service_name="test-service",
            target_revision="stable-revision-123"
        )
    
    @pytest.mark.asyncio
    async def test_execute_rollback_traffic_failure(self, rollback_executor,
                                                  sample_rollback_request,
                                                  sample_rollback_target):
        """Test rollback execution with traffic failure."""
        # Mock traffic failure
        rollback_executor.traffic_manager.rollback_traffic.return_value = TrafficUpdateResult(
            success=False,
            current_traffic={},
            error_message="Traffic update failed"
        )
        
        result = await rollback_executor.execute_rollback(
            sample_rollback_request, sample_rollback_target
        )
        
        assert result.success is False
        assert result.status == RollbackStatus.FAILED
        assert "Traffic rollback failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_execute_gradual_rollback_success(self, rollback_executor,
                                                  sample_rollback_request,
                                                  sample_rollback_target):
        """Test successful gradual rollback execution."""
        # Configure for gradual rollback
        rollback_executor.config.strategy = RollbackStrategy.GRADUAL
        rollback_executor.config.gradual_rollback_steps = 2
        rollback_executor.config.gradual_rollback_interval_seconds = 1
        
        result = await rollback_executor.execute_rollback(
            sample_rollback_request, sample_rollback_target
        )
        
        assert result.success is True
        assert result.status == RollbackStatus.COMPLETED
        assert len(result.traffic_results) == 2  # Two steps
        
        # Verify traffic manager was called for each step
        assert rollback_executor.traffic_manager.update_traffic.call_count == 2
    
    @pytest.mark.asyncio
    async def test_execute_blue_green_rollback_success(self, rollback_executor,
                                                     sample_rollback_request,
                                                     sample_rollback_target):
        """Test successful blue-green rollback execution."""
        # Configure for blue-green rollback
        rollback_executor.config.strategy = RollbackStrategy.BLUE_GREEN
        
        result = await rollback_executor.execute_rollback(
            sample_rollback_request, sample_rollback_target
        )
        
        assert result.success is True
        assert result.status == RollbackStatus.COMPLETED
        
        # Verify blue-green deployment was called
        rollback_executor.traffic_manager.execute_blue_green_deployment.assert_called_once_with(
            service_name="test-service",
            blue_revision="stable-revision-123",
            green_revision="current-revision-456",
            switch_to_green=False
        )
    
    @pytest.mark.asyncio
    async def test_rollback_verification_success(self, rollback_executor,
                                               sample_rollback_request,
                                               sample_rollback_target):
        """Test successful rollback verification."""
        result = await rollback_executor.execute_rollback(
            sample_rollback_request, sample_rollback_target
        )
        
        assert result.success is True
        assert result.verification_results is not None
        assert result.verification_results["health_check"] is True
        assert result.verification_results["performance_check"] is True
        assert result.verification_results["traffic_verification"] is True
    
    @pytest.mark.asyncio
    async def test_rollback_verification_failure(self, rollback_executor,
                                                sample_rollback_request,
                                                sample_rollback_target):
        """Test rollback verification failure."""
        # Mock health check failure
        rollback_executor.health_check_manager.run_health_checks.return_value = [
            Mock(success=False, endpoint="/health")
        ]
        
        result = await rollback_executor.execute_rollback(
            sample_rollback_request, sample_rollback_target
        )
        
        assert result.success is False
        assert result.status == RollbackStatus.FAILED
        assert "verification failed" in result.error_message
    
    @pytest.mark.asyncio
    async def test_rollback_with_notifications(self, rollback_executor,
                                             sample_rollback_request,
                                             sample_rollback_target):
        """Test rollback execution with notifications."""
        result = await rollback_executor.execute_rollback(
            sample_rollback_request, sample_rollback_target
        )
        
        assert result.success is True
        
        # Verify notifications were sent
        assert rollback_executor.notification_manager.send_notification.call_count >= 2
        
        # Check notification calls
        calls = rollback_executor.notification_manager.send_notification.call_args_list
        start_call = calls[0]
        complete_call = calls[-1]
        
        assert "started" in start_call[1]["message"]
        assert "completed" in complete_call[1]["message"]
    
    @pytest.mark.asyncio
    async def test_rollback_callbacks(self, rollback_executor,
                                    sample_rollback_request,
                                    sample_rollback_target):
        """Test rollback execution callbacks."""
        start_callback = AsyncMock()
        progress_callback = AsyncMock()
        complete_callback = AsyncMock()
        
        rollback_executor.add_callback('start', start_callback)
        rollback_executor.add_callback('progress', progress_callback)
        rollback_executor.add_callback('complete', complete_callback)
        
        result = await rollback_executor.execute_rollback(
            sample_rollback_request, sample_rollback_target
        )
        
        assert result.success is True
        
        # Verify callbacks were called
        start_callback.assert_called_once()
        progress_callback.assert_called_once()
        complete_callback.assert_called_once()
    
    def test_get_rollback_status(self, rollback_executor):
        """Test getting rollback status."""
        # Add a rollback to history
        result = RollbackResult(
            success=True,
            rollback_id="test_rollback_123",
            status=RollbackStatus.COMPLETED,
            target=RollbackTarget("test-service", "test-revision"),
            start_time=datetime.now()
        )
        rollback_executor.rollback_history.append(result)
        
        # Test getting status
        status = rollback_executor.get_rollback_status("test_rollback_123")
        assert status is not None
        assert status.rollback_id == "test_rollback_123"
        
        # Test non-existent rollback
        status = rollback_executor.get_rollback_status("non_existent")
        assert status is None
    
    def test_get_active_rollbacks(self, rollback_executor):
        """Test getting active rollbacks."""
        # Add active rollback
        result = RollbackResult(
            success=False,
            rollback_id="active_rollback_123",
            status=RollbackStatus.IN_PROGRESS,
            target=RollbackTarget("test-service", "test-revision"),
            start_time=datetime.now()
        )
        rollback_executor.active_rollbacks["active_rollback_123"] = result
        
        active_rollbacks = rollback_executor.get_active_rollbacks()
        assert len(active_rollbacks) == 1
        assert active_rollbacks[0].rollback_id == "active_rollback_123"
    
    def test_get_rollback_history(self, rollback_executor):
        """Test getting rollback history."""
        # Add multiple rollbacks to history
        for i in range(5):
            result = RollbackResult(
                success=True,
                rollback_id=f"rollback_{i}",
                status=RollbackStatus.COMPLETED,
                target=RollbackTarget("test-service", f"revision-{i}"),
                start_time=datetime.now()
            )
            rollback_executor.rollback_history.append(result)
        
        # Test getting all history
        history = rollback_executor.get_rollback_history()
        assert len(history) == 5
        
        # Test getting limited history
        limited_history = rollback_executor.get_rollback_history(limit=3)
        assert len(limited_history) == 3
        assert limited_history[-1].rollback_id == "rollback_4"  # Most recent
    
    @pytest.mark.asyncio
    async def test_cancel_rollback(self, rollback_executor):
        """Test cancelling an active rollback."""
        # Add active rollback
        result = RollbackResult(
            success=False,
            rollback_id="cancellable_rollback",
            status=RollbackStatus.IN_PROGRESS,
            target=RollbackTarget("test-service", "test-revision"),
            start_time=datetime.now()
        )
        rollback_executor.active_rollbacks["cancellable_rollback"] = result
        
        # Cancel rollback
        success = await rollback_executor.cancel_rollback("cancellable_rollback")
        assert success is True
        
        # Verify rollback was moved to history and marked as cancelled
        assert "cancellable_rollback" not in rollback_executor.active_rollbacks
        assert len(rollback_executor.rollback_history) == 1
        assert rollback_executor.rollback_history[0].status == RollbackStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cancel_non_existent_rollback(self, rollback_executor):
        """Test cancelling a non-existent rollback."""
        success = await rollback_executor.cancel_rollback("non_existent")
        assert success is False


class TestRollbackExecutorIntegration:
    """Integration tests for rollback executor."""
    
    @pytest.mark.asyncio
    async def test_full_rollback_workflow(self):
        """Test complete rollback workflow with realistic mocks."""
        # Create more realistic mocks
        traffic_manager = Mock()
        traffic_manager.rollback_traffic.return_value = TrafficUpdateResult(
            success=True,
            current_traffic={"stable-revision": 100}
        )
        traffic_manager.get_current_traffic.return_value = {"stable-revision": 100}
        
        revision_manager = Mock()
        
        health_check_manager = Mock()
        health_check_manager.run_health_checks = AsyncMock(return_value=[
            Mock(success=True, endpoint="/health", response_time_ms=100)
        ])
        
        performance_monitor = Mock()
        performance_monitor.get_metrics_history = AsyncMock(return_value=[
            Mock(response_time_ms=120, request_count=1000, error_count=5)
        ])
        
        notification_manager = Mock()
        notification_manager.send_notification = AsyncMock()
        
        # Create executor
        config = RollbackConfig(
            strategy=RollbackStrategy.IMMEDIATE,
            verification_timeout_seconds=30,
            notification_enabled=True
        )
        
        executor = RollbackExecutor(
            traffic_manager=traffic_manager,
            revision_manager=revision_manager,
            health_check_manager=health_check_manager,
            performance_monitor=performance_monitor,
            notification_manager=notification_manager,
            config=config
        )
        
        # Create rollback request and target
        request = RollbackRequest(
            trigger_id="integration_test",
            reason=RollbackReason.AUTOMATIC_HEALTH_FAILURE,
            timestamp=datetime.now(),
            severity="critical",
            message="Integration test rollback",
            failure_events=[],
            metadata={}
        )
        
        target = RollbackTarget(
            service_name="integration-test-service",
            target_revision="stable-revision",
            current_revision="failed-revision",
            environment="production"
        )
        
        # Execute rollback
        result = await executor.execute_rollback(request, target)
        
        # Verify successful execution
        assert result.success is True
        assert result.status == RollbackStatus.COMPLETED
        assert result.rollback_id.startswith("rollback_integration_test")
        
        # Verify all components were called
        traffic_manager.rollback_traffic.assert_called_once()
        health_check_manager.run_health_checks.assert_called()
        performance_monitor.get_metrics_history.assert_called()
        notification_manager.send_notification.assert_called()
        
        # Verify rollback is in history
        history = executor.get_rollback_history()
        assert len(history) == 1
        assert history[0].rollback_id == result.rollback_id


if __name__ == "__main__":
    pytest.main([__file__])