"""
Failure scenario and recovery integration tests.

Tests various failure scenarios and the system's ability to recover,
including network failures, partial deployments, and rollback scenarios.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
auto_deployment_dir = os.path.dirname(os.path.dirname(current_dir))
if auto_deployment_dir not in sys.path:
    sys.path.insert(0, auto_deployment_dir)

from orchestrator import DeploymentOrchestrator
from config import DeploymentConfig
from exceptions import DeploymentError, ValidationError, NetworkError


class TestFailureRecoveryScenarios:
    """Test various failure scenarios and recovery mechanisms."""
    
    @pytest.fixture
    def deployment_config(self):
        """Create test deployment configuration."""
        return DeploymentConfig(
            project_id="test-project",
            service_name="test-service",
            region="us-central1",
            environment="staging",
            memory="1Gi",
            cpu="1",
            min_instances=1,
            max_instances=10
        )
    
    @pytest.mark.asyncio
    async def test_network_failure_recovery(self, deployment_config):
        """Test recovery from network failures during deployment."""
        with patch.multiple(
            'orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(deployment_config)
            
            # Mock network failure followed by success on retry
            call_count = 0
            async def mock_deploy():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise NetworkError("Connection timeout")
                elif call_count == 2:
                    raise NetworkError("DNS resolution failed")
                return {
                    'revision_name': 'test-service-staging-001',
                    'status': 'success'
                }
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_deploy)
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Enable retry mechanism
            orchestrator.max_retries = 3
            orchestrator.retry_delay = 0.1
            
            result = await orchestrator.deploy_with_retry()
            
            assert result['status'] == 'success'
            assert call_count == 3  # Failed twice, succeeded on third attempt
            
            # Verify retry notifications were sent
            assert orchestrator.notification_manager.send_notification.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_partial_deployment_cleanup(self, deployment_config):
        """Test cleanup of partial deployment on failure."""
        with patch.multiple(
            'orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(deployment_config)
            
            # Mock partial deployment failure
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(
                side_effect=DeploymentError("Deployment failed after creating revision")
            )
            orchestrator.deployment_engine.cleanup_failed_deployment = AsyncMock()
            orchestrator.deployment_engine.get_partial_deployment_state = AsyncMock(return_value={
                'revision_created': True,
                'traffic_allocated': False,
                'revision_name': 'test-service-staging-001'
            })
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Execute deployment and expect failure
            with pytest.raises(DeploymentError):
                await orchestrator.deploy()
            
            # Verify cleanup was called with partial state
            orchestrator.deployment_engine.cleanup_failed_deployment.assert_called_once()
            cleanup_call = orchestrator.deployment_engine.cleanup_failed_deployment.call_args
            assert cleanup_call[0][0]['revision_created'] is True
    
    @pytest.mark.asyncio
    async def test_rollback_failure_escalation(self, deployment_config):
        """Test escalation when rollback fails."""
        with patch.multiple(
            'orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(deployment_config)
            
            # Mock deployment failure followed by rollback failure
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(
                side_effect=DeploymentError("Deployment failed")
            )
            orchestrator.rollback_manager.rollback = AsyncMock(
                side_effect=DeploymentError("Rollback failed - previous revision not found")
            )
            orchestrator.notification_manager.send_critical_alert = AsyncMock()
            orchestrator.notification_manager.escalate_to_oncall = AsyncMock()
            
            # Execute deployment and expect escalation
            with pytest.raises(DeploymentError):
                await orchestrator.deploy()
            
            # Verify critical alert and escalation were triggered
            orchestrator.notification_manager.send_critical_alert.assert_called_once()
            orchestrator.notification_manager.escalate_to_oncall.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_health_check_failure_recovery(self, deployment_config):
        """Test recovery from health check failures."""
        with patch.multiple(
            'orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(deployment_config)
            
            # Mock successful deployment but intermittent health check failures
            health_check_count = 0
            async def mock_health_check():
                nonlocal health_check_count
                health_check_count += 1
                if health_check_count <= 2:
                    return False  # Fail first two checks
                return True  # Succeed on third check
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-staging-001',
                'status': 'success'
            })
            orchestrator.health_monitor.check_health = AsyncMock(side_effect=mock_health_check)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Configure health check retries
            orchestrator.health_check_retries = 3
            orchestrator.health_check_delay = 0.1
            
            result = await orchestrator.deploy()
            
            assert result['status'] == 'success'
            assert health_check_count == 3
            
            # Verify health check was retried
            assert orchestrator.health_monitor.check_health.call_count == 3
    
    @pytest.mark.asyncio
    async def test_concurrent_deployment_conflict_resolution(self, deployment_config):
        """Test handling of concurrent deployment conflicts."""
        with patch.multiple(
            'orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            # Create two orchestrators for concurrent deployments
            orchestrator1 = DeploymentOrchestrator(deployment_config)
            orchestrator2 = DeploymentOrchestrator(deployment_config)
            
            # Mock deployment lock mechanism
            deployment_lock_acquired = False
            
            async def mock_acquire_lock(orchestrator_id):
                nonlocal deployment_lock_acquired
                if deployment_lock_acquired:
                    raise DeploymentError(f"Deployment already in progress")
                deployment_lock_acquired = True
                return True
            
            async def mock_release_lock():
                nonlocal deployment_lock_acquired
                deployment_lock_acquired = False
            
            # Setup first orchestrator (should succeed)
            orchestrator1.validator.validate_all = AsyncMock(return_value=True)
            orchestrator1.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator1.deployment_engine.acquire_deployment_lock = AsyncMock(
                side_effect=lambda: mock_acquire_lock("orchestrator1")
            )
            orchestrator1.deployment_engine.release_deployment_lock = AsyncMock(
                side_effect=mock_release_lock
            )
            orchestrator1.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-staging-001',
                'status': 'success'
            })
            orchestrator1.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator1.notification_manager.send_notification = AsyncMock()
            
            # Setup second orchestrator (should fail due to lock)
            orchestrator2.validator.validate_all = AsyncMock(return_value=True)
            orchestrator2.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator2.deployment_engine.acquire_deployment_lock = AsyncMock(
                side_effect=lambda: mock_acquire_lock("orchestrator2")
            )
            orchestrator2.notification_manager.send_notification = AsyncMock()
            
            # Start both deployments concurrently
            task1 = asyncio.create_task(orchestrator1.deploy())
            await asyncio.sleep(0.01)  # Small delay to ensure first deployment starts
            task2 = asyncio.create_task(orchestrator2.deploy())
            
            # Wait for both to complete
            result1 = await task1
            
            with pytest.raises(DeploymentError) as exc_info:
                await task2
            
            assert "Deployment already in progress" in str(exc_info.value)
            assert result1['status'] == 'success'
    
    @pytest.mark.asyncio
    async def test_resource_exhaustion_recovery(self, deployment_config):
        """Test recovery from resource exhaustion scenarios."""
        with patch.multiple(
            'orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(deployment_config)
            
            # Mock resource exhaustion followed by recovery
            attempt_count = 0
            async def mock_deploy():
                nonlocal attempt_count
                attempt_count += 1
                if attempt_count == 1:
                    raise DeploymentError("Insufficient CPU quota")
                elif attempt_count == 2:
                    raise DeploymentError("Memory limit exceeded")
                return {
                    'revision_name': 'test-service-staging-001',
                    'status': 'success'
                }
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.environment_manager.request_quota_increase = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_deploy)
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Enable resource recovery
            orchestrator.auto_resource_recovery = True
            orchestrator.max_retries = 3
            
            result = await orchestrator.deploy_with_resource_recovery()
            
            assert result['status'] == 'success'
            assert attempt_count == 3
            
            # Verify quota increase was requested
            orchestrator.environment_manager.request_quota_increase.assert_called()
    
    @pytest.mark.asyncio
    async def test_cascading_failure_prevention(self, deployment_config):
        """Test prevention of cascading failures across services."""
        services = ['auth', 'core-game', 'task-mgmt']
        
        # Mock a scenario where one service failure doesn't affect others
        results = {}
        
        for i, service in enumerate(services):
            config = deployment_config.copy()
            config.service_name = service
            
            with patch.multiple(
                'orchestrator',
                ValidationFramework=Mock(),
                CloudResourceManager=Mock(),
                BlueGreenStrategy=Mock(),
                HealthCheckSystem=Mock(),
                NotificationManager=Mock(),
                RollbackManager=Mock()
            ):
                orchestrator = DeploymentOrchestrator(config)
                
                # Make the second service fail
                if i == 1:  # core-game fails
                    orchestrator.validator.validate_all = AsyncMock(return_value=True)
                    orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
                    orchestrator.deployment_engine.deploy = AsyncMock(
                        side_effect=DeploymentError("Service-specific failure")
                    )
                    orchestrator.notification_manager.send_notification = AsyncMock()
                    
                    with pytest.raises(DeploymentError):
                        await orchestrator.deploy()
                    
                    results[service] = {'status': 'failed'}
                else:
                    # Other services succeed
                    orchestrator.validator.validate_all = AsyncMock(return_value=True)
                    orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
                    orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                        'revision_name': f'{service}-staging-001',
                        'status': 'success'
                    })
                    orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
                    orchestrator.notification_manager.send_notification = AsyncMock()
                    
                    result = await orchestrator.deploy()
                    results[service] = result
        
        # Verify that other services succeeded despite one failure
        assert results['auth']['status'] == 'success'
        assert results['core-game']['status'] == 'failed'
        assert results['task-mgmt']['status'] == 'success'


class TestRecoveryMechanisms:
    """Test specific recovery mechanisms and strategies."""
    
    @pytest.mark.asyncio
    async def test_automatic_retry_with_backoff(self):
        """Test automatic retry with exponential backoff."""
        config = DeploymentConfig(
            project_id="test-project",
            service_name="test-service",
            region="us-central1",
            environment="staging"
        )
        
        with patch.multiple(
            'orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Track retry attempts and timing
            retry_times = []
            
            async def mock_deploy():
                retry_times.append(time.time())
                if len(retry_times) < 3:
                    raise NetworkError("Temporary network issue")
                return {
                    'revision_name': 'test-service-staging-001',
                    'status': 'success'
                }
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_deploy)
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Configure exponential backoff
            orchestrator.max_retries = 3
            orchestrator.base_retry_delay = 0.1
            orchestrator.backoff_multiplier = 2
            
            start_time = time.time()
            result = await orchestrator.deploy_with_exponential_backoff()
            
            assert result['status'] == 'success'
            assert len(retry_times) == 3
            
            # Verify exponential backoff timing
            if len(retry_times) >= 2:
                delay1 = retry_times[1] - retry_times[0]
                delay2 = retry_times[2] - retry_times[1]
                assert delay2 > delay1  # Second delay should be longer
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_pattern(self):
        """Test circuit breaker pattern for repeated failures."""
        config = DeploymentConfig(
            project_id="test-project",
            service_name="test-service",
            region="us-central1",
            environment="staging"
        )
        
        with patch.multiple(
            'orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Mock repeated failures to trigger circuit breaker
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(
                side_effect=DeploymentError("Persistent service failure")
            )
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Configure circuit breaker
            orchestrator.circuit_breaker_threshold = 3
            orchestrator.circuit_breaker_timeout = 0.1
            
            # First few attempts should fail normally
            for i in range(3):
                with pytest.raises(DeploymentError):
                    await orchestrator.deploy()
            
            # Next attempt should be blocked by circuit breaker
            with pytest.raises(DeploymentError) as exc_info:
                await orchestrator.deploy()
            
            assert "Circuit breaker open" in str(exc_info.value)
            
            # After timeout, circuit breaker should allow attempts again
            await asyncio.sleep(0.2)
            
            with pytest.raises(DeploymentError):
                await orchestrator.deploy()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
