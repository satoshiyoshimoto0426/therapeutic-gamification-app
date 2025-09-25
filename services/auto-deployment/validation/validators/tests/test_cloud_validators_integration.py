"""
Integration tests for cloud resource and authentication validators.
"""

import pytest
import asyncio
import os
import json
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

from ..cloud_resource import CloudResourceValidator
from ..authentication import AuthenticationValidator
from ..environment import EnvironmentValidator
from ...base import ValidationSeverity


class TestCloudResourceValidatorIntegration:
    """Integration tests for CloudResourceValidator."""
    
    @pytest.fixture
    def validator_config(self):
        """Basic validator configuration."""
        return {
            'project_id': 'test-project',
            'region': 'us-central1',
            'check_quotas': True,
            'verify_permissions': True,
            'timeout_seconds': 30
        }
    
    @pytest.fixture
    def validator(self, validator_config):
        """Create CloudResourceValidator instance."""
        return CloudResourceValidator(validator_config)
    
    @pytest.mark.asyncio
    async def test_successful_cloud_resource_validation(self, validator):
        """Test successful cloud resource validation."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock gcloud version check
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b'Google Cloud SDK 400.0.0', b'')
            mock_subprocess.return_value = mock_process
            
            # Mock auth list
            auth_data = [{'account': 'test@example.com', 'status': 'ACTIVE'}]
            mock_process.communicate.side_effect = [
                (b'Google Cloud SDK 400.0.0', b''),  # version
                (json.dumps(auth_data).encode(), b''),  # auth list
                (b'test-project', b''),  # project config
                (json.dumps([{'name': 'run.googleapis.com'}]).encode(), b''),  # services list
                (json.dumps([]).encode(), b''),  # cloud run services
                (json.dumps([]).encode(), b''),  # run services list
                (json.dumps([]).encode(), b''),  # builds list
                (json.dumps([]).encode(), b'')   # secrets list
            ]
            
            result = await validator.validate()
            
            assert result.severity == ValidationSeverity.SUCCESS
            assert "All cloud resource checks passed" in result.message
            assert 'gcloud' in result.details
            assert 'project' in result.details
    
    @pytest.mark.asyncio
    async def test_gcloud_not_available(self, validator):
        """Test when gcloud CLI is not available."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_subprocess.side_effect = FileNotFoundError()
            
            result = await validator.validate()
            
            assert result.severity == ValidationSeverity.ERROR
            assert "Google Cloud CLI not available" in result.message
            assert any(
                issue.get('type') == 'gcloud_missing' 
                for issue in result.details.get('gcloud', {}).get('issues', [])
            )
    
    @pytest.mark.asyncio
    async def test_api_not_enabled(self, validator):
        """Test when required APIs are not enabled."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            # Mock responses - missing required API
            auth_data = [{'account': 'test@example.com', 'status': 'ACTIVE'}]
            services_data = [{'name': 'compute.googleapis.com'}]  # Missing run.googleapis.com
            
            mock_process.communicate.side_effect = [
                (b'Google Cloud SDK 400.0.0', b''),  # version
                (json.dumps(auth_data).encode(), b''),  # auth list
                (b'test-project', b''),  # project config
                (json.dumps(services_data).encode(), b''),  # services list
                (json.dumps([]).encode(), b''),  # quotas
                (json.dumps([]).encode(), b''),  # permissions
                (json.dumps([]).encode(), b''),
                (json.dumps([]).encode(), b'')
            ]
            
            result = await validator.validate()
            
            assert result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            assert any(
                issue.get('type') == 'api_not_enabled' 
                for issue in result.details.get('apis', {}).get('issues', [])
            )
    
    @pytest.mark.asyncio
    async def test_permission_denied(self, validator):
        """Test when permissions are insufficient."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            mock_process = AsyncMock()
            mock_subprocess.return_value = mock_process
            
            # Mock successful initial checks but permission failure
            auth_data = [{'account': 'test@example.com', 'status': 'ACTIVE'}]
            services_data = [{'name': 'run.googleapis.com'}, {'name': 'cloudbuild.googleapis.com'}]
            
            def mock_communicate(*args, **kwargs):
                # Different responses based on call order
                responses = [
                    (b'Google Cloud SDK 400.0.0', b''),  # version
                    (json.dumps(auth_data).encode(), b''),  # auth list
                    (b'test-project', b''),  # project config
                    (json.dumps(services_data).encode(), b''),  # services list
                    (json.dumps([]).encode(), b''),  # quotas
                ]
                
                if hasattr(mock_communicate, 'call_count'):
                    mock_communicate.call_count += 1
                else:
                    mock_communicate.call_count = 0
                
                if mock_communicate.call_count < len(responses):
                    mock_process.returncode = 0
                    return responses[mock_communicate.call_count]
                else:
                    # Permission denied for subsequent calls
                    mock_process.returncode = 1
                    return (b'', b'ERROR: (gcloud.run.services.list) User does not have permission')
            
            mock_process.communicate.side_effect = mock_communicate
            
            result = await validator.validate()
            
            assert result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]


class TestAuthenticationValidatorIntegration:
    """Integration tests for AuthenticationValidator."""
    
    @pytest.fixture
    def validator_config(self):
        """Basic validator configuration."""
        return {
            'project_id': 'test-project',
            'verify_service_accounts': True,
            'check_api_keys': True,
            'check_environment_vars': True,
            'check_github_auth': True,
            'timeout_seconds': 30
        }
    
    @pytest.fixture
    def validator(self, validator_config):
        """Create AuthenticationValidator instance."""
        return AuthenticationValidator(validator_config)
    
    @pytest.mark.asyncio
    async def test_successful_authentication_validation(self, validator):
        """Test successful authentication validation."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess, \
             patch.dict(os.environ, {
                 'GOOGLE_APPLICATION_CREDENTIALS': '/tmp/test-creds.json',
                 'GOOGLE_CLOUD_PROJECT': 'test-project',
                 'GITHUB_TOKEN': 'ghp_test_token'
             }), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open') as mock_open:
            
            # Mock credentials file
            mock_creds = {
                'type': 'service_account',
                'project_id': 'test-project',
                'private_key': 'test-key',
                'client_email': 'test@test-project.iam.gserviceaccount.com'
            }
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_creds)
            
            # Mock subprocess calls
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            auth_data = [{'account': 'test@example.com', 'status': 'ACTIVE'}]
            service_accounts = [{'email': 'compute@test-project.iam.gserviceaccount.com'}]
            
            mock_process.communicate.side_effect = [
                (json.dumps(auth_data).encode(), b''),  # auth list
                (b'test-token', b''),  # ADC token
                (json.dumps(service_accounts).encode(), b''),  # service accounts
                (json.dumps([]).encode(), b''),  # service account keys
                (b'', b''),  # GitHub CLI auth status
                (json.dumps([]).encode(), b''),  # Cloud Run permission test
                (json.dumps([]).encode(), b''),  # Cloud Build permission test
                (json.dumps([]).encode(), b''),  # Secret Manager permission test
                (json.dumps([]).encode(), b'')   # IAM permission test
            ]
            
            result = await validator.validate()
            
            assert result.severity == ValidationSeverity.SUCCESS
            assert "All authentication and authorization checks passed" in result.message
    
    @pytest.mark.asyncio
    async def test_missing_credentials(self, validator):
        """Test when credentials are missing."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess, \
             patch.dict(os.environ, {}, clear=True):
            
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process
            
            # Mock no active auth
            mock_process.communicate.side_effect = [
                (json.dumps([]).encode(), b''),  # no active auth
                (b'', b'No credentials found'),  # ADC failure
                (json.dumps([]).encode(), b''),  # service accounts
                (b'', b'not logged in'),  # GitHub CLI not authenticated
                (b'', b'permission denied'),  # permission failures
                (b'', b'permission denied'),
                (b'', b'permission denied'),
                (b'', b'permission denied')
            ]
            
            result = await validator.validate()
            
            assert result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            assert any(
                issue.get('type') == 'no_active_auth' 
                for issue in result.details.get('gcloud_auth', {}).get('issues', [])
            )
    
    @pytest.mark.asyncio
    async def test_invalid_credentials_file(self, validator):
        """Test when credentials file is invalid."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess, \
             patch.dict(os.environ, {
                 'GOOGLE_APPLICATION_CREDENTIALS': '/tmp/invalid-creds.json',
                 'GOOGLE_CLOUD_PROJECT': 'test-project'
             }), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open') as mock_open:
            
            # Mock invalid JSON in credentials file
            mock_open.return_value.__enter__.return_value.read.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
            
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            auth_data = [{'account': 'test@example.com', 'status': 'ACTIVE'}]
            mock_process.communicate.side_effect = [
                (json.dumps(auth_data).encode(), b''),  # auth list
                (b'test-token', b''),  # ADC token
                (json.dumps([]).encode(), b''),  # service accounts
                (b'', b''),  # GitHub CLI
                (json.dumps([]).encode(), b''),  # permissions
                (json.dumps([]).encode(), b''),
                (json.dumps([]).encode(), b''),
                (json.dumps([]).encode(), b'')
            ]
            
            result = await validator.validate()
            
            assert result.severity in [ValidationSeverity.ERROR, ValidationSeverity.WARNING]
            assert any(
                issue.get('type') == 'invalid_credentials_file' 
                for issue in result.details.get('api_credentials', {}).get('issues', [])
            )


class TestEnvironmentValidatorIntegration:
    """Integration tests for EnvironmentValidator."""
    
    @pytest.fixture
    def validator_config(self):
        """Basic validator configuration."""
        return {
            'environment': 'production',
            'check_secrets': True,
            'check_env_vars': True,
            'check_config_files': True,
            'timeout_seconds': 30
        }
    
    @pytest.fixture
    def validator(self, validator_config):
        """Create EnvironmentValidator instance."""
        return EnvironmentValidator(validator_config)
    
    @pytest.mark.asyncio
    async def test_successful_production_validation(self, validator):
        """Test successful production environment validation."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess, \
             patch.dict(os.environ, {
                 'GOOGLE_CLOUD_PROJECT': 'test-project',
                 'ENVIRONMENT': 'production',
                 'LOG_LEVEL': 'INFO'
             }), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open') as mock_open:
            
            # Mock file stats
            mock_stat.return_value.st_size = 100
            
            # Mock config file content
            mock_open.return_value.__enter__.return_value.read.return_value = '{"valid": "json"}'
            
            # Mock secrets list
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            secrets_data = [
                {'name': 'projects/test-project/secrets/database-url'},
                {'name': 'projects/test-project/secrets/api-keys'},
                {'name': 'projects/test-project/secrets/auth-secrets'}
            ]
            mock_process.communicate.return_value = (json.dumps(secrets_data).encode(), b'')
            
            result = await validator.validate()
            
            assert result.severity == ValidationSeverity.SUCCESS
            assert "All environment requirements for production are satisfied" in result.message
    
    @pytest.mark.asyncio
    async def test_missing_production_requirements(self, validator):
        """Test when production requirements are missing."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess, \
             patch.dict(os.environ, {
                 'GOOGLE_CLOUD_PROJECT': 'test-project',
                 'DEBUG': 'true'  # Should not be enabled in production
             }), \
             patch('pathlib.Path.exists', return_value=False):
            
            # Mock missing secrets
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            mock_process.communicate.return_value = (json.dumps([]).encode(), b'')
            
            result = await validator.validate()
            
            assert result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            
            # Check for missing environment variable
            env_issues = result.details.get('environment_variables', {}).get('issues', [])
            assert any(
                issue.get('type') == 'missing_required_env_var' and issue.get('variable') == 'ENVIRONMENT'
                for issue in env_issues
            )
            
            # Check for DEBUG enabled in production
            assert any(
                issue.get('type') == 'debug_enabled_in_production'
                for issue in env_issues
            )
    
    @pytest.mark.asyncio
    async def test_missing_config_files(self, validator):
        """Test when required config files are missing."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess, \
             patch.dict(os.environ, {
                 'GOOGLE_CLOUD_PROJECT': 'test-project',
                 'ENVIRONMENT': 'production'
             }), \
             patch('pathlib.Path.exists', return_value=False):
            
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            mock_process.communicate.return_value = (json.dumps([]).encode(), b'')
            
            result = await validator.validate()
            
            assert result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            
            config_issues = result.details.get('config_files', {}).get('issues', [])
            assert any(
                issue.get('type') == 'missing_config_file'
                for issue in config_issues
            )


class TestValidatorIntegration:
    """Integration tests for all validators working together."""
    
    @pytest.mark.asyncio
    async def test_complete_validation_pipeline(self):
        """Test complete validation pipeline with all validators."""
        # Configuration for all validators
        cloud_config = {
            'project_id': 'test-project',
            'region': 'us-central1',
            'check_quotas': False,  # Skip for faster test
            'verify_permissions': False
        }
        
        auth_config = {
            'project_id': 'test-project',
            'verify_service_accounts': False,  # Skip for faster test
            'check_api_keys': True,
            'check_environment_vars': True,
            'check_github_auth': False
        }
        
        env_config = {
            'environment': 'development',
            'check_secrets': False,  # Skip for faster test
            'check_env_vars': True,
            'check_config_files': False
        }
        
        # Create validators
        cloud_validator = CloudResourceValidator(cloud_config)
        auth_validator = AuthenticationValidator(auth_config)
        env_validator = EnvironmentValidator(env_config)
        
        with patch('asyncio.create_subprocess_exec') as mock_subprocess, \
             patch.dict(os.environ, {
                 'GOOGLE_CLOUD_PROJECT': 'test-project',
                 'GOOGLE_APPLICATION_CREDENTIALS': '/tmp/test-creds.json'
             }), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open') as mock_open:
            
            # Mock credentials file
            mock_creds = {
                'type': 'service_account',
                'project_id': 'test-project',
                'private_key': 'test-key',
                'client_email': 'test@test-project.iam.gserviceaccount.com'
            }
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(mock_creds)
            
            # Mock subprocess responses
            mock_process = AsyncMock()
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            auth_data = [{'account': 'test@example.com', 'status': 'ACTIVE'}]
            services_data = [{'name': 'run.googleapis.com'}, {'name': 'cloudbuild.googleapis.com'}]
            
            mock_process.communicate.side_effect = [
                # Cloud resource validator calls
                (b'Google Cloud SDK 400.0.0', b''),
                (json.dumps(auth_data).encode(), b''),
                (b'test-project', b''),
                (json.dumps(services_data).encode(), b''),
                
                # Authentication validator calls
                (json.dumps(auth_data).encode(), b''),
                (b'test-token', b''),
                
                # Environment validator calls (minimal for development)
            ]
            
            # Run all validators
            cloud_result = await cloud_validator.validate()
            auth_result = await auth_validator.validate()
            env_result = await env_validator.validate()
            
            # All should pass for this configuration
            assert cloud_result.severity == ValidationSeverity.SUCCESS
            assert auth_result.severity == ValidationSeverity.SUCCESS
            assert env_result.severity == ValidationSeverity.SUCCESS
    
    @pytest.mark.asyncio
    async def test_validation_failure_cascade(self):
        """Test how validation failures cascade through the system."""
        # Create validators with strict requirements
        cloud_config = {'project_id': 'test-project', 'verify_permissions': True}
        auth_config = {'check_environment_vars': True}
        env_config = {'environment': 'production'}
        
        cloud_validator = CloudResourceValidator(cloud_config)
        auth_validator = AuthenticationValidator(auth_config)
        env_validator = EnvironmentValidator(env_config)
        
        with patch('asyncio.create_subprocess_exec') as mock_subprocess, \
             patch.dict(os.environ, {}, clear=True):  # Clear all env vars
            
            # Mock failures
            mock_process = AsyncMock()
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process
            mock_process.communicate.return_value = (b'', b'Permission denied')
            
            # Run validators
            cloud_result = await cloud_validator.validate()
            auth_result = await auth_validator.validate()
            env_result = await env_validator.validate()
            
            # All should fail due to missing configuration
            assert cloud_result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            assert auth_result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            assert env_result.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]
            
            # Check that remediation steps are provided
            assert len(cloud_result.remediation_steps) > 0
            assert len(auth_result.remediation_steps) > 0
            assert len(env_result.remediation_steps) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])