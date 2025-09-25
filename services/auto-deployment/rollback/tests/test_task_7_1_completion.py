"""
Task 7.1 completion test - Rollback detection and triggers implementation.

This test verifies that the rollback detection and trigger system is properly implemented.
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock


def test_task_7_1_imports():
    """Test that all required modules can be imported."""
    try:
        import sys
        import os
        
        # Add the services directory to Python path
        services_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
        if services_path not in sys.path:
            sys.path.insert(0, services_path)
        
        # Test failure detector imports
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from rollback.failure_detector import (
            FailureDetector, FailureType, FailureCondition, FailureEvent
        )
        
        # Test rollback triggers imports
        from rollback.rollback_triggers import (
            AutomaticRollbackTrigger, ManualRollbackTrigger, RollbackTriggerConfig,
            RollbackRequest, RollbackReason
        )
        
        # Test that enums have expected values
        assert FailureType.HEALTH_CHECK_FAILURE
        assert FailureType.PERFORMANCE_DEGRADATION
        assert FailureType.ERROR_RATE_SPIKE
        assert FailureType.RESOURCE_EXHAUSTION
        
        assert RollbackReason.AUTOMATIC_HEALTH_FAILURE
        assert RollbackReason.MANUAL_OPERATOR_REQUEST
        assert RollbackReason.MANUAL_EMERGENCY
        
        print("✅ All imports successful")
        
    except ImportError as e:
        pytest.fail(f"Import error: {e}")


def test_failure_detector_initialization():
    """Test failure detector can be initialized."""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from rollback.failure_detector import FailureDetector
        
        # Mock dependencies
        mock_health_manager = Mock()
        mock_performance_monitor = Mock()
        
        # Create failure detector
        detector = FailureDetector(
            health_check_manager=mock_health_manager,
            performance_monitor=mock_performance_monitor
        )
        
        # Verify initialization
        assert detector.monitoring_active is False
        assert len(detector.failure_conditions) == 4
        assert detector.failure_history == []
        
        print("✅ FailureDetector initialization successful")
        
    except Exception as e:
        pytest.fail(f"FailureDetector initialization failed: {e}")


def test_rollback_trigger_config():
    """Test rollback trigger configuration."""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from rollback.rollback_triggers import RollbackTriggerConfig
        
        # Test default config
        config = RollbackTriggerConfig()
        assert config.enabled is True
        assert config.cooldown_minutes == 10
        assert config.max_rollbacks_per_hour == 3
        assert config.require_confirmation is False
        
        # Test custom config
        custom_config = RollbackTriggerConfig(
            enabled=False,
            cooldown_minutes=5,
            max_rollbacks_per_hour=5,
            require_confirmation=True
        )
        assert custom_config.enabled is False
        assert custom_config.cooldown_minutes == 5
        assert custom_config.max_rollbacks_per_hour == 5
        assert custom_config.require_confirmation is True
        
        print("✅ RollbackTriggerConfig test successful")
        
    except Exception as e:
        pytest.fail(f"RollbackTriggerConfig test failed: {e}")


def test_manual_rollback_trigger():
    """Test manual rollback trigger functionality."""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from rollback.rollback_triggers import (
            ManualRollbackTrigger, RollbackTriggerConfig
        )
        
        # Create manual trigger
        config = RollbackTriggerConfig()
        manual_trigger = ManualRollbackTrigger(config)
        
        # Test initialization
        assert manual_trigger.active is False
        assert manual_trigger.rollback_history == []
        
        # Test status
        status = manual_trigger.get_rollback_status()
        assert "active" in status
        assert "config" in status
        assert "recent_rollbacks" in status
        assert "can_rollback" in status
        
        print("✅ ManualRollbackTrigger test successful")
        
    except Exception as e:
        pytest.fail(f"ManualRollbackTrigger test failed: {e}")


def test_automatic_rollback_trigger():
    """Test automatic rollback trigger functionality."""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from rollback.rollback_triggers import (
            AutomaticRollbackTrigger, RollbackTriggerConfig
        )
        from rollback.failure_detector import FailureDetector
        
        # Mock failure detector
        mock_failure_detector = Mock(spec=FailureDetector)
        mock_failure_detector.failure_history = []
        
        # Create automatic trigger
        config = RollbackTriggerConfig()
        auto_trigger = AutomaticRollbackTrigger(mock_failure_detector, config)
        
        # Test initialization
        assert auto_trigger.monitoring_active is False
        assert len(auto_trigger.trigger_conditions) == 4
        assert auto_trigger.rollback_history == []
        
        # Test severity threshold checking
        assert auto_trigger._meets_severity_threshold("critical", "warning") is True
        assert auto_trigger._meets_severity_threshold("warning", "critical") is False
        
        print("✅ AutomaticRollbackTrigger test successful")
        
    except Exception as e:
        pytest.fail(f"AutomaticRollbackTrigger test failed: {e}")


@pytest.mark.asyncio
async def test_manual_rollback_trigger_async():
    """Test manual rollback trigger async functionality."""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from rollback.rollback_triggers import (
            ManualRollbackTrigger, RollbackTriggerConfig
        )
        
        # Create manual trigger
        config = RollbackTriggerConfig(require_confirmation=False)
        manual_trigger = ManualRollbackTrigger(config)
        
        # Start trigger
        await manual_trigger.start()
        assert manual_trigger.active is True
        
        # Test callback system
        callback_called = False
        async def test_callback(request):
            nonlocal callback_called
            callback_called = True
            assert request.operator_id == "test_operator"
            assert request.reason.value == "manual_operator_request"
        
        manual_trigger.add_callback(test_callback)
        
        # Trigger rollback
        trigger_id = await manual_trigger.trigger_rollback(
            reason="Test rollback",
            operator_id="test_operator",
            severity="warning"
        )
        
        assert trigger_id.startswith("manual_test_operator_")
        assert callback_called is True
        assert len(manual_trigger.rollback_history) == 1
        
        # Stop trigger
        await manual_trigger.stop()
        assert manual_trigger.active is False
        
        print("✅ Manual rollback trigger async test successful")
        
    except Exception as e:
        pytest.fail(f"Manual rollback trigger async test failed: {e}")


def test_failure_event_creation():
    """Test failure event data structure."""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from rollback.failure_detector import FailureEvent, FailureType
        
        # Create failure event
        failure_event = FailureEvent(
            failure_type=FailureType.HEALTH_CHECK_FAILURE,
            timestamp=datetime.now(),
            severity="critical",
            message="Health check failed",
            metrics={"success_rate": 0.5},
            threshold_breached=0.8,
            actual_value=0.5
        )
        
        # Verify properties
        assert failure_event.failure_type == FailureType.HEALTH_CHECK_FAILURE
        assert failure_event.severity == "critical"
        assert failure_event.message == "Health check failed"
        assert failure_event.metrics["success_rate"] == 0.5
        assert failure_event.threshold_breached == 0.8
        assert failure_event.actual_value == 0.5
        
        print("✅ FailureEvent creation test successful")
        
    except Exception as e:
        pytest.fail(f"FailureEvent creation test failed: {e}")


def test_rollback_request_creation():
    """Test rollback request data structure."""
    try:
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
        from rollback.rollback_triggers import (
            RollbackRequest, RollbackReason
        )
        from rollback.failure_detector import (
            FailureEvent, FailureType
        )
        
        # Create failure event
        failure_event = FailureEvent(
            failure_type=FailureType.PERFORMANCE_DEGRADATION,
            timestamp=datetime.now(),
            severity="warning",
            message="Performance degraded",
            metrics={},
            threshold_breached=2000,
            actual_value=3000
        )
        
        # Create rollback request
        request = RollbackRequest(
            trigger_id="test_trigger_001",
            reason=RollbackReason.AUTOMATIC_PERFORMANCE_DEGRADATION,
            timestamp=datetime.now(),
            severity="warning",
            message="Automatic rollback due to performance issues",
            failure_events=[failure_event],
            metadata={"test": "data"},
            operator_id="system",
            confirmation_required=False
        )
        
        # Verify properties
        assert request.trigger_id == "test_trigger_001"
        assert request.reason == RollbackReason.AUTOMATIC_PERFORMANCE_DEGRADATION
        assert request.severity == "warning"
        assert len(request.failure_events) == 1
        assert request.metadata["test"] == "data"
        assert request.operator_id == "system"
        assert request.confirmation_required is False
        
        print("✅ RollbackRequest creation test successful")
        
    except Exception as e:
        pytest.fail(f"RollbackRequest creation test failed: {e}")


if __name__ == "__main__":
    # Run tests individually for debugging
    test_task_7_1_imports()
    test_failure_detector_initialization()
    test_rollback_trigger_config()
    test_manual_rollback_trigger()
    test_automatic_rollback_trigger()
    test_failure_event_creation()
    test_rollback_request_creation()
    
    # Run async test
    asyncio.run(test_manual_rollback_trigger_async())
    
    print("\n🎉 All Task 7.1 tests passed!")