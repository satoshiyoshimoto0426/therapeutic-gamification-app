"""
Tests for base validation classes.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock

from ..base import BaseValidator, ValidationResult, ValidationSeverity


class MockValidator(BaseValidator):
    """Mock validator for testing."""
    
    def __init__(self, config=None, should_succeed=True, severity=ValidationSeverity.INFO):
        super().__init__(config)
        self.should_succeed = should_succeed
        self.severity = severity
    
    async def validate(self) -> ValidationResult:
        if self.should_succeed:
            return self._success("Mock validation passed")
        else:
            return self._create_result(
                self.severity,
                "Mock validation failed",
                False,
                remediation_steps=["Fix the mock issue"]
            )
    
    @property
    def description(self) -> str:
        return "Mock validator for testing"


class TestValidationResult:
    """Test ValidationResult class."""
    
    def test_validation_result_creation(self):
        """Test creating a validation result."""
        result = ValidationResult(
            validator_name="TestValidator",
            severity=ValidationSeverity.INFO,
            message="Test message",
            success=True,
            timestamp=datetime.utcnow()
        )
        
        assert result.validator_name == "TestValidator"
        assert result.severity == ValidationSeverity.INFO
        assert result.message == "Test message"
        assert result.success is True
        assert isinstance(result.timestamp, datetime)
    
    def test_is_blocking_property(self):
        """Test the is_blocking property."""
        # Non-blocking severities
        info_result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.INFO,
            message="Info",
            success=True,
            timestamp=datetime.utcnow()
        )
        assert not info_result.is_blocking
        
        warning_result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.WARNING,
            message="Warning",
            success=True,
            timestamp=datetime.utcnow()
        )
        assert not warning_result.is_blocking
        
        # Blocking severities
        error_result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.ERROR,
            message="Error",
            success=False,
            timestamp=datetime.utcnow()
        )
        assert error_result.is_blocking
        
        critical_result = ValidationResult(
            validator_name="Test",
            severity=ValidationSeverity.CRITICAL,
            message="Critical",
            success=False,
            timestamp=datetime.utcnow()
        )
        assert critical_result.is_blocking


class TestBaseValidator:
    """Test BaseValidator class."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        config = {"enabled": True, "test_param": "value"}
        validator = MockValidator(config)
        
        assert validator.config == config
        assert validator.name == "MockValidator"
        assert validator.is_enabled is True
    
    def test_validator_disabled(self):
        """Test disabled validator."""
        config = {"enabled": False}
        validator = MockValidator(config)
        
        assert validator.is_enabled is False
    
    @pytest.mark.asyncio
    async def test_successful_validation(self):
        """Test successful validation."""
        validator = MockValidator(should_succeed=True)
        result = await validator.validate()
        
        assert result.success is True
        assert result.severity == ValidationSeverity.INFO
        assert result.validator_name == "MockValidator"
        assert "passed" in result.message
    
    @pytest.mark.asyncio
    async def test_failed_validation(self):
        """Test failed validation."""
        validator = MockValidator(should_succeed=False, severity=ValidationSeverity.ERROR)
        result = await validator.validate()
        
        assert result.success is False
        assert result.severity == ValidationSeverity.ERROR
        assert result.validator_name == "MockValidator"
        assert "failed" in result.message
        assert result.remediation_steps is not None
    
    def test_helper_methods(self):
        """Test validator helper methods."""
        validator = MockValidator()
        
        # Test success helper
        success_result = validator._success("Success message", {"key": "value"})
        assert success_result.success is True
        assert success_result.severity == ValidationSeverity.INFO
        assert success_result.message == "Success message"
        assert success_result.details == {"key": "value"}
        
        # Test warning helper
        warning_result = validator._warning("Warning message", remediation_steps=["Fix warning"])
        assert warning_result.success is True
        assert warning_result.severity == ValidationSeverity.WARNING
        assert warning_result.remediation_steps == ["Fix warning"]
        
        # Test error helper
        error_result = validator._error("Error message")
        assert error_result.success is False
        assert error_result.severity == ValidationSeverity.ERROR
        
        # Test critical helper
        critical_result = validator._critical("Critical message")
        assert critical_result.success is False
        assert critical_result.severity == ValidationSeverity.CRITICAL
    
    def test_description_property(self):
        """Test description property."""
        validator = MockValidator()
        assert validator.description == "Mock validator for testing"