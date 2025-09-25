"""
Main Cloud Run deployment orchestrator.

Coordinates deployment operations using the Cloud Run client, traffic manager,
and revision manager to provide a comprehensive deployment solution.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from .cloud_run_client import CloudRunClient, CloudRunService, DeploymentResult
from .traffic_manager import TrafficManager, TrafficStrategy, TrafficSplit
from .revision_manager import RevisionManager, RevisionInfo

logger = logging.getLogger(__name__)


class DeploymentStrategy(Enum):
    """Deployment strategy types."""
    IMMEDIATE = "immediate"
    CANARY = "canary"
    BLUE_GREEN = "blue_green"


@dataclass
class DeploymentConfig:
    """Configuration for Cloud Run deployment."""
    service_config: CloudRunService
    strategy: DeploymentStrategy = DeploymentStrategy.IMMEDIATE
    canary_percentage: int = 10
    monitoring_duration: int = 300  # 5 minutes
    cleanup_old_revisions: bool = True
    keep_revision_count: int = 5
    keep_revision_days: int = 30


@dataclass
class DeploymentStatus:
    """Status of a deployment operation."""
    success: bool
    service_name: str
    new_revision: str
    previous_revision: Optional[str]
    traffic_allocation: Dict[str, int]
    deployment_strategy: DeploymentStrategy
    error_message: Optional[str] = None
    rollback_available: bool = False


class CloudRunDeployer:
    """Main Cloud Run deployment orchestrator."""
    
    def __init__(self, project_id: str, region: str):
        """
        Initialize Cloud Run deployer.
        
        Args:
            project_id: Google Cloud project ID
            region: Cloud Run region
        """
        self.project_id = project_id
        self.region = region
        self.client = CloudRunClient(project_id, region)
        self.traffic_manager = TrafficManager(self.client)
        self.revision_manager = RevisionManager(self.client)
    
    def deploy(self, config: DeploymentConfig) -> DeploymentStatus:
        """
        Deploy a Cloud Run service using the specified configuration.
        
        Args:
            config: Deployment configuration
            
        Returns:
            DeploymentStatus with deployment results
        """
        service_name = config.service_config.name
        logger.info(f"Starting deployment for service: {service_name}")
        
        try:
            # Get current stable revision for rollback capability
            previous_revision = None
            stable_revision = self.revision_manager.get_stable_revision(service_name)
            if stable_revision:
                previous_revision = stable_revision.name
            
            # Deploy the service to create new revision
            deployment_result = self.client.deploy_service(config.service_config)
            if not deployment_result.success:
                return DeploymentStatus(
                    success=False,
                    service_name=service_name,
                    new_revision="",
                    previous_revision=previous_revision,
                    traffic_allocation={},
                    deployment_strategy=config.strategy,
                    error_message=deployment_result.error_message
                )
            
            new_revision = deployment_result.revision_name
            logger.info(f"Successfully created new revision: {new_revision}")
            
            # Execute deployment strategy
            traffic_result = self._execute_deployment_strategy(
                config, service_name, new_revision, previous_revision
            )
            
            if not traffic_result.success:
                return DeploymentStatus(
                    success=False,
                    service_name=service_name,
                    new_revision=new_revision,
                    previous_revision=previous_revision,
                    traffic_allocation=traffic_result.current_traffic,
                    deployment_strategy=config.strategy,
                    error_message=traffic_result.error_message,
                    rollback_available=previous_revision is not None
                )
            
            # Clean up old revisions if requested
            if config.cleanup_old_revisions:
                cleanup_result = self.revision_manager.cleanup_old_revisions(
                    service_name,
                    config.keep_revision_count,
                    config.keep_revision_days
                )
                if cleanup_result.success:
                    logger.info(f"Cleaned up {len(cleanup_result.cleaned_revisions)} old revisions")
                else:
                    logger.warning(f"Revision cleanup failed: {cleanup_result.error_message}")
            
            logger.info(f"Deployment completed successfully for service: {service_name}")
            return DeploymentStatus(
                success=True,
                service_name=service_name,
                new_revision=new_revision,
                previous_revision=previous_revision,
                traffic_allocation=traffic_result.current_traffic,
                deployment_strategy=config.strategy,
                rollback_available=previous_revision is not None
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during deployment of service {service_name}: {e}")
            return DeploymentStatus(
                success=False,
                service_name=service_name,
                new_revision="",
                previous_revision=previous_revision,
                traffic_allocation={},
                deployment_strategy=config.strategy,
                error_message=str(e)
            )
    
    def rollback(self, service_name: str, target_revision: Optional[str] = None) -> DeploymentStatus:
        """
        Rollback a service to a previous revision.
        
        Args:
            service_name: Name of the Cloud Run service
            target_revision: Specific revision to rollback to (if None, uses stable revision)
            
        Returns:
            DeploymentStatus with rollback results
        """
        logger.info(f"Starting rollback for service: {service_name}")
        
        try:
            # Determine target revision
            if not target_revision:
                # Find the previous stable revision
                revisions = self.revision_manager.list_revisions(service_name)
                serving_revisions = [rev for rev in revisions if rev.traffic_percentage > 0]
                
                if len(serving_revisions) < 2:
                    # Look for the most recent non-serving revision
                    non_serving = [rev for rev in revisions if rev.traffic_percentage == 0]
                    if non_serving:
                        target_revision = non_serving[0].name
                    else:
                        return DeploymentStatus(
                            success=False,
                            service_name=service_name,
                            new_revision="",
                            previous_revision=None,
                            traffic_allocation={},
                            deployment_strategy=DeploymentStrategy.IMMEDIATE,
                            error_message="No suitable revision found for rollback"
                        )
                else:
                    # Use the revision with second highest traffic
                    serving_revisions.sort(key=lambda x: x.traffic_percentage, reverse=True)
                    target_revision = serving_revisions[1].name
            
            # Execute rollback
            rollback_result = self.traffic_manager.rollback_traffic(service_name, target_revision)
            
            if rollback_result.success:
                logger.info(f"Rollback completed successfully for service: {service_name}")
            
            return DeploymentStatus(
                success=rollback_result.success,
                service_name=service_name,
                new_revision=target_revision,
                previous_revision=None,
                traffic_allocation=rollback_result.current_traffic,
                deployment_strategy=DeploymentStrategy.IMMEDIATE,
                error_message=rollback_result.error_message
            )
            
        except Exception as e:
            logger.error(f"Unexpected error during rollback of service {service_name}: {e}")
            return DeploymentStatus(
                success=False,
                service_name=service_name,
                new_revision="",
                previous_revision=None,
                traffic_allocation={},
                deployment_strategy=DeploymentStrategy.IMMEDIATE,
                error_message=str(e)
            )
    
    def get_deployment_status(self, service_name: str) -> Dict[str, Any]:
        """
        Get current deployment status for a service.
        
        Args:
            service_name: Name of the Cloud Run service
            
        Returns:
            Dictionary containing deployment status information
        """
        try:
            # Get service information
            service = self.client.get_service(service_name)
            if not service:
                return {"error": f"Service {service_name} not found"}
            
            # Get revision information
            revisions = self.revision_manager.list_revisions(service_name)
            serving_revisions = [rev for rev in revisions if rev.traffic_percentage > 0]
            
            # Get traffic allocation
            traffic_allocation = self.traffic_manager.get_current_traffic(service_name)
            
            return {
                "service_name": service_name,
                "service_url": getattr(service, 'uri', ''),
                "total_revisions": len(revisions),
                "serving_revisions": len(serving_revisions),
                "traffic_allocation": traffic_allocation,
                "latest_revision": revisions[0].name if revisions else None,
                "stable_revision": serving_revisions[0].name if serving_revisions else None,
                "revisions": [
                    {
                        "name": rev.name,
                        "image": rev.image,
                        "created_time": rev.created_time.isoformat(),
                        "status": rev.status.value,
                        "traffic_percentage": rev.traffic_percentage
                    }
                    for rev in revisions[:10]  # Limit to 10 most recent
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting deployment status for service {service_name}: {e}")
            return {"error": str(e)}
    
    def _execute_deployment_strategy(
        self,
        config: DeploymentConfig,
        service_name: str,
        new_revision: str,
        previous_revision: Optional[str]
    ):
        """Execute the specified deployment strategy."""
        if config.strategy == DeploymentStrategy.IMMEDIATE:
            # Route all traffic to new revision immediately
            traffic_splits = [TrafficSplit(revision_name=new_revision, percentage=100)]
            return self.traffic_manager.update_traffic(service_name, traffic_splits)
        
        elif config.strategy == DeploymentStrategy.CANARY:
            if not previous_revision:
                # No previous revision, fall back to immediate deployment
                logger.warning("No previous revision found, falling back to immediate deployment")
                traffic_splits = [TrafficSplit(revision_name=new_revision, percentage=100)]
                return self.traffic_manager.update_traffic(service_name, traffic_splits)
            
            return self.traffic_manager.execute_canary_deployment(
                service_name,
                new_revision,
                previous_revision,
                config.canary_percentage,
                config.monitoring_duration
            )
        
        elif config.strategy == DeploymentStrategy.BLUE_GREEN:
            if not previous_revision:
                # No previous revision, fall back to immediate deployment
                logger.warning("No previous revision found, falling back to immediate deployment")
                traffic_splits = [TrafficSplit(revision_name=new_revision, percentage=100)]
                return self.traffic_manager.update_traffic(service_name, traffic_splits)
            
            return self.traffic_manager.execute_blue_green_deployment(
                service_name,
                previous_revision,  # blue
                new_revision,       # green
                switch_to_green=True
            )
        
        else:
            raise ValueError(f"Unknown deployment strategy: {config.strategy}")