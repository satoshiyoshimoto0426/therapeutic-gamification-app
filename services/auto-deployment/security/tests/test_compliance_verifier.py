"""
Tests for compliance verifier.
"""

import unittest
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

from ..compliance_verifier import ComplianceVerifier
from ..security_config import SecurityConfig
from ..models import ComplianceStandard


class TestComplianceVerifier(unittest.TestCase):
    """Test compliance verifier functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SecurityConfig(
            require_encryption_at_rest=True,
            require_encryption_in_transit=True,
            rbac_enabled=True,
            audit_logging=True,
            data_retention_days=2555,
            principle_of_least_privilege=True,
            require_mfa=True,
            enable_waf=True,
            require_ssl_certificates=True,
            security_monitoring_enabled=True,
            enable_code_scanning=True,
            enable_dependency_scanning=True,
            secret_rotation_enabled=True,
            require_approval_for_production=True
        )
        self.verifier = ComplianceVerifier(self.config)
    
    def test_verify_gdpr_compliance_success(self):
        """Test successful GDPR compliance verification."""
        # Create privacy policy file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Privacy Policy\nThis is our privacy policy.")
            privacy_file = f.name
        
        # Temporarily rename to privacy_policy.md
        privacy_path = 'privacy_policy.md'
        os.rename(privacy_file, privacy_path)
        
        try:
            result = self.verifier.verify_gdpr_compliance()
            
            self.assertTrue(result.passed)
            self.assertEqual(result.standard, ComplianceStandard.GDPR)
            self.assertGreaterEqual(result.score, 0.8)
            self.assertTrue(len(result.requirements_met) > 0)
            self.assertIn('encryption_at_rest', result.evidence)
            self.assertIn('audit_logging', result.evidence)
        finally:
            if os.path.exists(privacy_path):
                os.unlink(privacy_path)
    
    def test_verify_gdpr_compliance_failure(self):
        """Test GDPR compliance verification failure."""
        # Create config that fails GDPR requirements
        non_compliant_config = SecurityConfig(
            require_encryption_at_rest=False,
            require_encryption_in_transit=False,
            rbac_enabled=False,
            audit_logging=False,
            data_retention_days=0,
            principle_of_least_privilege=False
        )
        verifier = ComplianceVerifier(non_compliant_config)
        
        result = verifier.verify_gdpr_compliance()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.standard, ComplianceStandard.GDPR)
        self.assertLess(result.score, 0.8)
        self.assertTrue(len(result.requirements_failed) > 0)
        self.assertTrue(len(result.recommendations) > 0)
    
    def test_verify_soc2_compliance_success(self):
        """Test successful SOC 2 compliance verification."""
        result = self.verifier.verify_soc2_compliance()
        
        self.assertTrue(result.passed)
        self.assertEqual(result.standard, ComplianceStandard.SOC2)
        self.assertGreaterEqual(result.score, 0.75)
        self.assertTrue(len(result.requirements_met) > 0)
        self.assertIn('access_controls', result.evidence)
        self.assertIn('encryption', result.evidence)
    
    def test_verify_soc2_compliance_failure(self):
        """Test SOC 2 compliance verification failure."""
        # Create config that fails SOC 2 requirements
        non_compliant_config = SecurityConfig(
            rbac_enabled=False,
            require_mfa=False,
            enable_waf=False,
            require_ssl_certificates=False,
            security_monitoring_enabled=False,
            enable_code_scanning=False,
            enable_dependency_scanning=False,
            require_encryption_at_rest=False,
            require_encryption_in_transit=False,
            data_retention_days=0
        )
        verifier = ComplianceVerifier(non_compliant_config)
        
        result = verifier.verify_soc2_compliance()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.standard, ComplianceStandard.SOC2)
        self.assertLess(result.score, 0.75)
        self.assertTrue(len(result.requirements_failed) > 0)
        self.assertTrue(len(result.recommendations) > 0)
    
    def test_verify_iso27001_compliance_success(self):
        """Test successful ISO 27001 compliance verification."""
        # Create security policy file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("# Security Policy\nThis is our security policy.")
            security_file = f.name
        
        # Temporarily rename to SECURITY.md
        security_path = 'SECURITY.md'
        os.rename(security_file, security_path)
        
        try:
            result = self.verifier.verify_iso27001_compliance()
            
            self.assertTrue(result.passed)
            self.assertEqual(result.standard, ComplianceStandard.ISO27001)
            self.assertGreaterEqual(result.score, 0.8)
            self.assertTrue(len(result.requirements_met) > 0)
            self.assertIn('security_policy', result.evidence)
        finally:
            if os.path.exists(security_path):
                os.unlink(security_path)
    
    def test_verify_iso27001_compliance_failure(self):
        """Test ISO 27001 compliance verification failure."""
        # Create config that fails ISO 27001 requirements
        non_compliant_config = SecurityConfig(
            vulnerability_threshold='low',
            enable_container_scanning=False,
            enable_dependency_scanning=False,
            rbac_enabled=False,
            principle_of_least_privilege=False,
            require_encryption_at_rest=False,
            require_encryption_in_transit=False,
            secret_rotation_enabled=False,
            security_monitoring_enabled=False,
            real_time_alerts=False,
            require_approval_for_production=False
        )
        verifier = ComplianceVerifier(non_compliant_config)
        
        result = verifier.verify_iso27001_compliance()
        
        self.assertFalse(result.passed)
        self.assertEqual(result.standard, ComplianceStandard.ISO27001)
        self.assertLess(result.score, 0.8)
        self.assertTrue(len(result.requirements_failed) > 0)
        self.assertTrue(len(result.recommendations) > 0)
    
    def test_verify_custom_compliance(self):
        """Test custom compliance verification."""
        custom_requirements = {
            'security': ['encryption_at_rest', 'access_controls'],
            'monitoring': ['audit_logging', 'monitoring'],
            'governance': ['approval_workflow']
        }
        
        result = self.verifier.verify_custom_compliance('Custom Standard', custom_requirements)
        
        self.assertIsInstance(result.passed, bool)
        self.assertGreaterEqual(result.score, 0.0)
        self.assertLessEqual(result.score, 1.0)
        self.assertIsInstance(result.requirements_met, list)
        self.assertIsInstance(result.requirements_failed, list)
        self.assertIsInstance(result.recommendations, list)
        self.assertIsInstance(result.evidence, dict)
    
    def test_check_requirement(self):
        """Test individual requirement checking."""
        # Test requirements that should pass
        self.assertTrue(self.verifier._check_requirement('encryption_at_rest'))
        self.assertTrue(self.verifier._check_requirement('access_controls'))
        self.assertTrue(self.verifier._check_requirement('audit_logging'))
        
        # Test requirements that should fail with default config
        non_compliant_config = SecurityConfig(
            require_encryption_at_rest=False,
            rbac_enabled=False,
            audit_logging=False
        )
        verifier = ComplianceVerifier(non_compliant_config)
        
        self.assertFalse(verifier._check_requirement('encryption_at_rest'))
        self.assertFalse(verifier._check_requirement('access_controls'))
        self.assertFalse(verifier._check_requirement('audit_logging'))
        
        # Test unknown requirement
        self.assertFalse(self.verifier._check_requirement('unknown_requirement'))
    
    def test_verify_all_standards(self):
        """Test verifying all compliance standards."""
        results = self.verifier.verify_all_standards()
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) >= 3)  # GDPR, SOC2, ISO27001
        
        # Check that all results are valid
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
    
    def test_generate_compliance_report(self):
        """Test compliance report generation."""
        # Create sample results
        results = [
            self.verifier.verify_gdpr_compliance(),
            self.verifier.verify_soc2_compliance(),
            self.verifier.verify_iso27001_compliance()
        ]
        
        report = self.verifier.generate_compliance_report(results)
        
        self.assertIsInstance(report, dict)
        self.assertIn('timestamp', report)
        self.assertIn('overall_compliance', report)
        self.assertIn('standards', report)
        self.assertIn('summary', report)
        self.assertIn('recommendations', report)
        
        # Check summary
        summary = report['summary']
        self.assertEqual(summary['total_standards'], len(results))
        self.assertIsInstance(summary['passed_standards'], int)
        self.assertIsInstance(summary['failed_standards'], int)
        self.assertIsInstance(summary['average_score'], float)
        
        # Check standards
        self.assertEqual(len(report['standards']), len(results))
        for standard_name, standard_data in report['standards'].items():
            self.assertIn('passed', standard_data)
            self.assertIn('score', standard_data)
            self.assertIn('requirements_met', standard_data)
            self.assertIn('requirements_failed', standard_data)
    
    def test_generate_compliance_report_empty(self):
        """Test compliance report generation with empty results."""
        report = self.verifier.generate_compliance_report([])
        
        self.assertIsInstance(report, dict)
        self.assertEqual(report['summary']['total_standards'], 0)
        self.assertEqual(report['summary']['passed_standards'], 0)
        self.assertEqual(report['summary']['failed_standards'], 0)
        self.assertEqual(report['summary']['average_score'], 0.0)
        self.assertEqual(len(report['standards']), 0)


if __name__ == '__main__':
    unittest.main()