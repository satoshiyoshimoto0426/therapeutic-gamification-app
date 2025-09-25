"""
Deployment action tracking system.
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import logging

from .audit_logger import AuditLogger, AuditContext, AuditEventType, AuditResult
from .security_config import SecurityConfig


class DeploymentStatus(Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    VALIDATING = "validating"
    BUILDING = "building"
    DEPLOYING = "deploying"
    TESTING = "testing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


class DeploymentStage(Enum):
    """Deployment stage enumeration."""
    PRE_VALIDATION = "pre_validation"
    BUILD = "build"
    SECURITY_SCAN = "security_scan"
    DEPLOY = "deploy"
    HEALTH_CHECK = "health_check"
    POST_VALIDATION = "post_validation"
    CLEANUP = "cleanup"


@dataclass
class DeploymentAction:
    """Deployment action record."""
    action_id: str
    deployment_id: str
    timestamp: datetime
    stage: DeploymentStage
    action: str
    status: DeploymentStatus
    duration_seconds: Optional[float]
    details: Dict[str, Any]
    user_id: Optional[str]
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'action_id': self.action_id,
            'deployment_id': self.deployment_id,
            'timestamp': self.timestamp.isoformat(),
            'stage': self.stage.value,
            'action': self.action,
            'status': self.status.value,
            'duration_seconds': self.duration_seconds,
            'details': self.details,
            'user_id': self.user_id,
            'error_message': self.error_message
        }


@dataclass
class DeploymentRecord:
    """Complete deployment record."""
    deployment_id: str
    created_at: datetime
    updated_at: datetime
    status: DeploymentStatus
    environment: str
    commit_sha: str
    image_tag: str
    user_id: str
    actions: List[DeploymentAction]
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'deployment_id': self.deployment_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'status': self.status.value,
            'environment': self.environment,
            'commit_sha': self.commit_sha,
            'image_tag': self.image_tag,
            'user_id': self.user_id,
            'actions': [action.to_dict() for action in self.actions],
            'metadata': self.metadata
        }


class DeploymentTracker:
    """Tracks deployment actions and maintains deployment history."""
    
    def __init__(self, config: SecurityConfig, audit_logger: AuditLogger):
        """Initialize deployment tracker."""
        self.config = config
        self.audit_logger = audit_logger
        self.logger = logging.getLogger(__name__)
        self._deployments: Dict[str, DeploymentRecord] = {}
        self._active_deployments: Dict[str, datetime] = {}
    
    def start_deployment(
        self,
        environment: str,
        commit_sha: str,
        image_tag: str,
        user_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        context: Optional[AuditContext] = None
    ) -> str:
        """Start tracking a new deployment."""
        deployment_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Create deployment record
        deployment_record = DeploymentRecord(
            deployment_id=deployment_id,
            created_at=timestamp,
            updated_at=timestamp,
            status=DeploymentStatus.PENDING,
            environment=environment,
            commit_sha=commit_sha,
            image_tag=image_tag,
            user_id=user_id,
            actions=[],
            metadata=metadata or {}
        )
        
        # Store deployment record
        self._deployments[deployment_id] = deployment_record
        self._active_deployments[deployment_id] = timestamp
        
        # Log deployment start
        self.audit_logger.log_deployment_start(
            deployment_id=deployment_id,
            environment=environment,
            commit_sha=commit_sha,
            context=context
        )
        
        # Track deployment start action
        self.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.PRE_VALIDATION,
            action="start_deployment",
            status=DeploymentStatus.PENDING,
            details={
                'environment': environment,
                'commit_sha': commit_sha,
                'image_tag': image_tag
            },
            user_id=user_id,
            context=context
        )
        
        return deployment_id
    
    def track_action(
        self,
        deployment_id: str,
        stage: DeploymentStage,
        action: str,
        status: DeploymentStatus,
        details: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        error_message: Optional[str] = None,
        context: Optional[AuditContext] = None
    ) -> str:
        """Track a deployment action."""
        if deployment_id not in self._deployments:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        action_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc)
        
        # Create deployment action
        deployment_action = DeploymentAction(
            action_id=action_id,
            deployment_id=deployment_id,
            timestamp=timestamp,
            stage=stage,
            action=action,
            status=status,
            duration_seconds=duration_seconds,
            details=details or {},
            user_id=user_id,
            error_message=error_message
        )
        
        # Add action to deployment record
        deployment_record = self._deployments[deployment_id]
        deployment_record.actions.append(deployment_action)
        deployment_record.updated_at = timestamp
        deployment_record.status = status
        
        # Log action to audit log
        self.audit_logger.log_event(
            event_type=AuditEventType.USER_ACTION,
            resource=f"deployment:{deployment_id}",
            action=action,
            result=self._status_to_audit_result(status),
            details={
                'stage': stage.value,
                'deployment_id': deployment_id,
                'duration_seconds': duration_seconds,
                'error_message': error_message,
                **(details or {})
            },
            context=context
        )
        
        return action_id
    
    def complete_deployment(
        self,
        deployment_id: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[AuditContext] = None
    ):
        """Complete a deployment."""
        if deployment_id not in self._deployments:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        deployment_record = self._deployments[deployment_id]
        start_time = self._active_deployments.get(deployment_id)
        
        # Calculate deployment duration
        duration_seconds = None
        if start_time:
            duration_seconds = (datetime.now(timezone.utc) - start_time).total_seconds()
            del self._active_deployments[deployment_id]
        
        # Update deployment status
        final_status = DeploymentStatus.COMPLETED if success else DeploymentStatus.FAILED
        deployment_record.status = final_status
        deployment_record.updated_at = datetime.now(timezone.utc)
        
        # Track completion action
        self.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.CLEANUP,
            action="complete_deployment",
            status=final_status,
            details={
                'success': success,
                'duration_seconds': duration_seconds,
                **(details or {})
            },
            user_id=deployment_record.user_id,
            duration_seconds=duration_seconds,
            context=context
        )
        
        # Log deployment completion
        if success:
            self.audit_logger.log_deployment_success(
                deployment_id=deployment_id,
                environment=deployment_record.environment,
                duration_seconds=duration_seconds or 0,
                context=context
            )
        else:
            self.audit_logger.log_deployment_failure(
                deployment_id=deployment_id,
                environment=deployment_record.environment,
                error_message=details.get('error_message', 'Deployment failed') if details else 'Deployment failed',
                error_details=details,
                context=context
            )
    
    def rollback_deployment(
        self,
        deployment_id: str,
        reason: str,
        target_revision: Optional[str] = None,
        context: Optional[AuditContext] = None
    ):
        """Track deployment rollback."""
        if deployment_id not in self._deployments:
            raise ValueError(f"Deployment {deployment_id} not found")
        
        deployment_record = self._deployments[deployment_id]
        deployment_record.status = DeploymentStatus.ROLLED_BACK
        deployment_record.updated_at = datetime.now(timezone.utc)
        
        # Track rollback action
        self.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.CLEANUP,
            action="rollback_deployment",
            status=DeploymentStatus.ROLLED_BACK,
            details={
                'reason': reason,
                'target_revision': target_revision
            },
            user_id=deployment_record.user_id,
            context=context
        )
        
        # Log rollback
        self.audit_logger.log_rollback(
            deployment_id=deployment_id,
            reason=reason,
            success=True,
            context=context
        )
    
    def get_deployment(self, deployment_id: str) -> Optional[DeploymentRecord]:
        """Get deployment record by ID."""
        return self._deployments.get(deployment_id)
    
    def get_deployments(
        self,
        environment: Optional[str] = None,
        status: Optional[DeploymentStatus] = None,
        user_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[DeploymentRecord]:
        """Get deployments with optional filtering."""
        deployments = list(self._deployments.values())
        
        # Apply filters
        if environment:
            deployments = [d for d in deployments if d.environment == environment]
        
        if status:
            deployments = [d for d in deployments if d.status == status]
        
        if user_id:
            deployments = [d for d in deployments if d.user_id == user_id]
        
        if start_time:
            deployments = [d for d in deployments if d.created_at >= start_time]
        
        if end_time:
            deployments = [d for d in deployments if d.created_at <= end_time]
        
        # Sort by creation time (newest first)
        deployments.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply limit
        if limit:
            deployments = deployments[:limit]
        
        return deployments
    
    def get_deployment_actions(
        self,
        deployment_id: str,
        stage: Optional[DeploymentStage] = None
    ) -> List[DeploymentAction]:
        """Get actions for a specific deployment."""
        if deployment_id not in self._deployments:
            return []
        
        actions = self._deployments[deployment_id].actions
        
        if stage:
            actions = [a for a in actions if a.stage == stage]
        
        return actions
    
    def get_deployment_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get deployment statistics."""
        deployments = self.get_deployments(start_time=start_time, end_time=end_time)
        
        if not deployments:
            return {
                'total_deployments': 0,
                'successful_deployments': 0,
                'failed_deployments': 0,
                'success_rate': 0.0,
                'average_duration_seconds': 0.0,
                'deployments_by_environment': {},
                'deployments_by_status': {}
            }
        
        # Calculate statistics
        total = len(deployments)
        successful = len([d for d in deployments if d.status == DeploymentStatus.COMPLETED])
        failed = len([d for d in deployments if d.status == DeploymentStatus.FAILED])
        success_rate = successful / total if total > 0 else 0.0
        
        # Calculate average duration
        durations = []
        for deployment in deployments:
            if deployment.actions:
                start_action = min(deployment.actions, key=lambda x: x.timestamp)
                end_action = max(deployment.actions, key=lambda x: x.timestamp)
                duration = (end_action.timestamp - start_action.timestamp).total_seconds()
                durations.append(duration)
        
        average_duration = sum(durations) / len(durations) if durations else 0.0
        
        # Count by environment
        environments = {}
        for deployment in deployments:
            env = deployment.environment
            environments[env] = environments.get(env, 0) + 1
        
        # Count by status
        statuses = {}
        for deployment in deployments:
            status = deployment.status.value
            statuses[status] = statuses.get(status, 0) + 1
        
        return {
            'total_deployments': total,
            'successful_deployments': successful,
            'failed_deployments': failed,
            'success_rate': success_rate,
            'average_duration_seconds': average_duration,
            'deployments_by_environment': environments,
            'deployments_by_status': statuses
        }
    
    def export_deployment_history(
        self,
        file_path: str,
        format: str = 'json',
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ):
        """Export deployment history to file."""
        deployments = self.get_deployments(start_time=start_time, end_time=end_time)
        
        if format.lower() == 'json':
            with open(file_path, 'w') as f:
                json.dump([deployment.to_dict() for deployment in deployments], f, indent=2)
        elif format.lower() == 'csv':
            import csv
            with open(file_path, 'w', newline='') as f:
                if deployments:
                    # Flatten deployment data for CSV
                    fieldnames = [
                        'deployment_id', 'created_at', 'updated_at', 'status',
                        'environment', 'commit_sha', 'image_tag', 'user_id'
                    ]
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for deployment in deployments:
                        row = {
                            'deployment_id': deployment.deployment_id,
                            'created_at': deployment.created_at.isoformat(),
                            'updated_at': deployment.updated_at.isoformat(),
                            'status': deployment.status.value,
                            'environment': deployment.environment,
                            'commit_sha': deployment.commit_sha,
                            'image_tag': deployment.image_tag,
                            'user_id': deployment.user_id
                        }
                        writer.writerow(row)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def cleanup_old_deployments(self, retention_days: int):
        """Clean up old deployment records."""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)
        
        # Find deployments to remove
        to_remove = []
        for deployment_id, deployment in self._deployments.items():
            if deployment.created_at < cutoff_date:
                to_remove.append(deployment_id)
        
        # Remove old deployments
        for deployment_id in to_remove:
            del self._deployments[deployment_id]
            if deployment_id in self._active_deployments:
                del self._active_deployments[deployment_id]
        
        # Log cleanup action
        self.audit_logger.log_event(
            event_type=AuditEventType.SYSTEM_CHANGE,
            resource="deployment_history",
            action="cleanup_old_deployments",
            result=AuditResult.INFO,
            details={
                'retention_days': retention_days,
                'cutoff_date': cutoff_date.isoformat(),
                'removed_count': len(to_remove),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        )
    
    def _status_to_audit_result(self, status: DeploymentStatus) -> AuditResult:
        """Convert deployment status to audit result."""
        if status in [DeploymentStatus.COMPLETED]:
            return AuditResult.SUCCESS
        elif status in [DeploymentStatus.FAILED, DeploymentStatus.CANCELLED]:
            return AuditResult.FAILURE
        elif status in [DeploymentStatus.ROLLED_BACK]:
            return AuditResult.WARNING
        else:
            return AuditResult.INFO