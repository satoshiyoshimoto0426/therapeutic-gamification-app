"""
Abstract base class for deployment strategies.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List


class DeploymentStatus(Enum):
    """Deployment status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class DeploymentResult:
    """Result of a deployment operation."""
    status: DeploymentStatus
    message: str
    timestamp: datetime
    revision_name: Optional[str] = None
    traffic_allocation: Optional[Dict[str, int]] = None
    rollback_revision: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None


@dataclass
class DeploymentConfig:
    """Configuration for deployment operations."""
    service_name: str
    project_id: str
    region: str
    image_url: str
    environment: str
    memory: str = "2Gi"
    cpu: str = "2"
    min_instances: int = 1
    max_instances: int = 100
    timeout_seconds: int = 300
    traffic_split_percentage: int = 100
    health_check_path: str = "/health"
    environment_variables: Optional[Dict[str, str]] = None


class DeploymentStrategy(ABC):
    """Abstract base class for deployment strategies."""
    
    def __init__(self, config: DeploymentConfig):
        """Initialize deployment strategy with configuration."""
        self.config = config
        self._deployment_history: List[DeploymentResult] = []
    
    @abstractmethod
    def deploy(self) -> DeploymentResult:
        """
        Execute the deployment strategy.
        
        Returns:
            DeploymentResult: Result of the deployment operation
        """
        pass
    
    @abstractmethod
    def rollback(self, target_revision: Optional[str] = None) -> DeploymentResult:
        """
        Rollback to a previous deployment.
        
        Args:
            target_revision: Specific revision to rollback to. If None, rollback to previous stable revision.
            
        Returns:
            DeploymentResult: Result of the rollback operation
        """
        pass
    
    @abstractmethod
    def get_current_status(self) -> DeploymentResult:
        """
        Get current deployment status.
        
        Returns:
            DeploymentResult: Current deployment status
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate deployment configuration.
        
        Returns:
            bool: True if configuration is valid
        """
        required_fields = ['service_name', 'project_id', 'region', 'image_url', 'environment']
        for field in required_fields:
            if not getattr(self.config, field):
                raise ValueError(f"Required configuration field '{field}' is missing")
        
        if self.config.traffic_split_percentage < 0 or self.config.traffic_split_percentage > 100:
            raise ValueError("Traffic split percentage must be between 0 and 100")
        
        return True
    
    def add_to_history(self, result: DeploymentResult) -> None:
        """Add deployment result to history."""
        self._deployment_history.append(result)
    
    def get_deployment_history(self) -> List[DeploymentResult]:
        """Get deployment history."""
        return self._deployment_history.copy()
    
    def get_last_successful_deployment(self) -> Optional[DeploymentResult]:
        """Get the last successful deployment from history."""
        for result in reversed(self._deployment_history):
            if result.status == DeploymentStatus.SUCCESS:
                return result
        return None