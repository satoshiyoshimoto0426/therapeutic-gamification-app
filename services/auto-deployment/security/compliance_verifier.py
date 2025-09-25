"""
Compliance verification system.
"""

import os
import json
import yaml
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .models import ComplianceResult, ComplianceStandard
from .security_config import SecurityConfig


class ComplianceVerifier:
    """Verifies compliance with various security standards."""
    
    def __init__(self, config: SecurityConfig):
        """Initialize compliance verifier."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Compliance requirements mapping
        self.compliance_requirements = {
            ComplianceStandard.GDPR: {
                'data_protection': ['encryption_at_rest', 'encryption_in_transit', 'access_controls'],
                'privacy_by_design': ['data_minimization', 'purpose_limitation', 'consent_management'],
                'data_subject_rights': ['data_portability', 'right_to_erasure', 'access_requests'],
                'accountability': ['audit_logging', 'data_protection_impact_assessment', 'privacy_policy'],
                'breach_notification': ['incident_response', 'notification_procedures', 'breach_logging']
            },
            ComplianceStandard.SOC2: {
                'security': ['access_controls', 'logical_access', 'network_security'],
                'availability': ['monitoring', 'incident_response', 'backup_procedures'],
                'processing_integrity': ['data_validation', 'error_handling', 'quality_controls'],
                'confidentiality': ['encryption', 'access_restrictions', 'data_classification'],
                'privacy': ['privacy_notice', 'consent_management', 'data_retention']
            },
            ComplianceStandard.ISO27001: {
                'information_security_policy': ['policy_document', 'management_commitment', 'policy_review'],
                'risk_management': ['risk_assessment', 'risk_treatment', 'risk_monitoring'],
                'asset_management': ['asset_inventory', 'asset_classification', 'asset_handling'],
                'access_control': ['access_policy', 'user_access_management', 'privileged_access'],
                'cryptography': ['encryption_policy', 'key_management', 'cryptographic_controls']
            }
        }
    
    def verify_all_standards(self) -> List[ComplianceResult]:
        """Verify compliance with all configured standards."""
        results = []
        
        if self.config.gdpr_compliance:
            results.append(self.verify_gdpr_compliance())
        
        # Add other standards as needed
        results.append(self.verify_soc2_compliance())
        results.append(self.verify_iso27001_compliance())
        
        return results
    
    def verify_gdpr_compliance(self) -> ComplianceResult:
        """Verify GDPR compliance."""
        requirements_met = []
        requirements_failed = []
        evidence = {}
        recommendations = []
        
        # Data Protection requirements
        if self.config.require_encryption_at_rest:
            requirements_met.append("Encryption at rest implemented")
            evidence['encryption_at_rest'] = True
        else:
            requirements_failed.append("Encryption at rest not implemented")
            recommendations.append("Enable encryption at rest for GDPR compliance")
        
        if self.config.require_encryption_in_transit:
            requirements_met.append("Encryption in transit implemented")
            evidence['encryption_in_transit'] = True
        else:
            requirements_failed.append("Encryption in transit not implemented")
            recommendations.append("Enable encryption in transit for GDPR compliance")
        
        # Access Controls
        if self.config.rbac_enabled:
            requirements_met.append("Role-based access control implemented")
            evidence['rbac'] = True
        else:
            requirements_failed.append("Role-based access control not implemented")
            recommendations.append("Implement RBAC for proper access control")
        
        # Audit Logging
        if self.config.audit_logging:
            requirements_met.append("Audit logging enabled")
            evidence['audit_logging'] = True
        else:
            requirements_failed.append("Audit logging not enabled")
            recommendations.append("Enable audit logging for GDPR compliance")
        
        # Data Retention
        if self.config.data_retention_days > 0:
            requirements_met.append("Data retention policy configured")
            evidence['data_retention_days'] = self.config.data_retention_days
        else:
            requirements_failed.append("Data retention policy not configured")
            recommendations.append("Configure data retention policy")
        
        # Privacy by Design
        if self.config.principle_of_least_privilege:
            requirements_met.append("Principle of least privilege implemented")
            evidence['least_privilege'] = True
        else:
            requirements_failed.append("Principle of least privilege not implemented")
            recommendations.append("Implement principle of least privilege")
        
        # Check for privacy policy and consent management (mock)
        privacy_policy_exists = os.path.exists('privacy_policy.md') or os.path.exists('PRIVACY.md')
        if privacy_policy_exists:
            requirements_met.append("Privacy policy documented")
            evidence['privacy_policy'] = True
        else:
            requirements_failed.append("Privacy policy not documented")
            recommendations.append("Create and maintain privacy policy documentation")
        
        # Calculate compliance score
        total_requirements = len(requirements_met) + len(requirements_failed)
        score = len(requirements_met) / total_requirements if total_requirements > 0 else 0.0
        passed = score >= 0.8  # 80% compliance threshold
        
        return ComplianceResult(
            passed=passed,
            standard=ComplianceStandard.GDPR,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            score=score,
            recommendations=recommendations,
            evidence=evidence
        )
    
    def verify_soc2_compliance(self) -> ComplianceResult:
        """Verify SOC 2 compliance."""
        requirements_met = []
        requirements_failed = []
        evidence = {}
        recommendations = []
        
        # Security - Access Controls
        if self.config.rbac_enabled and self.config.require_mfa:
            requirements_met.append("Access controls implemented")
            evidence['access_controls'] = True
        else:
            requirements_failed.append("Access controls insufficient")
            recommendations.append("Implement RBAC and MFA for SOC 2 compliance")
        
        # Security - Network Security
        if self.config.enable_waf and self.config.require_ssl_certificates:
            requirements_met.append("Network security controls implemented")
            evidence['network_security'] = True
        else:
            requirements_failed.append("Network security controls insufficient")
            recommendations.append("Enable WAF and SSL certificates")
        
        # Availability - Monitoring
        if self.config.security_monitoring_enabled:
            requirements_met.append("Security monitoring implemented")
            evidence['monitoring'] = True
        else:
            requirements_failed.append("Security monitoring not implemented")
            recommendations.append("Enable security monitoring for availability")
        
        # Processing Integrity - Data Validation
        if self.config.enable_code_scanning and self.config.enable_dependency_scanning:
            requirements_met.append("Data validation controls implemented")
            evidence['data_validation'] = True
        else:
            requirements_failed.append("Data validation controls insufficient")
            recommendations.append("Enable code and dependency scanning")
        
        # Confidentiality - Encryption
        if self.config.require_encryption_at_rest and self.config.require_encryption_in_transit:
            requirements_met.append("Encryption controls implemented")
            evidence['encryption'] = True
        else:
            requirements_failed.append("Encryption controls insufficient")
            recommendations.append("Enable encryption at rest and in transit")
        
        # Privacy - Data Retention
        if self.config.data_retention_days > 0:
            requirements_met.append("Data retention policy implemented")
            evidence['data_retention'] = True
        else:
            requirements_failed.append("Data retention policy not implemented")
            recommendations.append("Implement data retention policy")
        
        # Calculate compliance score
        total_requirements = len(requirements_met) + len(requirements_failed)
        score = len(requirements_met) / total_requirements if total_requirements > 0 else 0.0
        passed = score >= 0.75  # 75% compliance threshold for SOC 2
        
        return ComplianceResult(
            passed=passed,
            standard=ComplianceStandard.SOC2,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            score=score,
            recommendations=recommendations,
            evidence=evidence
        )
    
    def verify_iso27001_compliance(self) -> ComplianceResult:
        """Verify ISO 27001 compliance."""
        requirements_met = []
        requirements_failed = []
        evidence = {}
        recommendations = []
        
        # Information Security Policy
        security_policy_exists = os.path.exists('SECURITY.md') or os.path.exists('security_policy.md')
        if security_policy_exists:
            requirements_met.append("Information security policy documented")
            evidence['security_policy'] = True
        else:
            requirements_failed.append("Information security policy not documented")
            recommendations.append("Create and maintain information security policy")
        
        # Risk Management
        if self.config.vulnerability_threshold in ['medium', 'high', 'critical']:
            requirements_met.append("Risk management controls implemented")
            evidence['risk_management'] = True
        else:
            requirements_failed.append("Risk management controls insufficient")
            recommendations.append("Set appropriate vulnerability threshold for risk management")
        
        # Asset Management
        if self.config.enable_container_scanning and self.config.enable_dependency_scanning:
            requirements_met.append("Asset management controls implemented")
            evidence['asset_management'] = True
        else:
            requirements_failed.append("Asset management controls insufficient")
            recommendations.append("Enable container and dependency scanning for asset management")
        
        # Access Control
        if self.config.rbac_enabled and self.config.principle_of_least_privilege:
            requirements_met.append("Access control implemented")
            evidence['access_control'] = True
        else:
            requirements_failed.append("Access control insufficient")
            recommendations.append("Implement RBAC and principle of least privilege")
        
        # Cryptography
        if (self.config.require_encryption_at_rest and 
            self.config.require_encryption_in_transit and 
            self.config.secret_rotation_enabled):
            requirements_met.append("Cryptographic controls implemented")
            evidence['cryptography'] = True
        else:
            requirements_failed.append("Cryptographic controls insufficient")
            recommendations.append("Implement comprehensive cryptographic controls")
        
        # Incident Management
        if self.config.security_monitoring_enabled and self.config.real_time_alerts:
            requirements_met.append("Incident management controls implemented")
            evidence['incident_management'] = True
        else:
            requirements_failed.append("Incident management controls insufficient")
            recommendations.append("Enable security monitoring and real-time alerts")
        
        # Business Continuity
        if self.config.require_approval_for_production:
            requirements_met.append("Business continuity controls implemented")
            evidence['business_continuity'] = True
        else:
            requirements_failed.append("Business continuity controls insufficient")
            recommendations.append("Require approval for production deployments")
        
        # Calculate compliance score
        total_requirements = len(requirements_met) + len(requirements_failed)
        score = len(requirements_met) / total_requirements if total_requirements > 0 else 0.0
        passed = score >= 0.8  # 80% compliance threshold for ISO 27001
        
        return ComplianceResult(
            passed=passed,
            standard=ComplianceStandard.ISO27001,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            score=score,
            recommendations=recommendations,
            evidence=evidence
        )
    
    def verify_custom_compliance(self, standard_name: str, requirements: Dict[str, List[str]]) -> ComplianceResult:
        """Verify compliance with custom standard."""
        requirements_met = []
        requirements_failed = []
        evidence = {}
        recommendations = []
        
        for category, req_list in requirements.items():
            for requirement in req_list:
                # Mock implementation - in real system would check actual compliance
                if self._check_requirement(requirement):
                    requirements_met.append(f"{category}: {requirement}")
                    evidence[requirement] = True
                else:
                    requirements_failed.append(f"{category}: {requirement}")
                    recommendations.append(f"Implement {requirement} for {category}")
        
        # Calculate compliance score
        total_requirements = len(requirements_met) + len(requirements_failed)
        score = len(requirements_met) / total_requirements if total_requirements > 0 else 0.0
        passed = score >= 0.75  # 75% compliance threshold
        
        return ComplianceResult(
            passed=passed,
            standard=ComplianceStandard.ISO27001,  # Use as default
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            score=score,
            recommendations=recommendations,
            evidence=evidence
        )
    
    def _check_requirement(self, requirement: str) -> bool:
        """Check if a specific requirement is met."""
        # Map requirements to configuration checks
        requirement_checks = {
            'encryption_at_rest': self.config.require_encryption_at_rest,
            'encryption_in_transit': self.config.require_encryption_in_transit,
            'access_controls': self.config.rbac_enabled,
            'audit_logging': self.config.audit_logging,
            'mfa': self.config.require_mfa,
            'monitoring': self.config.security_monitoring_enabled,
            'vulnerability_scanning': self.config.enable_dependency_scanning,
            'secret_management': self.config.secret_rotation_enabled,
            'network_security': self.config.enable_waf,
            'data_retention': self.config.data_retention_days > 0,
            'least_privilege': self.config.principle_of_least_privilege,
            'approval_workflow': self.config.require_approval_for_production
        }
        
        return requirement_checks.get(requirement, False)
    
    def generate_compliance_report(self, results: List[ComplianceResult]) -> Dict[str, Any]:
        """Generate comprehensive compliance report."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_compliance': True,
            'standards': {},
            'summary': {
                'total_standards': len(results),
                'passed_standards': 0,
                'failed_standards': 0,
                'average_score': 0.0
            },
            'recommendations': []
        }
        
        total_score = 0.0
        all_recommendations = set()
        
        for result in results:
            report['standards'][result.standard.value] = result.to_dict()
            
            if result.passed:
                report['summary']['passed_standards'] += 1
            else:
                report['summary']['failed_standards'] += 1
                report['overall_compliance'] = False
            
            total_score += result.score
            all_recommendations.update(result.recommendations)
        
        if results:
            report['summary']['average_score'] = total_score / len(results)
        
        report['recommendations'] = list(all_recommendations)
        
        return report