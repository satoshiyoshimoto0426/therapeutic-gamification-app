"""
Tests for security configuration.
"""

import unittest
import os
from unittest.mock import patch

from ..security_config import SecurityConfig, EncryptionAlgorithm


class TestSecurityConfig(unittest.TestCase):
    """Test security configuration functionality."""
    
    def test_default_config(self):
        """Test default configuration values."""
        config = SecurityConfig()
        
        self.assertEqual(config.encryption_algorithm, EncryptionAlgorithm.AES_256_GCM)
        self.assertEqual(config.key_rotation_days, 90)
        self.assertTrue(config.require_encryption_at_rest)
        self.assertTrue(config.require_encryption_in_transit)
        self.assertTrue(config.require_mfa)
        self.assertEqual(config.session_timeout_minutes, 30)
        self.assertEqual(config.max_login_attempts, 3)
        self.assertEqual(config.password_min_length, 12)
        self.assertTrue(config.password_require_special_chars)
        self.assertTrue(config.rbac_enabled)
        self.assertTrue(config.principle_of_least_privilege)
        self.assertTrue(config.require_approval_for_production)
        self.assertEqual(config.allowed_ip_ranges, [])
        self.assertFalse(config.require_vpn)
        self.assertTrue(config.enable_waf)
        self.assertTrue(config.gdpr_compliance)
        self.assertTrue(config.audit_logging)
        self.assertEqual(config.data_retention_days, 2555)
        self.assertTrue(config.enable_dependency_scanning)
        self.assertTrue(config.enable_container_scanning)
        self.assertTrue(config.enable_code_scanning)
        self.assertEqual(config.vulnerability_threshold, "medium")
        self.assertTrue(config.secret_rotation_enabled)
        self.assertEqual(config.secret_expiry_warning_days, 30)
        self.assertTrue(config.require_secret_encryption)
        self.assertTrue(config.require_private_endpoints)
        self.assertTrue(config.enable_cloud_armor)
        self.assertTrue(config.require_ssl_certificates)
        self.assertTrue(config.security_monitoring_enabled)
        self.assertTrue(config.anomaly_detection_enabled)
        self.assertTrue(config.real_time_alerts)
    
    def test_custom_config(self):
        """Test custom configuration values."""
        config = SecurityConfig(
            encryption_algorithm=EncryptionAlgorithm.CHACHA20_POLY1305,
            key_rotation_days=30,
            require_encryption_at_rest=False,
            session_timeout_minutes=60,
            password_min_length=16,
            allowed_ip_ranges=['192.168.1.0/24', '10.0.0.0/8'],
            vulnerability_threshold='high'
        )
        
        self.assertEqual(config.encryption_algorithm, EncryptionAlgorithm.CHACHA20_POLY1305)
        self.assertEqual(config.key_rotation_days, 30)
        self.assertFalse(config.require_encryption_at_rest)
        self.assertEqual(config.session_timeout_minutes, 60)
        self.assertEqual(config.password_min_length, 16)
        self.assertEqual(config.allowed_ip_ranges, ['192.168.1.0/24', '10.0.0.0/8'])
        self.assertEqual(config.vulnerability_threshold, 'high')
    
    @patch.dict(os.environ, {
        'SECURITY_ENCRYPTION_ALGORITHM': 'chacha20-poly1305',
        'SECURITY_KEY_ROTATION_DAYS': '60',
        'SECURITY_REQUIRE_ENCRYPTION_AT_REST': 'false',
        'SECURITY_REQUIRE_MFA': 'false',
        'SECURITY_SESSION_TIMEOUT_MINUTES': '45',
        'SECURITY_PASSWORD_MIN_LENGTH': '14',
        'SECURITY_ALLOWED_IP_RANGES': '192.168.1.0/24,10.0.0.0/8',
        'SECURITY_VULNERABILITY_THRESHOLD': 'high',
        'SECURITY_GDPR_COMPLIANCE': 'false'
    })
    def test_from_environment(self):
        """Test configuration from environment variables."""
        config = SecurityConfig.from_environment()
        
        self.assertEqual(config.encryption_algorithm, EncryptionAlgorithm.CHACHA20_POLY1305)
        self.assertEqual(config.key_rotation_days, 60)
        self.assertFalse(config.require_encryption_at_rest)
        self.assertFalse(config.require_mfa)
        self.assertEqual(config.session_timeout_minutes, 45)
        self.assertEqual(config.password_min_length, 14)
        self.assertEqual(config.allowed_ip_ranges, ['192.168.1.0/24', '10.0.0.0/8'])
        self.assertEqual(config.vulnerability_threshold, 'high')
        self.assertFalse(config.gdpr_compliance)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_environment_defaults(self):
        """Test configuration from environment with default values."""
        config = SecurityConfig.from_environment()
        
        # Should use default values when environment variables are not set
        self.assertEqual(config.encryption_algorithm, EncryptionAlgorithm.AES_256_GCM)
        self.assertEqual(config.key_rotation_days, 90)
        self.assertTrue(config.require_encryption_at_rest)
        self.assertTrue(config.require_mfa)
        self.assertEqual(config.session_timeout_minutes, 30)
        self.assertEqual(config.password_min_length, 12)
        self.assertEqual(config.allowed_ip_ranges, [])
        self.assertEqual(config.vulnerability_threshold, 'medium')
        self.assertTrue(config.gdpr_compliance)
    
    def test_to_dict(self):
        """Test configuration serialization to dictionary."""
        config = SecurityConfig(
            encryption_algorithm=EncryptionAlgorithm.AES_256_GCM,
            key_rotation_days=90,
            require_mfa=True,
            allowed_ip_ranges=['192.168.1.0/24']
        )
        
        config_dict = config.to_dict()
        
        self.assertIsInstance(config_dict, dict)
        self.assertEqual(config_dict['encryption_algorithm'], 'aes-256-gcm')
        self.assertEqual(config_dict['key_rotation_days'], 90)
        self.assertTrue(config_dict['require_mfa'])
        self.assertEqual(config_dict['allowed_ip_ranges'], ['192.168.1.0/24'])
        
        # Check that all expected keys are present
        expected_keys = [
            'encryption_algorithm', 'key_rotation_days', 'require_encryption_at_rest',
            'require_encryption_in_transit', 'require_mfa', 'session_timeout_minutes',
            'max_login_attempts', 'password_min_length', 'password_require_special_chars',
            'rbac_enabled', 'principle_of_least_privilege', 'require_approval_for_production',
            'allowed_ip_ranges', 'require_vpn', 'enable_waf', 'gdpr_compliance',
            'audit_logging', 'data_retention_days', 'enable_dependency_scanning',
            'enable_container_scanning', 'enable_code_scanning', 'vulnerability_threshold',
            'secret_rotation_enabled', 'secret_expiry_warning_days', 'require_secret_encryption',
            'require_private_endpoints', 'enable_cloud_armor', 'require_ssl_certificates',
            'security_monitoring_enabled', 'anomaly_detection_enabled', 'real_time_alerts'
        ]
        
        for key in expected_keys:
            self.assertIn(key, config_dict)
    
    def test_validate_success(self):
        """Test successful configuration validation."""
        config = SecurityConfig()
        errors = config.validate()
        
        self.assertEqual(len(errors), 0)
    
    def test_validate_key_rotation_days_invalid(self):
        """Test validation with invalid key rotation days."""
        config = SecurityConfig(key_rotation_days=0)
        errors = config.validate()
        
        self.assertIn("Key rotation days must be at least 1", errors)
    
    def test_validate_session_timeout_invalid(self):
        """Test validation with invalid session timeout."""
        config = SecurityConfig(session_timeout_minutes=4)
        errors = config.validate()
        
        self.assertIn("Session timeout must be at least 5 minutes", errors)
    
    def test_validate_max_login_attempts_invalid(self):
        """Test validation with invalid max login attempts."""
        config = SecurityConfig(max_login_attempts=0)
        errors = config.validate()
        
        self.assertIn("Max login attempts must be at least 1", errors)
    
    def test_validate_password_min_length_invalid(self):
        """Test validation with invalid password minimum length."""
        config = SecurityConfig(password_min_length=7)
        errors = config.validate()
        
        self.assertIn("Password minimum length must be at least 8", errors)
    
    def test_validate_data_retention_days_invalid(self):
        """Test validation with invalid data retention days."""
        config = SecurityConfig(data_retention_days=0)
        errors = config.validate()
        
        self.assertIn("Data retention days must be at least 1", errors)
    
    def test_validate_secret_expiry_warning_days_invalid(self):
        """Test validation with invalid secret expiry warning days."""
        config = SecurityConfig(secret_expiry_warning_days=0)
        errors = config.validate()
        
        self.assertIn("Secret expiry warning days must be at least 1", errors)
    
    def test_validate_vulnerability_threshold_invalid(self):
        """Test validation with invalid vulnerability threshold."""
        config = SecurityConfig(vulnerability_threshold='invalid')
        errors = config.validate()
        
        self.assertIn("Vulnerability threshold must be one of: ['low', 'medium', 'high', 'critical']", errors)
    
    def test_validate_multiple_errors(self):
        """Test validation with multiple errors."""
        config = SecurityConfig(
            key_rotation_days=0,
            session_timeout_minutes=2,
            password_min_length=4,
            vulnerability_threshold='invalid'
        )
        errors = config.validate()
        
        self.assertEqual(len(errors), 4)
        self.assertIn("Key rotation days must be at least 1", errors)
        self.assertIn("Session timeout must be at least 5 minutes", errors)
        self.assertIn("Password minimum length must be at least 8", errors)
        self.assertIn("Vulnerability threshold must be one of: ['low', 'medium', 'high', 'critical']", errors)
    
    def test_encryption_algorithm_enum(self):
        """Test encryption algorithm enumeration."""
        self.assertEqual(EncryptionAlgorithm.AES_256_GCM.value, "aes-256-gcm")
        self.assertEqual(EncryptionAlgorithm.CHACHA20_POLY1305.value, "chacha20-poly1305")
        self.assertEqual(EncryptionAlgorithm.RSA_4096.value, "rsa-4096")


if __name__ == '__main__':
    unittest.main()