"""
Tests for code quality validator.
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import tempfile
from pathlib import Path
import subprocess

from code_quality import CodeQualityValidator
from base import ValidationSeverity


class TestCodeQualityValidator:
    """Test CodeQualityValidator class."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        config = {
            'min_test_coverage': 0.9,
            'run_linting': False,
            'run_type_checking': True,
            'project_root': '/test/path'
        }
        validator = CodeQualityValidator(config)
        
        assert validator.min_test_coverage == 0.9
        assert validator.run_linting is False
        assert validator.run_type_checking is True
        assert validator.project_root == Path('/test/path')
    
    def test_validator_default_config(self):
        """Test validator with default configuration."""
        validator = CodeQualityValidator()
        
        assert validator.min_test_coverage == 0.8
        assert validator.run_linting is True
        assert validator.run_type_checking is True
        assert validator.project_root == Path('.')
    
    def test_description_property(self):
        """Test description property."""
        validator = CodeQualityValidator()
        assert "code quality" in validator.description.lower()
        assert "test coverage" in validator.description.lower()
    
    @pytest.mark.asyncio
    @patch('coverage.Coverage')
    async def test_check_test_coverage_success(self, mock_coverage_class):
        """Test successful test coverage check."""
        # Mock coverage instance
        mock_coverage = MagicMock()
        mock_coverage.report.return_value = 85.0  # 85% coverage
        mock_coverage_class.return_value = mock_coverage
        
        validator = CodeQualityValidator({'min_test_coverage': 0.8})
        result = await validator._check_test_coverage()
        
        assert result is not None
        assert result['coverage_percentage'] == 85.0
        assert result['required_coverage'] == 80.0
        assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    @patch('coverage.Coverage')
    async def test_check_test_coverage_low(self, mock_coverage_class):
        """Test low test coverage detection."""
        # Mock coverage instance
        mock_coverage = MagicMock()
        mock_coverage.report.return_value = 60.0  # 60% coverage
        mock_coverage_class.return_value = mock_coverage
        
        validator = CodeQualityValidator({'min_test_coverage': 0.8})
        result = await validator._check_test_coverage()
        
        assert result is not None
        assert result['coverage_percentage'] == 60.0
        assert len(result['issues']) == 1
        assert result['issues'][0]['type'] == 'low_coverage'
        assert result['issues'][0]['severity'] == 'warning'
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_run_linting_success(self, mock_subprocess):
        """Test successful linting check."""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        validator = CodeQualityValidator()
        result = await validator._run_linting()
        
        assert result is not None
        assert result['total_issues'] == 0
        assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_run_linting_with_issues(self, mock_subprocess):
        """Test linting with issues found."""
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout='[{"filename": "test.py", "line_number": 10, "column_number": 5, "code": "E302", "text": "expected 2 blank lines"}]',
            stderr=''
        )
        
        validator = CodeQualityValidator()
        result = await validator._run_linting()
        
        assert result is not None
        assert result['total_issues'] == 1
        assert len(result['issues']) == 1
        assert result['issues'][0]['type'] == 'linting'
        assert result['issues'][0]['file'] == 'test.py'
        assert result['issues'][0]['line'] == 10
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_run_linting_tool_missing(self, mock_subprocess):
        """Test linting when flake8 is not installed."""
        mock_subprocess.side_effect = FileNotFoundError()
        
        validator = CodeQualityValidator()
        result = await validator._run_linting()
        
        assert result is not None
        assert result['total_issues'] == 0
        assert len(result['issues']) == 1
        assert result['issues'][0]['type'] == 'tool_missing'
        assert result['issues'][0]['severity'] == 'warning'
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_run_type_checking_success(self, mock_subprocess):
        """Test successful type checking."""
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout='',
            stderr=''
        )
        
        validator = CodeQualityValidator()
        result = await validator._run_type_checking()
        
        assert result is not None
        assert result['total_issues'] == 0
        assert len(result['issues']) == 0
    
    @pytest.mark.asyncio
    @patch('subprocess.run')
    async def test_run_type_checking_with_errors(self, mock_subprocess):
        """Test type checking with errors."""
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout='test.py:10:5: error: Incompatible types\ntest.py:15:10: note: Consider using Optional',
            stderr=''
        )
        
        validator = CodeQualityValidator()
        result = await validator._run_type_checking()
        
        assert result is not None
        assert result['total_issues'] == 2
        assert len(result['issues']) == 2
        assert result['issues'][0]['type'] == 'type_checking'
        assert result['issues'][0]['severity'] == 'error'
        assert result['issues'][1]['severity'] == 'warning'
    
    @pytest.mark.asyncio
    async def test_validate_all_checks_pass(self):
        """Test validation when all checks pass."""
        validator = CodeQualityValidator({
            'run_linting': False,
            'run_type_checking': False
        })
        
        with patch.object(validator, '_check_test_coverage') as mock_coverage:
            mock_coverage.return_value = {
                'coverage_percentage': 90.0,
                'issues': []
            }
            
            result = await validator.validate()
            
            assert result.success is True
            assert result.severity == ValidationSeverity.INFO
            assert "passed" in result.message
    
    @pytest.mark.asyncio
    async def test_validate_with_critical_issues(self):
        """Test validation with critical issues."""
        validator = CodeQualityValidator({
            'run_linting': False,
            'run_type_checking': False
        })
        
        with patch.object(validator, '_check_test_coverage') as mock_coverage:
            mock_coverage.return_value = {
                'coverage_percentage': 30.0,
                'issues': [{
                    'type': 'low_coverage',
                    'severity': 'critical',
                    'message': 'Very low coverage'
                }]
            }
            
            result = await validator.validate()
            
            assert result.success is False
            assert result.severity == ValidationSeverity.CRITICAL
            assert "critical" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_validate_with_errors(self):
        """Test validation with error-level issues."""
        validator = CodeQualityValidator({
            'run_linting': False,
            'run_type_checking': False
        })
        
        with patch.object(validator, '_check_test_coverage') as mock_coverage:
            mock_coverage.return_value = {
                'coverage_percentage': 60.0,
                'issues': [{
                    'type': 'low_coverage',
                    'severity': 'error',
                    'message': 'Low coverage'
                }]
            }
            
            result = await validator.validate()
            
            assert result.success is False
            assert result.severity == ValidationSeverity.ERROR
            assert "issues found" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_validate_with_warnings(self):
        """Test validation with warning-level issues."""
        validator = CodeQualityValidator({
            'run_linting': False,
            'run_type_checking': False
        })
        
        with patch.object(validator, '_check_test_coverage') as mock_coverage:
            mock_coverage.return_value = {
                'coverage_percentage': 75.0,
                'issues': [{
                    'type': 'low_coverage',
                    'severity': 'warning',
                    'message': 'Coverage could be better'
                }]
            }
            
            result = await validator.validate()
            
            assert result.success is True
            assert result.severity == ValidationSeverity.WARNING
            assert "warnings found" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_validate_exception_handling(self):
        """Test validation exception handling."""
        validator = CodeQualityValidator()
        
        with patch.object(validator, '_check_test_coverage') as mock_coverage:
            mock_coverage.side_effect = Exception("Test error")
            
            result = await validator.validate()
            
            assert result.success is False
            assert result.severity == ValidationSeverity.ERROR
            assert "failed" in result.message.lower()
            assert result.remediation_steps is not None
    
    def test_get_flake8_severity(self):
        """Test flake8 severity mapping."""
        validator = CodeQualityValidator()
        
        assert validator._get_flake8_severity('E901') == 'error'  # Syntax error
        assert validator._get_flake8_severity('F401') == 'error'  # Undefined name
        assert validator._get_flake8_severity('E101') == 'warning'  # Indentation
        assert validator._get_flake8_severity('W291') == 'warning'  # Warning
        assert validator._get_flake8_severity('C901') == 'warning'  # Default
    
    def test_get_mypy_severity(self):
        """Test mypy severity mapping."""
        validator = CodeQualityValidator()
        
        assert validator._get_mypy_severity('error: Incompatible types') == 'error'
        assert validator._get_mypy_severity('note: Consider using Optional') == 'warning'
        assert validator._get_mypy_severity('warning: Unused import') == 'warning'
    
    def test_get_remediation_steps(self):
        """Test remediation steps generation."""
        validator = CodeQualityValidator()
        
        issues = [
            {'type': 'low_coverage', 'severity': 'error'},
            {'type': 'linting', 'severity': 'warning'},
            {'type': 'type_checking', 'severity': 'error'},
            {'type': 'tool_missing', 'severity': 'warning'}
        ]
        
        steps = validator._get_remediation_steps(issues)
        
        assert len(steps) == 4
        assert any('test coverage' in step.lower() for step in steps)
        assert any('linting' in step.lower() for step in steps)
        assert any('type' in step.lower() for step in steps)
        assert any('install' in step.lower() for step in steps)