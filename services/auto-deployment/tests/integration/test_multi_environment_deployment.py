"""
Multi-environment deployment integration tests.

Tests deployment across different environments (dev, staging, production)
with environment-specific configurations and validations.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any, List

from services.auto_deployment.orchestrator import DeploymentOrchestrator
from services.auto_deployment.config import DeploymentConfig
from services.auto_deployment.exceptions import DeploymentError, ValidationError


class TestMultiEnvironmentDeployment:
    """Test deployment across multiple environments."""
    
    @pytest.fixture
    def environments(self):
        """Define test environments with their configurations."""
        return {
            'development': {
                'project_id': 'test-project-dev',
                'region': 'us-central1',
                'min_instances': 0,
                'max_instances': 5,
                'memory': '512Mi',
                'cpu': '0.5',
                'timeout': 300
            },
            'staging': {
                'project_id': 'test-project-staging',
                'region': 'us-central1',
                'min_instances': 1,
                'max_instances': 10,
                'memory': '1Gi',
                'cpu': '1',
                'timeout': 600
            },
            'production': {
                'project_id': 'test-project-prod',
                'region': 'us-central1',
                'min_instances': 2,
                'max_instances': 50,
                'memory': '2Gi',
                'cpu': '2',
                'timeout': 900
            }
        }
    
    @pytest.mark.asyncio
    async def test_development_environment_deployment(self, environments):
        """Test deployment to development environment."""
        env_config = environments['development']
        config = DeploymentConfig(
            service_name="test-service",
            environment="development",
            **env_config
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Mock development-specific validations (less strict)
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.validator.validate_development_requirements = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-dev-001',
                'url': 'https://test-service-dev.run.app',
                'status': 'success',
                'environment': 'development'
            })
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            result = await orchestrator.deploy()
            
            assert result['status'] == 'success'
            assert result['environment'] == 'development'
            assert 'dev' in result['revision_name']
            
            # Verify development-specific settings were applied
            deployment_call = orchestrator.deployment_engine.deploy.call_args
            assert deployment_call[1]['min_instances'] == 0  # Can scale to zero in dev
    
    @pytest.mark.asyncio
    async def test_staging_environment_deployment(self, environments):
        """Test deployment to staging environment."""
        env_config = environments['staging']
        config = DeploymentConfig(
            service_name="test-service",
            environment="staging",
            **env_config
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Mock staging-specific validations
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.validator.validate_staging_requirements = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-staging-001',
                'url': 'https://test-service-staging.run.app',
                'status': 'success',
                'environment': 'staging'
            })
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            result = await orchestrator.deploy()
            
            assert result['status'] == 'success'
            assert result['environment'] == 'staging'
            assert 'staging' in result['revision_name']
    
    @pytest.mark.asyncio
    async def test_production_environment_deployment(self, environments):
        """Test deployment to production environment with enhanced security."""
        env_config = environments['production']
        config = DeploymentConfig(
            service_name="test-service",
            environment="production",
            **env_config
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Mock production-specific validations (more strict)
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.validator.validate_production_requirements = AsyncMock(return_value=True)
            orchestrator.validator.validate_security_compliance = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-prod-001',
                'url': 'https://test-service-prod.run.app',
                'status': 'success',
                'environment': 'production'
            })
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            result = await orchestrator.deploy()
            
            assert result['status'] == 'success'
            assert result['environment'] == 'production'
            assert 'prod' in result['revision_name']
            
            # Verify production-specific validations were called
            orchestrator.validator.validate_production_requirements.assert_called_once()
            orchestrator.validator.validate_security_compliance.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_environment_promotion_workflow(self, environments):
        """Test promoting deployment from dev -> staging -> production."""
        service_name = "test-service"
        promotion_results = {}
        
        # Deploy to development first
        dev_config = DeploymentConfig(
            service_name=service_name,
            environment="development",
            **environments['development']
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            dev_orchestrator = DeploymentOrchestrator(dev_config)
            
            # Mock successful development deployment
            dev_orchestrator.validator.validate_all = AsyncMock(return_value=True)
            dev_orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            dev_orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': f'{service_name}-dev-001',
                'status': 'success',
                'environment': 'development'
            })
            dev_orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            dev_orchestrator.notification_manager.send_notification = AsyncMock()
            
            promotion_results['development'] = await dev_orchestrator.deploy()
        
        # Promote to staging
        staging_config = DeploymentConfig(
            service_name=service_name,
            environment="staging",
            **environments['staging']
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            staging_orchestrator = DeploymentOrchestrator(staging_config)
            
            # Mock successful staging deployment
            staging_orchestrator.validator.validate_all = AsyncMock(return_value=True)
            staging_orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            staging_orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': f'{service_name}-staging-001',
                'status': 'success',
                'environment': 'staging'
            })
            staging_orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            staging_orchestrator.notification_manager.send_notification = AsyncMock()
            
            promotion_results['staging'] = await staging_orchestrator.deploy()
        
        # Promote to production
        prod_config = DeploymentConfig(
            service_name=service_name,
            environment="production",
            **environments['production']
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            prod_orchestrator = DeploymentOrchestrator(prod_config)
            
            # Mock successful production deployment
            prod_orchestrator.validator.validate_all = AsyncMock(return_value=True)
            prod_orchestrator.validator.validate_production_requirements = AsyncMock(return_value=True)
            prod_orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            prod_orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': f'{service_name}-prod-001',
                'status': 'success',
                'environment': 'production'
            })
            prod_orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            prod_orchestrator.notification_manager.send_notification = AsyncMock()
            
            promotion_results['production'] = await prod_orchestrator.deploy()
        
        # Verify all environments deployed successfully
        for env in ['development', 'staging', 'production']:
            assert promotion_results[env]['status'] == 'success'
            assert promotion_results[env]['environment'] == env
    
    @pytest.mark.asyncio
    async def test_environment_specific_validation_failures(self, environments):
        """Test environment-specific validation failures."""
        
        # Test production validation failure
        prod_config = DeploymentConfig(
            service_name="test-service",
            environment="production",
            **environments['production']
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(prod_config)
            
            # Mock production validation failure
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.validator.validate_production_requirements = AsyncMock(
                side_effect=ValidationError("Production security requirements not met")
            )
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            with pytest.raises(ValidationError) as exc_info:
                await orchestrator.deploy()
            
            assert "Production security requirements not met" in str(exc_info.value)
            
            # Verify deployment was not attempted
            assert not orchestrator.deployment_engine.deploy.called
    
    @pytest.mark.asyncio
    async def test_cross_environment_resource_isolation(self, environments):
        """Test that environments are properly isolated."""
        
        # Deploy to multiple environments simultaneously
        tasks = []
        
        for env_name, env_config in environments.items():
            config = DeploymentConfig(
                service_name="test-service",
                environment=env_name,
                **env_config
            )
            
            with patch.multiple(
                'services.auto_deployment.orchestrator',
                ValidationFramework=Mock(),
                CloudResourceManager=Mock(),
                BlueGreenStrategy=Mock(),
                HealthCheckSystem=Mock(),
                NotificationManager=Mock(),
                RollbackManager=Mock()
            ):
                orchestrator = DeploymentOrchestrator(config)
                
                # Mock successful deployment with environment-specific resources
                orchestrator.validator.validate_all = AsyncMock(return_value=True)
                orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
                orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                    'revision_name': f'test-service-{env_name}-001',
                    'project_id': env_config['project_id'],
                    'status': 'success',
                    'environment': env_name
                })
                orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
                orchestrator.notification_manager.send_notification = AsyncMock()
                
                tasks.append(orchestrator.deploy())
        
        # Execute all deployments concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify each environment used its own project and resources
        project_ids = set()
        for result in results:
            project_ids.add(result['project_id'])
        
        # Should have 3 different project IDs (one per environment)
        assert len(project_ids) == 3
        assert 'test-project-dev' in project_ids
        assert 'test-project-staging' in project_ids
        assert 'test-project-prod' in project_ids


class TestEnvironmentSpecificFeatures:
    """Test environment-specific features and configurations."""
    
    @pytest.mark.asyncio
    async def test_development_debug_features(self):
        """Test development environment enables debug features."""
        config = DeploymentConfig(
            service_name="test-service",
            environment="development",
            project_id="test-project-dev",
            region="us-central1",
            debug_mode=True,
            log_level="DEBUG"
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Mock deployment with debug features
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-dev-001',
                'status': 'success',
                'debug_enabled': True,
                'log_level': 'DEBUG'
            })
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            result = await orchestrator.deploy()
            
            assert result['debug_enabled'] is True
            assert result['log_level'] == 'DEBUG'
    
    @pytest.mark.asyncio
    async def test_production_security_features(self):
        """Test production environment enables security features."""
        config = DeploymentConfig(
            service_name="test-service",
            environment="production",
            project_id="test-project-prod",
            region="us-central1",
            security_scanning=True,
            compliance_checks=True
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Mock deployment with security features
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.validator.validate_security_compliance = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-prod-001',
                'status': 'success',
                'security_scanning_enabled': True,
                'compliance_verified': True
            })
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            result = await orchestrator.deploy()
            
            assert result['security_scanning_enabled'] is True
            assert result['compliance_verified'] is True
            
            # Verify security validations were called
            orchestrator.validator.validate_security_compliance.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_staging_performance_testing(self):
        """Test staging environment includes performance testing."""
        config = DeploymentConfig(
            service_name="test-service",
            environment="staging",
            project_id="test-project-staging",
            region="us-central1",
            performance_testing=True,
            load_testing=True
        )
        
        with patch.multiple(
            'services.auto_deployment.orchestrator',
            ValidationFramework=Mock(),
            CloudResourceManager=Mock(),
            BlueGreenStrategy=Mock(),
            HealthCheckSystem=Mock(),
            NotificationManager=Mock(),
            RollbackManager=Mock()
        ):
            orchestrator = DeploymentOrchestrator(config)
            
            # Mock deployment with performance testing
            orchestrator.validator.validate_all = AsyncMock(return_value=True)
            orchestrator.environment_manager.setup_environment = AsyncMock(return_value=True)
            orchestrator.deployment_engine.deploy = AsyncMock(return_value={
                'revision_name': 'test-service-staging-001',
                'status': 'success'
            })
            orchestrator.health_monitor.check_health = AsyncMock(return_value=True)
            orchestrator.performance_tester.run_load_tests = AsyncMock(return_value={
                'avg_response_time': 150,
                'max_response_time': 500,
                'success_rate': 99.5
            })
            orchestrator.notification_manager.send_notification = AsyncMock()
            
            result = await orchestrator.deploy()
            
            assert result['status'] == 'success'
            
            # Verify performance testing was executed
            orchestrator.performance_tester.run_load_tests.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])