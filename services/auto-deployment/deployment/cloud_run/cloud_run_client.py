"""
Google Cloud Run API client wrapper.

Provides a simplified interface for interacting with Google Cloud Run services.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from google.cloud import run_v2
from google.api_core import exceptions as gcp_exceptions
import time

logger = logging.getLogger(__name__)


@dataclass
class CloudRunService:
    """Represents a Cloud Run service configuration."""
    name: str
    project_id: str
    region: str
    image: str
    memory: str = "2Gi"
    cpu: str = "2"
    min_instances: int = 1
    max_instances: int = 100
    port: int = 8080
    env_vars: Optional[Dict[str, str]] = None
    service_account: Optional[str] = None
    
    def __post_init__(self):
        if self.env_vars is None:
            self.env_vars = {}


@dataclass
class DeploymentResult:
    """Result of a Cloud Run deployment operation."""
    success: bool
    service_name: str
    revision_name: str
    url: str
    traffic_allocation: Dict[str, int]
    error_message: Optional[str] = None


class CloudRunClient:
    """Client for interacting with Google Cloud Run API."""
    
    def __init__(self, project_id: str, region: str):
        """
        Initialize Cloud Run client.
        
        Args:
            project_id: Google Cloud project ID
            region: Cloud Run region
        """
        self.project_id = project_id
        self.region = region
        self.client = run_v2.ServicesClient()
        self.parent = f"projects/{project_id}/locations/{region}"
        
    def deploy_service(self, service_config: CloudRunService) -> DeploymentResult:
        """
        Deploy a Cloud Run service.
        
        Args:
            service_config: Service configuration
            
        Returns:
            DeploymentResult with deployment status and details
        """
        try:
            logger.info(f"Deploying Cloud Run service: {service_config.name}")
            
            # Create service specification
            service_spec = self._create_service_spec(service_config)
            
            # Check if service exists
            service_name = f"{self.parent}/services/{service_config.name}"
            existing_service = self._get_service(service_name)
            
            if existing_service:
                # Update existing service
                logger.info(f"Updating existing service: {service_config.name}")
                operation = self.client.update_service(
                    service=service_spec
                )
            else:
                # Create new service
                logger.info(f"Creating new service: {service_config.name}")
                operation = self.client.create_service(
                    parent=self.parent,
                    service=service_spec,
                    service_id=service_config.name
                )
            
            # Wait for operation to complete
            result = operation.result(timeout=600)  # 10 minutes timeout
            
            # Get service URL and revision info
            service_url = result.uri
            revision_name = result.latest_ready_revision_name
            
            # Get traffic allocation
            traffic_allocation = self._get_traffic_allocation(result)
            
            logger.info(f"Successfully deployed service: {service_config.name}")
            return DeploymentResult(
                success=True,
                service_name=service_config.name,
                revision_name=revision_name,
                url=service_url,
                traffic_allocation=traffic_allocation
            )
            
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to deploy service {service_config.name}: {e}")
            return DeploymentResult(
                success=False,
                service_name=service_config.name,
                revision_name="",
                url="",
                traffic_allocation={},
                error_message=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error deploying service {service_config.name}: {e}")
            return DeploymentResult(
                success=False,
                service_name=service_config.name,
                revision_name="",
                url="",
                traffic_allocation={},
                error_message=str(e)
            )
    
    def get_service(self, service_name: str) -> Optional[Any]:
        """
        Get Cloud Run service details.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service object or None if not found
        """
        full_service_name = f"{self.parent}/services/{service_name}"
        return self._get_service(full_service_name)
    
    def list_services(self) -> List[str]:
        """
        List all Cloud Run services in the project/region.
        
        Returns:
            List of service names
        """
        try:
            services = self.client.list_services(parent=self.parent)
            return [service.name.split('/')[-1] for service in services]
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to list services: {e}")
            return []
    
    def delete_service(self, service_name: str) -> bool:
        """
        Delete a Cloud Run service.
        
        Args:
            service_name: Name of the service to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            full_service_name = f"{self.parent}/services/{service_name}"
            operation = self.client.delete_service(name=full_service_name)
            operation.result(timeout=300)  # 5 minutes timeout
            logger.info(f"Successfully deleted service: {service_name}")
            return True
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to delete service {service_name}: {e}")
            return False
    
    def get_service_revisions(self, service_name: str) -> List[str]:
        """
        Get all revisions for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            List of revision names
        """
        try:
            revisions_client = run_v2.RevisionsClient()
            parent = f"{self.parent}/services/{service_name}"
            revisions = revisions_client.list_revisions(parent=parent)
            return [revision.name.split('/')[-1] for revision in revisions]
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Failed to get revisions for service {service_name}: {e}")
            return []
    
    def _create_service_spec(self, config: CloudRunService) -> Any:
        """Create Cloud Run service specification."""
        # Environment variables
        env_vars = []
        for key, value in config.env_vars.items():
            env_vars.append(run_v2.EnvVar(name=key, value=value))
        
        # Container specification
        container = run_v2.Container(
            image=config.image,
            ports=[run_v2.ContainerPort(container_port=config.port)],
            env=env_vars,
            resources=run_v2.ResourceRequirements(
                limits={
                    "memory": config.memory,
                    "cpu": config.cpu
                }
            )
        )
        
        # Revision template
        template = run_v2.RevisionTemplate(
            scaling=run_v2.RevisionScaling(
                min_instance_count=config.min_instances,
                max_instance_count=config.max_instances
            ),
            spec=run_v2.RevisionSpec(
                containers=[container],
                service_account=config.service_account
            )
        )
        
        # Service specification
        service = run_v2.Service(
            name=f"{self.parent}/services/{config.name}",
            spec=run_v2.ServiceSpec(
                template=template
            )
        )
        
        return service
    
    def _get_service(self, service_name: str) -> Optional[Any]:
        """Get service by full name."""
        try:
            return self.client.get_service(name=service_name)
        except gcp_exceptions.NotFound:
            return None
        except gcp_exceptions.GoogleAPIError as e:
            logger.error(f"Error getting service {service_name}: {e}")
            return None
    
    def _get_traffic_allocation(self, service: Any) -> Dict[str, int]:
        """Extract traffic allocation from service."""
        traffic_allocation = {}
        if hasattr(service, 'spec') and hasattr(service.spec, 'traffic'):
            for traffic in service.spec.traffic:
                if hasattr(traffic, 'revision') and hasattr(traffic, 'percent'):
                    traffic_allocation[traffic.revision] = traffic.percent
        return traffic_allocation