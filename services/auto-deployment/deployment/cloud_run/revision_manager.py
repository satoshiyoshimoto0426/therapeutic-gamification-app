"""
Cloud Run revision management system.

Handles revision lifecycle, metadata tracking, and cleanup operations.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from google.cloud import run_v2
from google.api_core import exceptions as gcp_exceptions

from .cloud_run_client import CloudRunClient

logger = logging.getLogger(__name__)


class RevisionStatus(Enum):
    """Revision status types."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SERVING = "serving"
    RETIRED = "retired"


@dataclass
class RevisionInfo:
    """Information about a Cloud Run revision."""
    name: str
    service_name: str
    image: str
    created_time: datetime
    status: RevisionStatus
    traffic_percentage: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)
    resource_limits: Dict[str, str] = field(default_factory=dict)
    env_vars: Dict[str, str] = field(default_factory=dict)


@dataclass
class RevisionCleanupResult:
    """Result of revision cleanup operation."""
    success: bool
    cleaned_revisions: List[str]
    error_message: Optional[str] = None


class RevisionManager:
    """Manages Cloud Run service revisions."""
    
    def __init__(self, cloud_run_client: CloudRunClient):
        """
        Initialize revision manager.
        
        Args:
            cloud_run_client: Cloud Run client instance
        """
        self.client = cloud_run_client
        self.revisions_client = run_v2.RevisionsClient()
        self.services_client = run_v2.ServicesClient()
    
    def get_revision_info(self, service_name: str, revision_name: str) -> Optional[RevisionInfo]:
        """
        Get detailed information about a specific revision.
        
        Args:
            service_name: Name of the Cloud Run service
            revision_name: Name of the revision
            
        Returns:
            RevisionInfo object or None if not found
        """
        try:
            full_revision_name = f"{self.client.parent}/services/{service_name}/revisions/{revision_name}"
            revision = self.revisions_client.get_revision(name=full_revision_name)
            
            # Get traffic information
            service = self.client.get_service(service_name)
            traffic_percentage = 0
            if service:
                traffic_allocation = self.client._get_traffic_allocation(service)
                traffic_percentage = traffic_allocation.get(revision_name, 0)
            
            return self._convert_to_revision_info(revision, service_name, traffic_percentage)
            
        except gcp_exceptions.NotFound:
            logger.warning(f"Revision {revision_name} not found for service {service_name}")
            return None
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Error getting revision info: {e}")
            return None
    
    def list_revisions(self, service_name: str) -> List[RevisionInfo]:
        """
        List all revisions for a service with detailed information.
        
        Args:
            service_name: Name of the Cloud Run service
            
        Returns:
            List of RevisionInfo objects
        """
        try:
            parent = f"{self.client.parent}/services/{service_name}"
            revisions = self.revisions_client.list_revisions(parent=parent)
            
            # Get traffic allocation for the service
            service = self.client.get_service(service_name)
            traffic_allocation = {}
            if service:
                traffic_allocation = self.client._get_traffic_allocation(service)
            
            revision_infos = []
            for revision in revisions:
                revision_name = revision.name.split('/')[-1]
                traffic_percentage = traffic_allocation.get(revision_name, 0)
                revision_info = self._convert_to_revision_info(revision, service_name, traffic_percentage)
                revision_infos.append(revision_info)
            
            # Sort by creation time (newest first)
            revision_infos.sort(key=lambda x: x.created_time, reverse=True)
            return revision_infos
            
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Error listing revisions for service {service_name}: {e}")
            return []
    
    def get_latest_revision(self, service_name: str) -> Optional[RevisionInfo]:
        """
        Get the latest revision for a service.
        
        Args:
            service_name: Name of the Cloud Run service
            
        Returns:
            Latest RevisionInfo or None if no revisions found
        """
        revisions = self.list_revisions(service_name)
        return revisions[0] if revisions else None
    
    def get_serving_revisions(self, service_name: str) -> List[RevisionInfo]:
        """
        Get all revisions currently serving traffic.
        
        Args:
            service_name: Name of the Cloud Run service
            
        Returns:
            List of RevisionInfo objects serving traffic
        """
        revisions = self.list_revisions(service_name)
        return [rev for rev in revisions if rev.traffic_percentage > 0]
    
    def get_stable_revision(self, service_name: str) -> Optional[RevisionInfo]:
        """
        Get the stable revision (highest traffic allocation).
        
        Args:
            service_name: Name of the Cloud Run service
            
        Returns:
            Stable RevisionInfo or None if no serving revisions
        """
        serving_revisions = self.get_serving_revisions(service_name)
        if not serving_revisions:
            return None
        
        # Return revision with highest traffic percentage
        return max(serving_revisions, key=lambda x: x.traffic_percentage)
    
    def cleanup_old_revisions(
        self,
        service_name: str,
        keep_count: int = 5,
        keep_days: int = 30
    ) -> RevisionCleanupResult:
        """
        Clean up old revisions based on age and count limits.
        
        Args:
            service_name: Name of the Cloud Run service
            keep_count: Number of recent revisions to keep
            keep_days: Number of days to keep revisions
            
        Returns:
            RevisionCleanupResult with cleanup status
        """
        try:
            logger.info(f"Starting revision cleanup for service: {service_name}")
            
            revisions = self.list_revisions(service_name)
            if not revisions:
                return RevisionCleanupResult(
                    success=True,
                    cleaned_revisions=[],
                    error_message="No revisions found"
                )
            
            # Identify revisions to clean up
            revisions_to_delete = self._identify_revisions_for_cleanup(
                revisions, keep_count, keep_days
            )
            
            if not revisions_to_delete:
                logger.info(f"No revisions to clean up for service: {service_name}")
                return RevisionCleanupResult(
                    success=True,
                    cleaned_revisions=[]
                )
            
            # Delete identified revisions
            cleaned_revisions = []
            for revision_name in revisions_to_delete:
                if self._delete_revision(service_name, revision_name):
                    cleaned_revisions.append(revision_name)
                    logger.info(f"Deleted revision: {revision_name}")
                else:
                    logger.warning(f"Failed to delete revision: {revision_name}")
            
            logger.info(f"Cleanup completed for service: {service_name}. Deleted {len(cleaned_revisions)} revisions")
            return RevisionCleanupResult(
                success=True,
                cleaned_revisions=cleaned_revisions
            )
            
        except Exception as e:
            logger.error(f"Error during revision cleanup for service {service_name}: {e}")
            return RevisionCleanupResult(
                success=False,
                cleaned_revisions=[],
                error_message=str(e)
            )
    
    def tag_revision(
        self,
        service_name: str,
        revision_name: str,
        tag: str
    ) -> bool:
        """
        Add a tag to a revision for easier identification.
        
        Args:
            service_name: Name of the Cloud Run service
            revision_name: Name of the revision
            tag: Tag to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current service
            service = self.client.get_service(service_name)
            if not service:
                logger.error(f"Service {service_name} not found")
                return False
            
            # Find the revision in traffic allocation and add tag
            updated_traffic = []
            for traffic in service.spec.traffic:
                if traffic.revision == revision_name:
                    traffic.tag = tag
                updated_traffic.append(traffic)
            
            # If revision not in traffic, add it with 0% and tag
            revision_found = any(t.revision == revision_name for t in service.spec.traffic)
            if not revision_found:
                new_traffic = run_v2.TrafficTarget(
                    revision=revision_name,
                    percent=0,
                    tag=tag
                )
                updated_traffic.append(new_traffic)
            
            service.spec.traffic = updated_traffic
            
            # Update service
            operation = self.services_client.update_service(service=service)
            operation.result(timeout=300)
            
            logger.info(f"Successfully tagged revision {revision_name} with tag: {tag}")
            return True
            
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to tag revision {revision_name}: {e}")
            return False
    
    def compare_revisions(
        self,
        service_name: str,
        revision1: str,
        revision2: str
    ) -> Dict[str, Any]:
        """
        Compare two revisions and return differences.
        
        Args:
            service_name: Name of the Cloud Run service
            revision1: First revision name
            revision2: Second revision name
            
        Returns:
            Dictionary containing comparison results
        """
        rev1_info = self.get_revision_info(service_name, revision1)
        rev2_info = self.get_revision_info(service_name, revision2)
        
        if not rev1_info or not rev2_info:
            return {"error": "One or both revisions not found"}
        
        comparison = {
            "image_changed": rev1_info.image != rev2_info.image,
            "resource_changes": {},
            "env_var_changes": {},
            "metadata_changes": {}
        }
        
        # Compare resource limits
        for key in set(rev1_info.resource_limits.keys()) | set(rev2_info.resource_limits.keys()):
            val1 = rev1_info.resource_limits.get(key)
            val2 = rev2_info.resource_limits.get(key)
            if val1 != val2:
                comparison["resource_changes"][key] = {"from": val1, "to": val2}
        
        # Compare environment variables
        for key in set(rev1_info.env_vars.keys()) | set(rev2_info.env_vars.keys()):
            val1 = rev1_info.env_vars.get(key)
            val2 = rev2_info.env_vars.get(key)
            if val1 != val2:
                comparison["env_var_changes"][key] = {"from": val1, "to": val2}
        
        # Compare metadata
        for key in set(rev1_info.metadata.keys()) | set(rev2_info.metadata.keys()):
            val1 = rev1_info.metadata.get(key)
            val2 = rev2_info.metadata.get(key)
            if val1 != val2:
                comparison["metadata_changes"][key] = {"from": val1, "to": val2}
        
        return comparison
    
    def _convert_to_revision_info(
        self,
        revision: Any,
        service_name: str,
        traffic_percentage: int
    ) -> RevisionInfo:
        """Convert Cloud Run revision object to RevisionInfo."""
        revision_name = revision.name.split('/')[-1]
        
        # Extract image from container spec
        image = ""
        if hasattr(revision, 'spec') and hasattr(revision.spec, 'template'):
            template = revision.spec.template
            if hasattr(template, 'spec') and hasattr(template.spec, 'containers'):
                containers = template.spec.containers
                if containers:
                    image = containers[0].image
        
        # Extract creation time
        created_time = datetime.now()
        if hasattr(revision, 'create_time'):
            created_time = revision.create_time
        
        # Determine status
        status = RevisionStatus.INACTIVE
        if traffic_percentage > 0:
            status = RevisionStatus.SERVING
        elif hasattr(revision, 'status') and revision.status:
            # Map Cloud Run status to our enum
            if hasattr(revision.status, 'conditions'):
                for condition in revision.status.conditions:
                    if condition.type == "Ready" and condition.status == "True":
                        status = RevisionStatus.ACTIVE
                        break
        
        # Extract metadata
        metadata = {}
        if hasattr(revision, 'metadata') and hasattr(revision.metadata, 'labels'):
            metadata = dict(revision.metadata.labels)
        
        # Extract resource limits
        resource_limits = {}
        env_vars = {}
        if hasattr(revision, 'spec') and hasattr(revision.spec, 'template'):
            template = revision.spec.template
            if hasattr(template, 'spec') and hasattr(template.spec, 'containers'):
                containers = template.spec.containers
                if containers:
                    container = containers[0]
                    if hasattr(container, 'resources') and hasattr(container.resources, 'limits'):
                        resource_limits = dict(container.resources.limits)
                    if hasattr(container, 'env'):
                        env_vars = {env.name: env.value for env in container.env if hasattr(env, 'value')}
        
        return RevisionInfo(
            name=revision_name,
            service_name=service_name,
            image=image,
            created_time=created_time,
            status=status,
            traffic_percentage=traffic_percentage,
            metadata=metadata,
            resource_limits=resource_limits,
            env_vars=env_vars
        )
    
    def _identify_revisions_for_cleanup(
        self,
        revisions: List[RevisionInfo],
        keep_count: int,
        keep_days: int
    ) -> List[str]:
        """Identify revisions that should be cleaned up."""
        # Never delete revisions that are serving traffic
        serving_revisions = {rev.name for rev in revisions if rev.traffic_percentage > 0}
        
        # Calculate cutoff date
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        # Sort revisions by creation time (newest first)
        sorted_revisions = sorted(revisions, key=lambda x: x.created_time, reverse=True)
        
        revisions_to_delete = []
        for i, revision in enumerate(sorted_revisions):
            # Skip if serving traffic
            if revision.name in serving_revisions:
                continue
            
            # Keep recent revisions (by count)
            if i < keep_count:
                continue
            
            # Keep revisions newer than cutoff date
            if revision.created_time > cutoff_date:
                continue
            
            revisions_to_delete.append(revision.name)
        
        return revisions_to_delete
    
    def _delete_revision(self, service_name: str, revision_name: str) -> bool:
        """Delete a specific revision."""
        try:
            full_revision_name = f"{self.client.parent}/services/{service_name}/revisions/{revision_name}"
            operation = self.revisions_client.delete_revision(name=full_revision_name)
            operation.result(timeout=300)
            return True
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to delete revision {revision_name}: {e}")
            return False