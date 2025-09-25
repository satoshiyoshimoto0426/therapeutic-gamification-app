"""
Security and compliance data models.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime


class SecurityLevel(Enum):
    """Security level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ComplianceStandard(Enum):
    """Compliance standard enumeration."""
    GDPR = "gdpr"
    SOC2 = "soc2"
    ISO27001 = "iso27001"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"


@dataclass
class SecurityResult:
    """Security validation result."""
    passed: bool
    level: SecurityLevel
    message: str
    details: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime
    validator_name: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'passed': self.passed,
            'level': self.level.value,
            'message': self.message,
            'details': self.details,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat(),
            'validator_name': self.validator_name
        }


@dataclass
class CredentialResult:
    """Credential security check result."""
    passed: bool
    credential_type: str
    issues: List[str]
    recommendations: List[str]
    expiry_date: Optional[datetime]
    last_rotated: Optional[datetime]
    strength_score: float  # 0.0 to 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'passed': self.passed,
            'credential_type': self.credential_type,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'last_rotated': self.last_rotated.isoformat() if self.last_rotated else None,
            'strength_score': self.strength_score
        }


@dataclass
class ComplianceResult:
    """Compliance verification result."""
    passed: bool
    standard: ComplianceStandard
    requirements_met: List[str]
    requirements_failed: List[str]
    score: float  # 0.0 to 1.0
    recommendations: List[str]
    evidence: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'passed': self.passed,
            'standard': self.standard.value,
            'requirements_met': self.requirements_met,
            'requirements_failed': self.requirements_failed,
            'score': self.score,
            'recommendations': self.recommendations,
            'evidence': self.evidence
        }


@dataclass
class SecurityAuditEvent:
    """Security audit event."""
    event_id: str
    timestamp: datetime
    event_type: str
    user_id: Optional[str]
    resource: str
    action: str
    result: str
    details: Dict[str, Any]
    ip_address: Optional[str]
    user_agent: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'user_id': self.user_id,
            'resource': self.resource,
            'action': self.action,
            'result': self.result,
            'details': self.details,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent
        }