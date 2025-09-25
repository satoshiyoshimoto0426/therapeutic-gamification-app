"""
Tests for cloud resource validator.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import json

from ..cloud_resource import CloudResourceValidator
from ...base import ValidationSeverity


class TestCloudResourceValidator:
    """Test cases for CloudResourceValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance for testing."""
        config = {
            'timeout_seconds': 10,
            'project_id': 'test-project',
            'region': 'us-central1',
            'required_apis': ['run.googleapis.com', 'cloudbuild.googleapis.com']
        }
        return CloudResourceValidator(config)
    
    @pytest.mark.asyncio
    async def test_successful_validation(self, validator):
        """Test successful cloud resource validation."""
        with patch.object(validator, '_check_gcloud_availability') as mock_gcloud, \
             patch.object(validator, '_check_project_config') as mock_project, \
             patch.object(validator, '_check_api_enablement') as mock_api, \
             patch.object(validator, '_check_quotas') as mock_quotas, \
             patch.object(validator, '_check_permissions') as mock_perms:
            
            # Mock all checks to return no issues
            mock_gcloud.return_value = {'gcloud_available': True, 'issues': []}
            mock_project.return_value = {'current_project': 'test-project', 'issues': []}
            mock_api.return_value = {'enabled_apis': ['run.googleapis.com'], 'issues': []}
            mock_quotas.return_value = {'quota_info': {}, 'issues': []}
            mock_perms.return_value = {'permissions_info': {}, 'issues': []}
            
            result = await validator.validate()
            
            assert result.severity == ValidationSeverity.SUCCESS
            assert "All cloud resource checks passed" in result.message
    
    @pytest.mark.asyncio
    async def test_gcloud_missing(self, validator):
        """Test validation when gcloud is missing."""
        with patch.object(validator, '_check_gcloud_availability') as mock_gcloud:
            mock_gcloud.return_value = {
                'gcloud_available': False,
                'issues': [{
                    'type': 'gcloud_missing',
                    'severity': 'critical',
                    'message': 'Google Cloud CLI not found'
                }]
            }
            
            result = await validator.validate()
            
            assert result.severity == ValidationSeverity.ERROR
            assert "cannot perform cloud resource validation" in result.message
    
    @pytest.mark.asyncio
    async def test_gcloud_availability_success(self, validator):
        """Test successful gcloud availability check."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'Google Cloud SDK 400.0.0', b''))
        
        mock_auth_process = Mock()
        mock_auth_process.returncode = 0
        mock_auth_process.communicate = AsyncMock(return_value=(
            json.dumps([{'account': 'test@example.com', 'status': 'ACTIVE'}]).encode(),
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', side_effect=[mock_process, mock_auth_process]), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_gcloud_availability()
            
            assert result['gcloud_available'] is True
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_gcloud_not_found(self, validator):
        """Test gcloud CLI not found."""
        with patch('asyncio.create_subprocess_exec', side_effect=FileNotFoundError()):
            result = await validator._check_gcloud_availability()
            
            assert result['gcloud_available'] is False
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'gcloud_missing'
    
    @pytest.mark.asyncio
    async def test_project_config_success(self, validator):
        """Test successful project configuration check."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'test-project', b''))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_project_config()
            
            assert result['current_project'] == 'test-project'
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_no_project_set(self, validator):
        """Test no project set."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'(unset)', b''))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_project_config()
            
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'no_project_set'
    
    @pytest.mark.asyncio
    async def test_api_enablement_success(self, validator):
        """Test successful API enablement check."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps([
                {'name': 'run.googleapis.com'},
                {'name': 'cloudbuild.googleapis.com'}
            ]).encode(),
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_api_enablement()
            
            assert 'run.googleapis.com' in result['enabled_apis']
            assert 'cloudbuild.googleapis.com' in result['enabled_apis']
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_api_not_enabled(self, validator):
        """Test API not enabled."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps([{'name': 'run.googleapis.com'}]).encode(),  # Missing cloudbuild
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_api_enablement()
            
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'api_not_enabled'
            assert result['issues'][0]['api'] == 'cloudbuild.googleapis.com'
    
    @pytest.mark.asyncio
    async def test_quota_check_success(self, validator):
        """Test successful quota check."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps([
                {'metadata': {'name': 'service1'}},
                {'metadata': {'name': 'service2'}}
            ]).encode(),
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_quotas()
            
            assert result['quota_info']['cloud_run_services'] == 2
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_quota_warning(self, validator):
        """Test quota warning for high usage."""
        # Create mock data for 85 services (above warning threshold)
        services_data = [{'metadata': {'name': f'service{i}'}} for i in range(85)]
        
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps(services_data).encode(),
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_quotas()
            
            assert result['quota_info']['cloud_run_services'] == 85
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'quota_warning'
    
    @pytest.mark.asyncio
    async def test_permissions_success(self, validator):
        """Test successful permissions check."""
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(b'[]', b''))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_permissions()
            
            assert all(status == 'accessible' for status in result['permissions_info'].values())
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_permission_denied(self, validator):
        """Test permission denied."""
        mock_process = Mock()
        mock_process.returncode = 1
        mock_process.communicate = AsyncMock(return_value=(b'', b'permission denied'))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            result = await validator._check_permissions()
            
            assert len(result['issues']) == 3  # Three services checked
            assert all(issue['type'] == 'permission_denied' for issue in result['issues'])
    
    def test_remediation_steps_generation(self, validator):
        """Test remediation steps generation."""
        issues = [
            {'type': 'gcloud_missing', 'severity': 'critical'},
            {'type': 'no_project_set', 'severity': 'error'},
            {'type': 'api_not_enabled', 'severity': 'error', 'api': 'run.googleapis.com'}
        ]
        
        steps = validator._get_remediation_steps(issues)
        
        assert any("Install and configure Google Cloud CLI" in step for step in steps)
        assert any("Set the correct Google Cloud project" in step for step in steps)
        assert any("gcloud services enable run.googleapis.com" in step for step in steps)


if __name__ == '__main__':
    pytest.main([__file__])