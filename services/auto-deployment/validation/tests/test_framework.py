"""
Tests for validation framework.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

from ..framework import ValidationFramework
from ..config import ValidationConfig
from ..base import BaseValidator, ValidationResult, ValidationSeverity


class MockSuccessValidator(BaseValidator):
    """Mock validator that always succeeds."""
    
    async def validate(self) -> ValidationResult:
        await asyncio.sleep(0.01)  # Simulate some work
        return self._success("Mock validation passed")
    
    @property
    def description(self) -> str:
        return "Mock success validator"


class MockFailureValidator(BaseValidator):
    """Mock validator that always fails."""
    
    async def validate(self) -> ValidationResult:
        await asyncio.sleep(0.01)  # Simulate some work
        return self._error("Mock validation failed", remediation_steps=["Fix the issue"])
    
    @property
    def description(self) -> str:
        return "Mock failure validator"


class MockSlowValidator(BaseValidator):
    """Mock validator that takes a long time."""
    
    async def validate(self) -> ValidationResult:
        await asyncio.sleep(2)  # Simulate slow work
        return self._success("Slow validation completed")
    
    @property
    def description(self) -> str:
        return "Mock slow validator"


class MockExceptionValidator(BaseValidator):
    """Mock validator that raises an exception."""
    
    async def validate(self) -> ValidationResult:
        raise ValueError("Mock exception")
    
    @property
    def description(self) -> str:
        return "Mock exception validator"


class TestValidationFramework:
    """Test ValidationFramework class."""
    
    def test_framework_initialization(self):
        """Test framework initialization."""
        config = ValidationConfig(enabled=True, parallel_execution=False)
        framework = ValidationFramework(config)
        
        assert framework.config == config
        assert len(framework.validators) == 0
        assert len(framework.results) == 0
    
    def test_register_validator(self):
        """Test registering validators."""
        framework = ValidationFramework()
        validator = MockSuccessValidator()
        
        framework.register_validator(validator)
        
        assert "MockSuccessValidator" in framework.validators
        assert framework.validators["MockSuccessValidator"] == validator
    
    def test_register_validator_class(self):
        """Test registering validator classes."""
        framework = ValidationFramework()
        config = {"enabled": True, "test_param": "value"}
        
        framework.register_validator_class(MockSuccessValidator, config)
        
        assert "MockSuccessValidator" in framework.validators
        validator = framework.validators["MockSuccessValidator"]
        assert validator.config == config
    
    def test_get_enabled_validators(self):
        """Test getting enabled validators."""
        config = ValidationConfig()
        config.validator_configs = {
            "MockSuccessValidator": {"enabled": True},
            "MockFailureValidator": {"enabled": False}
        }
        
        framework = ValidationFramework(config)
        framework.register_validator(MockSuccessValidator({"enabled": True}))
        framework.register_validator(MockFailureValidator({"enabled": False}))
        
        enabled_validators = framework.get_enabled_validators()
        
        assert len(enabled_validators) == 1
        assert enabled_validators[0].name == "MockSuccessValidator"
    
    @pytest.mark.asyncio
    async def test_run_validation_disabled_framework(self):
        """Test running validation when framework is disabled."""
        config = ValidationConfig(enabled=False)
        framework = ValidationFramework(config)
        framework.register_validator(MockSuccessValidator())
        
        results = await framework.run_validation()
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_run_validation_no_validators(self):
        """Test running validation with no validators."""
        framework = ValidationFramework()
        
        results = await framework.run_validation()
        
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_run_validation_parallel_success(self):
        """Test successful parallel validation."""
        config = ValidationConfig(parallel_execution=True)
        framework = ValidationFramework(config)
        
        # Create validators with different names
        validator1 = MockSuccessValidator()
        validator1.name = "MockSuccessValidator1"
        validator2 = MockSuccessValidator({"enabled": True})
        validator2.name = "MockSuccessValidator2"
        
        framework.register_validator(validator1)
        framework.register_validator(validator2)
        
        results = await framework.run_validation()
        
        assert len(results) == 2
        assert all(result.success for result in results)
        assert all(result.severity == ValidationSeverity.INFO for result in results)
    
    @pytest.mark.asyncio
    async def test_run_validation_sequential_success(self):
        """Test successful sequential validation."""
        config = ValidationConfig(parallel_execution=False)
        framework = ValidationFramework(config)
        
        # Create validators with different names
        validator1 = MockSuccessValidator()
        validator1.name = "MockSuccessValidator1"
        validator2 = MockSuccessValidator({"enabled": True})
        validator2.name = "MockSuccessValidator2"
        
        framework.register_validator(validator1)
        framework.register_validator(validator2)
        
        results = await framework.run_validation()
        
        assert len(results) == 2
        assert all(result.success for result in results)
    
    @pytest.mark.asyncio
    async def test_run_validation_with_failures(self):
        """Test validation with failures."""
        framework = ValidationFramework()
        
        framework.register_validator(MockSuccessValidator())
        framework.register_validator(MockFailureValidator())
        
        results = await framework.run_validation()
        
        assert len(results) == 2
        success_results = [r for r in results if r.success]
        failure_results = [r for r in results if not r.success]
        
        assert len(success_results) == 1
        assert len(failure_results) == 1
        assert failure_results[0].severity == ValidationSeverity.ERROR
    
    @pytest.mark.asyncio
    async def test_run_validation_fail_fast(self):
        """Test fail fast behavior."""
        config = ValidationConfig(fail_fast=True, parallel_execution=False)
        framework = ValidationFramework(config)
        
        framework.register_validator(MockFailureValidator())
        framework.register_validator(MockSuccessValidator())  # Should not run
        
        results = await framework.run_validation()
        
        assert len(results) == 1  # Only first validator should run
        assert not results[0].success
    
    @pytest.mark.asyncio
    async def test_run_validation_with_exception(self):
        """Test validation with exception."""
        framework = ValidationFramework()
        framework.register_validator(MockExceptionValidator())
        
        results = await framework.run_validation()
        
        assert len(results) == 1
        assert not results[0].success
        assert results[0].severity == ValidationSeverity.ERROR
        assert "Mock exception" in results[0].message
    
    @pytest.mark.asyncio
    async def test_run_validation_timeout(self):
        """Test validation timeout."""
        config = ValidationConfig(timeout_seconds=1, parallel_execution=True)
        framework = ValidationFramework(config)
        
        framework.register_validator(MockSlowValidator())
        
        results = await framework.run_validation()
        
        assert len(results) == 1
        assert not results[0].success
        assert "timed out" in results[0].message
    
    @pytest.mark.asyncio
    async def test_run_validation_specific_validators(self):
        """Test running specific validators."""
        framework = ValidationFramework()
        
        framework.register_validator(MockSuccessValidator())
        framework.register_validator(MockFailureValidator())
        
        # Run only success validator
        results = await framework.run_validation(validators=["MockSuccessValidator"])
        
        assert len(results) == 1
        assert results[0].success
        assert results[0].validator_name == "MockSuccessValidator"
    
    def test_has_blocking_errors(self):
        """Test checking for blocking errors."""
        framework = ValidationFramework()
        
        # No errors
        results = [
            ValidationResult(
                validator_name="Test",
                severity=ValidationSeverity.INFO,
                message="Success",
                success=True,
                timestamp=datetime.utcnow()
            )
        ]
        assert not framework.has_blocking_errors(results)
        
        # With blocking error
        results.append(
            ValidationResult(
                validator_name="Test",
                severity=ValidationSeverity.ERROR,
                message="Error",
                success=False,
                timestamp=datetime.utcnow()
            )
        )
        assert framework.has_blocking_errors(results)
    
    def test_get_results_by_severity(self):
        """Test filtering results by severity."""
        framework = ValidationFramework()
        
        results = [
            ValidationResult(
                validator_name="Test1",
                severity=ValidationSeverity.INFO,
                message="Info",
                success=True,
                timestamp=datetime.utcnow()
            ),
            ValidationResult(
                validator_name="Test2",
                severity=ValidationSeverity.WARNING,
                message="Warning",
                success=True,
                timestamp=datetime.utcnow()
            ),
            ValidationResult(
                validator_name="Test3",
                severity=ValidationSeverity.ERROR,
                message="Error",
                success=False,
                timestamp=datetime.utcnow()
            )
        ]
        
        warnings = framework.get_results_by_severity(ValidationSeverity.WARNING, results)
        errors = framework.get_results_by_severity(ValidationSeverity.ERROR, results)
        
        assert len(warnings) == 1
        assert warnings[0].validator_name == "Test2"
        assert len(errors) == 1
        assert errors[0].validator_name == "Test3"
    
    def test_clear_results(self):
        """Test clearing results."""
        framework = ValidationFramework()
        framework.results = [
            ValidationResult(
                validator_name="Test",
                severity=ValidationSeverity.INFO,
                message="Test",
                success=True,
                timestamp=datetime.utcnow()
            )
        ]
        
        assert len(framework.results) == 1
        framework.clear_results()
        assert len(framework.results) == 0
    
    def test_get_validation_report(self):
        """Test generating validation report."""
        framework = ValidationFramework()
        
        # Test with no results
        report = framework.get_validation_report()
        assert report['status'] == 'no_validation_run'
        
        # Test with results
        framework.results = [
            ValidationResult(
                validator_name="Success",
                severity=ValidationSeverity.INFO,
                message="Success",
                success=True,
                timestamp=datetime.utcnow()
            ),
            ValidationResult(
                validator_name="Warning",
                severity=ValidationSeverity.WARNING,
                message="Warning",
                success=True,
                timestamp=datetime.utcnow()
            ),
            ValidationResult(
                validator_name="Error",
                severity=ValidationSeverity.ERROR,
                message="Error",
                success=False,
                timestamp=datetime.utcnow()
            )
        ]
        
        report = framework.get_validation_report()
        
        assert report['status'] == 'failed'  # Due to error
        assert 'timestamp' in report
        assert report['summary']['total_validators'] == 3
        assert report['summary']['successful'] == 2
        assert report['summary']['warnings'] == 1
        assert report['summary']['errors'] == 1
        assert report['summary']['blocking_errors'] is True
        assert len(report['results']) == 3