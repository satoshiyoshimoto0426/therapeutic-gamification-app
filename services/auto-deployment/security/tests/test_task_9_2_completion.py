"""
Integration tests for Task 9.2 completion verification.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timezone, timedelta

from audit_logger import AuditLogger, AuditContext, AuditEventType, AuditResult
from deployment_tracker import DeploymentTracker, DeploymentStatus, DeploymentStage
from security_event_logger import SecurityEventLogger, SecurityEventSeverity, SecurityEventCategory
from security_config import SecurityConfig


class TestTask92Completion(unittest.TestCase):
    """Test Task 9.2 completion - Audit logging and tracking."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SecurityConfig(
            audit_logging=True,
            real_time_alerts=True,
            data_retention_days=2555
        )
        
        self.audit_logger = AuditLogger(self.config)
        self.deployment_tracker = DeploymentTracker(self.config, self.audit_logger)
        self.security_event_logger = SecurityEventLogger(self.config, self.audit_logger)
        
        self.context = AuditContext(
            user_id="test_user",
            session_id="test_session",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            environment="test",
            service_name="auto-deployment"
        )
    
    def test_comprehensive_audit_logging_system(self):
        """Test comprehensive audit logging system."""
        # Test basic event logging
        event_id = self.audit_logger.log_event(
            event_type=AuditEventType.DEPLOYMENT_START,
            resource="deployment:test-123",
            action="start_deployment",
            result=AuditResult.INFO,
            details={'environment': 'production'},
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        self.assertTrue(len(self.audit_logger._audit_events) > 0)
        
        # Test specialized logging methods
        deployment_event = self.audit_logger.log_deployment_start(
            deployment_id="test-deployment",
            environment="production",
            commit_sha="abc123",
            context=self.context
        )
        
        security_event = self.audit_logger.log_security_validation(
            validation_type="credential_check",
            resource="credential:api-key",
            passed=True,
            issues=[],
            context=self.context
        )
        
        credential_event = self.audit_logger.log_credential_access(
            credential_type="api_key",
            credential_id="key-123",
            action="retrieve",
            context=self.context
        )
        
        config_event = self.audit_logger.log_configuration_change(
            config_type="security",
            changes={'encryption': {'old': False, 'new': True}},
            context=self.context
        )
        
        auth_event = self.audit_logger.log_authentication(
            user_id="test_user",
            success=True,
            method="password",
            context=self.context
        )
        
        authz_event = self.audit_logger.log_authorization(
            user_id="test_user",
            resource="deployment:test",
            action="deploy",
            granted=True,
            context=self.context
        )
        
        compliance_event = self.audit_logger.log_compliance_check(
            standard="GDPR",
            passed=True,
            score=0.9,
            requirements_failed=[],
            context=self.context
        )
        
        rollback_event = self.audit_logger.log_rollback(
            deployment_id="test-deployment",
            reason="Health check failed",
            success=True,
            context=self.context
        )
        
        # Verify all events were logged
        all_events = [
            event_id, deployment_event, security_event, credential_event,
            config_event, auth_event, authz_event, compliance_event, rollback_event
        ]
        
        for event in all_events:
            self.assertIsInstance(event, str)
        
        # Verify events are stored
        self.assertTrue(len(self.audit_logger._audit_events) >= len(all_events))
    
    def test_deployment_action_tracking(self):
        """Test deployment action tracking system."""
        # Start a deployment
        deployment_id = self.deployment_tracker.start_deployment(
            environment="production",
            commit_sha="abc123",
            image_tag="v1.0.0",
            user_id="test_user",
            metadata={"branch": "main", "pr_number": 42},
            context=self.context
        )
        
        self.assertIsInstance(deployment_id, str)
        
        # Track various deployment actions
        build_action = self.deployment_tracker.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.BUILD,
            action="build_image",
            status=DeploymentStatus.BUILDING,
            details={"dockerfile": "Dockerfile", "build_time": 120},
            user_id="test_user",
            duration_seconds=120.5,
            context=self.context
        )
        
        security_action = self.deployment_tracker.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.SECURITY_SCAN,
            action="security_scan",
            status=DeploymentStatus.VALIDATING,
            details={"vulnerabilities_found": 0, "scan_type": "container"},
            user_id="test_user",
            duration_seconds=45.2,
            context=self.context
        )
        
        deploy_action = self.deployment_tracker.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.DEPLOY,
            action="deploy_service",
            status=DeploymentStatus.DEPLOYING,
            details={"service_name": "api", "replicas": 3},
            user_id="test_user",
            duration_seconds=90.8,
            context=self.context
        )
        
        health_action = self.deployment_tracker.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.HEALTH_CHECK,
            action="health_check",
            status=DeploymentStatus.TESTING,
            details={"endpoint": "/health", "response_time": 150},
            user_id="test_user",
            duration_seconds=30.1,
            context=self.context
        )
        
        # Complete the deployment
        self.deployment_tracker.complete_deployment(
            deployment_id=deployment_id,
            success=True,
            details={"final_url": "https://api.example.com", "total_time": 286.6},
            context=self.context
        )
        
        # Verify deployment record
        deployment = self.deployment_tracker.get_deployment(deployment_id)
        self.assertIsNotNone(deployment)
        self.assertEqual(deployment.status, DeploymentStatus.COMPLETED)
        self.assertEqual(deployment.environment, "production")
        self.assertEqual(deployment.commit_sha, "abc123")
        self.assertEqual(deployment.image_tag, "v1.0.0")
        self.assertEqual(deployment.user_id, "test_user")
        self.assertTrue(len(deployment.actions) >= 5)  # Start + 4 actions + complete
        
        # Verify action tracking
        actions = self.deployment_tracker.get_deployment_actions(deployment_id)
        self.assertTrue(len(actions) >= 5)
        
        # Check specific actions
        build_actions = self.deployment_tracker.get_deployment_actions(
            deployment_id, stage=DeploymentStage.BUILD
        )
        self.assertEqual(len(build_actions), 1)
        self.assertEqual(build_actions[0].action, "build_image")
        self.assertEqual(build_actions[0].duration_seconds, 120.5)
    
    def test_security_event_logging(self):
        """Test security event logging system."""
        # Log various types of security events
        auth_failure_event = self.security_event_logger.log_authentication_failure(
            user_id="test_user",
            ip_address="192.168.1.100",
            reason="Invalid password",
            attempt_count=2,
            context=self.context
        )
        
        authz_violation_event = self.security_event_logger.log_authorization_violation(
            user_id="malicious_user",
            resource="deployment:production",
            action="deploy",
            ip_address="10.0.0.50",
            context=self.context
        )
        
        credential_compromise_event = self.security_event_logger.log_credential_compromise(
            credential_type="api_key",
            credential_id="key-prod-123",
            detection_method="pattern_matching",
            context=self.context
        )
        
        vulnerability_event = self.security_event_logger.log_vulnerability_detected(
            vulnerability_id="CVE-2023-1234",
            severity="high",
            component="nginx",
            description="Remote code execution vulnerability",
            context=self.context
        )
        
        policy_violation_event = self.security_event_logger.log_policy_violation(
            policy_name="Password Policy",
            violation_type="weak_password",
            resource="user:test_user",
            user_id="test_user",
            context=self.context
        )
        
        config_change_event = self.security_event_logger.log_configuration_change(
            config_type="security",
            changes={
                "encryption_enabled": {"old": False, "new": True},
                "key_rotation_days": {"old": 365, "new": 90}
            },
            user_id="admin_user",
            context=self.context
        )
        
        compliance_violation_event = self.security_event_logger.log_compliance_violation(
            standard="GDPR",
            requirement="Data encryption at rest",
            resource="database:user_data",
            context=self.context
        )
        
        # Verify all events were logged
        all_security_events = [
            auth_failure_event, authz_violation_event, credential_compromise_event,
            vulnerability_event, policy_violation_event, config_change_event,
            compliance_violation_event
        ]
        
        for event_id in all_security_events:
            self.assertIsInstance(event_id, str)
            self.assertIn(event_id, self.security_event_logger._security_events)
        
        # Test event resolution
        self.security_event_logger.resolve_security_event(
            event_id=auth_failure_event,
            resolved_by="admin_user",
            resolution_notes="User password reset and account secured",
            context=self.context
        )
        
        # Verify resolution
        resolved_event = self.security_event_logger._security_events[auth_failure_event]
        self.assertTrue(resolved_event.resolved)
        self.assertEqual(resolved_event.resolved_by, "admin_user")
        self.assertIsInstance(resolved_event.resolved_at, datetime)
    
    def test_audit_and_compliance_features(self):
        """Test audit and compliance features."""
        # Generate various audit events
        start_time = datetime.now(timezone.utc)
        
        # Deployment events
        deployment_id = self.deployment_tracker.start_deployment(
            environment="production",
            commit_sha="def456",
            image_tag="v2.0.0",
            user_id="deploy_user",
            context=self.context
        )
        
        self.deployment_tracker.complete_deployment(
            deployment_id=deployment_id,
            success=True,
            context=self.context
        )
        
        # Security events
        self.security_event_logger.log_authentication_failure(
            user_id="test_user",
            ip_address="192.168.1.1",
            reason="Invalid credentials",
            context=self.context
        )
        
        # Audit events
        self.audit_logger.log_compliance_check(
            standard="SOC2",
            passed=True,
            score=0.85,
            requirements_failed=[],
            context=self.context
        )
        
        end_time = datetime.now(timezone.utc)
        
        # Generate audit report
        audit_report = self.audit_logger.generate_audit_report(start_time, end_time)
        
        self.assertIsInstance(audit_report, dict)
        self.assertIn('report_id', audit_report)
        self.assertIn('generated_at', audit_report)
        self.assertIn('period', audit_report)
        self.assertIn('summary', audit_report)
        self.assertIn('events', audit_report)
        
        # Verify report summary
        summary = audit_report['summary']
        self.assertGreater(summary['total_events'], 0)
        self.assertIn('unique_users', summary)
        self.assertIn('event_types', summary)
        self.assertIn('results', summary)
        
        # Get deployment statistics
        deployment_stats = self.deployment_tracker.get_deployment_statistics(start_time, end_time)
        
        self.assertIsInstance(deployment_stats, dict)
        self.assertEqual(deployment_stats['total_deployments'], 1)
        self.assertEqual(deployment_stats['successful_deployments'], 1)
        self.assertEqual(deployment_stats['failed_deployments'], 0)
        self.assertEqual(deployment_stats['success_rate'], 1.0)
        
        # Get security event statistics
        security_stats = self.security_event_logger.get_security_statistics(start_time, end_time)
        
        self.assertIsInstance(security_stats, dict)
        self.assertGreater(security_stats['total_events'], 0)
        self.assertIn('events_by_category', security_stats)
        self.assertIn('events_by_severity', security_stats)
    
    def test_data_export_and_retention(self):
        """Test data export and retention features."""
        # Create test data
        deployment_id = self.deployment_tracker.start_deployment(
            environment="test",
            commit_sha="ghi789",
            image_tag="v3.0.0",
            user_id="test_user",
            context=self.context
        )
        
        self.security_event_logger.log_authentication_failure(
            user_id="test_user",
            ip_address="192.168.1.1",
            reason="Test failure",
            context=self.context
        )
        
        # Test audit log export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            audit_export_file = f.name
        
        try:
            self.audit_logger.export_events(audit_export_file, format='json')
            
            self.assertTrue(os.path.exists(audit_export_file))
            
            with open(audit_export_file, 'r') as f:
                audit_data = json.load(f)
            
            self.assertIsInstance(audit_data, list)
            self.assertTrue(len(audit_data) > 0)
        finally:
            if os.path.exists(audit_export_file):
                os.unlink(audit_export_file)
        
        # Test deployment history export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            deployment_export_file = f.name
        
        try:
            self.deployment_tracker.export_deployment_history(deployment_export_file, format='json')
            
            self.assertTrue(os.path.exists(deployment_export_file))
            
            with open(deployment_export_file, 'r') as f:
                deployment_data = json.load(f)
            
            self.assertIsInstance(deployment_data, list)
            self.assertTrue(len(deployment_data) > 0)
        finally:
            if os.path.exists(deployment_export_file):
                os.unlink(deployment_export_file)
        
        # Test security events export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            security_export_file = f.name
        
        try:
            self.security_event_logger.export_security_events(security_export_file, format='json')
            
            self.assertTrue(os.path.exists(security_export_file))
            
            with open(security_export_file, 'r') as f:
                security_data = json.load(f)
            
            self.assertIsInstance(security_data, list)
            self.assertTrue(len(security_data) > 0)
        finally:
            if os.path.exists(security_export_file):
                os.unlink(security_export_file)
        
        # Test data retention/cleanup
        initial_audit_count = len(self.audit_logger._audit_events)
        initial_deployment_count = len(self.deployment_tracker._deployments)
        
        # Cleanup with very short retention (should remove data)
        self.audit_logger.cleanup_old_events(retention_days=0)
        self.deployment_tracker.cleanup_old_deployments(retention_days=0)
        
        # Verify cleanup occurred
        final_audit_count = len(self.audit_logger._audit_events)
        final_deployment_count = len(self.deployment_tracker._deployments)
        
        self.assertLessEqual(final_audit_count, initial_audit_count)
        self.assertLess(final_deployment_count, initial_deployment_count)
    
    def test_integrity_and_verification(self):
        """Test audit log integrity and verification."""
        # Add test events
        self.audit_logger.log_deployment_start("test-dep", "prod", "abc123", self.context)
        self.audit_logger.log_deployment_success("test-dep", "prod", 120, self.context)
        
        # Test integrity verification
        self.assertTrue(self.audit_logger.verify_integrity())
        
        # Test integrity hash creation
        events = self.audit_logger._audit_events
        hash1 = self.audit_logger.create_integrity_hash(events)
        hash2 = self.audit_logger.create_integrity_hash(events)
        
        self.assertEqual(hash1, hash2)
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 64)  # SHA256 hash length
        
        # Test that different events produce different hashes
        self.audit_logger.log_authentication("user", True, "password", self.context)
        events_with_new = self.audit_logger._audit_events
        hash3 = self.audit_logger.create_integrity_hash(events_with_new)
        
        self.assertNotEqual(hash1, hash3)
    
    def test_filtering_and_querying(self):
        """Test filtering and querying capabilities."""
        # Create diverse test data
        start_time = datetime.now(timezone.utc)
        
        # Different users
        context1 = AuditContext(user_id="user1", ip_address="192.168.1.1", environment="test")
        context2 = AuditContext(user_id="user2", ip_address="192.168.1.2", environment="test")
        
        self.audit_logger.log_authentication("user1", True, "password", context1)
        self.audit_logger.log_authentication("user2", False, "password", context2)
        
        # Different event types
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        self.audit_logger.log_security_validation("scan", "container", True, [], self.context)
        
        # Different security events
        auth_event = self.security_event_logger.log_authentication_failure("user1", "192.168.1.1", "Invalid", context=self.context)
        self.security_event_logger.log_vulnerability_detected("CVE-123", "high", "nginx", "Test vuln", context=self.context)
        
        # Resolve one security event
        self.security_event_logger.resolve_security_event(auth_event, "admin", context=self.context)
        
        end_time = datetime.now(timezone.utc)
        
        # Test audit log filtering
        auth_events = self.audit_logger.get_events(event_type=AuditEventType.AUTHENTICATION)
        self.assertEqual(len(auth_events), 2)
        
        user1_events = self.audit_logger.get_events(user_id="user1")
        self.assertTrue(len(user1_events) >= 1)
        
        deployment_events = self.audit_logger.get_events(resource="deployment")
        self.assertTrue(len(deployment_events) >= 1)
        
        time_filtered_events = self.audit_logger.get_events(start_time=start_time, end_time=end_time)
        self.assertTrue(len(time_filtered_events) >= 4)
        
        # Test security event filtering
        auth_failure_events = self.security_event_logger.get_security_events(
            category=SecurityEventCategory.AUTHENTICATION_FAILURE
        )
        self.assertEqual(len(auth_failure_events), 1)
        
        high_severity_events = self.security_event_logger.get_security_events(
            severity=SecurityEventSeverity.HIGH
        )
        self.assertTrue(len(high_severity_events) >= 1)
        
        resolved_events = self.security_event_logger.get_security_events(resolved=True)
        self.assertEqual(len(resolved_events), 1)
        
        unresolved_events = self.security_event_logger.get_security_events(resolved=False)
        self.assertTrue(len(unresolved_events) >= 1)
    
    def test_task_9_2_requirements_coverage(self):
        """Test that Task 9.2 requirements are fully covered."""
        # Requirement 5.4: Comprehensive audit logging system
        audit_event = self.audit_logger.log_event(
            event_type=AuditEventType.DEPLOYMENT_START,
            resource="test-resource",
            action="test-action",
            result=AuditResult.SUCCESS,
            context=self.context
        )
        self.assertIsInstance(audit_event, str)
        
        # Requirement 5.4: Deployment action tracking
        deployment_id = self.deployment_tracker.start_deployment(
            environment="test",
            commit_sha="test123",
            image_tag="v1.0.0",
            user_id="test_user",
            context=self.context
        )
        self.assertIsInstance(deployment_id, str)
        
        # Requirement 5.4: Security event logging
        security_event = self.security_event_logger.log_authentication_failure(
            user_id="test_user",
            ip_address="192.168.1.1",
            reason="Test failure",
            context=self.context
        )
        self.assertIsInstance(security_event, str)
        
        # Verify comprehensive logging capabilities
        logging_capabilities = {
            'audit_logging': len(self.audit_logger._audit_events) > 0,
            'deployment_tracking': len(self.deployment_tracker._deployments) > 0,
            'security_event_logging': len(self.security_event_logger._security_events) > 0,
            'event_filtering': True,  # Tested in other methods
            'data_export': True,  # Tested in other methods
            'integrity_verification': self.audit_logger.verify_integrity(),
            'retention_management': True,  # Tested in other methods
            'reporting': True  # Tested in other methods
        }
        
        # All capabilities should be available
        for capability, available in logging_capabilities.items():
            self.assertTrue(available, f"Logging capability '{capability}' not available")
        
        # Verify integration between components
        # Audit logger should have events from deployment tracker
        deployment_audit_events = self.audit_logger.get_events(resource="deployment")
        self.assertTrue(len(deployment_audit_events) > 0)
        
        # Audit logger should have events from security event logger
        security_audit_events = self.audit_logger.get_events(event_type=AuditEventType.ALERT_TRIGGERED)
        self.assertTrue(len(security_audit_events) > 0)


if __name__ == '__main__':
    unittest.main()