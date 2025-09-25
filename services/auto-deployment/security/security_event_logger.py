"""
Security event logging system.
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass
import logging
import hashlib

from .audit_logger import AuditLogger, AuditContext, AuditEventType, AuditResult
from .security_config import SecurityConfig


class SecurityEventSeverity(Enum):
    """Security event severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityEventCategory(Enum):
    """Security event categories."""
    AUTHENTICATION_FAILURE = "authentication_failure"
    AUTHORIZATION_VIOLATION = "authorization_violation"
    CREDENTIAL_COMPROMISE = "credential_compromise"
    VULNERABILITY_DETECTED = "vulnerability_detected"
    MALICIOUS_ACTIVITY = "malicious_activity"
    POLICY_VIOLATION = "policy_violation"
    CONFIGURATION_CHANGE = "configuration_change"
    DATA_BREACH = "data_breach"
    SYSTEM_COMPROMISE = "system_compromise"
    COMPLIANCE_VIOLATION = "compliance_violation"


@dataclass
class SecurityEvent:
    """Security event record."""
    event_id: str
    timestamp: datetime
    category: SecurityEventCategory
    severity: SecurityEventSeverity
    title: str
    description: str
    source: str
    affected_resource: str
    user_id: Optional[str]
    ip_address: Optional[str]
    details: Dict[str, Any]
    remediation_steps: List[str]
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'category': self.category.value,
            'severity': self.severity.value,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'affected_resource': self.affected_resource,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'details': self.details,
            'remediation_steps': self.remediation_steps,
            'resolved': self.resolved,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
            'resolved_by': self.resolved_by
        }


class SecurityEventLogger:
    """Logs and manages security events."""
    
    def __init__(self, config: SecurityConfig, audit_logger: AuditLogger):
        """Initialize security event logger."""
        self.config = config
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        self._security_events: Dict[str, SecurityEvent] = {}
        self._setup_security_logger()
    
    def _setup_security_logger(self):
        """Set up security event logger."""
        # Create security log handler
        security_handler = logging.FileHandler('security_events.log')
        security_handler.setLevel(logging.WARNING)
        
        # Create security log formatter
        security_formatter = logging.Formatter(
            '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
        )
        security_handler.setFormatter(security_formatter)
        
        # Add handler to logger
        self.logger.addHandler(security_handler)
        self.logger.setLevel(logging.WARNING)
        self.logger.propagate = False
    
    def log_security_event(
        self,
        category: SecurityEventCategory,
        severity: SecurityEventSeverity,
        title: str,
        description: str,
        source: str,
        affected_resource: str,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        remediation_steps: Optional[List[str]] = None,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log a security event."""
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Create security event
        security_event = SecurityEvent(
            event_id=event_id,
            timestamp=timestamp,
            category=category,
            severity=severity,
            title=title,
            description=description,
            source=source,
            affected_resource=affected_resource,
            user_id=user_id,
            ip_address=ip_address,
            details=details or {},
            remediation_steps=remediation_steps or []
        )
        
        # Store security event
        self._security_events[event_id] = security_event
        
        # Log to file
        self._log_security_event_to_file(security_event)
        
        # Log to audit system
        self.audit_logger.log_event(
            event_type=AuditEventType.ALERT_TRIGGERED,
            resource=affected_resource,
            action="security_event",
            result=self._severity_to_audit_result(severity),
            details={
                'security_event_id': event_id,
                'category': category.value,
                'severity': severity.value,
                'title': title,
                'description': description,
                'source': source,
                **(details or {})
            },
            context=context
        )
        
        # Send real-time alerts for high/critical events
        if severity in [SecurityEventSeverity.HIGH, SecurityEventSeverity.CRITICAL]:
            self._send_real_time_alert(security_event)
        
        return event_id
    
    def _log_security_event_to_file(self, event: SecurityEvent):
        """Log security event to file."""
        log_entry = {
            'event_id': event.event_id,
            'timestamp': event.timestamp.isoformat(),
            'category': event.category.value,
            'severity': event.severity.value,
            'title': event.title,
            'description': event.description,
            'source': event.source,
            'affected_resource': event.affected_resource,
            'user_id': event.user_id,
            'ip_address': event.ip_address,
            'details': event.details
        }
        
        # Log with appropriate level based on severity
        if event.severity == SecurityEventSeverity.CRITICAL:
            self.logger.critical(json.dumps(log_entry))
        elif event.severity == SecurityEventSeverity.HIGH:
            self.logger.error(json.dumps(log_entry))
        elif event.severity == SecurityEventSeverity.MEDIUM:
            self.logger.warning(json.dumps(log_entry))
        else:
            self.logger.info(json.dumps(log_entry))
    
    def _send_real_time_alert(self, event: SecurityEvent):
        """Send real-time alert for security event."""
        if not self.config.real_time_alerts:
            return
        
        # In a real implementation, this would:
        # - Send to SIEM systems
        # - Trigger incident response workflows
        # - Send notifications to security teams
        # - Update security dashboards
        pass
    
    def log_authentication_failure(
        self,
        user_id: str,
        ip_address: str,
        reason: str,
        attempt_count: int = 1,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log authentication failure event."""
        severity = SecurityEventSeverity.HIGH if attempt_count >= self.config.max_login_attempts else SecurityEventSeverity.MEDIUM
        
        return self.log_security_event(
            category=SecurityEventCategory.AUTHENTICATION_FAILURE,
            severity=severity,
            title=f"Authentication failure for user {user_id}",
            description=f"User {user_id} failed to authenticate from {ip_address}. Reason: {reason}",
            source="authentication_system",
            affected_resource=f"user:{user_id}",
            details={
                'user_id': user_id,
                'ip_address': ip_address,
                'reason': reason,
                'attempt_count': attempt_count
            },
            user_id=user_id,
            ip_address=ip_address,
            remediation_steps=[
                "Review authentication logs",
                "Check for brute force attacks",
                "Consider account lockout if multiple failures",
                "Verify user credentials"
            ],
            context=context
        )
    
    def log_authorization_violation(
        self,
        user_id: str,
        resource: str,
        action: str,
        ip_address: Optional[str] = None,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log authorization violation event."""
        return self.log_security_event(
            category=SecurityEventCategory.AUTHORIZATION_VIOLATION,
            severity=SecurityEventSeverity.HIGH,
            title=f"Authorization violation by user {user_id}",
            description=f"User {user_id} attempted unauthorized action '{action}' on resource '{resource}'",
            source="authorization_system",
            affected_resource=resource,
            details={
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'ip_address': ip_address
            },
            user_id=user_id,
            ip_address=ip_address,
            remediation_steps=[
                "Review user permissions",
                "Check for privilege escalation attempts",
                "Verify resource access policies",
                "Consider user access review"
            ],
            context=context
        )
    
    def log_credential_compromise(
        self,
        credential_type: str,
        credential_id: str,
        detection_method: str,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log credential compromise event."""
        return self.log_security_event(
            category=SecurityEventCategory.CREDENTIAL_COMPROMISE,
            severity=SecurityEventSeverity.CRITICAL,
            title=f"Potential credential compromise detected",
            description=f"Credential compromise detected for {credential_type} '{credential_id}' via {detection_method}",
            source="credential_monitoring",
            affected_resource=f"credential:{credential_id}",
            details={
                'credential_type': credential_type,
                'credential_id': credential_id,
                'detection_method': detection_method
            },
            remediation_steps=[
                "Immediately rotate compromised credentials",
                "Review access logs for unauthorized usage",
                "Check for lateral movement",
                "Notify affected users/systems",
                "Update security policies"
            ],
            context=context
        )
    
    def log_vulnerability_detected(
        self,
        vulnerability_id: str,
        severity: str,
        component: str,
        description: str,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log vulnerability detection event."""
        # Map vulnerability severity to security event severity
        severity_mapping = {
            'low': SecurityEventSeverity.LOW,
            'medium': SecurityEventSeverity.MEDIUM,
            'high': SecurityEventSeverity.HIGH,
            'critical': SecurityEventSeverity.CRITICAL
        }
        
        event_severity = severity_mapping.get(severity.lower(), SecurityEventSeverity.MEDIUM)
        
        return self.log_security_event(
            category=SecurityEventCategory.VULNERABILITY_DETECTED,
            severity=event_severity,
            title=f"Vulnerability detected in {component}",
            description=f"Vulnerability {vulnerability_id} detected in {component}: {description}",
            source="vulnerability_scanner",
            affected_resource=f"component:{component}",
            details={
                'vulnerability_id': vulnerability_id,
                'severity': severity,
                'component': component,
                'description': description
            },
            remediation_steps=[
                "Review vulnerability details",
                "Apply security patches if available",
                "Implement workarounds if patches unavailable",
                "Update dependency versions",
                "Schedule regular vulnerability scans"
            ],
            context=context
        )
    
    def log_policy_violation(
        self,
        policy_name: str,
        violation_type: str,
        resource: str,
        user_id: Optional[str] = None,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log policy violation event."""
        return self.log_security_event(
            category=SecurityEventCategory.POLICY_VIOLATION,
            severity=SecurityEventSeverity.MEDIUM,
            title=f"Policy violation: {policy_name}",
            description=f"Policy '{policy_name}' violated: {violation_type} on resource '{resource}'",
            source="policy_engine",
            affected_resource=resource,
            details={
                'policy_name': policy_name,
                'violation_type': violation_type,
                'resource': resource,
                'user_id': user_id
            },
            user_id=user_id,
            remediation_steps=[
                "Review policy configuration",
                "Check resource compliance",
                "Update resource configuration",
                "Train users on policy requirements"
            ],
            context=context
        )
    
    def log_configuration_change(
        self,
        config_type: str,
        changes: Dict[str, Any],
        user_id: str,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log security-relevant configuration change."""
        return self.log_security_event(
            category=SecurityEventCategory.CONFIGURATION_CHANGE,
            severity=SecurityEventSeverity.MEDIUM,
            title=f"Security configuration change: {config_type}",
            description=f"Security configuration '{config_type}' modified by user {user_id}",
            source="configuration_system",
            affected_resource=f"config:{config_type}",
            details={
                'config_type': config_type,
                'changes': changes,
                'user_id': user_id
            },
            user_id=user_id,
            remediation_steps=[
                "Review configuration changes",
                "Verify changes are authorized",
                "Test security impact",
                "Update documentation"
            ],
            context=context
        )
    
    def log_compliance_violation(
        self,
        standard: str,
        requirement: str,
        resource: str,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log compliance violation event."""
        return self.log_security_event(
            category=SecurityEventCategory.COMPLIANCE_VIOLATION,
            severity=SecurityEventSeverity.HIGH,
            title=f"Compliance violation: {standard}",
            description=f"Compliance requirement '{requirement}' violated for {standard} on resource '{resource}'",
            source="compliance_monitor",
            affected_resource=resource,
            details={
                'standard': standard,
                'requirement': requirement,
                'resource': resource
            },
            remediation_steps=[
                "Review compliance requirements",
                "Implement necessary controls",
                "Update policies and procedures",
                "Schedule compliance audit"
            ],
            context=context
        )
    
    def resolve_security_event(
        self,
        event_id: str,
        resolved_by: str,
        resolution_notes: Optional[str] = None,
        context: Optional[AuditContext] = None
    ):
        """Mark a security event as resolved."""
        if event_id not in self._security_events:
            raise ValueError(f"Security event {event_id} not found")
        
        event = self._security_events[event_id]
        event.resolved = True
        event.resolved_at = datetime.now(timezone.utc)
        event.resolved_by = resolved_by
        
        if resolution_notes:
            event.details['resolution_notes'] = resolution_notes
        
        # Log resolution
        self.audit_logger.log_event(
            event_type=AuditEventType.USER_ACTION,
            resource=event.affected_resource,
            action="resolve_security_event",
            result=AuditResult.SUCCESS,
            details={
                'security_event_id': event_id,
                'resolved_by': resolved_by,
                'resolution_notes': resolution_notes,
                'original_category': event.category.value,
                'original_severity': event.severity.value
            },
            context=context
        )
    
    def get_security_events(
        self,
        category: Optional[SecurityEventCategory] = None,
        severity: Optional[SecurityEventSeverity] = None,
        resolved: Optional[bool] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[SecurityEvent]:
        """Get security events with optional filtering."""
        events = list(self._security_events.values())
        
        # Apply filters
        if category:
            events = [e for e in events if e.category == category]
        
        if severity:
            events = [e for e in events if e.severity == severity]
        
        if resolved is not None:
            events = [e for e in events if e.resolved == resolved]
        
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            events = events[:limit]
        
        return events
    
    def get_security_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get security event statistics."""
        events = self.get_security_events(start_time=start_time, end_time=end_time)
        
        if not events:
            return {
                'total_events': 0,
                'resolved_events': 0,
                'unresolved_events': 0,
                'events_by_category': {},
                'events_by_severity': {},
                'resolution_rate': 0.0
            }
        
        total = len(events)
        resolved = len([e for e in events if e.resolved])
        unresolved = total - resolved
        resolution_rate = resolved / total if total > 0 else 0.0
        
        # Count by category
        categories = {}
        for event in events:
            cat = event.category.value
            categories[cat] = categories.get(cat, 0) + 1
        
        # Count by severity
        severities = {}
        for event in events:
            sev = event.severity.value
            severities[sev] = severities.get(sev, 0) + 1
        
        return {
            'total_events': total,
            'resolved_events': resolved,
            'unresolved_events': unresolved,
            'events_by_category': categories,
            'events_by_severity': severities,
            'resolution_rate': resolution_rate
        }
    
    def export_security_events(
        self,
        file_path: str,
        format: str = 'json',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ):
        """Export security events to file."""
        events = self.get_security_events(start_time=start_time, end_time=end_time)
        
        if format.lower() == 'json':
            with open(file_path, 'w') as f:
                json.dump([event.to_dict() for event in events], f, indent=2)
        elif format.lower() == 'csv':
            import csv
            with open(file_path, 'w', newline='') as f:
                if events:
                    fieldnames = [
                        'event_id', 'timestamp', 'category', 'severity', 'title',
                        'description', 'source', 'affected_resource', 'user_id',
                        'ip_address', 'resolved', 'resolved_at', 'resolved_by'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for event in events:
                        row = {
                            'event_id': event.event_id,
                            'timestamp': event.timestamp.isoformat(),
                            'category': event.category.value,
                            'severity': event.severity.value,
                            'title': event.title,
                            'description': event.description,
                            'source': event.source,
                            'affected_resource': event.affected_resource,
                            'user_id': event.user_id,
                            'ip_address': event.ip_address,
                            'resolved': event.resolved,
                            'resolved_at': event.resolved_at.isoformat() if event.resolved_at else '',
                            'resolved_by': event.resolved_by or ''
                        }
                        writer.writerow(row)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _severity_to_audit_result(self, severity: SecurityEventSeverity) -> AuditResult:
        """Convert security event severity to audit result."""
        if severity == SecurityEventSeverity.CRITICAL:
            return AuditResult.ERROR
        elif severity == SecurityEventSeverity.HIGH:
            return AuditResult.FAILURE
        elif severity == SecurityEventSeverity.MEDIUM:
            return AuditResult.WARNING
        else:
            return AuditResult.INFO