"""
Tests for environment validator.
"""

import pytest
import os
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

from ..environment import EnvironmentValidator
from ...base import ValidationSeverity


class TestEnvironmentValidator:
    """Test cases for EnvironmentValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance for testing."""
        config = {
            'environment': 'development',
            'timeout_seconds': 10
        }
        return EnvironmentValidator(config)
    
    @pytest.fixture
    def production_validator(self):
        """Create production validator instance for testing."""
        config = {
            'environment': 'production',
            'timeout_seconds': 10
        }
        return EnvironmentValidator(config)
    
    @pytest.mark.asyncio
    async def test_successful_validation(self, validator):
        """Test successful environment validation."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'test-project'}), \
             patch.object(validator, '_check_secrets') as mock_secrets, \
             patch.object(validator, '_check_config_files') as mock_config, \
             patch.object(validator, '_check_resource_requirements') as mock_resources:
            
            mock_secrets.return_value = {'secret_status': {}, 'issues': []}
            mock_config.return_value = {'file_status': {}, 'issues': []}
            mock_resources.return_value = {'resource_info': {}, 'issues': []}
            
            result = await validator.validate()
            
            assert result.severity == ValidationSeverity.SUCCESS
            assert "All environment requirements for development are satisfied" in result.message
    
    @pytest.mark.asyncio
    async def test_unknown_environment(self):
        """Test validation with unknown environment."""
        config = {'environment': 'unknown'}
        validator = EnvironmentValidator(config)
        
        result = await validator.validate()
        
        assert result.severity == ValidationSeverity.WARNING
        assert "No specific requirements defined for environment: unknown" in result.message
    
    @pytest.mark.asyncio
    async def test_missing_required_env_vars(self, validator):
        """Test missing required environment variables."""
        with patch.dict(os.environ, {}, clear=True):
            result = await validator._check_environment_variables(
                validator.env_requirements['development']
            )
            
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'missing_required_env_var'
            assert result['issues'][0]['variable'] == 'GOOGLE_CLOUD_PROJECT'
    
    @pytest.mark.asyncio
    async def test_debug_enabled_in_production(self, production_validator):
        """Test DEBUG enabled in production."""
        with patch.dict(os.environ, {
            'GOOGLE_CLOUD_PROJECT': 'test-project',
            'ENVIRONMENT': 'production',
            'DEBUG': 'true'
        }):
            result = await production_validator._check_environment_variables(
                production_validator.env_requirements['production']
            )
            
            debug_issues = [i for i in result['issues'] if i['type'] == 'debug_enabled_in_production']
            assert len(debug_issues) == 1
            assert debug_issues[0]['variable'] == 'DEBUG'
    
    @pytest.mark.asyncio
    async def test_secrets_check_success(self, validator):
        """Test successful secrets check."""
        import json
        
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps([
                {'name': 'projects/test-project/secrets/database-url'},
                {'name': 'projects/test-project/secrets/api-keys'}
            ]).encode(),
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            env_reqs = {'required_secrets': ['database-url', 'api-keys']}
            result = await validator._check_secrets(env_reqs)
            
            assert result['secret_status']['database-url'] == 'exists'
            assert result['secret_status']['api-keys'] == 'exists'
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_missing_secrets(self, validator):
        """Test missing secrets."""
        import json
        
        mock_process = Mock()
        mock_process.returncode = 0
        mock_process.communicate = AsyncMock(return_value=(
            json.dumps([]).encode(),  # No secrets
            b''
        ))
        
        with patch('asyncio.create_subprocess_exec', return_value=mock_process), \
             patch('asyncio.wait_for', side_effect=lambda coro, timeout: coro):
            
            env_reqs = {'required_secrets': ['database-url', 'api-keys']}
            result = await validator._check_secrets(env_reqs)
            
            assert len(result['issues']) == 2
            assert all(issue['type'] == 'missing_secret' for issue in result['issues'])
    
    @pytest.mark.asyncio
    async def test_config_files_exist(self, validator):
        """Test configuration files exist."""
        test_files = ['firebase_config/firestore.rules']
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat:
            
            mock_stat.return_value.st_size = 100  # Non-empty file
            
            env_reqs = {'config_files': test_files}
            result = await validator._check_config_files(env_reqs)
            
            assert result['file_status']['firebase_config/firestore.rules'] == 'exists'
            assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_missing_config_files(self, validator):
        """Test missing configuration files."""
        test_files = ['firebase_config/firestore.rules', 'missing_file.json']
        
        with patch('pathlib.Path.exists', side_effect=lambda: False):
            env_reqs = {'config_files': test_files}
            result = await validator._check_config_files(env_reqs)
            
            assert len(result['issues']) == 2
            assert all(issue['type'] == 'missing_config_file' for issue in result['issues'])
    
    @pytest.mark.asyncio
    async def test_empty_config_file(self, validator):
        """Test empty configuration file."""
        test_files = ['empty_file.json']
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat:
            
            mock_stat.return_value.st_size = 0  # Empty file
            
            env_reqs = {'config_files': test_files}
            result = await validator._check_config_files(env_reqs)
            
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'empty_config_file'
    
    @pytest.mark.asyncio
    async def test_invalid_json_config(self, validator):
        """Test invalid JSON configuration file."""
        test_files = ['invalid.json']
        
        with patch('pathlib.Path.exists', return_value=True), \
             patch('pathlib.Path.is_file', return_value=True), \
             patch('pathlib.Path.stat') as mock_stat, \
             patch('builtins.open', mock_open(read_data='invalid json')):
            
            mock_stat.return_value.st_size = 12  # Non-empty file
            
            env_reqs = {'config_files': test_files}
            result = await validator._check_config_files(env_reqs)
            
            assert len(result['issues']) == 1
            assert result['issues'][0]['type'] == 'invalid_json_config'
    
    @pytest.mark.asyncio
    async def test_resource_requirements_valid(self, validator):
        """Test valid resource requirements."""
        env_reqs = {
            'min_resources': {
                'memory': '2Gi',
                'cpu': '1'
            }
        }
        
        result = await validator._check_resource_requirements(env_reqs)
        
        assert result['resource_info']['required_memory'] == '2Gi'
        assert result['resource_info']['required_cpu'] == '1'
        assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_resource_format(self, validator):
        """Test invalid resource format."""
        env_reqs = {
            'min_resources': {
                'memory': 'invalid',
                'cpu': 'invalid'
            }
        }
        
        result = await validator._check_resource_requirements(env_reqs)
        
        assert len(result['issues']) == 2
        memory_issues = [i for i in result['issues'] if i['type'] == 'invalid_memory_format']
        cpu_issues = [i for i in result['issues'] if i['type'] == 'invalid_cpu_format']
        assert len(memory_issues) == 1
        assert len(cpu_issues) == 1
    
    def test_memory_format_validation(self, validator):
        """Test memory format validation."""
        assert validator._validate_memory_format('2Gi') is True
        assert validator._validate_memory_format('1024Mi') is True
        assert validator._validate_memory_format('1G') is True
        assert validator._validate_memory_format('invalid') is False
    
    def test_cpu_format_validation(self, validator):
        """Test CPU format validation."""
        assert validator._validate_cpu_format('1') is True
        assert validator._validate_cpu_format('2') is True
        assert validator._validate_cpu_format('0.5') is True
        assert validator._validate_cpu_format('invalid') is False
    
    @pytest.mark.asyncio
    async def test_security_requirements(self, production_validator):
        """Test security requirements check."""
        env_reqs = {
            'security_requirements': {
                'https_only': True,
                'cors_restricted': True,
                'rate_limiting': True
            }
        }
        
        result = await production_validator._check_security_requirements(env_reqs)
        
        assert result['security_info']['https_only'] is True
        assert result['security_info']['cors_restricted'] is True
        assert result['security_info']['rate_limiting'] is True
        assert len(result['issues']) == 0
    
    def test_remediation_steps_generation(self, validator):
        """Test remediation steps generation."""
        issues = [
            {'type': 'missing_required_env_var', 'variable': 'GOOGLE_CLOUD_PROJECT'},
            {'type': 'missing_secret', 'secret': 'database-url'},
            {'type': 'missing_config_file', 'file': 'config.json'}
        ]
        env_reqs = {}
        
        steps = validator._get_remediation_steps(issues, env_reqs)
        
        assert any("Set required environment variables" in step for step in steps)
        assert any("Create required secrets" in step for step in steps)
        assert any("Fix configuration files" in step for step in steps)


class AsyncMock:
    """Simple async mock for testing."""
    def __init__(self, return_value=None):
        self.return_value = return_value
    
    async def __call__(self, *args, **kwargs):
        return self.return_value


if __name__ == '__main__':
    pytest.main([__file__])