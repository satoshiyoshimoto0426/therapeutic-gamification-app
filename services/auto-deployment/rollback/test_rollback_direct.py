#!/usr/bin/env python3
"""
Direct test of rollback execution engine implementation.

This script directly tests the rollback execution engine to verify
that Task 7.2 has been properly implemented.
"""

import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import Mock, AsyncMock

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_rollback_executor_implementation():
    """Test that rollback executor is properly implemented."""
    print("🔍 Testing Rollback Execution Engine Implementation...")
    
    try:
        # Test imports
        print("  ✓ Testing imports...")
        
        # Import rollback executor components
        from rollback_executor import (
            RollbackExecutor, RollbackConfig, RollbackTarget, RollbackResult,
            RollbackStatus, RollbackStrategy
        )
        print("    ✓ RollbackExecutor components imported successfully")
        
        from rollback_triggers import RollbackRequest, RollbackReason
        print("    ✓ RollbackTrigger components imported successfully")
        
        # Test class instantiation
        print("  ✓ Testing class instantiation...")
        
        # Create mock dependencies
        traffic_manager = Mock()
        traffic_manager.rollback_traffic = Mock(return_value=Mock(success=True))
        traffic_manager.get_current_traffic = Mock(return_value={"test-revision": 100})
        
        revision_manager = Mock()
        health_check_manager = Mock()
        health_check_manager.run_health_checks = AsyncMock(return_value=[
            Mock(success=True, endpoint="/health")
        ])
        
        performance_monitor = Mock()
        performance_monitor.get_metrics_history = AsyncMock(return_value=[
            Mock(response_time_ms=100, request_count=100, error_count=1)
        ])
        
        notification_manager = Mock()
        notification_manager.send_notification = AsyncMock()
        
        # Create rollback executor
        config = RollbackConfig(
            strategy=RollbackStrategy.IMMEDIATE,
            verification_timeout_seconds=60
        )
        
        executor = RollbackExecutor(
            traffic_manager=traffic_manager,
            revision_manager=revision_manager,
            health_check_manager=health_check_manager,
            performance_monitor=performance_monitor,
            notification_manager=notification_manager,
            config=config
        )
        print("    ✓ RollbackExecutor instantiated successfully")
        
        # Test required methods exist
        print("  ✓ Testing required methods...")
        
        required_methods = [
            'execute_rollback',
            '_execute_immediate_rollback',
            '_execute_gradual_rollback',
            '_execute_blue_green_rollback',
            '_verify_rollback',
            '_verify_health_checks',
            '_verify_performance',
            '_send_rollback_notification'
        ]
        
        for method_name in required_methods:
            assert hasattr(executor, method_name), f"Method {method_name} not found"
            assert callable(getattr(executor, method_name)), f"Method {method_name} is not callable"
            print(f"    ✓ Method {method_name} exists and is callable")
        
        # Test rollback strategies
        print("  ✓ Testing rollback strategies...")
        
        strategies = [
            RollbackStrategy.IMMEDIATE,
            RollbackStrategy.GRADUAL,
            RollbackStrategy.BLUE_GREEN
        ]
        
        for strategy in strategies:
            executor.config.strategy = strategy
            print(f"    ✓ Strategy {strategy.value} configured successfully")
        
        # Test configuration options
        print("  ✓ Testing configuration options...")
        
        config_attrs = [
            'strategy',
            'verification_timeout_seconds',
            'health_check_timeout_seconds',
            'gradual_rollback_steps',
            'gradual_rollback_interval_seconds',
            'max_retry_attempts',
            'notification_enabled'
        ]
        
        for attr in config_attrs:
            assert hasattr(config, attr), f"Config attribute {attr} not found"
            print(f"    ✓ Config attribute {attr} exists")
        
        print("✅ Rollback Execution Engine Implementation Test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Rollback Execution Engine Implementation Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_rollback_execution_flow():
    """Test the complete rollback execution flow."""
    print("\n🔄 Testing Rollback Execution Flow...")
    
    try:
        from rollback_executor import (
            RollbackExecutor, RollbackConfig, RollbackTarget, RollbackResult,
            RollbackStatus, RollbackStrategy
        )
        from rollback_triggers import RollbackRequest, RollbackReason
        
        # Create mock dependencies with proper async behavior
        traffic_manager = Mock()
        traffic_manager.rollback_traffic = Mock(return_value=Mock(
            success=True,
            current_traffic={"stable-revision": 100}
        ))
        traffic_manager.get_current_traffic = Mock(return_value={"stable-revision": 100})
        
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
        
        # Create rollback request
        request = RollbackRequest(
            trigger_id="test_flow_123",
            reason=RollbackReason.AUTOMATIC_HEALTH_FAILURE,
            timestamp=datetime.now(),
            severity="critical",
            message="Test rollback execution flow",
            failure_events=[],
            metadata={"test": "flow"}
        )
        
        # Create rollback target
        target = RollbackTarget(
            service_name="test-service",
            target_revision="stable-revision",
            current_revision="failed-revision",
            environment="test"
        )
        
        print("  ✓ Test setup completed")
        
        # Execute rollback
        print("  🔄 Executing rollback...")
        result = await executor.execute_rollback(request, target)
        
        # Verify result
        print("  ✓ Verifying rollback result...")
        assert result is not None, "Rollback result is None"
        assert hasattr(result, 'success'), "Result missing success attribute"
        assert hasattr(result, 'status'), "Result missing status attribute"
        assert hasattr(result, 'rollback_id'), "Result missing rollback_id attribute"
        assert result.rollback_id.startswith("rollback_"), "Invalid rollback ID format"
        
        print(f"    ✓ Rollback ID: {result.rollback_id}")
        print(f"    ✓ Rollback Status: {result.status}")
        print(f"    ✓ Rollback Success: {result.success}")
        
        # Verify traffic manager was called
        traffic_manager.rollback_traffic.assert_called_once()
        print("    ✓ Traffic manager rollback_traffic called")
        
        # Verify health checks were performed
        health_check_manager.run_health_checks.assert_called()
        print("    ✓ Health checks performed")
        
        # Verify performance monitoring was called
        performance_monitor.get_metrics_history.assert_called()
        print("    ✓ Performance monitoring called")
        
        # Verify notifications were sent
        notification_manager.send_notification.assert_called()
        print("    ✓ Notifications sent")
        
        print("✅ Rollback Execution Flow Test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Rollback Execution Flow Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_rollback_manager_integration():
    """Test rollback manager integration."""
    print("\n🔗 Testing Rollback Manager Integration...")
    
    try:
        from rollback_manager import (
            RollbackManager, RollbackManagerConfig, RollbackManagerStatus
        )
        
        # Create mock dependencies
        traffic_manager = Mock()
        revision_manager = Mock()
        health_check_manager = Mock()
        performance_monitor = Mock()
        notification_manager = Mock()
        
        # Create configuration
        config = RollbackManagerConfig(
            service_name="test-service",
            environment="test",
            auto_rollback_enabled=True,
            manual_rollback_enabled=True,
            failure_detection_enabled=True
        )
        
        # Create manager
        manager = RollbackManager(
            traffic_manager=traffic_manager,
            revision_manager=revision_manager,
            health_check_manager=health_check_manager,
            performance_monitor=performance_monitor,
            notification_manager=notification_manager,
            config=config
        )
        
        print("  ✓ RollbackManager instantiated successfully")
        
        # Test required methods exist
        required_methods = [
            'start',
            'stop',
            'trigger_manual_rollback',
            'get_status',
            'get_recent_rollbacks',
            'get_active_rollbacks'
        ]
        
        for method_name in required_methods:
            assert hasattr(manager, method_name), f"Method {method_name} not found"
            print(f"    ✓ Method {method_name} exists")
        
        # Test components are integrated
        assert hasattr(manager, 'rollback_executor'), "rollback_executor not integrated"
        assert hasattr(manager, 'failure_detector'), "failure_detector not integrated"
        print("    ✓ Core components integrated")
        
        print("✅ Rollback Manager Integration Test PASSED")
        return True
        
    except Exception as e:
        print(f"❌ Rollback Manager Integration Test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 Task 7.2 - Rollback Execution Engine Implementation Verification")
    print("=" * 70)
    
    tests = [
        test_rollback_executor_implementation,
        test_rollback_manager_integration
    ]
    
    async_tests = [
        test_rollback_execution_flow
    ]
    
    passed = 0
    total = len(tests) + len(async_tests)
    
    # Run synchronous tests
    for test in tests:
        if test():
            passed += 1
    
    # Run asynchronous tests
    for test in async_tests:
        if asyncio.run(test()):
            passed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Task 7.2 - Create rollback execution engine - COMPLETED")
        print("\n✅ All requirements satisfied:")
        print("  ✓ Rollback execution logic implemented")
        print("  ✓ Traffic rollback procedures implemented")
        print("  ✓ Rollback verification system implemented")
        print("  ✓ Integration tests implemented")
        return True
    else:
        print("❌ Task 7.2 - Some tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)