"""
Base classes for the validation framework.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime


class ValidationSeverity(Enum):
    """Severity levels for validation results."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    validator_name: str
    severity: ValidationSeverity
    message: str
    success: bool
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None
    remediation_steps: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    @property
    def is_blocking(self) -> bool:
        """Returns True if this result should block deployment."""
        return self.severity in [ValidationSeverity.ERROR, ValidationSeverity.CRITICAL]


class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.name = self.__class__.__name__
    
    @abstractmethod
    async def validate(self) -> ValidationResult:
        """
        Perform the validation check.
        
        Returns:
            ValidationResult: The result of the validation
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this validator checks."""
        pass
    
    @property
    def is_enabled(self) -> bool:
        """Whether this validator is enabled."""
        return self.config.get('enabled', True)
    
    def _create_result(
        self,
        severity: ValidationSeverity,
        message: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
        remediation_steps: Optional[List[str]] = None
    ) -> ValidationResult:
        """Helper method to create validation results."""
        return ValidationResult(
            validator_name=self.name,
            severity=severity,
            message=message,
            success=success,
            timestamp=datetime.utcnow(),
            details=details,
            remediation_steps=remediation_steps
        )
    
    def _success(self, message: str, details: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Create a successful validation result."""
        return self._create_result(
            ValidationSeverity.INFO,
            message,
            True,
            details
        )
    
    def _warning(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        remediation_steps: Optional[List[str]] = None
    ) -> ValidationResult:
        """Create a warning validation result."""
        return self._create_result(
            ValidationSeverity.WARNING,
            message,
            True,
            details,
            remediation_steps
        )
    
    def _error(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        remediation_steps: Optional[List[str]] = None
    ) -> ValidationResult:
        """Create an error validation result."""
        return self._create_result(
            ValidationSeverity.ERROR,
            message,
            False,
            details,
            remediation_steps
        )
    
    def _critical(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        remediation_steps: Optional[List[str]] = None
    ) -> ValidationResult:
        """Create a critical validation result."""
        return self._create_result(
            ValidationSeverity.CRITICAL,
            message,
            False,
            details,
            remediation_steps
        )