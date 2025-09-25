"""
Tests for failure detection algorithms.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch

import sys
import os

# Add the services directory to Python path
services_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
if services_path not in sys.path:
    sys.path.insert(0, services_path)

# Add the auto-deployment directory to Python path
auto_deployment_path = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.append(auto_deployment_path)

from rollback.failure_detector import (
    FailureDetector, FailureType, FailureCondition, FailureEvent
)
from monitoring.health_check import HealthCheckResult
from monitoring.performance_monitor import MetricValue
from exceptions import RollbackError


class TestFailureDetector:
    """Test failure detection algorithms."""
    
    @pytest.fixture
    def mock_health_manager(self):
        """Mock health check manager."""
        manager = Mock()
        manager.get_health_history = AsyncMock()
        return manager
    
    @pytest.fixture
    def mock_performance_monitor(self):
        """Mock performance monitor."""
        monitor = Mock()
        monitor.get_metrics_history = AsyncMock()
        monitor.get_current_metrics = AsyncMock()
        return monitor
    
    @pytest.fixture
    def failure_detector(self, mock_health_manager, mock_performance_monitor):
        """Create failure detector instance."""
        return FailureDetector(
            health_check_manager=mock_health_manager,
            performance_monitor=mock_performance_monitor
        )
    
    def test_initialization(self, failure_detector):
        """Test failure detector initialization."""
        assert failure_detector.monitoring_active is False
        assert len(failure_detector.failure_conditions) == 4
        assert failure_detector.failure_history == []
    
    def test_default_conditions(self, failure_detector):
        """Test default failure conditions."""
        conditions = failure_detector.failure_conditions
        
        # Check that all expected failure types are present
        failure_types = {c.failure_type for c in conditions}
        expected_types = {
            FailureType.HEALTH_CHECK_FAILURE,
            FailureType.PERFORMANCE_DEGRADATION,
            FailureType.ERROR_RATE_SPIKE,
            FailureType.RESOURCE_EXHAUSTION
        }
        assert failure_types == expected_types
        
        # Check that all conditions are enabled by default
        assert all(c.enabled for c in conditions)
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, failure_detector):
        """Test starting and stopping monitoring."""
        # Start monitoring
        await failure_detector.start_monitoring()
        assert failure_detector.monitoring_active is True
        assert failure_detector._monitoring_task is not None
        
        # Stop monitoring
        await failure_detector.stop_monitoring()
        assert failure_detector.monitoring_active is False
    
    @pytest.mark.asyncio
    async def test_health_check_failure_detection(self, failure_detector, mock_health_manager):
        """Test health check failure detection."""
        # Mock health check results with low success rate
        health_results = [
            HealthCheckResult(endpoint="/health", timestamp=datetime.now(), 
                            status_code=200, response_time_ms=100, success=True),
            HealthCheckResult(endpoint="/health", timestamp=datetime.now(), 
                            status_code=500, response_time_ms=5000, success=False),
            HealthCheckResult(endpoint="/health", timestamp=datetime.now(), 
                            status_code=500, response_time_ms=5000, success=False),
            HealthCheckResult(endpoint="/health", timestamp=datetime.now(), 
                            status_code=500, response_time_ms=5000, success=False),
        ]
        mock_health_manager.get_health_history.return_value = health_results
        
        # Find health check condition
        health_condition = next(
            c for c in failure_detector.failure_conditions 
            if c.failure_type == FailureType.HEALTH_CHECK_FAILURE
        )
        
        # Check condition
        failure_event = await failure_detector._check_condition(health_condition)
        
        assert failure_event is not None
        assert failure_event.failure_type == FailureType.HEALTH_CHECK_FAILURE
        assert failure_event.severity in ["warning", "critical"]
        assert failure_event.actual_value < health_condition.threshold
    
    @pytest.mark.asyncio
    async def test_performance_degradation_detection(self, failure_detector, mock_performance_monitor):
        """Test performance degradation detection."""
        # Mock performance metrics with high response times
        class MockMetrics:
            def __init__(self, timestamp, response_time_ms, request_count, error_count):
                self.timestamp = timestamp
                self.response_time_ms = response_time_ms
                self.request_count = request_count
                self.error_count = error_count
        
        metrics = [
            MockMetrics(timestamp=datetime.now(), response_time_ms=3000, 
                       request_count=10, error_count=0),
            MockMetrics(timestamp=datetime.now(), response_time_ms=2500, 
                       request_count=15, error_count=1),
            MockMetrics(timestamp=datetime.now(), response_time_ms=4000, 
                       request_count=8, error_count=0),
        ]
        mock_performance_monitor.get_metrics_history.return_value = metrics
        
        # Find performance condition
        perf_condition = next(
            c for c in failure_detector.failure_conditions 
            if c.failure_type == FailureType.PERFORMANCE_DEGRADATION
        )
        
        # Check condition
        failure_event = await failure_detector._check_condition(perf_condition)
        
        assert failure_event is not None
        assert failure_event.failure_type == FailureType.PERFORMANCE_DEGRADATION
        assert failure_event.actual_value > perf_condition.threshold
    
    @pytest.mark.asyncio
    async def test_error_rate_spike_detection(self, failure_detector, mock_performance_monitor):
        """Test error rate spike detection."""
        # Mock performance metrics with high error rate
        class MockMetrics:
            def __init__(self, timestamp, response_time_ms, request_count, error_count):
                self.timestamp = timestamp
                self.response_time_ms = response_time_ms
                self.request_count = request_count
                self.error_count = error_count
        
        metrics = [
            MockMetrics(timestamp=datetime.now(), response_time_ms=200, 
                       request_count=100, error_count=10),
            MockMetrics(timestamp=datetime.now(), response_time_ms=250, 
                       request_count=80, error_count=8),
        ]
        mock_performance_monitor.get_metrics_history.return_value = metrics
        
        # Find error rate condition
        error_condition = next(
            c for c in failure_detector.failure_conditions 
            if c.failure_type == FailureType.ERROR_RATE_SPIKE
        )
        
        # Check condition
        failure_event = await failure_detector._check_condition(error_condition)
        
        assert failure_event is not None
        assert failure_event.failure_type == FailureType.ERROR_RATE_SPIKE
        assert failure_event.actual_value > error_condition.threshold
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_detection(self, failure_detector, mock_performance_monitor):
        """Test resource exhaustion detection."""
        # Mock current metrics with high resource usage
        class MockCurrentMetrics:
            def __init__(self):
                self.timestamp = datetime.now()
                self.response_time_ms = 200
                self.request_count = 100
                self.error_count = 2
                self.resource_utilization = {'cpu_percent': 95, 'memory_percent': 88}
        
        current_metrics = MockCurrentMetrics()
        mock_performance_monitor.get_current_metrics.return_value = current_metrics
        
        # Find resource condition
        resource_condition = next(
            c for c in failure_detector.failure_conditions 
            if c.failure_type == FailureType.RESOURCE_EXHAUSTION
        )
        
        # Check condition
        failure_event = await failure_detector._check_condition(resource_condition)
        
        assert failure_event is not None
        assert failure_event.failure_type == FailureType.RESOURCE_EXHAUSTION
        assert failure_event.actual_value > resource_condition.threshold
    
    def test_get_recent_failures(self, failure_detector):
        """Test getting recent failures."""
        # Add some failure events
        now = datetime.now()
        failure_detector.failure_history = [
            FailureEvent(
                failure_type=FailureType.HEALTH_CHECK_FAILURE,
                timestamp=now - timedelta(minutes=5),
                severity="warning",
                message="Test failure 1",
                metrics={},
                threshold_breached=0.8,
                actual_value=0.6
            ),
            FailureEvent(
                failure_type=FailureType.PERFORMANCE_DEGRADATION,
                timestamp=now - timedelta(minutes=15),
                severity="critical",
                message="Test failure 2",
                metrics={},
                threshold_breached=2000,
                actual_value=3000
            ),
        ]
        
        # Get recent failures (last 10 minutes)
        recent = failure_detector.get_recent_failures(10)
        assert len(recent) == 1
        assert recent[0].failure_type == FailureType.HEALTH_CHECK_FAILURE
    
    def test_has_critical_failures(self, failure_detector):
        """Test checking for critical failures."""
        # Add critical failure
        failure_detector.failure_history = [
            FailureEvent(
                failure_type=FailureType.RESOURCE_EXHAUSTION,
                timestamp=datetime.now() - timedelta(minutes=2),
                severity="critical",
                message="Critical failure",
                metrics={},
                threshold_breached=0.9,
                actual_value=0.95
            )
        ]
        
        assert failure_detector.has_critical_failures(5) is True
        assert failure_detector.has_critical_failures(1) is False
    
    def test_get_failure_summary(self, failure_detector):
        """Test getting failure summary."""
        summary = failure_detector.get_failure_summary()
        
        assert "monitoring_active" in summary
        assert "total_conditions" in summary
        assert "enabled_conditions" in summary
        assert "recent_failures" in summary
        assert "failure_counts" in summary
        assert "has_critical_failures" in summary
        assert "last_check" in summary
        
        assert summary["total_conditions"] == 4
        assert summary["enabled_conditions"] == 4
    
    @pytest.mark.asyncio
    async def test_monitoring_loop_error_handling(self, failure_detector):
        """Test error handling in monitoring loop."""
        # Mock an exception in check_all_conditions
        with patch.object(failure_detector, '_check_all_conditions', 
                         side_effect=Exception("Test error")):
            with pytest.raises(RollbackError):
                await failure_detector._monitoring_loop()
    
    @pytest.mark.asyncio
    async def test_condition_check_error_handling(self, failure_detector, mock_health_manager):
        """Test error handling in condition checking."""
        # Mock an exception in health manager
        mock_health_manager.get_health_history.side_effect = Exception("Health check error")
        
        # Find health check condition
        health_condition = next(
            c for c in failure_detector.failure_conditions 
            if c.failure_type == FailureType.HEALTH_CHECK_FAILURE
        )
        
        # Should not raise exception, should return None
        failure_event = await failure_detector._check_condition(health_condition)
        assert failure_event is None