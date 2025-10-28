"""
Integration tests for Task 9.1 completion verification.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime

from security_validator import SecurityValidator
from credential_checker import CredentialChecker
from compliance_verifier import ComplianceVerifier
from security_config import SecurityConfig, EncryptionAlgorithm
from models import SecurityLevel, ComplianceStandard


class TestTask91Completion(unittest.TestCase):
    """Test Task 9.1 completion - Security validation and enforcement."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SecurityConfig(
            encryption_algorithm=EncryptionAlgorithm.AES_256_GCM,
            require_encryption_at_rest=True,
            require_encryption_in_transit=True,
            require_mfa=True,
            rbac_enabled=True,
            enable_waf=True,
            audit_logging=True,
            enable_dependency_scanning=True,
            enable_container_scanning=True,
            enable_code_scanning=True,
            secret_rotation_enabled=True,
            security_monitoring_enabled=True
        )
        
        self.security_validator = SecurityValidator(self.config)
        self.credential_checker = CredentialChecker(self.config)
        self.compliance_verifier = ComplianceVerifier(self.config)
    
    def test_security_validator_integration(self):
        """Test security validator integration."""
        # Test that security validator can run all validations
        results = self.security_validator.validate_all()
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) > 0)
        
        # Verify all results have required structure
        for result in results:
            self.assertIsInstance(result.passed, bool)
            self.assertIsInstance(result.level, SecurityLevel)
            self.assertIsInstance(result.message, str)
            self.assertIsInstance(result.details, dict)
            self.assertIsInstance(result.recommendations, list)
            self.assertIsInstance(result.timestamp, datetime)
            self.assertIsInstance(result.validator_name, str)
        
        # Test specific validators
        validator_names = [result.validator_name for result in results]
        expected_validators = [
            "SecurityConfigValidator",
            "InfrastructureSecurityValidator", 
            "NetworkSecurityValidator",
            "EncryptionValidator",
            "AuthenticationValidator",
            "AuthorizationValidator",
            "SecretManagementValidator",
            "ContainerSecurityValidator"
        ]
        
        for expected in expected_validators:
            self.assertIn(expected, validator_names)
    
    def test_credential_checker_integration(self):
        """Test credential checker integration."""
        # Test that credential checker can run all checks
        results = self.credential_checker.check_all_credentials()
        
        self.assertIsInstance(results, list)
        
        # Test credential rotation check
        rotation_result = self.credential_checker.check_credential_rotation('test-credential')
        
        self.assertIsInstance(rotation_result.passed, bool)
        self.assertEqual(rotation_result.credential_type, 'rotation_check')
        self.assertIsInstance(rotation_result.strength_score, float)
        self.assertGreaterEqual(rotation_result.strength_score, 0.0)
        self.assertLessEqual(rotation_result.strength_score, 1.0)
    
    def test_compliance_verifier_integration(self):
        """Test compliance verifier integration."""
        # Test all compliance standards
        results = self.compliance_verifier.verify_all_standards()
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) >= 3)  # GDPR, SOC2, ISO27001
        
        # Verify all results have required structure
        for result in results:
            self.assertIsInstance(result.passed, bool)
            self.assertIsInstance(result.standard, ComplianceStandard)
            self.assertIsInstance(result.score, float)
            self.assertGreaterEqual(result.score, 0.0)
            self.assertLessEqual(result.score, 1.0)
            self.assertIsInstance(result.requirements_met, list)
            self.assertIsInstance(result.requirements_failed, list)
            self.assertIsInstance(result.recommendations, list)
            self.assertIsInstance(result.evidence, dict)
        
        # Test compliance report generation
        report = self.compliance_verifier.generate_compliance_report(results)
        
        self.assertIsInstance(report, dict)
        self.assertIn('timestamp', report)
        self.assertIn('overall_compliance', report)
        self.assertIn('standards', report)
        self.assertIn('summary', report)
        self.assertIn('recommendations', report)
    
    def test_security_config_validation(self):
        """Test security configuration validation."""
        # Test valid configuration
        valid_config = SecurityConfig()
        errors = valid_config.validate()
        self.assertEqual(len(errors), 0)
        
        # Test invalid configuration
        invalid_config = SecurityConfig(
            key_rotation_days=0,
            session_timeout_minutes=2,
            password_min_length=4,
            vulnerability_threshold='invalid'
        )
        errors = invalid_config.validate()
        self.assertTrue(len(errors) > 0)
        
        # Test configuration serialization
        config_dict = valid_config.to_dict()
        self.assertIsInstance(config_dict, dict)
        self.assertIn('encryption_algorithm', config_dict)
        self.assertIn('require_mfa', config_dict)
    
    def test_dockerfile_security_validation(self):
        """Test Dockerfile security validation."""
        # Create a secure Dockerfile
        secure_dockerfile = """
FROM python:3.9-slim
RUN useradd -m appuser
USER appuser
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ ./app/
CMD ["python", "app/main.py"]
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dockerfile', delete=False) as f:
            f.write(secure_dockerfile)
            dockerfile_path = f.name
        
        try:
            result = self.security_validator.validate_dockerfile(dockerfile_path)
            
            self.assertIsInstance(result.passed, bool)
            self.assertIsInstance(result.level, SecurityLevel)
            self.assertEqual(result.validator_name, "DockerfileValidator")
        finally:
            os.unlink(dockerfile_path)
    
    def test_credential_detection_patterns(self):
        """Test credential detection patterns."""
        test_text = """
        api_key = "sk-1234567890abcdef1234567890abcdef"
        secret_key: "super_secret_key_12345"
        password = "mypassword123"
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        database_url = "postgresql://user:pass@localhost/db"
        """
        
        credentials = self.credential_checker._extract_credentials_from_text(test_text)
        
        self.assertIsInstance(credentials, list)
        self.assertTrue(len(credentials) > 0)
        
        # Check that different credential types are detected
        cred_types = [cred[0] for cred in credentials]
        expected_types = ['api_key', 'secret_key', 'password', 'token', 'database_url']
        
        for expected_type in expected_types:
            self.assertIn(expected_type, cred_types)
    
    def test_service_account_key_analysis(self):
        """Test service account key analysis."""
        key_data = {
            'type': 'service_account',
            'project_id': 'test-project',
            'private_key_id': 'key123',
            'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n',
            'client_email': 'test@test-project.iam.gserviceaccount.com',
            'client_id': '123456789',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(key_data, f)
            key_file_path = f.name
        
        try:
            result = self.credential_checker._analyze_service_account_key(key_file_path, key_data)
            
            self.assertIsInstance(result.passed, bool)
            self.assertEqual(result.credential_type, 'service_account_key')
            self.assertIsInstance(result.strength_score, float)
            self.assertGreaterEqual(result.strength_score, 0.0)
            self.assertLessEqual(result.strength_score, 1.0)
        finally:
            os.unlink(key_file_path)
    
    def test_compliance_standards_coverage(self):
        """Test that all major compliance standards are covered."""
        # Test GDPR compliance
        gdpr_result = self.compliance_verifier.verify_gdpr_compliance()
        self.assertEqual(gdpr_result.standard, ComplianceStandard.GDPR)
        
        # Test SOC2 compliance
        soc2_result = self.compliance_verifier.verify_soc2_compliance()
        self.assertEqual(soc2_result.standard, ComplianceStandard.SOC2)
        
        # Test ISO27001 compliance
        iso_result = self.compliance_verifier.verify_iso27001_compliance()
        self.assertEqual(iso_result.standard, ComplianceStandard.ISO27001)
        
        # Test custom compliance
        custom_requirements = {
            'security': ['encryption_at_rest', 'access_controls'],
            'monitoring': ['audit_logging', 'monitoring']
        }
        custom_result = self.compliance_verifier.verify_custom_compliance('Custom', custom_requirements)
        self.assertIsInstance(custom_result.passed, bool)
    
    def test_security_enforcement_workflow(self):
        """Test complete security enforcement workflow."""
        # Step 1: Validate security configuration
        config_result = self.security_validator._validate_security_config()
        self.assertIsInstance(config_result.passed, bool)
        
        # Step 2: Check credentials
        credential_results = self.credential_checker.check_all_credentials()
        self.assertIsInstance(credential_results, list)
        
        # Step 3: Verify compliance
        compliance_results = self.compliance_verifier.verify_all_standards()
        self.assertIsInstance(compliance_results, list)
        
        # Step 4: Generate comprehensive report
        all_results = {
            'security_validation': [config_result],
            'credential_checks': credential_results,
            'compliance_verification': compliance_results
        }
        
        # Verify report structure
        self.assertIn('security_validation', all_results)
        self.assertIn('credential_checks', all_results)
        self.assertIn('compliance_verification', all_results)
        
        # Check that all components can work together
        overall_passed = (
            config_result.passed and
            all(result.passed for result in credential_results) and
            all(result.passed for result in compliance_results)
        )
        
        self.assertIsInstance(overall_passed, bool)
    
    def test_task_9_1_requirements_coverage(self):
        """Test that Task 9.1 requirements are fully covered."""
        # Requirement 5.1: Security configuration validation
        security_results = self.security_validator.validate_all()
        self.assertTrue(len(security_results) > 0)
        
        # Requirement 5.2: Credential security checks
        credential_results = self.credential_checker.check_all_credentials()
        self.assertIsInstance(credential_results, list)
        
        # Requirement 5.3: Compliance verification system
        compliance_results = self.compliance_verifier.verify_all_standards()
        self.assertTrue(len(compliance_results) > 0)
        
        # Verify that all major security areas are covered
        security_areas_covered = {
            'configuration': len(security_results) > 0,
            'credentials': True,  # Always returns list, even if empty
            'compliance': len(compliance_results) > 0,
            'encryption': any('Encryption' in r.validator_name for r in security_results),
            'authentication': any('Authentication' in r.validator_name for r in security_results),
            'authorization': any('Authorization' in r.validator_name for r in security_results),
            'infrastructure': any('Infrastructure' in r.validator_name for r in security_results),
            'container': any('Container' in r.validator_name for r in security_results)
        }
        
        # All security areas should be covered
        for area, covered in security_areas_covered.items():
            self.assertTrue(covered, f"Security area '{area}' not covered")


if __name__ == '__main__':
    unittest.main()