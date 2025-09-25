"""
Cloud Run traffic management and routing system.

Handles traffic splitting, canary deployments, and blue-green deployments
for Cloud Run services.
"""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from google.cloud import run_v2
from google.api_core import exceptions as gcp_exceptions
import time

from .cloud_run_client import CloudRunClient

logger = logging.getLogger(__name__)


class TrafficStrategy(Enum):
    """Traffic routing strategies."""
    IMMEDIATE = "immediate"  # 100% traffic to new revision
    CANARY = "canary"       # Gradual traffic shift
    BLUE_GREEN = "blue_green"  # Switch between two revisions


@dataclass
class TrafficSplit:
    """Represents traffic split configuration."""
    revision_name: str
    percentage: int
    tag: Optional[str] = None


@dataclass
class TrafficUpdateResult:
    """Result of traffic update operation."""
    success: bool
    current_traffic: Dict[str, int]
    error_message: Optional[str] = None


class TrafficManager:
    """Manages Cloud Run service traffic routing."""
    
    def __init__(self, cloud_run_client: CloudRunClient):
        """
        Initialize traffic manager.
        
        Args:
            cloud_run_client: Cloud Run client instance
        """
        self.client = cloud_run_client
        self.services_client = run_v2.ServicesClient()
    
    def update_traffic(
        self, 
        service_name: str, 
        traffic_splits: List[TrafficSplit]
    ) -> TrafficUpdateResult:
        """
        Update traffic allocation for a service.
        
        Args:
            service_name: Name of the Cloud Run service
            traffic_splits: List of traffic split configurations
            
        Returns:
            TrafficUpdateResult with operation status
        """
        try:
            # Validate traffic splits
            if not self._validate_traffic_splits(traffic_splits):
                return TrafficUpdateResult(
                    success=False,
                    current_traffic={},
                    error_message="Invalid traffic splits: percentages must sum to 100"
                )
            
            logger.info(f"Updating traffic for service: {service_name}")
            
            # Get current service
            service = self.client.get_service(service_name)
            if not service:
                return TrafficUpdateResult(
                    success=False,
                    current_traffic={},
                    error_message=f"Service {service_name} not found"
                )
            
            # Create traffic specifications
            traffic_specs = []
            for split in traffic_splits:
                traffic_spec = run_v2.TrafficTarget(
                    revision=split.revision_name,
                    percent=split.percentage
                )
                if split.tag:
                    traffic_spec.tag = split.tag
                traffic_specs.append(traffic_spec)
            
            # Update service with new traffic allocation
            service.spec.traffic = traffic_specs
            
            operation = self.services_client.update_service(service=service)
            result = operation.result(timeout=300)  # 5 minutes timeout
            
            # Get updated traffic allocation
            current_traffic = self.client._get_traffic_allocation(result)
            
            logger.info(f"Successfully updated traffic for service: {service_name}")
            return TrafficUpdateResult(
                success=True,
                current_traffic=current_traffic
            )
            
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to update traffic for service {service_name}: {e}")
            return TrafficUpdateResult(
                success=False,
                current_traffic={},
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error updating traffic for service {service_name}: {e}")
            return TrafficUpdateResult(
                success=False,
                current_traffic={},
                error_message=str(e)
            )
    
    def execute_canary_deployment(
        self,
        service_name: str,
        new_revision: str,
        old_revision: str,
        canary_percentage: int = 10,
        monitoring_duration: int = 300  # 5 minutes
    ) -> TrafficUpdateResult:
        """
        Execute canary deployment with gradual traffic shift.
        
        Args:
            service_name: Name of the Cloud Run service
            new_revision: New revision to deploy
            old_revision: Current stable revision
            canary_percentage: Initial percentage for canary
            monitoring_duration: Time to monitor before full rollout
            
        Returns:
            TrafficUpdateResult with final traffic allocation
        """
        logger.info(f"Starting canary deployment for service: {service_name}")
        
        # Phase 1: Route small percentage to new revision
        canary_splits = [
            TrafficSplit(revision_name=new_revision, percentage=canary_percentage, tag="canary"),
            TrafficSplit(revision_name=old_revision, percentage=100 - canary_percentage, tag="stable")
        ]
        
        result = self.update_traffic(service_name, canary_splits)
        if not result.success:
            return result
        
        logger.info(f"Canary phase started: {canary_percentage}% traffic to new revision")
        
        # Monitor canary for specified duration
        # In a real implementation, this would include health checks and metrics monitoring
        time.sleep(monitoring_duration)
        
        # Phase 2: Full rollout (this could be conditional based on metrics)
        full_rollout_splits = [
            TrafficSplit(revision_name=new_revision, percentage=100, tag="stable")
        ]
        
        result = self.update_traffic(service_name, full_rollout_splits)
        if result.success:
            logger.info(f"Canary deployment completed successfully for service: {service_name}")
        
        return result
    
    def execute_blue_green_deployment(
        self,
        service_name: str,
        blue_revision: str,
        green_revision: str,
        switch_to_green: bool = True
    ) -> TrafficUpdateResult:
        """
        Execute blue-green deployment.
        
        Args:
            service_name: Name of the Cloud Run service
            blue_revision: Blue (current) revision
            green_revision: Green (new) revision
            switch_to_green: Whether to switch traffic to green
            
        Returns:
            TrafficUpdateResult with traffic allocation
        """
        logger.info(f"Starting blue-green deployment for service: {service_name}")
        
        if switch_to_green:
            # Switch all traffic to green revision
            traffic_splits = [
                TrafficSplit(revision_name=green_revision, percentage=100, tag="live"),
                TrafficSplit(revision_name=blue_revision, percentage=0, tag="standby")
            ]
            logger.info("Switching traffic to green revision")
        else:
            # Keep traffic on blue revision
            traffic_splits = [
                TrafficSplit(revision_name=blue_revision, percentage=100, tag="live"),
                TrafficSplit(revision_name=green_revision, percentage=0, tag="standby")
            ]
            logger.info("Keeping traffic on blue revision")
        
        result = self.update_traffic(service_name, traffic_splits)
        if result.success:
            logger.info(f"Blue-green deployment completed for service: {service_name}")
        
        return result
    
    def rollback_traffic(
        self,
        service_name: str,
        target_revision: str
    ) -> TrafficUpdateResult:
        """
        Rollback all traffic to a specific revision.
        
        Args:
            service_name: Name of the Cloud Run service
            target_revision: Revision to rollback to
            
        Returns:
            TrafficUpdateResult with rollback status
        """
        logger.info(f"Rolling back traffic for service: {service_name} to revision: {target_revision}")
        
        rollback_splits = [
            TrafficSplit(revision_name=target_revision, percentage=100, tag="stable")
        ]
        
        result = self.update_traffic(service_name, rollback_splits)
        if result.success:
            logger.info(f"Traffic rollback completed for service: {service_name}")
        
        return result
    
    def get_current_traffic(self, service_name: str) -> Dict[str, int]:
        """
        Get current traffic allocation for a service.
        
        Args:
            service_name: Name of the Cloud Run service
            
        Returns:
            Dictionary mapping revision names to traffic percentages
        """
        service = self.client.get_service(service_name)
        if not service:
            return {}
        
        return self.client._get_traffic_allocation(service)
    
    def split_traffic_evenly(
        self,
        service_name: str,
        revisions: List[str]
    ) -> TrafficUpdateResult:
        """
        Split traffic evenly between multiple revisions.
        
        Args:
            service_name: Name of the Cloud Run service
            revisions: List of revision names
            
        Returns:
            TrafficUpdateResult with traffic allocation
        """
        if not revisions:
            return TrafficUpdateResult(
                success=False,
                current_traffic={},
                error_message="No revisions provided"
            )
        
        percentage_per_revision = 100 // len(revisions)
        remainder = 100 % len(revisions)
        
        traffic_splits = []
        for i, revision in enumerate(revisions):
            percentage = percentage_per_revision
            if i < remainder:  # Distribute remainder to first few revisions
                percentage += 1
            
            traffic_splits.append(TrafficSplit(
                revision_name=revision,
                percentage=percentage
            ))
        
        return self.update_traffic(service_name, traffic_splits)
    
    def _validate_traffic_splits(self, traffic_splits: List[TrafficSplit]) -> bool:
        """
        Validate that traffic splits are valid.
        
        Args:
            traffic_splits: List of traffic split configurations
            
        Returns:
            True if valid, False otherwise
        """
        if not traffic_splits:
            return False
        
        total_percentage = sum(split.percentage for split in traffic_splits)
        return total_percentage == 100