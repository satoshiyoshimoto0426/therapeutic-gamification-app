"""
Security configuration validator.
"""

import os
import json
import yaml
import subprocess
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

from .models import SecurityResult, SecurityLevel
from .security_config import SecurityConfig


class SecurityValidator:
    """Validates security configurations and settings."""
    
    def __init__(self, config: SecurityConfig):
        """Initialize security validator."""
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def validate_all(self) -> List[SecurityResult]:
        """Run all security validations."""
        results = []
        
        # Configuration validation
        results.append(self._validate_security_config())
        
        # Infrastructure security
        results.append(self._validate_infrastructure_security())
        
        # Network security
        results.append(self._validate_network_security())
        
        # Encryption validation
        results.append(self._validate_encryption_settings())
        
        # Authentication validation
        results.append(self._validate_authentication_settings())
        
        # Authorization validation
        results.append(self._validate_authorization_settings())
        
        # Secret management validation
        results.append(self._validate_secret_management())
        
        # Container security validation
        results.append(self._validate_container_security())
        
        return results
    
    def _validate_security_config(self) -> SecurityResult:
        """Validate security configuration."""
        try:
            errors = self.config.validate()
            
            if errors:
                return SecurityResult(
                    passed=False,
                    level=SecurityLevel.HIGH,
                    message="Security configuration validation failed",
                    details={'errors': errors},
                    recommendations=[
                        "Fix configuration errors",
                        "Review security settings",
                        "Ensure all required settings are properly configured"
                    ],
                    timestamp=datetime.now(),
                    validator_name="SecurityConfigValidator"
                )
            
            return SecurityResult(
                passed=True,
                level=SecurityLevel.LOW,
                message="Security configuration is valid",
                details={'config': self.config.to_dict()},
                recommendations=[],
                timestamp=datetime.now(),
                validator_name="SecurityConfigValidator"
            )
            
        except Exception as e:
            self.logger.error(f"Security config validation error: {e}")
            return SecurityResult(
                passed=False,
                level=SecurityLevel.CRITICAL,
                message=f"Security configuration validation error: {str(e)}",
                details={'error': str(e)},
                recommendations=["Check configuration file format and syntax"],
                timestamp=datetime.now(),
                validator_name="SecurityConfigValidator"
            )
    
    def _validate_infrastructure_security(self) -> SecurityResult:
        """Validate infrastructure security settings."""
        issues = []
        recommendations = []
        
        # Check for HTTPS enforcement
        if not self.config.require_ssl_certificates:
            issues.append("SSL certificates not required")
            recommendations.append("Enable SSL certificate requirement")
        
        # Check for private endpoints
        if not self.config.require_private_endpoints:
            issues.append("Private endpoints not required")
            recommendations.append("Enable private endpoint requirement")
        
        # Check for WAF
        if not self.config.enable_waf:
            issues.append("Web Application Firewall not enabled")
            recommendations.append("Enable WAF protection")
        
        # Check for Cloud Armor
        if not self.config.enable_cloud_armor:
            issues.append("Cloud Armor not enabled")
            recommendations.append("Enable Cloud Armor for DDoS protection")
        
        level = SecurityLevel.HIGH if issues else SecurityLevel.LOW
        passed = len(issues) == 0
        
        return SecurityResult(
            passed=passed,
            level=level,
            message=f"Infrastructure security validation {'passed' if passed else 'failed'}",
            details={'issues': issues},
            recommendations=recommendations,
            timestamp=datetime.now(),
            validator_name="InfrastructureSecurityValidator"
        )
    
    def _validate_network_security(self) -> SecurityResult:
        """Validate network security settings."""
        issues = []
        recommendations = []
        
        # Check IP restrictions
        if not self.config.allowed_ip_ranges:
            issues.append("No IP range restrictions configured")
            recommendations.append("Configure allowed IP ranges for enhanced security")
        
        # Check VPN requirement
        if not self.config.require_vpn and not self.config.allowed_ip_ranges:
            issues.append("Neither VPN nor IP restrictions are required")
            recommendations.append("Enable VPN requirement or configure IP restrictions")
        
        level = SecurityLevel.MEDIUM if issues else SecurityLevel.LOW
        passed = len(issues) == 0
        
        return SecurityResult(
            passed=passed,
            level=level,
            message=f"Network security validation {'passed' if passed else 'has warnings'}",
            details={'issues': issues},
            recommendations=recommendations,
            timestamp=datetime.now(),
            validator_name="NetworkSecurityValidator"
        )
    
    def _validate_encryption_settings(self) -> SecurityResult:
        """Validate encryption settings."""
        issues = []
        recommendations = []
        
        # Check encryption at rest
        if not self.config.require_encryption_at_rest:
            issues.append("Encryption at rest not required")
            recommendations.append("Enable encryption at rest requirement")
        
        # Check encryption in transit
        if not self.config.require_encryption_in_transit:
            issues.append("Encryption in transit not required")
            recommendations.append("Enable encryption in transit requirement")
        
        # Check key rotation
        if self.config.key_rotation_days > 365:
            issues.append("Key rotation period too long")
            recommendations.append("Set key rotation to 90 days or less")
        
        level = SecurityLevel.HIGH if issues else SecurityLevel.LOW
        passed = len(issues) == 0
        
        return SecurityResult(
            passed=passed,
            level=level,
            message=f"Encryption settings validation {'passed' if passed else 'failed'}",
            details={'issues': issues, 'algorithm': self.config.encryption_algorithm.value},
            recommendations=recommendations,
            timestamp=datetime.now(),
            validator_name="EncryptionValidator"
        )
    
    def _validate_authentication_settings(self) -> SecurityResult:
        """Validate authentication settings."""
        issues = []
        recommendations = []
        
        # Check MFA requirement
        if not self.config.require_mfa:
            issues.append("Multi-factor authentication not required")
            recommendations.append("Enable MFA requirement for all users")
        
        # Check session timeout
        if self.config.session_timeout_minutes > 60:
            issues.append("Session timeout too long")
            recommendations.append("Set session timeout to 30 minutes or less")
        
        # Check password policy
        if self.config.password_min_length < 12:
            issues.append("Password minimum length too short")
            recommendations.append("Set password minimum length to 12 characters or more")
        
        if not self.config.password_require_special_chars:
            issues.append("Special characters not required in passwords")
            recommendations.append("Require special characters in passwords")
        
        level = SecurityLevel.HIGH if issues else SecurityLevel.LOW
        passed = len(issues) == 0
        
        return SecurityResult(
            passed=passed,
            level=level,
            message=f"Authentication settings validation {'passed' if passed else 'failed'}",
            details={'issues': issues},
            recommendations=recommendations,
            timestamp=datetime.now(),
            validator_name="AuthenticationValidator"
        )
    
    def _validate_authorization_settings(self) -> SecurityResult:
        """Validate authorization settings."""
        issues = []
        recommendations = []
        
        # Check RBAC
        if not self.config.rbac_enabled:
            issues.append("Role-based access control not enabled")
            recommendations.append("Enable RBAC for proper access control")
        
        # Check principle of least privilege
        if not self.config.principle_of_least_privilege:
            issues.append("Principle of least privilege not enforced")
            recommendations.append("Enable principle of least privilege")
        
        # Check production approval requirement
        if not self.config.require_approval_for_production:
            issues.append("Production deployment approval not required")
            recommendations.append("Require approval for production deployments")
        
        level = SecurityLevel.HIGH if issues else SecurityLevel.LOW
        passed = len(issues) == 0
        
        return SecurityResult(
            passed=passed,
            level=level,
            message=f"Authorization settings validation {'passed' if passed else 'failed'}",
            details={'issues': issues},
            recommendations=recommendations,
            timestamp=datetime.now(),
            validator_name="AuthorizationValidator"
        )
    
    def _validate_secret_management(self) -> SecurityResult:
        """Validate secret management settings."""
        issues = []
        recommendations = []
        
        # Check secret rotation
        if not self.config.secret_rotation_enabled:
            issues.append("Secret rotation not enabled")
            recommendations.append("Enable automatic secret rotation")
        
        # Check secret encryption
        if not self.config.require_secret_encryption:
            issues.append("Secret encryption not required")
            recommendations.append("Require encryption for all secrets")
        
        # Check expiry warning
        if self.config.secret_expiry_warning_days < 7:
            issues.append("Secret expiry warning period too short")
            recommendations.append("Set secret expiry warning to at least 7 days")
        
        level = SecurityLevel.MEDIUM if issues else SecurityLevel.LOW
        passed = len(issues) == 0
        
        return SecurityResult(
            passed=passed,
            level=level,
            message=f"Secret management validation {'passed' if passed else 'has warnings'}",
            details={'issues': issues},
            recommendations=recommendations,
            timestamp=datetime.now(),
            validator_name="SecretManagementValidator"
        )
    
    def _validate_container_security(self) -> SecurityResult:
        """Validate container security settings."""
        issues = []
        recommendations = []
        
        # Check container scanning
        if not self.config.enable_container_scanning:
            issues.append("Container vulnerability scanning not enabled")
            recommendations.append("Enable container vulnerability scanning")
        
        # Check dependency scanning
        if not self.config.enable_dependency_scanning:
            issues.append("Dependency vulnerability scanning not enabled")
            recommendations.append("Enable dependency vulnerability scanning")
        
        # Check code scanning
        if not self.config.enable_code_scanning:
            issues.append("Code vulnerability scanning not enabled")
            recommendations.append("Enable code vulnerability scanning")
        
        # Check vulnerability threshold
        if self.config.vulnerability_threshold == 'low':
            issues.append("Vulnerability threshold set too low")
            recommendations.append("Set vulnerability threshold to medium or higher")
        
        level = SecurityLevel.HIGH if issues else SecurityLevel.LOW
        passed = len(issues) == 0
        
        return SecurityResult(
            passed=passed,
            level=level,
            message=f"Container security validation {'passed' if passed else 'failed'}",
            details={'issues': issues, 'threshold': self.config.vulnerability_threshold},
            recommendations=recommendations,
            timestamp=datetime.now(),
            validator_name="ContainerSecurityValidator"
        )
    
    def validate_dockerfile(self, dockerfile_path: str) -> SecurityResult:
        """Validate Dockerfile security."""
        try:
            if not os.path.exists(dockerfile_path):
                return SecurityResult(
                    passed=False,
                    level=SecurityLevel.MEDIUM,
                    message="Dockerfile not found",
                    details={'path': dockerfile_path},
                    recommendations=["Ensure Dockerfile exists in the project root"],
                    timestamp=datetime.now(),
                    validator_name="DockerfileValidator"
                )
            
            with open(dockerfile_path, 'r') as f:
                content = f.read()
            
            issues = []
            recommendations = []
            
            # Check for root user
            if 'USER root' in content or 'USER 0' in content:
                issues.append("Container runs as root user")
                recommendations.append("Use non-root user in container")
            
            # Check for latest tag
            if ':latest' in content:
                issues.append("Using 'latest' tag for base image")
                recommendations.append("Use specific version tags for base images")
            
            # Check for COPY/ADD with broad permissions
            if 'COPY . .' in content or 'ADD . .' in content:
                issues.append("Copying entire context to container")
                recommendations.append("Copy only necessary files to container")
            
            level = SecurityLevel.MEDIUM if issues else SecurityLevel.LOW
            passed = len(issues) == 0
            
            return SecurityResult(
                passed=passed,
                level=level,
                message=f"Dockerfile security validation {'passed' if passed else 'has warnings'}",
                details={'issues': issues, 'file': dockerfile_path},
                recommendations=recommendations,
                timestamp=datetime.now(),
                validator_name="DockerfileValidator"
            )
            
        except Exception as e:
            self.logger.error(f"Dockerfile validation error: {e}")
            return SecurityResult(
                passed=False,
                level=SecurityLevel.MEDIUM,
                message=f"Dockerfile validation error: {str(e)}",
                details={'error': str(e)},
                recommendations=["Check Dockerfile format and accessibility"],
                timestamp=datetime.now(),
                validator_name="DockerfileValidator"
            )