"""
Data models for deployment reporting system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
import uuid


class DeploymentStatus(Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    VALIDATING = "validating"
    DEPLOYING = "deploying"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


class DeploymentPhase(Enum):
    """Deployment phase enumeration."""
    VALIDATION = "validation"
    ENVIRONMENT_SETUP = "environment_setup"
    BUILD = "build"
    DEPLOYMENT = "deployment"
    HEALTH_CHECK = "health_check"
    MONITORING = "monitoring"
    COMPLETION = "completion"


class ProgressStatus(Enum):
    """Progress status enumeration."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class DeploymentMetrics:
    """Deployment performance metrics."""
    total_duration_seconds: float = 0.0
    validation_duration_seconds: float = 0.0
    build_duration_seconds: float = 0.0
    deployment_duration_seconds: float = 0.0
    health_check_duration_seconds: float = 0.0
    
    # Resource metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    network_io_mb: float = 0.0
    
    # Success metrics
    success_rate: float = 0.0
    error_count: int = 0
    warning_count: int = 0


@dataclass
class PhaseProgress:
    """Progress information for a deployment phase."""
    phase: DeploymentPhase
    status: ProgressStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    progress_percentage: float = 0.0
    current_step: str = ""
    total_steps: int = 0
    completed_steps: int = 0
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeploymentRecord:
    """Complete deployment record with all information."""
    deployment_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    environment: str = ""
    commit_sha: str = ""
    image_tag: str = ""
    revision_name: str = ""
    
    # Status and timing
    status: DeploymentStatus = DeploymentStatus.PENDING
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    
    # Progress tracking
    phases: Dict[DeploymentPhase, PhaseProgress] = field(default_factory=dict)
    current_phase: Optional[DeploymentPhase] = None
    overall_progress_percentage: float = 0.0
    
    # Configuration
    deployment_config: Dict[str, Any] = field(default_factory=dict)
    environment_config: Dict[str, Any] = field(default_factory=dict)
    
    # Results and metrics
    metrics: DeploymentMetrics = field(default_factory=DeploymentMetrics)
    health_check_results: List[Dict[str, Any]] = field(default_factory=list)
    validation_results: List[Dict[str, Any]] = field(default_factory=list)
    
    # Error handling
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Rollback information
    rollback_revision: Optional[str] = None
    rollback_reason: Optional[str] = None
    rollback_time: Optional[datetime] = None
    
    # Notification tracking
    notifications_sent: List[Dict[str, Any]] = field(default_factory=list)
    
    # Additional metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_duration_seconds(self) -> Optional[float]:
        """Get total deployment duration in seconds."""
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        return None
    
    def is_completed(self) -> bool:
        """Check if deployment is completed (success or failure)."""
        return self.status in [
            DeploymentStatus.COMPLETED,
            DeploymentStatus.FAILED,
            DeploymentStatus.ROLLED_BACK
        ]
    
    def is_successful(self) -> bool:
        """Check if deployment was successful."""
        return self.status == DeploymentStatus.COMPLETED
    
    def get_phase_progress(self, phase: DeploymentPhase) -> Optional[PhaseProgress]:
        """Get progress information for a specific phase."""
        return self.phases.get(phase)
    
    def update_phase_progress(self, phase: DeploymentPhase, **kwargs):
        """Update progress information for a specific phase."""
        if phase not in self.phases:
            self.phases[phase] = PhaseProgress(phase=phase, status=ProgressStatus.NOT_STARTED)
        
        phase_progress = self.phases[phase]
        for key, value in kwargs.items():
            if hasattr(phase_progress, key):
                setattr(phase_progress, key, value)
    
    def calculate_overall_progress(self) -> float:
        """Calculate overall deployment progress percentage."""
        if not self.phases:
            return 0.0
        
        total_weight = len(DeploymentPhase)
        completed_weight = 0.0
        
        for phase in DeploymentPhase:
            phase_progress = self.phases.get(phase)
            if phase_progress:
                if phase_progress.status == ProgressStatus.COMPLETED:
                    completed_weight += 1.0
                elif phase_progress.status == ProgressStatus.IN_PROGRESS:
                    completed_weight += phase_progress.progress_percentage / 100.0
        
        self.overall_progress_percentage = (completed_weight / total_weight) * 100.0
        return self.overall_progress_percentage


@dataclass
class DeploymentSummary:
    """Summary information for deployment reporting."""
    deployment_id: str
    environment: str
    status: DeploymentStatus
    start_time: datetime
    end_time: Optional[datetime]
    duration_seconds: Optional[float]
    commit_sha: str
    image_tag: str
    success: bool
    error_count: int
    warning_count: int
    
    @classmethod
    def from_record(cls, record: DeploymentRecord) -> 'DeploymentSummary':
        """Create summary from deployment record."""
        return cls(
            deployment_id=record.deployment_id,
            environment=record.environment,
            status=record.status,
            start_time=record.start_time,
            end_time=record.end_time,
            duration_seconds=record.get_duration_seconds(),
            commit_sha=record.commit_sha,
            image_tag=record.image_tag,
            success=record.is_successful(),
            error_count=len(record.errors),
            warning_count=len(record.warnings)
        )


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    include_metrics: bool = True
    include_logs: bool = True
    include_health_checks: bool = True
    include_validation_results: bool = True
    include_notifications: bool = True
    format: str = "json"  # json, html, markdown
    template_path: Optional[str] = None
    output_path: Optional[str] = None