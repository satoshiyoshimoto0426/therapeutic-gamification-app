"""
Tests for rollback trigger system.
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

from rollback.rollback_triggers import (
    AutomaticRollbackTrigger, ManualRollbackTrigger, RollbackTriggerConfig,
    RollbackRequest, RollbackReason
)
from rollback.failure_detector import FailureDetector, FailureEvent, FailureType
from exceptions import RollbackError


class TestRollbackTriggerConfig:
    """Test rollback trigger configuration."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = RollbackTriggerConfig()
        
        assert config.enabled is True
        assert config.cooldown_minutes == 10
        assert config.max_rollbacks_per_hour == 3
        assert config.require_confirmation is False
        assert config.notification_channels is None
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = RollbackTriggerConfig(
            enabled=False,
            cooldown_minutes=5,
            max_rollbacks_per_hour=5,
            require_confirmation=True,
            notification_channels=["slack", "email"]
        )
        
        assert config.enabled is False
        assert config.cooldown_minutes == 5
        assert config.max_rollbacks_per_hour == 5
        assert config.require_confirmation is True
        assert config.notification_channels == ["slack", "email"]


class TestRollbackRequest:
    """Test rollback request data structure."""
    
    def test_rollback_request_creation(self):
        """Test creating rollback request."""
        failure_event = FailureEvent(
            failure_type=FailureType.HEALTH_CHECK_FAILURE,
            timestamp=datetime.now(),
            severity="critical",
            message="Health check failed",
            metrics={},
            threshold_breached=0.8,
            actual_value=0.5
        )
        
        request = RollbackRequest(
            trigger_id="test_trigger_001",
            reason=RollbackReason.AUTOMATIC_HEALTH_FAILURE,
            timestamp=datetime.now(),
            severity="critical",
            message="Automatic rollback due to health failures",
            failure_events=[failure_event],
            metadata={"test": "data"},
            operator_id="system",
            confirmation_required=False
        )
        
        assert request.trigger_id == "test_trigger_001"
        assert request.reason == RollbackReason.AUTOMATIC_HEALTH_FAILURE
        assert request.severity == "critical"
        assert len(request.failure_events) == 1
        assert request.metadata["test"] == "data"
        assert request.operator_id == "system"
        assert request.confirmation_required is False


class TestAutomaticRollbackTrigger:
    """Test automatic rollback trigger."""
    
    @pytest.fixture
    def mock_failure_detector(self):
        """Mock failure detector."""
        detector = Mock(spec=FailureDetector)
        detector.failure_history = []
        return detector
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return RollbackTriggerConfig(
            enabled=True,
            cooldown_minutes=5,
            max_rollbacks_per_hour=2
        )
    
    @pytest.fixture
    def automatic_trigger(self, mock_failure_detector, config):
        """Create automatic rollback trigger."""
        return AutomaticRollbackTrigger(mock_failure_detector, config)
    
    def test_initialization(self, automatic_trigger):
        """Test automatic trigger initialization."""
        assert automatic_trigger.monitoring_active is False
        assert len(automatic_trigger.trigger_conditions) == 4
        assert automatic_trigger.rollback_history == []
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, automatic_trigger):
        """Test starting and stopping monitoring."""
        # Start monitoring
        await automatic_trigger.start()
        assert automatic_trigger.monitoring_active is True
        assert automatic_trigger._monitoring_task is not None
        
        # Stop monitoring
        await automatic_trigger.stop()
        assert automatic_trigger.monitoring_active is False
    
    def test_severity_threshold_check(self, automatic_trigger):
        """Test severity threshold checking."""
        assert automatic_trigger._meets_severity_threshold("critical", "warning") is True
        assert automatic_trigger._meets_severity_threshold("warning", "critical") is False
        assert automatic_trigger._meets_severity_threshold("warning", "warning") is True
        assert automatic_trigger._meets_severity_threshold("info", "warning") is False
    
    @pytest.mark.asyncio
    async def test_should_trigger_rollback(self, automatic_trigger, mock_failure_detector):
        """Test rollback trigger condition checking."""
        # Add failure events to history
        now = datetime.now()
        failure_events = [
            FailureEvent(
                failure_type=FailureType.HEALTH_CHECK_FAILURE,
                timestamp=now - timedelta(minutes=2),
                severity="warning",
                message="Health check failed",
                metrics={},
                threshold_breached=0.8,
                actual_value=0.6
            ),
            FailureEvent(
                failure_type=FailureType.HEALTH_CHECK_FAILURE,
                timestamp=now - timedelta(minutes=3),
                severity="critical",
                message="Health check failed",
                metrics={},
                threshold_breached=0.8,
                actual_value=0.4
            ),
            FailureEvent(
                failure_type=FailureType.HEALTH_CHECK_FAILURE,
                timestamp=now - timedelta(minutes=4),
                severity="warning",
                message="Health check failed",
                metrics={},
                threshold_breached=0.8,
                actual_value=0.7
            )
        ]
        mock_failure_detector.failure_history = failure_events
        
        # Check if rollback should be triggered
        condition = automatic_trigger.trigger_conditions[FailureType.HEALTH_CHECK_FAILURE]
        should_trigger = await automatic_trigger._should_trigger_rollback(
            FailureType.HEALTH_CHECK_FAILURE, condition
        )
        
        assert should_trigger is True
    
    @pytest.mark.asyncio
    async def test_create_automatic_rollback_request(self, automatic_trigger, mock_failure_detector):
        """Test creating automatic rollback request."""
        # Add failure events to history
        now = datetime.now()
        failure_events = [
            FailureEvent(
                failure_type=FailureType.PERFORMANCE_DEGRADATION,
                timestamp=now - timedelta(minutes=2),
                severity="critical",
                message="Performance degraded",
                metrics={},
                threshold_breached=2000,
                actual_value=3000
            )
        ]
        mock_failure_detector.failure_history = failure_events
        
        # Mock the trigger callback
        callback_called = False
        async def mock_callback(request):
            nonlocal callback_called
            callback_called = True
            assert request.reason == RollbackReason.AUTOMATIC_PERFORMANCE_DEGRADATION
            assert request.severity == "critical"
            assert len(request.failure_events) == 1
        
        automatic_trigger.add_callback(mock_callback)
        
        # Create rollback request
        condition = automatic_trigger.trigger_conditions[FailureType.PERFORMANCE_DEGRADATION]
        await automatic_trigger._create_automatic_rollback_request(
            FailureType.PERFORMANCE_DEGRADATION, condition
        )
        
        assert callback_called is True
        assert len(automatic_trigger.rollback_history) == 1
    
    def test_cooldown_check(self, automatic_trigger):
        """Test cooldown period checking."""
        # No previous rollbacks - should allow
        assert automatic_trigger._check_cooldown() is True
        
        # Add recent rollback
        recent_rollback = RollbackRequest(
            trigger_id="test",
            reason=RollbackReason.AUTOMATIC_HEALTH_FAILURE,
            timestamp=datetime.now() - timedelta(minutes=2),
            severity="warning",
            message="Test rollback",
            failure_events=[],
            metadata={}
        )
        automatic_trigger.rollback_history.append(recent_rollback)
        
        # Should be in cooldown
        assert automatic_trigger._check_cooldown() is False
        
        # Add old rollback
        old_rollback = RollbackRequest(
            trigger_id="test_old",
            reason=RollbackReason.AUTOMATIC_HEALTH_FAILURE,
            timestamp=datetime.now() - timedelta(minutes=10),
            severity="warning",
            message="Old rollback",
            failure_events=[],
            metadata={}
        )
        automatic_trigger.rollback_history = [old_rollback]
        
        # Should allow rollback
        assert automatic_trigger._check_cooldown() is True
    
    def test_rate_limit_check(self, automatic_trigger):
        """Test rate limiting."""
        # No previous rollbacks - should allow
        assert automatic_trigger._check_rate_limit() is True
        
        # Add rollbacks within the hour
        now = datetime.now()
        for i in range(3):
            rollback = RollbackRequest(
                trigger_id=f"test_{i}",
                reason=RollbackReason.AUTOMATIC_HEALTH_FAILURE,
                timestamp=now - timedelta(minutes=i * 10),
                severity="warning",
                message=f"Test rollback {i}",
                failure_events=[],
                metadata={}
            )
            automatic_trigger.rollback_history.append(rollback)
        
        # Should hit rate limit
        assert automatic_trigger._check_rate_limit() is False
        
        # Add old rollback (outside the hour)
        automatic_trigger.rollback_history = [
            RollbackRequest(
                trigger_id="old",
                reason=RollbackReason.AUTOMATIC_HEALTH_FAILURE,
                timestamp=now - timedelta(hours=2),
                severity="warning",
                message="Old rollback",
                failure_events=[],
                metadata={}
            )
        ]
        
        # Should allow rollback
        assert automatic_trigger._check_rate_limit() is True


class TestManualRollbackTrigger:
    """Test manual rollback trigger."""
    
    @pytest.fixture
    def config(self):
        """Test configuration."""
        return RollbackTriggerConfig(
            enabled=True,
            cooldown_minutes=5,
            max_rollbacks_per_hour=2,
            require_confirmation=True
        )
    
    @pytest.fixture
    def manual_trigger(self, config):
        """Create manual rollback trigger."""
        return ManualRollbackTrigger(config)
    
    def test_initialization(self, manual_trigger):
        """Test manual trigger initialization."""
        assert manual_trigger.active is False
        assert manual_trigger.rollback_history == []
    
    @pytest.mark.asyncio
    async def test_start_stop(self, manual_trigger):
        """Test starting and stopping manual trigger."""
        await manual_trigger.start()
        assert manual_trigger.active is True
        
        await manual_trigger.stop()
        assert manual_trigger.active is False
    
    @pytest.mark.asyncio
    async def test_trigger_rollback(self, manual_trigger):
        """Test manual rollback triggering."""
        await manual_trigger.start()
        
        # Mock callback
        callback_called = False
        async def mock_callback(request):
            nonlocal callback_called
            callback_called = True
            assert request.reason == RollbackReason.MANUAL_OPERATOR_REQUEST
            assert request.operator_id == "test_operator"
            assert request.confirmation_required is True
        
        manual_trigger.add_callback(mock_callback)
        
        # Trigger rollback
        trigger_id = await manual_trigger.trigger_rollback(
            reason="Test rollback",
            operator_id="test_operator",
            severity="warning"
        )
        
        assert trigger_id.startswith("manual_test_operator_")
        assert callback_called is True
        assert len(manual_trigger.rollback_history) == 1
    
    @pytest.mark.asyncio
    async def test_trigger_emergency_rollback(self, manual_trigger):
        """Test emergency rollback triggering."""
        await manual_trigger.start()
        
        # Mock callback
        callback_called = False
        async def mock_callback(request):
            nonlocal callback_called
            callback_called = True
            assert request.reason == RollbackReason.MANUAL_EMERGENCY
            assert request.confirmation_required is False  # Emergency bypasses confirmation
        
        manual_trigger.add_callback(mock_callback)
        
        # Trigger emergency rollback
        trigger_id = await manual_trigger.trigger_rollback(
            reason="Emergency rollback",
            operator_id="test_operator",
            severity="critical",
            emergency=True
        )
        
        assert trigger_id.startswith("manual_test_operator_")
        assert callback_called is True
    
    @pytest.mark.asyncio
    async def test_trigger_scheduled_rollback(self, manual_trigger):
        """Test scheduled rollback."""
        await manual_trigger.start()
        
        # Mock callback
        callback_called = False
        async def mock_callback(request):
            nonlocal callback_called
            callback_called = True
            assert request.reason == RollbackReason.MANUAL_SCHEDULED
        
        manual_trigger.add_callback(mock_callback)
        
        # Schedule rollback for past time (should trigger immediately)
        scheduled_time = datetime.now() - timedelta(minutes=1)
        trigger_id = await manual_trigger.trigger_scheduled_rollback(
            reason="Scheduled rollback",
            operator_id="test_operator",
            scheduled_time=scheduled_time
        )
        
        assert trigger_id.startswith("scheduled_test_operator_")
        assert callback_called is True
    
    @pytest.mark.asyncio
    async def test_inactive_trigger_error(self, manual_trigger):
        """Test error when trigger is inactive."""
        # Don't start the trigger
        
        with pytest.raises(RollbackError, match="not active"):
            await manual_trigger.trigger_rollback(
                reason="Test",
                operator_id="test_operator"
            )
    
    def test_get_rollback_status(self, manual_trigger):
        """Test getting rollback status."""
        status = manual_trigger.get_rollback_status()
        
        assert "active" in status
        assert "config" in status
        assert "recent_rollbacks" in status
        assert "can_rollback" in status
        assert "last_rollback" in status
        
        assert status["active"] is False
        assert status["config"]["enabled"] is True
        assert status["recent_rollbacks"] == 0
        assert status["last_rollback"] is None
    
    @pytest.mark.asyncio
    async def test_callback_management(self, manual_trigger):
        """Test adding and removing callbacks."""
        callback1_called = False
        callback2_called = False
        
        async def callback1(request):
            nonlocal callback1_called
            callback1_called = True
        
        async def callback2(request):
            nonlocal callback2_called
            callback2_called = True
        
        # Add callbacks
        manual_trigger.add_callback(callback1)
        manual_trigger.add_callback(callback2)
        assert len(manual_trigger._callbacks) == 2
        
        # Remove one callback
        manual_trigger.remove_callback(callback1)
        assert len(manual_trigger._callbacks) == 1
        
        # Start trigger and test remaining callback
        await manual_trigger.start()
        await manual_trigger.trigger_rollback(
            reason="Test",
            operator_id="test_operator"
        )
        
        assert callback1_called is False
        assert callback2_called is True