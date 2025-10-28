"""
Full deployment workflow integration tests.

Tests the complete deployment process from start to finish,
including validation, deployment, monitoring, and rollback scenarios.
"""

import pytest
import sys
import os

# Add auto-deployment directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
auto_deployment_dir = os.path.dirname(os.path.dirname(current_dir))
if auto_deployment_dir not in sys.path:
    sys.path.insert(0, auto_deployment_dir)

import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List
import json
import tempfile
import os

from orchestrator import DeploymentOrchestrator
from config import DeploymentConfig
from validation.framework import ValidationFramework
from environment.cloud_resource_manager import CloudResourceManager
from deployment.strategies.blue_green import BlueGreenStrategy
from monitoring.health_check import HealthCheckSystem
from notification.notification_manager import NotificationManager
from rollback.rollback_manager import RollbackManager
from exceptions import DeploymentError, ValidationError


class TestFullDeploymentWorkflow:
    """Test complete deployment workflow scenarios."""
    
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
    
    @pytest.fixture
    def orchestrator(self, deployment_config):
        """Create deployment orchestrator with mocked dependencies."""
        with patch.multiple(
            'orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            return DeploymentOrchestrator(deployment_config)
    
    @pytest.mark.asyncio
    async def test_successful_deployment_workflow(self, orchestrator, deployment_config):
        """Test complete successful deployment workflow."""
        # Mock all components to return success
        orchestrator.validator.validate_all = AsyncMock(return_value=True)
        orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
        orchestrator.deployment_engine.deploy = AsyncMock(return_value={
            'revision_name': 'test-revision-001',
            'url': 'https://test-service-staging.run.app',
            'status': 'success'
        })
        orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
        orchestrator.notification_manager.send_notification = AsyncMock()
        
        # Execute deployment
        result = await orchestrator.deploy()
        
        # Verify workflow execution
        assert result['status'] == 'success'
        assert 'revision_name' in result
        assert 'url' in result
        
        # Verify all components were called
        orchestrator.validator.validate_all.assert_called_once()
        orchestrator.environment_manager.setup_environment.assert_called_once()
        orchestrator.deployment_engine.deploy.assert_called_once()
        orchestrator.health_monitor.check_health.assert_called_once()
        orchestrator.notification_manager.send_notification.assert_called()
    
    @pytest.mark.asyncio
    async def test_validation_failure_workflow(self, orchestrator):
        """Test workflow when validation fails."""
        # Mock validation failure
        orchestrator.validator.validate_all = AsyncMock(
            side_effect=ValidationError("Code quality check failed")
        )
        orchestrator.notification_manager.send_notification = AsyncMock()
        
        # Execute deployment and expect failure
        with pytest.raises(ValidationError):
            await orchestrator.deploy()
        
        # Verify deployment was not attempted
        assert not orchestrator.environment_manager.setup_environment.called
        assert not orchestrator.deployment_engine.deploy.called
        
        # Verify failure notification was sent
        orchestrator.notification_manager.send_notification.assert_called()
    
    @pytest.mark.asyncio
    async def test_deployment_failure_with_rollback(self, orchestrator):
        """Test deployment failure triggers rollback."""
        # Mock successful validation but deployment failure
        orchestrator.validator.validate_all = AsyncMock(return_value=True)
        orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
        orchestrator.deployment_engine.deploy = AsyncMock(
            side_effect=DeploymentError("Cloud Run deployment failed")
        )
        orchestrator.rollback_manager.rollback = AsyncMock(return_value=True)
        orchestrator.notification_manager.send_notification = AsyncMock()
        
        # Execute deployment and expect failure
        with pytest.raises(DeploymentError):
            await orchestrator.deploy()
        
        # Verify rollback was triggered
        orchestrator.rollback_manager.rollback.assert_called_once()
        orchestrator.notification_manager.send_notification.assert_called()
    
    @pytest.mark.asyncio
    async def test_health_check_failure_triggers_rollback(self, orchestrator):
        """Test health check failure triggers automatic rollback."""
        # Mock successful deployment but health check failure
        orchestrator.validator.validate_all = AsyncMock(return_value=True)
        orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
        orchestrator.deployment_engine.deploy = AsyncMock(return_value={
            'revision_name': 'test-revision-001',
            'status': 'success'
        })
        orchestrator.health_monitor.check_health = AsyncMock(return_value=False)
        orchestrator.rollback_manager.rollback = AsyncMock(return_value=True)
        orchestrator.notification_manager.send_notification = AsyncMock()
        
        # Execute deployment
        result = await orchestrator.deploy()
        
        # Verify rollback was triggered due to health check failure
        assert result['status'] == 'rolled_back'
        orchestrator.rollback_manager.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multi_service_deployment_workflow(self, deployment_config):
        """Test deployment of multiple services."""
        services = ['auth', 'core-game', 'task-mgmt']
        results = {}
        
        for service in services:
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
                
                # Mock successful deployment
                orchestrator.validator.validate_all = AsyncMock(return_value=True)
                orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
                orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                    'revision_name': f'{service}-revision-001',
                    'status': 'success'
                })
                orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
                orchestrator.notification_manager.send_notification = AsyncMock()
                
                result = await orchestrator.deploy()
                results[service] = result
        
        # Verify all services deployed successfully
        for service in services:
            assert results[service]['status'] == 'success'
            assert service in results[service]['revision_name']


class TestMultiEnvironmentDeployment:
    """Test deployment across different environments."""
    
    @pytest.mark.asyncio
    async def test_development_environment_deployment(self):
        """Test deployment to development environment."""
        config = DeploymentConfig(
            project_id="test-project",
            service_name="test-service",
            region="us-central1",
            environment="development",
            min_instances=0,  # Development can scale to zero
            max_instances=5
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
            
            # Mock successful deployment with development-specific settings
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-dev-001',
                'status': 'success',
                'environment': 'development'
            })
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            result = await orchestrator.deploy()
            
            assert result['status'] == 'success'
            assert result['environment'] == 'development'
    
    @pytest.mark.asyncio
    async def test_production_environment_deployment(self):
        """Test deployment to production environment with enhanced security."""
        config = DeploymentConfig(
            project_id="test-project",
            service_name="test-service",
            region="us-central1",
            environment="production",
            min_instances=2,  # Production requires minimum instances
            max_instances=50
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
            
            # Mock enhanced validation for production
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.validator.validate_production_requirements = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-prod-001',
                'status': 'success',
                'environment': 'production'
            })
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            result = await orchestrator.deploy()
            
            assert result['status'] == 'success'
            assert result['environment'] == 'production'
            
            # Verify production-specific validations were called
            orchestrator.validator.validate_production_requirements.assert_called_once()


class TestFailureScenarioAndRecovery:
    """Test various failure scenarios and recovery mechanisms."""
    
    @pytest.mark.asyncio
    async def test_network_failure_recovery(self):
        """Test recovery from network failures during deployment."""
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
            
            # Mock network failure followed by success on retry
            call_count = 0
            async def mock_deploy():
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise DeploymentError("Network timeout")
                return {'revision_name': 'test-revision-001', 'status': 'success'}
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_deploy)
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Enable retry mechanism
            orchestrator.max_retries = 2
            
            result = await orchestrator.deploy_with_retry()
            
            assert result['status'] == 'success'
            assert call_count == 2  # Failed once, succeeded on retry
    
    @pytest.mark.asyncio
    async def test_partial_deployment_cleanup(self):
        """Test cleanup of partial deployment on failure."""
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
            
            # Mock partial deployment failure
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(
                side_effect=DeploymentError("Deployment failed after creating revision")
            )
            orchestrator.deployment_engine.cleanup_failed_deployment = AsyncMock()
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Execute deployment and expect failure
            with pytest.raises(DeploymentError):
                await orchestrator.deploy()
            
            # Verify cleanup was called
            orchestrator.deployment_engine.cleanup_failed_deployment.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rollback_failure_escalation(self):
        """Test escalation when rollback fails."""
        config = DeploymentConfig(
            project_id="test-project",
            service_name="test-service",
            region="us-central1",
            environment="production"
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
            
            # Mock deployment failure followed by rollback failure
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(
                side_effect=DeploymentError("Deployment failed")
            )
            orchestrator.rollback_manager.rollback = AsyncMock(
                side_effect=DeploymentError("Rollback failed")
            )
            orchestrator.notification_manager.send_critical_alert = AsyncMock()
            
            # Execute deployment and expect escalation
            with pytest.raises(DeploymentError):
                await orchestrator.deploy()
            
            # Verify critical alert was sent
            orchestrator.notification_manager.send_critical_alert.assert_called_once()


class TestPerformanceAndLoad:
    """Test performance and load scenarios."""
    
    @pytest.mark.asyncio
    async def test_concurrent_deployments(self):
        """Test handling of concurrent deployment requests."""
        config = DeploymentConfig(
            project_id="test-project",
            service_name="test-service",
            region="us-central1",
            environment="staging"
        )
        
        # Create multiple orchestrators for concurrent deployments
        orchestrators = []
        for i in range(3):
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
                
                # Mock successful deployment with delay
                async def mock_deploy_with_delay():
                    await asyncio.sleep(0.1)  # Simulate deployment time
                    return {
                        'revision_name': f'test-revision-{i:03d}',
                        'status': 'success'
                    }
                
                orchestrator.validator.validate_all = AsyncMock(return_value=True)
                orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
                orchestrator.deployment_engine.deploy = AsyncMock(side_effect=mock_deploy_with_delay)
                orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
                orchestrator.notification_manager.send_notification = AsyncMock()
                
                orchestrators.append(orchestrator)
        
        # Execute concurrent deployments
        start_time = time.time()
        tasks = [orchestrator.deploy() for orchestrator in orchestrators]
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # Verify all deployments succeeded
        for result in results:
            assert result['status'] == 'success'
        
        # Verify deployments ran concurrently (should take ~0.1s, not 0.3s)
        assert end_time - start_time < 0.2
    
    @pytest.mark.asyncio
    async def test_deployment_timeout_handling(self):
        """Test handling of deployment timeouts."""
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
            orchestrator.deployment_timeout = 0.1  # Very short timeout for testing
            
            # Mock slow deployment
            async def slow_deploy():
                await asyncio.sleep(0.2)  # Longer than timeout
                return {'revision_name': 'test-revision-001', 'status': 'success'}
            
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(side_effect=slow_deploy)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            # Execute deployment and expect timeout
            with pytest.raises(asyncio.TimeoutError):
                await orchestrator.deploy_with_timeout()
    
    def test_memory_usage_during_deployment(self):
        """Test memory usage remains reasonable during deployment."""
        import psutil
        import gc
        
        config = DeploymentConfig(
            project_id="test-project",
            service_name="test-service",
            region="us-central1",
            environment="staging"
        )
        
        # Measure initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Create and destroy multiple orchestrators
        for i in range(100):
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
                # Simulate some work
                orchestrator.config.service_name = f"test-service-{i}"
        
        # Force garbage collection
        gc.collect()
        
        # Measure final memory
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])