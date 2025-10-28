"""
Tests for audit logger.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from ..audit_logger import AuditLogger, AuditContext, AuditEventType, AuditResult
from ..security_config import SecurityConfig
from ..models import SecurityAuditEvent


class TestAuditLogger(unittest.TestCase):
    """Test audit logger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SecurityConfig(audit_logging=True)
        self.audit_logger = AuditLogger(self.config)
        self.context = AuditContext(
            user_id="test_user",
            session_id="test_session",
            ip_address="192.168.1.1",
            user_agent="test_agent",
            environment="test"
        )
    
    def test_log_event(self):
        """Test basic event logging."""
        event_id = self.audit_logger.log_event(
            event_type=AuditEventType.DEPLOYMENT_START,
            resource="deployment:test-123",
            action="start_deployment",
            result=AuditResult.INFO,
            details={'test': 'data'},
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        self.assertTrue(len(self.audit_logger._audit_events) > 0)
        
        # Check that event was stored
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_id, event_id)
        self.assertEqual(event.event_type, AuditEventType.DEPLOYMENT_START.value)
        self.assertEqual(event.resource, "deployment:test-123")
        self.assertEqual(event.action, "start_deployment")
        self.assertEqual(event.result, AuditResult.INFO.value)
        self.assertEqual(event.user_id, "test_user")
        self.assertEqual(event.ip_address, "192.168.1.1")
    
    def test_log_deployment_start(self):
        """Test deployment start logging."""
        event_id = self.audit_logger.log_deployment_start(
            deployment_id="test-deployment",
            environment="production",
            commit_sha="abc123",
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        
        # Check event details
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.DEPLOYMENT_START.value)
        self.assertIn('deployment_id', event.details)
        self.assertIn('environment', event.details)
        self.assertIn('commit_sha', event.details)
        self.assertEqual(event.details['deployment_id'], "test-deployment")
        self.assertEqual(event.details['environment'], "production")
        self.assertEqual(event.details['commit_sha'], "abc123")
    
    def test_log_deployment_success(self):
        """Test deployment success logging."""
        event_id = self.audit_logger.log_deployment_success(
            deployment_id="test-deployment",
            environment="production",
            duration_seconds=120.5,
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        
        # Check event details
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.DEPLOYMENT_SUCCESS.value)
        self.assertEqual(event.result, AuditResult.SUCCESS.value)
        self.assertEqual(event.details['duration_seconds'], 120.5)
    
    def test_log_deployment_failure(self):
        """Test deployment failure logging."""
        error_details = {'error_code': 500, 'stack_trace': 'test trace'}
        
        event_id = self.audit_logger.log_deployment_failure(
            deployment_id="test-deployment",
            environment="production",
            error_message="Deployment failed",
            error_details=error_details,
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        
        # Check event details
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.DEPLOYMENT_FAILURE.value)
        self.assertEqual(event.result, AuditResult.FAILURE.value)
        self.assertEqual(event.details['error_message'], "Deployment failed")
        self.assertEqual(event.details['error_details'], error_details)
    
    def test_log_security_validation(self):
        """Test security validation logging."""
        issues = ["Issue 1", "Issue 2"]
        
        event_id = self.audit_logger.log_security_validation(
            validation_type="credential_check",
            resource="credential:api-key",
            passed=False,
            issues=issues,
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        
        # Check event details
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.SECURITY_VALIDATION.value)
        self.assertEqual(event.result, AuditResult.FAILURE.value)
        self.assertEqual(event.details['validation_type'], "credential_check")
        self.assertEqual(event.details['passed'], False)
        self.assertEqual(event.details['issues'], issues)
    
    def test_log_credential_access(self):
        """Test credential access logging."""
        event_id = self.audit_logger.log_credential_access(
            credential_type="api_key",
            credential_id="key-123",
            action="retrieve",
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        
        # Check event details
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.CREDENTIAL_ACCESS.value)
        self.assertEqual(event.details['credential_type'], "api_key")
        self.assertEqual(event.details['credential_id'], "key-123")
    
    def test_log_configuration_change(self):
        """Test configuration change logging."""
        changes = {'setting1': {'old': 'value1', 'new': 'value2'}}
        
        event_id = self.audit_logger.log_configuration_change(
            config_type="security",
            changes=changes,
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        
        # Check event details
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.CONFIGURATION_CHANGE.value)
        self.assertEqual(event.details['config_type'], "security")
        self.assertEqual(event.details['changes'], changes)
    
    def test_log_authentication(self):
        """Test authentication logging."""
        # Test successful authentication
        event_id = self.audit_logger.log_authentication(
            user_id="test_user",
            success=True,
            method="password",
            context=self.context
        )
        
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.AUTHENTICATION.value)
        self.assertEqual(event.result, AuditResult.SUCCESS.value)
        
        # Test failed authentication
        event_id = self.audit_logger.log_authentication(
            user_id="test_user",
            success=False,
            method="password",
            context=self.context
        )
        
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.result, AuditResult.FAILURE.value)
    
    def test_log_authorization(self):
        """Test authorization logging."""
        # Test granted authorization
        event_id = self.audit_logger.log_authorization(
            user_id="test_user",
            resource="deployment:test",
            action="deploy",
            granted=True,
            context=self.context
        )
        
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.AUTHORIZATION.value)
        self.assertEqual(event.result, AuditResult.SUCCESS.value)
        
        # Test denied authorization
        event_id = self.audit_logger.log_authorization(
            user_id="test_user",
            resource="deployment:test",
            action="deploy",
            granted=False,
            context=self.context
        )
        
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.result, AuditResult.FAILURE.value)
    
    def test_log_compliance_check(self):
        """Test compliance check logging."""
        requirements_failed = ["Requirement 1", "Requirement 2"]
        
        event_id = self.audit_logger.log_compliance_check(
            standard="GDPR",
            passed=False,
            score=0.7,
            requirements_failed=requirements_failed,
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        
        # Check event details
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.COMPLIANCE_CHECK.value)
        self.assertEqual(event.result, AuditResult.FAILURE.value)
        self.assertEqual(event.details['standard'], "GDPR")
        self.assertEqual(event.details['score'], 0.7)
        self.assertEqual(event.details['requirements_failed'], requirements_failed)
    
    def test_log_rollback(self):
        """Test rollback logging."""
        # Test successful rollback
        event_id = self.audit_logger.log_rollback(
            deployment_id="test-deployment",
            reason="Health check failed",
            success=True,
            context=self.context
        )
        
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.ROLLBACK_COMPLETED.value)
        self.assertEqual(event.result, AuditResult.SUCCESS.value)
        
        # Test rollback initiation
        event_id = self.audit_logger.log_rollback(
            deployment_id="test-deployment",
            reason="Health check failed",
            success=False,
            context=self.context
        )
        
        event = self.audit_logger._audit_events[-1]
        self.assertEqual(event.event_type, AuditEventType.ROLLBACK_INITIATED.value)
        self.assertEqual(event.result, AuditResult.WARNING.value)
    
    def test_get_events_no_filter(self):
        """Test getting all events without filters."""
        # Add some test events
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        self.audit_logger.log_deployment_success("dep1", "prod", 120, self.context)
        
        events = self.audit_logger.get_events()
        
        self.assertEqual(len(events), 2)
        self.assertIsInstance(events[0], SecurityAuditEvent)
    
    def test_get_events_with_filters(self):
        """Test getting events with filters."""
        # Add test events
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        self.audit_logger.log_authentication("user1", True, "password", self.context)
        
        # Filter by event type
        deployment_events = self.audit_logger.get_events(
            event_type=AuditEventType.DEPLOYMENT_START
        )
        self.assertEqual(len(deployment_events), 1)
        self.assertEqual(deployment_events[0].event_type, AuditEventType.DEPLOYMENT_START.value)
        
        # Filter by user
        user_events = self.audit_logger.get_events(user_id="test_user")
        self.assertTrue(len(user_events) >= 2)  # Both events have test_user
        
        # Filter by resource
        deployment_resource_events = self.audit_logger.get_events(resource="deployment")
        self.assertEqual(len(deployment_resource_events), 1)
    
    def test_get_events_time_filter(self):
        """Test getting events with time filters."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        future = now + timedelta(hours=1)
        
        # Add test event
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        
        # Filter by start time
        events_after_past = self.audit_logger.get_events(start_time=past)
        self.assertTrue(len(events_after_past) >= 1)
        
        # Filter by end time
        events_before_future = self.audit_logger.get_events(end_time=future)
        self.assertTrue(len(events_before_future) >= 1)
        
        # Filter by time range
        events_in_range = self.audit_logger.get_events(start_time=past, end_time=future)
        self.assertTrue(len(events_in_range) >= 1)
    
    def test_generate_audit_report(self):
        """Test audit report generation."""
        start_time = datetime.now(timezone.utc) - timedelta(hours=1)
        end_time = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Add test events
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        self.audit_logger.log_deployment_success("dep1", "prod", 120, self.context)
        self.audit_logger.log_authentication("user1", True, "password", self.context)
        
        report = self.audit_logger.generate_audit_report(start_time, end_time)
        
        self.assertIsInstance(report, dict)
        self.assertIn('report_id', report)
        self.assertIn('generated_at', report)
        self.assertIn('period', report)
        self.assertIn('summary', report)
        self.assertIn('events', report)
        
        # Check summary
        summary = report['summary']
        self.assertGreaterEqual(summary['total_events'], 3)
        self.assertIn('unique_users', summary)
        self.assertIn('unique_resources', summary)
        self.assertIn('event_types', summary)
        self.assertIn('results', summary)
    
    def test_export_events_json(self):
        """Test exporting events to JSON."""
        # Add test events
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
        
        try:
            self.audit_logger.export_events(export_file, format='json')
            
            # Verify file was created and contains data
            self.assertTrue(os.path.exists(export_file))
            
            with open(export_file, 'r') as f:
                data = json.load(f)
            
            self.assertIsInstance(data, list)
            self.assertTrue(len(data) > 0)
            self.assertIn('event_id', data[0])
            self.assertIn('timestamp', data[0])
        finally:
            if os.path.exists(export_file):
                os.unlink(export_file)
    
    def test_export_events_csv(self):
        """Test exporting events to CSV."""
        # Add test events
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            export_file = f.name
        
        try:
            self.audit_logger.export_events(export_file, format='csv')
            
            # Verify file was created and contains data
            self.assertTrue(os.path.exists(export_file))
            
            with open(export_file, 'r') as f:
                content = f.read()
            
            self.assertIn('event_id', content)  # Header should be present
            self.assertIn('timestamp', content)
        finally:
            if os.path.exists(export_file):
                os.unlink(export_file)
    
    def test_export_events_invalid_format(self):
        """Test exporting events with invalid format."""
        with self.assertRaises(ValueError):
            self.audit_logger.export_events('test.txt', format='invalid')
    
    def test_verify_integrity(self):
        """Test audit log integrity verification."""
        # Add test events
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        
        # Should pass integrity check
        self.assertTrue(self.audit_logger.verify_integrity())
        
        # Corrupt an event
        if self.audit_logger._audit_events:
            self.audit_logger._audit_events[0].event_id = None
            self.assertFalse(self.audit_logger.verify_integrity())
    
    def test_create_integrity_hash(self):
        """Test integrity hash creation."""
        # Add test events
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        self.audit_logger.log_deployment_success("dep1", "prod", 120, self.context)
        
        events = self.audit_logger._audit_events
        hash1 = self.audit_logger.create_integrity_hash(events)
        hash2 = self.audit_logger.create_integrity_hash(events)
        
        # Same events should produce same hash
        self.assertEqual(hash1, hash2)
        self.assertIsInstance(hash1, str)
        self.assertEqual(len(hash1), 64)  # SHA256 hash length
    
    def test_cleanup_old_events(self):
        """Test cleanup of old events."""
        # Add test events
        self.audit_logger.log_deployment_start("dep1", "prod", "abc123", self.context)
        initial_count = len(self.audit_logger._audit_events)
        
        # Cleanup with very short retention (should remove all events)
        self.audit_logger.cleanup_old_events(retention_days=0)
        
        # Should have fewer events (cleanup event might be added)
        final_count = len(self.audit_logger._audit_events)
        self.assertLessEqual(final_count, initial_count)


if __name__ == '__main__':
    unittest.main()