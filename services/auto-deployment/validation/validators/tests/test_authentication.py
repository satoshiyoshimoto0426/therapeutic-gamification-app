"""
Tests for authentication validator.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json
import os

from ..authentication import AuthenticationValidator
from ...base import ValidationSeverity


class TestAuthenticationValidator:
    """Test cases for AuthenticationValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance for testing."""
        config = {
            'timeout_seconds': 5,
            'project_id': 'test-project',
            'required_credentials': ['GOOGLE_APPLICATION_CREDENTIALS', 'GOOGLE_CLOUD_PROJECT']
        }
        return AuthenticationValidator(config)
    
    @pytest.mark.asyncio
    async def test_successful_validation(self, validator):
        """Test successful authentication validation."""
        with patch.object(validator, '_check_gcloud_authentication') as mock_gcloud, \
             patch.object(validator, '_check_service_accounts') as mock_sa, \
             patch.object(validator, '_check_api_credentials') as mock_api, \
             patch.object(validator, '_check_credential_environment_vars') as mock_env, \
             patch.object(validator, '_check_github_authentication') as mock_github, \
             patch.object(validator, '_check_deployment_permissions') as mock_perms:
            
            # Mock all checks to return no issues
            mock_gcloud.return_value = {'auth_info': {}, 'issues': []}
            mock_sa.return_value = {'service_account_info': {}, 'issues': []}
            mock_api.return_value = {'credential_info': {}, 'issues': []}
            mock_env.return_value = {'env_var_status': {}, 'issues': []}
            mock_github.return_value = {'github_info': {}, 'issues': []}
            mock_perms.return_value = {'permission_info': {}, 'issues': []}
            
            result = await validator.validate()
            
            assert result.severity == ValidationSeverity.SUCCESS
            assert "All authentication and authorization checks passed" in result.message
    
    @pytest.mark.asyncio
    async def test_critical_issues(self, validator):
        """Test validation with critical issues."""
        with patch.object(validator, '_check_gcloud_authentication') as mock_gcloud:
            mock_gcloud.return_value = {
                'auth_info': {},
                'issues': [{
                    'type': 'gcloud_not_found',
                    'severity': 'critical',
                    'message': 'Google Cloud CLI not found'
                }]
            }
            
            # Mock other methods to return no issues
            with patch.object(validator, '_check_service_accounts', return_value={'service_account_info': {}, 'issues': []}), \
                 patch.object(validator, '_check_api_credentials', return_value={'credential_info': {}, 'issues': []}), \
                 patch.object(validator, '_check_credential_environment_vars', return_value={'env_var_status': {}, 'issues': []}), \
                 patch.object(validator, '_check_github_authentication', return_value={'github_info': {}, 'issues': []}), \
                 patch.object(validator, '_check_deployment_permissions', return_value={'permission_info': {}, 'issues': []}):
                
                result = await validator.validate()
                
                assert result.severity == ValidationSeverity.CRITICAL
                assert "Critical authentication issues found" in result.message
                assert "Install Google Cloud CLI (gcloud)" in result.remediation_steps
    
    @pytest.mark.asyncio
    async def test_gcloud_authentication_success(self, validator):
        """Test successful gcloud authentication check."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps([{'account': 'test@example.com', 'status': 'ACTIVE'}]).encode(),
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro), \
             patch.object(validator, '_check_application_default_credentials', return_value={'status': {}, 'issues': []}):
            
            result = await validator._check_gcloud_authentication()
            
            assert result['auth_info']['active_accounts'] == ['test@example.com']
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_gcloud_not_found(self, validator):
        """Test gcloud CLI not found."""
        with patch('asyncio.create_subprocess_exec', side_effect=FileNotFoundError()):
            result = await validator._check_gcloud_authentication()
            
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'gcloud_not_found'
            assert result['issues'][0]['severity'] == 'critical'
    
    @pytest.mark.asyncio
    async def test_no_active_authentication(self, validator):
        """Test no active authentication."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps([{'account': 'test@example.com', 'status': 'INACTIVE'}]).encode(),
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro), \
             patch.object(validator, '_check_application_default_credentials', return_value={'status': {}, 'issues': []}):
            
            result = await validator._check_gcloud_authentication()
            
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'no_active_auth'
            assert result['issues'][0]['severity'] == 'critical'
    
    @pytest.mark.asyncio
    async def test_service_accounts_check(self, validator):
        """Test service accounts check."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps([
                {'email': 'compute@test-project.iam.gserviceaccount.com'},
                {'email': 'deployment@test-project.iam.gserviceaccount.com'}
            ]).encode(),
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro), \
             patch.object(validator, '_check_service_account_keys', return_value={'issues': []}):
            
            result = await validator._check_service_accounts()
            
            assert 'compute@test-project.iam.gserviceaccount.com' in result['service_account_info']['available_accounts']
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_api_credentials_check_with_file(self, validator):
        """Test API credentials check with credentials file."""
        test_creds = {
            'type': 'service_account',
            'project_id': 'test-project',
            'private_key': 'test-key',
            'client_email': 'test@test-project.iam.gserviceaccount.com'
        }
        
        with patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/creds.json'}), \
             patch('pathlib.Path.exists', return_value=True), \
             patch('builtins.open', mock_open_json(test_creds)):
            
            result = await validator._check_api_credentials()
            
            assert result['credential_info']['google_credentials_file']['type'] == 'service_account'
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_missing_credentials_file(self, validator):
        """Test missing credentials file."""
        with patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/missing.json'}), \
             patch('pathlib.Path.exists', return_value=False):
            
            result = await validator._check_api_credentials()
            
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'credentials_file_not_found'
            assert result['issues'][0]['severity'] == 'error'
    
    @pytest.mark.asyncio
    async def test_environment_variables_check(self, validator):
        """Test environment variables check."""
        with patch.dict(os.environ, {
            'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/creds.json',
            'GOOGLE_CLOUD_PROJECT': 'test-project'
        }):
            result = await validator._check_credential_environment_vars()
            
            assert result['env_var_status']['GOOGLE_APPLICATION_CREDENTIALS'] == 'present'
            assert result['env_var_status']['GOOGLE_CLOUD_PROJECT'] == 'present'
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_missing_environment_variables(self, validator):
        """Test missing environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            result = await validator._check_credential_environment_vars()
            
            assert len(result['issues']) == 2  # Both required vars missing
            assert all(issue['type'] == 'missing_credential_env_var' for issue in result['issues'])
            assert all(issue['severity'] == 'error' for issue in result['issues'])
    
    @pytest.mark.asyncio
    async def test_github_authentication_success(self, validator):
        """Test successful GitHub authentication."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'Logged in to github.com', b''))
        
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'ghp_test_token'}), \
             patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_github_authentication()
            
            assert result['github_info']['token_available'] is True
            assert result['github_info']['gh_cli_authenticated'] is True
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_missing_github_token(self, validator):
        """Test missing GitHub token."""
        with patch.dict(os.environ, {}, clear=True):
            result = await validator._check_github_authentication()
            
            assert result['github_info']['token_available'] is False
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'missing_github_token'
            assert result['issues'][0]['severity'] == 'warning'
    
    @pytest.mark.asyncio
    async def test_deployment_permissions_success(self, validator):
        """Test successful deployment permissions check."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'[]', b''))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_deployment_permissions()
            
            assert all(status == 'accessible' for status in result['permission_info'].values())
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_insufficient_permissions(self, validator):
        """Test insufficient permissions."""
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b'', b'permission denied'))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_deployment_permissions()
            
            assert len(result['issues']) == 4  # One for each service
            assert all(issue['type'] == 'insufficient_permissions' for issue in result['issues'])
            assert all(issue['severity'] == 'error' for issue in result['issues'])
    
    def test_remediation_steps_generation(self, validator):
        """Test remediation steps generation."""
        issues = [
            {'type': 'gcloud_not_found', 'severity': 'critical'},
            {'type': 'no_active_auth', 'severity': 'critical'},
            {'type': 'missing_github_token', 'severity': 'warning'}
        ]
        
        steps = validator._get_remediation_steps(issues)
        
        assert "Install Google Cloud CLI (gcloud)" in steps
        assert "Run 'gcloud auth login' to authenticate" in steps
        assert "Set GITHUB_TOKEN environment variable with a valid GitHub token" in steps


def mock_open_json(data):
    """Helper to mock open() for JSON files."""
    from unittest.mock import mock_open
    return mock_open(read_data=json.dumps(data))


if __name__ == '__main__':
    pytest.main([__file__])