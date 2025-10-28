"""
Tests for security validator.
"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import tempfile
from pathlib import Path

from security import SecurityValidator
from base import ValidationSeverity


class TestSecurityValidator:
    """Test SecurityValidator class."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        config = {
            'run_vulnerability_scan': False,
            'check_dependencies': True,
            'severity_threshold': 'high',
            'project_root': '/test/path'
        }
        validator = SecurityValidator(config)
        
        assert validator.run_vulnerability_scan is False
        assert validator.check_dependencies is True
        assert validator.severity_threshold == 'high'
        assert validator.project_root == Path('/test/path')
    
    def test_validator_default_config(self):
        """Test validator with default configuration."""
        validator = SecurityValidator()
        
        assert validator.run_vulnerability_scan is True
        assert validator.check_dependencies is True
        assert validator.severity_threshold == 'medium'
        assert validator.project_root == Path('.')
    
    def test_description_property(self):
        """Test description property."""
        validator = SecurityValidator()
        assert "security" in validator.description.lower()
        assert "vulnerability" in validator.description.lower()
    
    def test_get_secret_patterns(self):
        """Test secret patterns generation."""
        validator = SecurityValidator()
        patterns = validator._get_secret_patterns()
        
        assert 'api_key' in patterns
        assert 'password' in patterns
        assert 'private_key' in patterns
        assert 'aws_access_key' in patterns
        assert isinstance(patterns['api_key'], str)
    
    @pytest.mark.asyncio
    async def test_check_secrets_no_secrets(self):
        """Test secret checking with no secrets found."""
        validator = SecurityValidator()
        
        with patch.object(validator.project_root, 'rglob') as mock_rglob:
            mock_file = MagicMock()
            mock_file.relative_to.return_value = Path('test.py')
            mock_rglob.return_value = [mock_file]
            
            with patch('builtins.open', mock_open(read_data='print("Hello World")\n')):
                with patch.object(validator, '_should_exclude_file', return_value=False):
                    result = await validator._check_secrets()
        
        assert result is not None
        assert result['files_scanned'] == 1
        assert result['secrets_found'] == 0
        assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    async def test_check_secrets_with_secrets(self):
        """Test secret checking with secrets found."""
        validator = SecurityValidator()
        
        code_with_secret = '''
API_KEY = "sk-1234567890abcdef1234567890abcdef"
password = "mysecretpassword123"
'''
        
        with patch.object(validator.project_root, 'rglob') as mock_rglob:
            mock_file = MagicMock()
            mock_file.relative_to.return_value = Path('config.py')
            mock_rglob.return_value = [mock_file]
            
            with patch('builtins.open', mock_open(read_data=code_with_secret)):
                with patch.object(validator, '_should_exclude_file', return_value=False):
                    result = await validator._check_secrets()
        
        assert result is not None
        assert result['files_scanned'] == 1
        assert result['secrets_found'] >= 1
        assert len(result['issues']) >= 1
        assert result['issues'][0]['type'] == 'secret_detected'
        assert result['issues'][0]['severity'] == 'critical'
    
    @pytest.mark.asyncio
    @patch('services.auto_deployment.validation.validators.security.subprocess.run')
    async def test_run_vulnerability_scan_success(self, mock_subprocess):
        """Test successful vulnerability scan."""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout='{"results": []}',
            stderr=''
        )
        
        validator = SecurityValidator()
        result = await validator._run_vulnerability_scan()
        
        assert result is not None
        assert result['total_issues'] == 0
        assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    @patch('services.auto_deployment.validation.validators.security.subprocess.run')
    async def test_run_vulnerability_scan_with_issues(self, mock_subprocess):
        """Test vulnerability scan with issues found."""
        bandit_output = {
            "results": [{
                "filename": "test.py",
                "line_number": 10,
                "issue_severity": "HIGH",
                "issue_confidence": "HIGH",
                "issue_text": "Use of insecure MD5 hash function",
                "test_id": "B303",
                "test_name": "blacklist"
            }]
        }
        
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout=str(bandit_output).replace("'", '"'),
            stderr=''
        )
        
        validator = SecurityValidator()
        
        with patch('json.loads', return_value=bandit_output):
            result = await validator._run_vulnerability_scan()
        
        assert result is not None
        assert result['total_issues'] == 1
        assert len(result['issues']) == 1
        assert result['issues'][0]['type'] == 'vulnerability'
        assert result['issues'][0]['severity'] == 'high'
    
    @pytest.mark.asyncio
    @patch('services.auto_deployment.validation.validators.security.subprocess.run')
    async def test_run_vulnerability_scan_tool_missing(self, mock_subprocess):
        """Test vulnerability scan when bandit is not installed."""
        mock_subprocess.side_effect = FileNotFoundError()
        
        validator = SecurityValidator()
        result = await validator._run_vulnerability_scan()
        
        assert result is not None
        assert result['total_issues'] == 0
        assert len(result['issues']) == 1
        assert result['issues'][0]['type'] == 'tool_missing'
        assert result['issues'][0]['severity'] == 'warning'
    
    @pytest.mark.asyncio
    @patch('services.auto_deployment.validation.validators.security.subprocess.run')
    async def test_check_dependencies_success(self, mock_subprocess):
        """Test successful dependency vulnerability check."""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout='[]',
            stderr=''
        )
        
        validator = SecurityValidator()
        result = await validator._check_dependencies()
        
        assert result is not None
        assert result['total_vulnerabilities'] == 0
        assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    @patch('services.auto_deployment.validation.validators.security.subprocess.run')
    async def test_check_dependencies_with_vulnerabilities(self, mock_subprocess):
        """Test dependency check with vulnerabilities found."""
        safety_output = [{
            "package": "django",
            "installed_version": "2.0.0",
            "vulnerability_id": "12345",
            "advisory": "Django has a critical SQL injection vulnerability",
            "more_info_url": "https://example.com/vuln/12345"
        }]
        
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout=str(safety_output).replace("'", '"'),
            stderr=''
        )
        
        validator = SecurityValidator()
        
        with patch('json.loads', return_value=safety_output):
            result = await validator._check_dependencies()
        
        assert result is not None
        assert result['total_vulnerabilities'] == 1
        assert len(result['issues']) == 1
        assert result['issues'][0]['type'] == 'dependency_vulnerability'
        assert result['issues'][0]['severity'] == 'critical'
    
    @pytest.mark.asyncio
    async def test_check_insecure_configurations(self):
        """Test insecure configuration checking."""
        validator = SecurityValidator()
        
        insecure_config = '''
DEBUG = True
SSL_VERIFY = False
'''
        
        with patch.object(validator.project_root, 'rglob') as mock_rglob:
            mock_file = MagicMock()
            mock_file.relative_to.return_value = Path('settings.py')
            mock_rglob.return_value = [mock_file]
            
            with patch('builtins.open', mock_open(read_data=insecure_config)):
                with patch.object(validator, '_should_exclude_file', return_value=False):
                    result = await validator._check_insecure_configurations()
        
        assert result is not None
        assert result['total_issues'] >= 1
        assert len(result['issues']) >= 1
        
        # Check for debug mode issue
        debug_issues = [i for i in result['issues'] if 'debug' in i['message'].lower()]
        assert len(debug_issues) >= 1
        assert debug_issues[0]['severity'] == 'medium'
    
    @pytest.mark.asyncio
    async def test_validate_all_checks_pass(self):
        """Test validation when all checks pass."""
        validator = SecurityValidator({
            'run_vulnerability_scan': False,
            'check_dependencies': False
        })
        
        with patch.object(validator, '_check_secrets') as mock_secrets, \
             patch.object(validator, '_check_insecure_configurations') as mock_config:
            
            mock_secrets.return_value = {'issues': []}
            mock_config.return_value = {'issues': []}
            
            result = await validator.validate()
            
            assert result.success is True
            assert result.severity == ValidationSeverity.INFO
            assert "passed" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_with_critical_issues(self):
        """Test validation with critical issues."""
        validator = SecurityValidator({
            'run_vulnerability_scan': False,
            'check_dependencies': False
        })
        
        with patch.object(validator, '_check_secrets') as mock_secrets, \
             patch.object(validator, '_check_insecure_configurations') as mock_config:
            
            mock_secrets.return_value = {
                'issues': [{
                    'type': 'secret_detected',
                    'severity': 'critical',
                    'message': 'API key found'
                }]
            }
            mock_config.return_value = {'issues': []}
            
            result = await validator.validate()
            
            assert result.success is False
            assert result.severity == ValidationSeverity.CRITICAL
            assert "critical" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_validate_exception_handling(self):
        """Test validation exception handling."""
        validator = SecurityValidator()
        
        with patch.object(validator, '_check_secrets') as mock_secrets:
            mock_secrets.side_effect = Exception("Test error")
            
            result = await validator.validate()
            
            assert result.success is False
            assert result.severity == ValidationSeverity.ERROR
            assert "failed" in result.message.lower()
            assert result.remediation_steps is not None
    
    def test_should_exclude_file(self):
        """Test file exclusion logic."""
        validator = SecurityValidator()
        
        # Should exclude test files
        assert validator._should_exclude_file(Path('/project/tests/test_file.py')) is True
        assert validator._should_exclude_file(Path('/project/test_something.py')) is True
        
        # Should not exclude regular files
        assert validator._should_exclude_file(Path('/project/main.py')) is False
        assert validator._should_exclude_file(Path('/project/config.py')) is False
    
    def test_map_bandit_severity(self):
        """Test bandit severity mapping."""
        validator = SecurityValidator()
        
        assert validator._map_bandit_severity('HIGH') == 'high'
        assert validator._map_bandit_severity('MEDIUM') == 'medium'
        assert validator._map_bandit_severity('LOW') == 'low'
        assert validator._map_bandit_severity('UNKNOWN') == 'medium'
    
    def test_map_safety_severity(self):
        """Test safety severity mapping."""
        validator = SecurityValidator()
        
        critical_vuln = {'advisory': 'Critical remote code execution vulnerability'}
        assert validator._map_safety_severity(critical_vuln) == 'critical'
        
        high_vuln = {'advisory': 'High severity SQL injection vulnerability'}
        assert validator._map_safety_severity(high_vuln) == 'high'
        
        medium_vuln = {'advisory': 'Medium severity denial of service'}
        assert validator._map_safety_severity(medium_vuln) == 'medium'
        
        unknown_vuln = {'advisory': 'Some other vulnerability'}
        assert validator._map_safety_severity(unknown_vuln) == 'medium'
    
    def test_get_remediation_steps(self):
        """Test remediation steps generation."""
        validator = SecurityValidator()
        
        issues = [
            {'type': 'secret_detected', 'severity': 'critical'},
            {'type': 'vulnerability', 'severity': 'high'},
            {'type': 'dependency_vulnerability', 'severity': 'medium'},
            {'type': 'insecure_config', 'severity': 'medium'},
            {'type': 'tool_missing', 'severity': 'warning'}
        ]
        
        steps = validator._get_remediation_steps(issues)
        
        assert len(steps) == 5
        assert any('secret' in step.lower() for step in steps)
        assert any('vulnerabilit' in step.lower() for step in steps)
        assert any('dependenc' in step.lower() for step in steps)
        assert any('configuration' in step.lower() for step in steps)
        assert any('install' in step.lower() for step in steps)