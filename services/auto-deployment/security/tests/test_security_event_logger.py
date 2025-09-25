"""
Tests for security event logger.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from ..security_event_logger import SecurityEventLogger, SecurityEventSeverity, SecurityEventCategory
from ..audit_logger import AuditLogger, AuditContext
from ..security_config import SecurityConfig


class TestSecurityEventLogger(unittest.TestCase):
    """Test security event logger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SecurityConfig(
            audit_logging=True,
            real_time_alerts=True,
            max_login_attempts=3
        )
        self.audit_logger = AuditLogger(self.config)
        self.security_logger = SecurityEventLogger(self.config, self.audit_logger)
        self.context = AuditContext(
            user_id="test_user",
            session_id="test_session",
            ip_address="192.168.1.1",
            environment="test"
        )
    
    def test_log_security_event(self):
        """Test basic security event logging."""
        event_id = self.security_logger.log_security_event(
            category=SecurityEventCategory.AUTHENTICATION_FAILURE,
            severity=SecurityEventSeverity.HIGH,
            title="Authentication failed",
            description="User failed to authenticate",
            source="auth_system",
            affected_resource="user:test_user",
            details={"attempt_count": 3},
            user_id="test_user",
            ip_address="192.168.1.1",
            remediation_steps=["Check credentials", "Review logs"],
            context=self.context
        )
        
        self.assertIsInstance(event_id, str)
        self.assertIn(event_id, self.security_logger._security_events)
        
        # Check event details
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.category, SecurityEventCategory.AUTHENTICATION_FAILURE)
        self.assertEqual(event.severity, SecurityEventSeverity.HIGH)
        self.assertEqual(event.title, "Authentication failed")
        self.assertEqual(event.description, "User failed to authenticate")
        self.assertEqual(event.source, "auth_system")
        self.assertEqual(event.affected_resource, "user:test_user")
        self.assertEqual(event.user_id, "test_user")
        self.assertEqual(event.ip_address, "192.168.1.1")
        self.assertEqual(event.details["attempt_count"], 3)
        self.assertIn("Check credentials", event.remediation_steps)
        self.assertFalse(event.resolved)
    
    def test_log_authentication_failure(self):
        """Test authentication failure logging."""
        # Test single failure (medium severity)
        event_id = self.security_logger.log_authentication_failure(
            user_id="test_user",
            ip_address="192.168.1.1",
            reason="Invalid password",
            attempt_count=1,
            context=self.context
        )
        
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.category, SecurityEventCategory.AUTHENTICATION_FAILURE)
        self.assertEqual(event.severity, SecurityEventSeverity.MEDIUM)
        self.assertIn("test_user", event.title)
        
        # Test multiple failures (high severity)
        event_id = self.security_logger.log_authentication_failure(
            user_id="test_user",
            ip_address="192.168.1.1",
            reason="Invalid password",
            attempt_count=3,
            context=self.context
        )
        
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.severity, SecurityEventSeverity.HIGH)
    
    def test_log_authorization_violation(self):
        """Test authorization violation logging."""
        event_id = self.security_logger.log_authorization_violation(
            user_id="test_user",
            resource="deployment:prod",
            action="deploy",
            ip_address="192.168.1.1",
            context=self.context
        )
        
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.category, SecurityEventCategory.AUTHORIZATION_VIOLATION)
        self.assertEqual(event.severity, SecurityEventSeverity.HIGH)
        self.assertEqual(event.affected_resource, "deployment:prod")
        self.assertEqual(event.details["action"], "deploy")
        self.assertIn("unauthorized action", event.description)
    
    def test_log_credential_compromise(self):
        """Test credential compromise logging."""
        event_id = self.security_logger.log_credential_compromise(
            credential_type="api_key",
            credential_id="key-123",
            detection_method="pattern_matching",
            context=self.context
        )
        
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.category, SecurityEventCategory.CREDENTIAL_COMPROMISE)
        self.assertEqual(event.severity, SecurityEventSeverity.CRITICAL)
        self.assertEqual(event.affected_resource, "credential:key-123")
        self.assertEqual(event.details["credential_type"], "api_key")
        self.assertEqual(event.details["detection_method"], "pattern_matching")
        self.assertIn("rotate", event.remediation_steps[0].lower())
    
    def test_log_vulnerability_detected(self):
        """Test vulnerability detection logging."""
        # Test critical vulnerability
        event_id = self.security_logger.log_vulnerability_detected(
            vulnerability_id="CVE-2023-1234",
            severity="critical",
            component="nginx",
            description="Remote code execution vulnerability",
            context=self.context
        )
        
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.category, SecurityEventCategory.VULNERABILITY_DETECTED)
        self.assertEqual(event.severity, SecurityEventSeverity.CRITICAL)
        self.assertEqual(event.affected_resource, "component:nginx")
        self.assertEqual(event.details["vulnerability_id"], "CVE-2023-1234")
        
        # Test low severity vulnerability
        event_id = self.security_logger.log_vulnerability_detected(
            vulnerability_id="CVE-2023-5678",
            severity="low",
            component="library",
            description="Information disclosure",
            context=self.context
        )
        
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.severity, SecurityEventSeverity.LOW)
    
    def test_log_policy_violation(self):
        """Test policy violation logging."""
        event_id = self.security_logger.log_policy_violation(
            policy_name="Password Policy",
            violation_type="weak_password",
            resource="user:test_user",
            user_id="test_user",
            context=self.context
        )
        
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.category, SecurityEventCategory.POLICY_VIOLATION)
        self.assertEqual(event.severity, SecurityEventSeverity.MEDIUM)
        self.assertEqual(event.affected_resource, "user:test_user")
        self.assertEqual(event.details["policy_name"], "Password Policy")
        self.assertEqual(event.details["violation_type"], "weak_password")
    
    def test_log_configuration_change(self):
        """Test configuration change logging."""
        changes = {
            "encryption_enabled": {"old": False, "new": True},
            "key_rotation_days": {"old": 365, "new": 90}
        }
        
        event_id = self.security_logger.log_configuration_change(
            config_type="security",
            changes=changes,
            user_id="admin_user",
            context=self.context
        )
        
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.category, SecurityEventCategory.CONFIGURATION_CHANGE)
        self.assertEqual(event.severity, SecurityEventSeverity.MEDIUM)
        self.assertEqual(event.affected_resource, "config:security")
        self.assertEqual(event.details["changes"], changes)
        self.assertEqual(event.user_id, "admin_user")
    
    def test_log_compliance_violation(self):
        """Test compliance violation logging."""
        event_id = self.security_logger.log_compliance_violation(
            standard="GDPR",
            requirement="Data encryption at rest",
            resource="database:user_data",
            context=self.context
        )
        
        event = self.security_logger._security_events[event_id]
        self.assertEqual(event.category, SecurityEventCategory.COMPLIANCE_VIOLATION)
        self.assertEqual(event.severity, SecurityEventSeverity.HIGH)
        self.assertEqual(event.affected_resource, "database:user_data")
        self.assertEqual(event.details["standard"], "GDPR")
        self.assertEqual(event.details["requirement"], "Data encryption at rest")
    
    def test_resolve_security_event(self):
        """Test resolving security events."""
        # Create a security event
        event_id = self.security_logger.log_authentication_failure(
            user_id="test_user",
            ip_address="192.168.1.1",
            reason="Invalid password",
            context=self.context
        )
        
        # Resolve the event
        self.security_logger.resolve_security_event(
            event_id=event_id,
            resolved_by="admin_user",
            resolution_notes="User password reset",
            context=self.context
        )
        
        # Check event was resolved
        event = self.security_logger._security_events[event_id]
        self.assertTrue(event.resolved)
        self.assertEqual(event.resolved_by, "admin_user")
        self.assertIsInstance(event.resolved_at, datetime)
        self.assertEqual(event.details["resolution_notes"], "User password reset")
    
    def test_resolve_security_event_invalid_id(self):
        """Test resolving security event with invalid ID."""
        with self.assertRaises(ValueError):
            self.security_logger.resolve_security_event(
                event_id="invalid-id",
                resolved_by="admin_user"
            )
    
    def test_get_security_events_no_filter(self):
        """Test getting all security events without filters."""
        # Create test events
        self.security_logger.log_authentication_failure("user1", "192.168.1.1", "Invalid password", context=self.context)
        self.security_logger.log_authorization_violation("user2", "resource", "action", context=self.context)
        
        events = self.security_logger.get_security_events()
        
        self.assertEqual(len(events), 2)
        self.assertIsInstance(events[0].timestamp, datetime)
    
    def test_get_security_events_with_filters(self):
        """Test getting security events with filters."""
        # Create test events
        auth_event_id = self.security_logger.log_authentication_failure("user1", "192.168.1.1", "Invalid password", context=self.context)
        self.security_logger.log_authorization_violation("user2", "resource", "action", context=self.context)
        
        # Resolve one event
        self.security_logger.resolve_security_event(auth_event_id, "admin", context=self.context)
        
        # Filter by category
        auth_events = self.security_logger.get_security_events(
            category=SecurityEventCategory.AUTHENTICATION_FAILURE
        )
        self.assertEqual(len(auth_events), 1)
        self.assertEqual(auth_events[0].category, SecurityEventCategory.AUTHENTICATION_FAILURE)
        
        # Filter by severity
        high_events = self.security_logger.get_security_events(
            severity=SecurityEventSeverity.HIGH
        )
        self.assertTrue(len(high_events) >= 1)
        
        # Filter by resolved status
        resolved_events = self.security_logger.get_security_events(resolved=True)
        self.assertEqual(len(resolved_events), 1)
        self.assertTrue(resolved_events[0].resolved)
        
        unresolved_events = self.security_logger.get_security_events(resolved=False)
        self.assertTrue(len(unresolved_events) >= 1)
        self.assertFalse(unresolved_events[0].resolved)
        
        # Filter with limit
        limited_events = self.security_logger.get_security_events(limit=1)
        self.assertEqual(len(limited_events), 1)
    
    def test_get_security_events_time_filter(self):
        """Test getting security events with time filters."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        future = now + timedelta(hours=1)
        
        # Create test event
        self.security_logger.log_authentication_failure("user1", "192.168.1.1", "Invalid password", context=self.context)
        
        # Filter by start time
        events_after_past = self.security_logger.get_security_events(start_time=past)
        self.assertEqual(len(events_after_past), 1)
        
        # Filter by end time
        events_before_future = self.security_logger.get_security_events(end_time=future)
        self.assertEqual(len(events_before_future), 1)
        
        # Filter by time range
        events_in_range = self.security_logger.get_security_events(start_time=past, end_time=future)
        self.assertEqual(len(events_in_range), 1)
    
    def test_get_security_statistics(self):
        """Test getting security event statistics."""
        # Create test events
        auth_event_id = self.security_logger.log_authentication_failure("user1", "192.168.1.1", "Invalid password", context=self.context)
        self.security_logger.log_authorization_violation("user2", "resource", "action", context=self.context)
        self.security_logger.log_credential_compromise("api_key", "key-123", "pattern_matching", context=self.context)
        
        # Resolve one event
        self.security_logger.resolve_security_event(auth_event_id, "admin", context=self.context)
        
        stats = self.security_logger.get_security_statistics()
        
        self.assertEqual(stats['total_events'], 3)
        self.assertEqual(stats['resolved_events'], 1)
        self.assertEqual(stats['unresolved_events'], 2)
        self.assertAlmostEqual(stats['resolution_rate'], 1/3, places=2)
        
        # Check category breakdown
        self.assertEqual(stats['events_by_category']['authentication_failure'], 1)
        self.assertEqual(stats['events_by_category']['authorization_violation'], 1)
        self.assertEqual(stats['events_by_category']['credential_compromise'], 1)
        
        # Check severity breakdown
        self.assertTrue('high' in stats['events_by_severity'])
        self.assertTrue('critical' in stats['events_by_severity'])
    
    def test_get_security_statistics_empty(self):
        """Test getting statistics with no events."""
        stats = self.security_logger.get_security_statistics()
        
        self.assertEqual(stats['total_events'], 0)
        self.assertEqual(stats['resolved_events'], 0)
        self.assertEqual(stats['unresolved_events'], 0)
        self.assertEqual(stats['resolution_rate'], 0.0)
        self.assertEqual(stats['events_by_category'], {})
        self.assertEqual(stats['events_by_severity'], {})
    
    def test_export_security_events_json(self):
        """Test exporting security events to JSON."""
        # Create test event
        self.security_logger.log_authentication_failure("user1", "192.168.1.1", "Invalid password", context=self.context)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
        
        try:
            self.security_logger.export_security_events(export_file, format='json')
            
            # Verify file was created and contains data
            self.assertTrue(os.path.exists(export_file))
            
            with open(export_file, 'r') as f:
                data = json.load(f)
            
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 1)
            self.assertIn('event_id', data[0])
            self.assertIn('category', data[0])
            self.assertIn('severity', data[0])
        finally:
            if os.path.exists(export_file):
                os.unlink(export_file)
    
    def test_export_security_events_csv(self):
        """Test exporting security events to CSV."""
        # Create test event
        self.security_logger.log_authentication_failure("user1", "192.168.1.1", "Invalid password", context=self.context)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            export_file = f.name
        
        try:
            self.security_logger.export_security_events(export_file, format='csv')
            
            # Verify file was created and contains data
            self.assertTrue(os.path.exists(export_file))
            
            with open(export_file, 'r') as f:
                content = f.read()
            
            self.assertIn('event_id', content)  # Header should be present
            self.assertIn('category', content)
            self.assertIn('severity', content)
        finally:
            if os.path.exists(export_file):
                os.unlink(export_file)
    
    def test_export_security_events_invalid_format(self):
        """Test exporting security events with invalid format."""
        with self.assertRaises(ValueError):
            self.security_logger.export_security_events('test.txt', format='invalid')
    
    def test_severity_to_audit_result(self):
        """Test severity to audit result conversion."""
        # Test critical severity
        critical_result = self.security_logger._severity_to_audit_result(SecurityEventSeverity.CRITICAL)
        self.assertEqual(critical_result.value, "error")
        
        # Test high severity
        high_result = self.security_logger._severity_to_audit_result(SecurityEventSeverity.HIGH)
        self.assertEqual(high_result.value, "failure")
        
        # Test medium severity
        medium_result = self.security_logger._severity_to_audit_result(SecurityEventSeverity.MEDIUM)
        self.assertEqual(medium_result.value, "warning")
        
        # Test low severity
        low_result = self.security_logger._severity_to_audit_result(SecurityEventSeverity.LOW)
        self.assertEqual(low_result.value, "info")
    
    @patch('services.auto_deployment.security.security_event_logger.SecurityEventLogger._send_real_time_alert')
    def test_real_time_alerts(self, mock_alert):
        """Test real-time alerts for high/critical events."""
        # Test critical event triggers alert
        self.security_logger.log_credential_compromise(
            credential_type="api_key",
            credential_id="key-123",
            detection_method="pattern_matching",
            context=self.context
        )
        
        mock_alert.assert_called_once()
        
        # Reset mock
        mock_alert.reset_mock()
        
        # Test low event doesn't trigger alert
        self.security_logger.log_vulnerability_detected(
            vulnerability_id="CVE-2023-1234",
            severity="low",
            component="library",
            description="Minor issue",
            context=self.context
        )
        
        mock_alert.assert_not_called()


if __name__ == '__main__':
    unittest.main()