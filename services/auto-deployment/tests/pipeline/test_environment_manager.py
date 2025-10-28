"""
Test environment management for automated testing pipeline.

Handles creation, configuration, and cleanup of test environments
for different testing scenarios.
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
import os
import tempfile
import shutil
import json
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from config import DeploymentConfig
from environment.cloud_resource_manager import CloudResourceManager
from environment.config_manager import ConfigManager
from environment.secret_manager import SecretManager


class TestEnvironmentManager:
    """Manages test environments for automated testing."""
    
    def __init__(self):
        self.active_environments = {}
        self.temp_directories = []
        self.resource_managers = {}
        self.environment_configs = {}
    
    async def create_test_environment(self, env_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new test environment with specified configuration."""
        if env_name in self.active_environments:
            raise ValueError(f"Environment {env_name} already exists")
        
        # Create temporary directory for environment
        temp_dir = tempfile.mkdtemp(prefix=f"test-env-{env_name}-")
        self.temp_directories.append(temp_dir)
        
        # Set up environment configuration
        env_config = {
            'name': env_name,
            'temp_directory': temp_dir,
            'created_at': datetime.now().isoformat(),
            'project_id': config.get('project_id', f'test-project-{env_name}'),
            'region': config.get('region', 'us-central1'),
            'environment_type': config.get('environment_type', 'testing'),
            'resources': {},
            'services': {},
            'secrets': {},
            'status': 'creating'
        }
        
        try:
            # Set up cloud resources
            await self._setup_cloud_resources(env_name, env_config, config)
            
            # Set up configuration management
            await self._setup_configuration_management(env_name, env_config, config)
            
            # Set up secret management
            await self._setup_secret_management(env_name, env_config, config)
            
            # Set up networking and security
            await self._setup_networking(env_name, env_config, config)
            
            env_config['status'] = 'ready'
            self.active_environments[env_name] = env_config
            
            # Save environment configuration
            await self._save_environment_config(env_name, env_config)
            
            return env_config
            
        except Exception as e:
            env_config['status'] = 'failed'
            env_config['error'] = str(e)
            await self.cleanup_test_environment(env_name)
            raise
    
    async def _setup_cloud_resources(self, env_name: str, env_config: Dict[str, Any], config: Dict[str, Any]):
        """Set up cloud resources for test environment."""
        with patch('environment.cloud_resource_manager.CloudResourceManager') as MockManager:
            mock_manager = MockManager.return_value
            
            # Mock resource creation
            mock_manager.create_project = AsyncMock(return_value={
                'project_id': env_config['project_id'],
                'status': 'active'
            })
            
            mock_manager.enable_apis = AsyncMock(return_value=[
                'run.googleapis.com',
                'cloudbuild.googleapis.com',
                'secretmanager.googleapis.com'
            ])
            
            mock_manager.create_service_account = AsyncMock(return_value={
                'email': f'test-sa-{env_name}@{env_config["project_id"]}.iam.gserviceaccount.com',
                'key_id': f'test-key-{env_name}'
            })
            
            # Set up resources
            project_info = await mock_manager.create_project()
            enabled_apis = await mock_manager.enable_apis()
            service_account = await mock_manager.create_service_account()
            
            env_config['resources'].update({
                'project': project_info,
                'enabled_apis': enabled_apis,
                'service_account': service_account
            })
            
            self.resource_managers[env_name] = mock_manager
    
    async def _setup_configuration_management(self, env_name: str, env_config: Dict[str, Any], config: Dict[str, Any]):
        """Set up configuration management for test environment."""
        config_dir = Path(env_config['temp_directory']) / 'config'
        config_dir.mkdir(exist_ok=True)
        
        # Create deployment configuration
        deployment_config = {
            'project_id': env_config['project_id'],
            'region': env_config['region'],
            'environment': env_config['environment_type'],
            'services': config.get('services', {}),
            'networking': config.get('networking', {}),
            'security': config.get('security', {})
        }
        
        # Save configuration files
        config_file = config_dir / 'deployment.yaml'
        with open(config_file, 'w') as f:
            yaml.dump(deployment_config, f)
        
        env_config['configuration'] = {
            'config_directory': str(config_dir),
            'deployment_config_file': str(config_file),
            'deployment_config': deployment_config
        }
    
    async def _setup_secret_management(self, env_name: str, env_config: Dict[str, Any], config: Dict[str, Any]):
        """Set up secret management for test environment."""
        secrets_config = config.get('secrets', {})
        
        # Mock secret manager
        with patch('environment.secret_manager.SecretManager') as MockSecretManager:
            mock_secret_manager = MockSecretManager.return_value
            
            # Create test secrets
            test_secrets = {}
            for secret_name, secret_value in secrets_config.items():
                mock_secret_manager.create_secret = AsyncMock(return_value={
                    'name': f'projects/{env_config["project_id"]}/secrets/{secret_name}',
                    'version': '1'
                })
                
                secret_info = await mock_secret_manager.create_secret()
                test_secrets[secret_name] = secret_info
            
            env_config['secrets'] = test_secrets
    
    async def _setup_networking(self, env_name: str, env_config: Dict[str, Any], config: Dict[str, Any]):
        """Set up networking configuration for test environment."""
        networking_config = config.get('networking', {})
        
        # Mock networking setup
        network_config = {
            'vpc_name': f'test-vpc-{env_name}',
            'subnet_name': f'test-subnet-{env_name}',
            'firewall_rules': networking_config.get('firewall_rules', []),
            'load_balancer': networking_config.get('load_balancer', {})
        }
        
        env_config['networking'] = network_config
    
    async def _save_environment_config(self, env_name: str, env_config: Dict[str, Any]):
        """Save environment configuration to file."""
        config_file = Path(env_config['temp_directory']) / 'environment.json'
        
        # Create a serializable copy of the config
        serializable_config = {
            k: v for k, v in env_config.items() 
            if k not in ['temp_directory']  # Exclude non-serializable items
        }
        serializable_config['temp_directory'] = env_config['temp_directory']
        
        with open(config_file, 'w') as f:
            json.dump(serializable_config, f, indent=2)
        
        self.environment_configs[env_name] = str(config_file)
    
    async def get_environment_config(self, env_name: str) -> Dict[str, Any]:
        """Get configuration for specified environment."""
        if env_name not in self.active_environments:
            raise ValueError(f"Environment {env_name} does not exist")
        
        return self.active_environments[env_name].copy()
    
    async def list_environments(self) -> List[str]:
        """List all active test environments."""
        return list(self.active_environments.keys())
    
    async def update_environment_config(self, env_name: str, updates: Dict[str, Any]):
        """Update configuration for existing environment."""
        if env_name not in self.active_environments:
            raise ValueError(f"Environment {env_name} does not exist")
        
        env_config = self.active_environments[env_name]
        env_config.update(updates)
        env_config['updated_at'] = datetime.now().isoformat()
        
        # Save updated configuration
        await self._save_environment_config(env_name, env_config)
    
    async def cleanup_test_environment(self, env_name: str):
        """Clean up test environment and all associated resources."""
        if env_name not in self.active_environments:
            return  # Already cleaned up or never existed
        
        env_config = self.active_environments[env_name]
        
        try:
            # Clean up cloud resources
            if env_name in self.resource_managers:
                resource_manager = self.resource_managers[env_name]
                
                # Mock cleanup operations
                if hasattr(resource_manager, 'delete_service_account'):
                    await resource_manager.delete_service_account()
                
                if hasattr(resource_manager, 'delete_project'):
                    await resource_manager.delete_project()
                
                del self.resource_managers[env_name]
            
            # Clean up temporary directory
            temp_dir = env_config.get('temp_directory')
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                if temp_dir in self.temp_directories:
                    self.temp_directories.remove(temp_dir)
            
            # Remove from active environments
            del self.active_environments[env_name]
            
            # Remove config file reference
            if env_name in self.environment_configs:
                del self.environment_configs[env_name]
                
        except Exception as e:
            print(f"Error cleaning up environment {env_name}: {e}")
    
    async def cleanup_all_environments(self):
        """Clean up all test environments."""
        env_names = list(self.active_environments.keys())
        
        for env_name in env_names:
            await self.cleanup_test_environment(env_name)
        
        # Clean up any remaining temp directories
        for temp_dir in self.temp_directories[:]:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                self.temp_directories.remove(temp_dir)
    
    async def clone_environment(self, source_env: str, target_env: str, config_overrides: Dict[str, Any] = None) -> Dict[str, Any]:
        """Clone an existing environment with optional configuration overrides."""
        if source_env not in self.active_environments:
            raise ValueError(f"Source environment {source_env} does not exist")
        
        if target_env in self.active_environments:
            raise ValueError(f"Target environment {target_env} already exists")
        
        # Get source configuration
        source_config = self.active_environments[source_env].copy()
        
        # Create new configuration based on source
        new_config = {
            'project_id': f'test-project-{target_env}',
            'region': source_config['region'],
            'environment_type': source_config['environment_type'],
            'services': source_config.get('services', {}),
            'networking': source_config.get('networking', {}),
            'security': source_config.get('security', {}),
            'secrets': source_config.get('secrets', {})
        }
        
        # Apply overrides
        if config_overrides:
            new_config.update(config_overrides)
        
        # Create the new environment
        return await self.create_test_environment(target_env, new_config)
    
    async def get_environment_status(self, env_name: str) -> str:
        """Get the current status of a test environment."""
        if env_name not in self.active_environments:
            return 'not_found'
        
        return self.active_environments[env_name].get('status', 'unknown')
    
    async def validate_environment(self, env_name: str) -> Dict[str, Any]:
        """Validate that a test environment is properly configured and accessible."""
        if env_name not in self.active_environments:
            return {'valid': False, 'error': 'Environment not found'}
        
        env_config = self.active_environments[env_name]
        validation_results = {
            'valid': True,
            'checks': {},
            'errors': []
        }
        
        try:
            # Check temp directory exists
            temp_dir = env_config.get('temp_directory')
            validation_results['checks']['temp_directory'] = os.path.exists(temp_dir) if temp_dir else False
            
            # Check configuration files
            config_dir = Path(temp_dir) / 'config' if temp_dir else None
            validation_results['checks']['config_directory'] = config_dir.exists() if config_dir else False
            
            # Check environment config file
            env_config_file = Path(temp_dir) / 'environment.json' if temp_dir else None
            validation_results['checks']['environment_config'] = env_config_file.exists() if env_config_file else False
            
            # Check resource manager
            validation_results['checks']['resource_manager'] = env_name in self.resource_managers
            
            # Check overall status
            validation_results['checks']['status'] = env_config.get('status') == 'ready'
            
            # Determine if environment is valid
            validation_results['valid'] = all(validation_results['checks'].values())
            
            if not validation_results['valid']:
                failed_checks = [check for check, passed in validation_results['checks'].items() if not passed]
                validation_results['errors'] = [f"Failed check: {check}" for check in failed_checks]
            
        except Exception as e:
            validation_results['valid'] = False
            validation_results['errors'].append(f"Validation error: {str(e)}")
        
        return validation_results


class TestEnvironmentFactory:
    """Factory for creating different types of test environments."""
    
    def __init__(self, environment_manager: TestEnvironmentManager):
        self.environment_manager = environment_manager
    
    async def create_basic_test_environment(self, env_name: str) -> Dict[str, Any]:
        """Create a basic test environment for simple deployment tests."""
        config = {
            'project_id': f'test-project-{env_name}',
            'region': 'us-central1',
            'environment_type': 'testing',
            'services': {
                'test-service': {
                    'memory': '1Gi',
                    'cpu': '1',
                    'min_instances': 1,
                    'max_instances': 5
                }
            }
        }
        
        return await self.environment_manager.create_test_environment(env_name, config)
    
    async def create_multi_service_environment(self, env_name: str, services: List[str]) -> Dict[str, Any]:
        """Create a test environment with multiple services."""
        services_config = {}
        
        for service in services:
            services_config[service] = {
                'memory': '1Gi',
                'cpu': '1',
                'min_instances': 1,
                'max_instances': 10
            }
        
        config = {
            'project_id': f'test-project-{env_name}',
            'region': 'us-central1',
            'environment_type': 'testing',
            'services': services_config,
            'networking': {
                'firewall_rules': [
                    {'name': 'allow-http', 'ports': ['80', '443']},
                    {'name': 'allow-internal', 'source_ranges': ['10.0.0.0/8']}
                ]
            }
        }
        
        return await self.environment_manager.create_test_environment(env_name, config)
    
    async def create_performance_test_environment(self, env_name: str) -> Dict[str, Any]:
        """Create a test environment optimized for performance testing."""
        config = {
            'project_id': f'test-project-{env_name}',
            'region': 'us-central1',
            'environment_type': 'performance',
            'services': {
                'performance-test-service': {
                    'memory': '2Gi',
                    'cpu': '2',
                    'min_instances': 2,
                    'max_instances': 50
                }
            },
            'networking': {
                'load_balancer': {
                    'type': 'application',
                    'health_check': {
                        'path': '/health',
                        'interval': 10
                    }
                }
            }
        }
        
        return await self.environment_manager.create_test_environment(env_name, config)
    
    async def create_security_test_environment(self, env_name: str) -> Dict[str, Any]:
        """Create a test environment with enhanced security configurations."""
        config = {
            'project_id': f'test-project-{env_name}',
            'region': 'us-central1',
            'environment_type': 'security',
            'services': {
                'secure-test-service': {
                    'memory': '1Gi',
                    'cpu': '1',
                    'min_instances': 1,
                    'max_instances': 10
                }
            },
            'security': {
                'enable_security_scanning': True,
                'require_https': True,
                'enable_audit_logging': True,
                'iam_policies': [
                    {'role': 'roles/run.invoker', 'members': ['allUsers']}
                ]
            },
            'secrets': {
                'api_key': 'test-api-key-value',
                'database_password': 'test-db-password'
            }
        }
        
        return await self.environment_manager.create_test_environment(env_name, config)


# Test cases for the environment manager
class TestEnvironmentManagerTests:
    """Test cases for the TestEnvironmentManager."""
    
    @pytest.fixture
    def environment_manager(self):
        """Create a test environment manager."""
        return TestEnvironmentManager()
    
    @pytest.fixture
    def environment_factory(self, environment_manager):
        """Create a test environment factory."""
        return TestEnvironmentFactory(environment_manager)
    
    @pytest.mark.asyncio
    async def test_create_basic_environment(self, environment_manager):
        """Test creating a basic test environment."""
        config = {
            'project_id': 'test-project-basic',
            'region': 'us-central1',
            'environment_type': 'testing'
        }
        
        env_config = await environment_manager.create_test_environment('basic-test', config)
        
        assert env_config['name'] == 'basic-test'
        assert env_config['project_id'] == 'test-project-basic'
        assert env_config['status'] == 'ready'
        assert os.path.exists(env_config['temp_directory'])
        
        # Clean up
        await environment_manager.cleanup_test_environment('basic-test')
    
    @pytest.mark.asyncio
    async def test_environment_lifecycle(self, environment_manager):
        """Test complete environment lifecycle."""
        config = {'project_id': 'test-project-lifecycle'}
        
        # Create environment
        env_config = await environment_manager.create_test_environment('lifecycle-test', config)
        assert env_config['status'] == 'ready'
        
        # List environments
        environments = await environment_manager.list_environments()
        assert 'lifecycle-test' in environments
        
        # Get environment config
        retrieved_config = await environment_manager.get_environment_config('lifecycle-test')
        assert retrieved_config['name'] == 'lifecycle-test'
        
        # Update environment
        await environment_manager.update_environment_config('lifecycle-test', {'updated': True})
        updated_config = await environment_manager.get_environment_config('lifecycle-test')
        assert updated_config['updated'] is True
        
        # Validate environment
        validation = await environment_manager.validate_environment('lifecycle-test')
        assert validation['valid'] is True
        
        # Clean up
        await environment_manager.cleanup_test_environment('lifecycle-test')
        
        # Verify cleanup
        environments = await environment_manager.list_environments()
        assert 'lifecycle-test' not in environments
    
    @pytest.mark.asyncio
    async def test_environment_factory(self, environment_factory):
        """Test environment factory methods."""
        # Test basic environment
        basic_env = await environment_factory.create_basic_test_environment('factory-basic')
        assert basic_env['environment_type'] == 'testing'
        assert 'test-service' in basic_env['services']
        
        # Test multi-service environment
        multi_env = await environment_factory.create_multi_service_environment(
            'factory-multi', 
            ['auth', 'core-game', 'task-mgmt']
        )
        assert len(multi_env['services']) == 3
        assert 'auth' in multi_env['services']
        
        # Test performance environment
        perf_env = await environment_factory.create_performance_test_environment('factory-perf')
        assert perf_env['environment_type'] == 'performance'
        assert perf_env['services']['performance-test-service']['memory'] == '2Gi'
        
        # Test security environment
        sec_env = await environment_factory.create_security_test_environment('factory-sec')
        assert sec_env['environment_type'] == 'security'
        assert sec_env['security']['enable_security_scanning'] is True
        
        # Clean up all environments
        await environment_factory.environment_manager.cleanup_all_environments()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])