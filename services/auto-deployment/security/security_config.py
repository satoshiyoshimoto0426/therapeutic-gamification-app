"""
Security configuration management.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import os


class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""
    AES_256_GCM = "aes-256-gcm"
    CHACHA20_POLY1305 = "chacha20-poly1305"
    RSA_4096 = "rsa-4096"


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    
    # Encryption settings
    encryption_algorithm: EncryptionAlgorithm = EncryptionAlgorithm.AES_256_GCM
    key_rotation_days: int = 90
    require_encryption_at_rest: bool = True
    require_encryption_in_transit: bool = True
    
    # Authentication settings
    require_mfa: bool = True
    session_timeout_minutes: int = 30
    max_login_attempts: int = 3
    password_min_length: int = 12
    password_require_special_chars: bool = True
    
    # Authorization settings
    rbac_enabled: bool = True
    principle_of_least_privilege: bool = True
    require_approval_for_production: bool = True
    
    # Network security
    allowed_ip_ranges: List[str] = field(default_factory=list)
    require_vpn: bool = False
    enable_waf: bool = True
    
    # Compliance settings
    gdpr_compliance: bool = True
    audit_logging: bool = True
    data_retention_days: int = 2555  # 7 years
    
    # Vulnerability scanning
    enable_dependency_scanning: bool = True
    enable_container_scanning: bool = True
    enable_code_scanning: bool = True
    vulnerability_threshold: str = "medium"  # low, medium, high, critical
    
    # Secret management
    secret_rotation_enabled: bool = True
    secret_expiry_warning_days: int = 30
    require_secret_encryption: bool = True
    
    # Cloud security
    require_private_endpoints: bool = True
    enable_cloud_armor: bool = True
    require_ssl_certificates: bool = True
    
    # Monitoring and alerting
    security_monitoring_enabled: bool = True
    anomaly_detection_enabled: bool = True
    real_time_alerts: bool = True
    
    @classmethod
    def from_environment(cls) -> 'SecurityConfig':
        """Create configuration from environment variables."""
        return cls(
            encryption_algorithm=EncryptionAlgorithm(
                os.getenv('SECURITY_ENCRYPTION_ALGORITHM', 'aes-256-gcm')
            ),
            key_rotation_days=int(os.getenv('SECURITY_KEY_ROTATION_DAYS', '90')),
            require_encryption_at_rest=os.getenv('SECURITY_REQUIRE_ENCRYPTION_AT_REST', 'true').lower() == 'true',
            require_encryption_in_transit=os.getenv('SECURITY_REQUIRE_ENCRYPTION_IN_TRANSIT', 'true').lower() == 'true',
            require_mfa=os.getenv('SECURITY_REQUIRE_MFA', 'true').lower() == 'true',
            session_timeout_minutes=int(os.getenv('SECURITY_SESSION_TIMEOUT_MINUTES', '30')),
            max_login_attempts=int(os.getenv('SECURITY_MAX_LOGIN_ATTEMPTS', '3')),
            password_min_length=int(os.getenv('SECURITY_PASSWORD_MIN_LENGTH', '12')),
            password_require_special_chars=os.getenv('SECURITY_PASSWORD_REQUIRE_SPECIAL_CHARS', 'true').lower() == 'true',
            rbac_enabled=os.getenv('SECURITY_RBAC_ENABLED', 'true').lower() == 'true',
            principle_of_least_privilege=os.getenv('SECURITY_PRINCIPLE_OF_LEAST_PRIVILEGE', 'true').lower() == 'true',
            require_approval_for_production=os.getenv('SECURITY_REQUIRE_APPROVAL_FOR_PRODUCTION', 'true').lower() == 'true',
            allowed_ip_ranges=os.getenv('SECURITY_ALLOWED_IP_RANGES', '').split(',') if os.getenv('SECURITY_ALLOWED_IP_RANGES') else [],
            require_vpn=os.getenv('SECURITY_REQUIRE_VPN', 'false').lower() == 'true',
            enable_waf=os.getenv('SECURITY_ENABLE_WAF', 'true').lower() == 'true',
            gdpr_compliance=os.getenv('SECURITY_GDPR_COMPLIANCE', 'true').lower() == 'true',
            audit_logging=os.getenv('SECURITY_AUDIT_LOGGING', 'true').lower() == 'true',
            data_retention_days=int(os.getenv('SECURITY_DATA_RETENTION_DAYS', '2555')),
            enable_dependency_scanning=os.getenv('SECURITY_ENABLE_DEPENDENCY_SCANNING', 'true').lower() == 'true',
            enable_container_scanning=os.getenv('SECURITY_ENABLE_CONTAINER_SCANNING', 'true').lower() == 'true',
            enable_code_scanning=os.getenv('SECURITY_ENABLE_CODE_SCANNING', 'true').lower() == 'true',
            vulnerability_threshold=os.getenv('SECURITY_VULNERABILITY_THRESHOLD', 'medium'),
            secret_rotation_enabled=os.getenv('SECURITY_SECRET_ROTATION_ENABLED', 'true').lower() == 'true',
            secret_expiry_warning_days=int(os.getenv('SECURITY_SECRET_EXPIRY_WARNING_DAYS', '30')),
            require_secret_encryption=os.getenv('SECURITY_REQUIRE_SECRET_ENCRYPTION', 'true').lower() == 'true',
            require_private_endpoints=os.getenv('SECURITY_REQUIRE_PRIVATE_ENDPOINTS', 'true').lower() == 'true',
            enable_cloud_armor=os.getenv('SECURITY_ENABLE_CLOUD_ARMOR', 'true').lower() == 'true',
            require_ssl_certificates=os.getenv('SECURITY_REQUIRE_SSL_CERTIFICATES', 'true').lower() == 'true',
            security_monitoring_enabled=os.getenv('SECURITY_MONITORING_ENABLED', 'true').lower() == 'true',
            anomaly_detection_enabled=os.getenv('SECURITY_ANOMALY_DETECTION_ENABLED', 'true').lower() == 'true',
            real_time_alerts=os.getenv('SECURITY_REAL_TIME_ALERTS', 'true').lower() == 'true'
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'encryption_algorithm': self.encryption_algorithm.value,
            'key_rotation_days': self.key_rotation_days,
            'require_encryption_at_rest': self.require_encryption_at_rest,
            'require_encryption_in_transit': self.require_encryption_in_transit,
            'require_mfa': self.require_mfa,
            'session_timeout_minutes': self.session_timeout_minutes,
            'max_login_attempts': self.max_login_attempts,
            'password_min_length': self.password_min_length,
            'password_require_special_chars': self.password_require_special_chars,
            'rbac_enabled': self.rbac_enabled,
            'principle_of_least_privilege': self.principle_of_least_privilege,
            'require_approval_for_production': self.require_approval_for_production,
            'allowed_ip_ranges': self.allowed_ip_ranges,
            'require_vpn': self.require_vpn,
            'enable_waf': self.enable_waf,
            'gdpr_compliance': self.gdpr_compliance,
            'audit_logging': self.audit_logging,
            'data_retention_days': self.data_retention_days,
            'enable_dependency_scanning': self.enable_dependency_scanning,
            'enable_container_scanning': self.enable_container_scanning,
            'enable_code_scanning': self.enable_code_scanning,
            'vulnerability_threshold': self.vulnerability_threshold,
            'secret_rotation_enabled': self.secret_rotation_enabled,
            'secret_expiry_warning_days': self.secret_expiry_warning_days,
            'require_secret_encryption': self.require_secret_encryption,
            'require_private_endpoints': self.require_private_endpoints,
            'enable_cloud_armor': self.enable_cloud_armor,
            'require_ssl_certificates': self.require_ssl_certificates,
            'security_monitoring_enabled': self.security_monitoring_enabled,
            'anomaly_detection_enabled': self.anomaly_detection_enabled,
            'real_time_alerts': self.real_time_alerts
        }
    
    def validate(self) -> List[str]:
        """Validate configuration settings."""
        errors = []
        
        if self.key_rotation_days < 1:
            errors.append("Key rotation days must be at least 1")
        
        if self.session_timeout_minutes < 5:
            errors.append("Session timeout must be at least 5 minutes")
        
        if self.max_login_attempts < 1:
            errors.append("Max login attempts must be at least 1")
        
        if self.password_min_length < 8:
            errors.append("Password minimum length must be at least 8")
        
        if self.data_retention_days < 1:
            errors.append("Data retention days must be at least 1")
        
        if self.secret_expiry_warning_days < 1:
            errors.append("Secret expiry warning days must be at least 1")
        
        valid_thresholds = ['low', 'medium', 'high', 'critical']
        if self.vulnerability_threshold not in valid_thresholds:
            errors.append(f"Vulnerability threshold must be one of: {valid_thresholds}")
        
        return errors