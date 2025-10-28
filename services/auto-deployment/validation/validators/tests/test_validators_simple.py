"""
Simple tests for validators to verify basic functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from code_quality import CodeQualityValidator
from security import SecurityValidator
from dependency import DependencyValidator
from base import ValidationSeverity


class TestValidatorsBasic:
    """Basic tests for all validators."""
    
    def test_code_quality_validator_init(self):
        """Test CodeQualityValidator initialization."""
        validator = CodeQualityValidator()
        assert validator.name == "CodeQualityValidator"
        assert validator.is_enabled is True
        assert "code quality" in validator.description.lower()
    
    def test_security_validator_init(self):
        """Test SecurityValidator initialization."""
        validator = SecurityValidator()
        assert validator.name == "SecurityValidator"
        assert validator.is_enabled is True
        assert "security" in validator.description.lower()
    
    def test_dependency_validator_init(self):
        """Test DependencyValidator initialization."""
        validator = DependencyValidator()
        assert validator.name == "DependencyValidator"
        assert validator.is_enabled is True
        assert "dependency" in validator.description.lower()
    
    @pytest.mark.asyncio
    async def test_code_quality_validator_exception_handling(self):
        """Test CodeQualityValidator exception handling."""
        validator = CodeQualityValidator()
        
        with patch.object(validator, '_check_test_coverage') as mock_coverage:
            mock_coverage.side_effect = Exception("Test error")
            
            result = await validator.validate()
            
            assert result.success is False
            assert result.severity == ValidationSeverity.ERROR
            assert "failed" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_security_validator_exception_handling(self):
        """Test SecurityValidator exception handling."""
        validator = SecurityValidator()
        
        with patch.object(validator, '_check_secrets') as mock_secrets:
            mock_secrets.side_effect = Exception("Test error")
            
            result = await validator.validate()
            
            assert result.success is False
            assert result.severity == ValidationSeverity.ERROR
            assert "failed" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_dependency_validator_exception_handling(self):
        """Test DependencyValidator exception handling."""
        validator = DependencyValidator()
        
        with patch.object(validator, '_check_dependency_conflicts') as mock_conflicts:
            mock_conflicts.side_effect = Exception("Test error")
            
            result = await validator.validate()
            
            assert result.success is False
            assert result.severity == ValidationSeverity.ERROR
            assert "failed" in result.message.lower()
    
    @pytest.mark.asyncio
    async def test_code_quality_validator_success(self):
        """Test CodeQualityValidator success case."""
        validator = CodeQualityValidator({
            'run_linting': False,
            'run_type_checking': False
        })
        
        with patch.object(validator, '_check_test_coverage') as mock_coverage:
            mock_coverage.return_value = {'issues': []}
            
            result = await validator.validate()
            
            assert result.success is True
            assert result.severity == ValidationSeverity.INFO
    
    @pytest.mark.asyncio
    async def test_security_validator_success(self):
        """Test SecurityValidator success case."""
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
    
    @pytest.mark.asyncio
    async def test_dependency_validator_success(self):
        """Test DependencyValidator success case."""
        validator = DependencyValidator({
            'check_compatibility': False,
            'check_outdated': False,
            'check_conflicts': False
        })
        
        with patch.object(validator, '_check_requirements_consistency') as mock_consistency:
            mock_consistency.return_value = {'issues': []}
            
            result = await validator.validate()
            
            assert result.success is True
            assert result.severity == ValidationSeverity.INFO