"""
Tests for security validator.
"""

import unittest
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

from security_validator import SecurityValidator
from security_config import SecurityConfig, EncryptionAlgorithm
from models import SecurityLevel


class TestSecurityValidator(unittest.TestCase):
    """Test security validator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SecurityConfig(
            encryption_algorithm=EncryptionAlgorithm.AES_256_GCM,
            require_encryption_at_rest=True,
            require_encryption_in_transit=True,
            require_mfa=True,
            rbac_enabled=True,
            enable_waf=True,
            audit_logging=True
        )
        self.validator = SecurityValidator(self.config)
    
    def test_validate_security_config_success(self):
        """Test successful security configuration validation."""
        result = self.validator._validate_security_config()
        
        self.assertTrue(result.passed)
        self.assertEqual(result.level, SecurityLevel.LOW)
        self.assertEqual(result.validator_name, "SecurityConfigValidator")
        self.assertIn('config', result.details)
    
    def test_validate_security_config_failure(self):
        """Test security configuration validation failure."""
        # Create invalid config
        invalid_config = SecurityConfig(
            key_rotation_days=0,  # Invalid
            session_timeout_minutes=0,  # Invalid
            password_min_length=4  # Too short
        )
        validator = SecurityValidator(invalid_config)
        
        result = validator._validate_security_config()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.level, SecurityLevel.HIGH)
        self.assertIn('errors', result.details)
        self.assertTrue(len(result.details['errors']) > 0)
    
    def test_validate_infrastructure_security_success(self):
        """Test successful infrastructure security validation."""
        result = self.validator._validate_infrastructure_security()
        
        self.assertTrue(result.passed)
        self.assertEqual(result.level, SecurityLevel.LOW)
        self.assertEqual(result.validator_name, "InfrastructureSecurityValidator")
    
    def test_validate_infrastructure_security_failure(self):
        """Test infrastructure security validation failure."""
        # Create config with security issues
        insecure_config = SecurityConfig(
            require_ssl_certificates=False,
            require_private_endpoints=False,
            enable_waf=False,
            enable_cloud_armor=False
        )
        validator = SecurityValidator(insecure_config)
        
        result = validator._validate_infrastructure_security()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.level, SecurityLevel.HIGH)
        self.assertTrue(len(result.details['issues']) > 0)
        self.assertTrue(len(result.recommendations) > 0)
    
    def test_validate_network_security(self):
        """Test network security validation."""
        result = self.validator._validate_network_security()
        
        # Should pass with warnings since no IP restrictions are set
        self.assertFalse(result.passed)
        self.assertEqual(result.level, SecurityLevel.MEDIUM)
        self.assertEqual(result.validator_name, "NetworkSecurityValidator")
    
    def test_validate_encryption_settings_success(self):
        """Test successful encryption settings validation."""
        result = self.validator._validate_encryption_settings()
        
        self.assertTrue(result.passed)
        self.assertEqual(result.level, SecurityLevel.LOW)
        self.assertEqual(result.validator_name, "EncryptionValidator")
        self.assertIn('algorithm', result.details)
    
    def test_validate_encryption_settings_failure(self):
        """Test encryption settings validation failure."""
        # Create config with encryption issues
        weak_config = SecurityConfig(
            require_encryption_at_rest=False,
            require_encryption_in_transit=False,
            key_rotation_days=400  # Too long
        )
        validator = SecurityValidator(weak_config)
        
        result = validator._validate_encryption_settings()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.level, SecurityLevel.HIGH)
        self.assertTrue(len(result.details['issues']) > 0)
    
    def test_validate_authentication_settings_success(self):
        """Test successful authentication settings validation."""
        result = self.validator._validate_authentication_settings()
        
        self.assertTrue(result.passed)
        self.assertEqual(result.level, SecurityLevel.LOW)
        self.assertEqual(result.validator_name, "AuthenticationValidator")
    
    def test_validate_authentication_settings_failure(self):
        """Test authentication settings validation failure."""
        # Create config with authentication issues
        weak_auth_config = SecurityConfig(
            require_mfa=False,
            session_timeout_minutes=120,  # Too long
            password_min_length=6,  # Too short
            password_require_special_chars=False
        )
        validator = SecurityValidator(weak_auth_config)
        
        result = validator._validate_authentication_settings()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.level, SecurityLevel.HIGH)
        self.assertTrue(len(result.details['issues']) > 0)
    
    def test_validate_authorization_settings_success(self):
        """Test successful authorization settings validation."""
        result = self.validator._validate_authorization_settings()
        
        self.assertTrue(result.passed)
        self.assertEqual(result.level, SecurityLevel.LOW)
        self.assertEqual(result.validator_name, "AuthorizationValidator")
    
    def test_validate_authorization_settings_failure(self):
        """Test authorization settings validation failure."""
        # Create config with authorization issues
        weak_authz_config = SecurityConfig(
            rbac_enabled=False,
            principle_of_least_privilege=False,
            require_approval_for_production=False
        )
        validator = SecurityValidator(weak_authz_config)
        
        result = validator._validate_authorization_settings()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.level, SecurityLevel.HIGH)
        self.assertTrue(len(result.details['issues']) > 0)
    
    def test_validate_secret_management_success(self):
        """Test successful secret management validation."""
        result = self.validator._validate_secret_management()
        
        self.assertTrue(result.passed)
        self.assertEqual(result.level, SecurityLevel.LOW)
        self.assertEqual(result.validator_name, "SecretManagementValidator")
    
    def test_validate_secret_management_failure(self):
        """Test secret management validation failure."""
        # Create config with secret management issues
        weak_secret_config = SecurityConfig(
            secret_rotation_enabled=False,
            require_secret_encryption=False,
            secret_expiry_warning_days=1  # Too short
        )
        validator = SecurityValidator(weak_secret_config)
        
        result = validator._validate_secret_management()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.level, SecurityLevel.MEDIUM)
        self.assertTrue(len(result.details['issues']) > 0)
    
    def test_validate_container_security_success(self):
        """Test successful container security validation."""
        result = self.validator._validate_container_security()
        
        self.assertTrue(result.passed)
        self.assertEqual(result.level, SecurityLevel.LOW)
        self.assertEqual(result.validator_name, "ContainerSecurityValidator")
    
    def test_validate_container_security_failure(self):
        """Test container security validation failure."""
        # Create config with container security issues
        weak_container_config = SecurityConfig(
            enable_container_scanning=False,
            enable_dependency_scanning=False,
            enable_code_scanning=False,
            vulnerability_threshold='low'  # Too permissive
        )
        validator = SecurityValidator(weak_container_config)
        
        result = validator._validate_container_security()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.level, SecurityLevel.HIGH)
        self.assertTrue(len(result.details['issues']) > 0)
    
    def test_validate_dockerfile_success(self):
        """Test successful Dockerfile validation."""
        # Create a secure Dockerfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dockerfile', delete=False) as f:
            f.write("""
FROM python:3.9-slim
RUN useradd -m appuser
USER appuser
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["python", "app/main.py"]
""")
            dockerfile_path = f.name
        
        try:
            result = self.validator.validate_dockerfile(dockerfile_path)
            
            self.assertTrue(result.passed)
            self.assertEqual(result.level, SecurityLevel.LOW)
            self.assertEqual(result.validator_name, "DockerfileValidator")
        finally:
            os.unlink(dockerfile_path)
    
    def test_validate_dockerfile_security_issues(self):
        """Test Dockerfile validation with security issues."""
        # Create an insecure Dockerfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dockerfile', delete=False) as f:
            f.write("""
FROM python:latest
USER root
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app/main.py"]
""")
            dockerfile_path = f.name
        
        try:
            result = self.validator.validate_dockerfile(dockerfile_path)
            
            self.assertFalse(result.passed)
            self.assertEqual(result.level, SecurityLevel.MEDIUM)
            self.assertTrue(len(result.details['issues']) > 0)
            self.assertIn("Using 'latest' tag", str(result.details['issues']))
            self.assertIn("runs as root", str(result.details['issues']))
        finally:
            os.unlink(dockerfile_path)
    
    def test_validate_dockerfile_not_found(self):
        """Test Dockerfile validation when file doesn't exist."""
        result = self.validator.validate_dockerfile('nonexistent.dockerfile')
        
        self.assertFalse(result.passed)
        self.assertEqual(result.level, SecurityLevel.MEDIUM)
        self.assertEqual(result.message, "Dockerfile not found")
    
    def test_validate_all(self):
        """Test running all security validations."""
        results = self.validator.validate_all()
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        
        # Check that all results have required fields
        for result in results:
            self.assertIsInstance(result.passed, bool)
            self.assertIsInstance(result.level, SecurityLevel)
            self.assertIsInstance(result.message, str)
            self.assertIsInstance(result.details, dict)
            self.assertIsInstance(result.recommendations, list)
            self.assertIsInstance(result.timestamp, datetime)
            self.assertIsInstance(result.validator_name, str)


if __name__ == '__main__':
    unittest.main()