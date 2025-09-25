"""
Comprehensive audit logging system.
"""

import json
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import hashlib
import os

from .models import SecurityAuditEvent
from .security_config import SecurityConfig


class AuditEventType(Enum):
    """Audit event types."""
    DEPLOYMENT_START = "deployment_start"
    DEPLOYMENT_SUCCESS = "deployment_success"
    DEPLOYMENT_FAILURE = "deployment_failure"
    SECURITY_VALIDATION = "security_validation"
    CREDENTIAL_ACCESS = "credential_access"
    CONFIGURATION_CHANGE = "configuration_change"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    SYSTEM_CHANGE = "system_change"
    COMPLIANCE_CHECK = "compliance_check"
    ROLLBACK_INITIATED = "rollback_initiated"
    ROLLBACK_COMPLETED = "rollback_completed"
    ALERT_TRIGGERED = "alert_triggered"
    USER_ACTION = "user_action"


class AuditResult(Enum):
    """Audit result types."""
    SUCCESS = "success"
    FAILURE = "failure"
    WARNING = "warning"
    INFO = "info"
    ERROR = "error"


@dataclass
class AuditContext:
    """Audit context information."""
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    correlation_id: Optional[str] = None
    environment: Optional[str] = None
    service_name: Optional[str] = None


class AuditLogger:
    """Comprehensive audit logging system."""
    
    def __init__(self, config: SecurityConfig):
        """Initialize audit logger."""
        self.config = config
        self.logger = logging.getLogger('audit')
        self._setup_audit_logger()
        self._audit_events: List[SecurityAuditEvent] = []
        
    def _setup_audit_logger(self):
        """Set up audit logger configuration."""
        # Create audit log handler
        audit_handler = logging.FileHandler('audit.log')
        audit_handler.setLevel(logging.INFO)
        
        # Create audit log formatter
        audit_formatter = logging.Formatter(
            '%(asctime)s - AUDIT - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        
        # Add handler to audit logger
        self.logger.addHandler(audit_handler)
        self.logger.setLevel(logging.INFO)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def log_event(
        self,
        event_type: AuditEventType,
        resource: str,
        action: str,
        result: AuditResult,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log an audit event."""
        event_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Create audit event
        audit_event = SecurityAuditEvent(
            event_id=event_id,
            timestamp=timestamp,
            event_type=event_type.value,
            user_id=context.user_id if context else None,
            resource=resource,
            action=action,
            result=result.value,
            details=details or {},
            ip_address=context.ip_address if context else None,
            user_agent=context.user_agent if context else None
        )
        
        # Add context information to details
        if context:
            audit_event.details.update({
                'session_id': context.session_id,
                'request_id': context.request_id,
                'correlation_id': context.correlation_id,
                'environment': context.environment,
                'service_name': context.service_name
            })
        
        # Store event
        self._audit_events.append(audit_event)
        
        # Log to file
        self._log_to_file(audit_event)
        
        # Log to external systems if configured
        self._log_to_external_systems(audit_event)
        
        return event_id
    
    def _log_to_file(self, event: SecurityAuditEvent):
        """Log audit event to file."""
        log_entry = {
            'event_id': event.event_id,
            'timestamp': event.timestamp.isoformat(),
            'event_type': event.event_type,
            'user_id': event.user_id,
            'resource': event.resource,
            'action': event.action,
            'result': event.result,
            'details': event.details,
            'ip_address': event.ip_address,
            'user_agent': event.user_agent
        }
        
        self.logger.info(json.dumps(log_entry))
    
    def _log_to_external_systems(self, event: SecurityAuditEvent):
        """Log audit event to external systems."""
        # In a real implementation, this would send to:
        # - SIEM systems
        # - Cloud logging services (Google Cloud Logging, AWS CloudWatch)
        # - Security monitoring platforms
        # - Compliance databases
        pass
    
    def log_deployment_start(
        self,
        deployment_id: str,
        environment: str,
        commit_sha: str,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log deployment start event."""
        return self.log_event(
            event_type=AuditEventType.DEPLOYMENT_START,
            resource=f"deployment:{deployment_id}",
            action="start_deployment",
            result=AuditResult.INFO,
            details={
                'deployment_id': deployment_id,
                'environment': environment,
                'commit_sha': commit_sha,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def log_deployment_success(
        self,
        deployment_id: str,
        environment: str,
        duration_seconds: float,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log deployment success event."""
        return self.log_event(
            event_type=AuditEventType.DEPLOYMENT_SUCCESS,
            resource=f"deployment:{deployment_id}",
            action="complete_deployment",
            result=AuditResult.SUCCESS,
            details={
                'deployment_id': deployment_id,
                'environment': environment,
                'duration_seconds': duration_seconds,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def log_deployment_failure(
        self,
        deployment_id: str,
        environment: str,
        error_message: str,
        error_details: Optional[Dict[str, Any]] = None,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log deployment failure event."""
        return self.log_event(
            event_type=AuditEventType.DEPLOYMENT_FAILURE,
            resource=f"deployment:{deployment_id}",
            action="fail_deployment",
            result=AuditResult.FAILURE,
            details={
                'deployment_id': deployment_id,
                'environment': environment,
                'error_message': error_message,
                'error_details': error_details or {},
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def log_security_validation(
        self,
        validation_type: str,
        resource: str,
        passed: bool,
        issues: List[str],
        context: Optional[AuditContext] = None
    ) -> str:
        """Log security validation event."""
        return self.log_event(
            event_type=AuditEventType.SECURITY_VALIDATION,
            resource=resource,
            action=f"validate_{validation_type}",
            result=AuditResult.SUCCESS if passed else AuditResult.FAILURE,
            details={
                'validation_type': validation_type,
                'passed': passed,
                'issues': issues,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def log_credential_access(
        self,
        credential_type: str,
        credential_id: str,
        action: str,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log credential access event."""
        return self.log_event(
            event_type=AuditEventType.CREDENTIAL_ACCESS,
            resource=f"credential:{credential_id}",
            action=action,
            result=AuditResult.INFO,
            details={
                'credential_type': credential_type,
                'credential_id': credential_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def log_configuration_change(
        self,
        config_type: str,
        changes: Dict[str, Any],
        context: Optional[AuditContext] = None
    ) -> str:
        """Log configuration change event."""
        return self.log_event(
            event_type=AuditEventType.CONFIGURATION_CHANGE,
            resource=f"config:{config_type}",
            action="update_configuration",
            result=AuditResult.INFO,
            details={
                'config_type': config_type,
                'changes': changes,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def log_authentication(
        self,
        user_id: str,
        success: bool,
        method: str,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log authentication event."""
        return self.log_event(
            event_type=AuditEventType.AUTHENTICATION,
            resource=f"user:{user_id}",
            action="authenticate",
            result=AuditResult.SUCCESS if success else AuditResult.FAILURE,
            details={
                'user_id': user_id,
                'success': success,
                'method': method,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def log_authorization(
        self,
        user_id: str,
        resource: str,
        action: str,
        granted: bool,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log authorization event."""
        return self.log_event(
            event_type=AuditEventType.AUTHORIZATION,
            resource=resource,
            action=action,
            result=AuditResult.SUCCESS if granted else AuditResult.FAILURE,
            details={
                'user_id': user_id,
                'resource': resource,
                'action': action,
                'granted': granted,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def log_compliance_check(
        self,
        standard: str,
        passed: bool,
        score: float,
        requirements_failed: List[str],
        context: Optional[AuditContext] = None
    ) -> str:
        """Log compliance check event."""
        return self.log_event(
            event_type=AuditEventType.COMPLIANCE_CHECK,
            resource=f"compliance:{standard}",
            action="check_compliance",
            result=AuditResult.SUCCESS if passed else AuditResult.FAILURE,
            details={
                'standard': standard,
                'passed': passed,
                'score': score,
                'requirements_failed': requirements_failed,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def log_rollback(
        self,
        deployment_id: str,
        reason: str,
        success: bool,
        context: Optional[AuditContext] = None
    ) -> str:
        """Log rollback event."""
        event_type = AuditEventType.ROLLBACK_COMPLETED if success else AuditEventType.ROLLBACK_INITIATED
        
        return self.log_event(
            event_type=event_type,
            resource=f"deployment:{deployment_id}",
            action="rollback",
            result=AuditResult.SUCCESS if success else AuditResult.WARNING,
            details={
                'deployment_id': deployment_id,
                'reason': reason,
                'success': success,
                'timestamp': datetime.now(timezone.utc).isoformat()
            },
            context=context
        )
    
    def get_events(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        resource: Optional[str] = None
    ) -> List[SecurityAuditEvent]:
        """Get audit events with optional filtering."""
        filtered_events = self._audit_events.copy()
        
        if start_time:
            filtered_events = [e for e in filtered_events if e.timestamp >= start_time]
        
        if end_time:
            filtered_events = [e for e in filtered_events if e.timestamp <= end_time]
        
        if event_type:
            filtered_events = [e for e in filtered_events if e.event_type == event_type.value]
        
        if user_id:
            filtered_events = [e for e in filtered_events if e.user_id == user_id]
        
        if resource:
            filtered_events = [e for e in filtered_events if resource in e.resource]
        
        return filtered_events
    
    def generate_audit_report(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        events = self.get_events(start_time=start_time, end_time=end_time)
        
        # Calculate statistics
        total_events = len(events)
        event_types = {}
        results = {}
        users = set()
        resources = set()
        
        for event in events:
            # Count event types
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1
            
            # Count results
            results[event.result] = results.get(event.result, 0) + 1
            
            # Collect users and resources
            if event.user_id:
                users.add(event.user_id)
            resources.add(event.resource)
        
        # Generate report
        report = {
            'report_id': str(uuid.uuid4()),
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'period': {
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat()
            },
            'summary': {
                'total_events': total_events,
                'unique_users': len(users),
                'unique_resources': len(resources),
                'event_types': event_types,
                'results': results
            },
            'events': [event.to_dict() for event in events]
        }
        
        return report
    
    def export_events(
        self,
        file_path: str,
        format: str = 'json',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ):
        """Export audit events to file."""
        events = self.get_events(start_time=start_time, end_time=end_time)
        
        if format.lower() == 'json':
            with open(file_path, 'w') as f:
                json.dump([event.to_dict() for event in events], f, indent=2)
        elif format.lower() == 'csv':
            import csv
            with open(file_path, 'w', newline='') as f:
                if events:
                    writer = csv.DictWriter(f, fieldnames=events[0].to_dict().keys())
                    writer.writeheader()
                    for event in events:
                        writer.writerow(event.to_dict())
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def verify_integrity(self) -> bool:
        """Verify audit log integrity."""
        # In a real implementation, this would:
        # - Check cryptographic signatures
        # - Verify hash chains
        # - Check for tampering
        # - Validate timestamps
        
        # Simple integrity check for demonstration
        for event in self._audit_events:
            if not event.event_id or not event.timestamp:
                return False
        
        return True
    
    def create_integrity_hash(self, events: List[SecurityAuditEvent]) -> str:
        """Create integrity hash for audit events."""
        # Create hash of all events for integrity verification
        event_data = ''.join([
            f"{event.event_id}{event.timestamp.isoformat()}{event.event_type}"
            for event in sorted(events, key=lambda x: x.timestamp)
        ])
        
        return hashlib.sha256(event_data.encode()).hexdigest()
    
    def cleanup_old_events(self, retention_days: int):
        """Clean up old audit events based on retention policy."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        
        # Remove events older than retention period
        self._audit_events = [
            event for event in self._audit_events
            if event.timestamp >= cutoff_date
        ]
        
        # Log cleanup action
        self.log_event(
            event_type=AuditEventType.SYSTEM_CHANGE,
            resource="audit_log",
            action="cleanup_old_events",
            result=AuditResult.INFO,
            details={
                'retention_days': retention_days,
                'cutoff_date': cutoff_date.isoformat(),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )