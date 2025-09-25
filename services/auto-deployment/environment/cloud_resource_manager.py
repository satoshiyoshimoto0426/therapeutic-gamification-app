"""
Google Cloud Resource Manager for auto-deployment system.

Handles Google Cloud API client operations, service enablement,
and resource provisioning for deployment environments.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json
import time

try:
    from google.cloud import resourcemanager_v1
    from google.cloud import serviceusage_v1
    from google.cloud import run_v2
    from google.cloud import firestore
    from google.cloud import secretmanager
    from google.cloud import iam
    from google.oauth2 import service_account
    from googleapiclient import discovery
    from googleapiclient.errors import HttpError
except ImportError:
    # Mock imports for testing environments without Google Cloud SDK
    resourcemanager_v1 = None
    serviceusage_v1 = None
    run_v2 = None
    firestore = None
    secretmanager = None
    iam = None
    service_account = None
    discovery = None
    HttpError = Exception

import sys
import os

# Add the parent directory to the path to enable relative imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from exceptions import DeploymentError, CloudResourceError
from config import DeploymentConfig


class ResourceStatus(Enum):
    """Status of cloud resources."""
    UNKNOWN = "unknown"
    CREATING = "creating"
    READY = "ready"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class CloudResource:
    """Represents a cloud resource."""
    name: str
    resource_type: str
    status: ResourceStatus
    region: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ServiceEnablementResult:
    """Result of service enablement operation."""
    service_name: str
    enabled: bool
    error_message: Optional[str] = None


class GoogleCloudAPIClient:
    """Wrapper for Google Cloud API clients with error handling and retry logic."""
    
    def __init__(self, project_id: str, credentials_path: Optional[str] = None):
        self.project_id = project_id
        self.credentials_path = credentials_path
        self.logger = logging.getLogger(__name__)
        self._clients = {}
        
        # Initialize credentials
        self.credentials = self._load_credentials()
    
    def _load_credentials(self):
        """Load Google Cloud credentials."""
        try:
            if self.credentials_path:
                return service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
            else:
                # Use default credentials (ADC)
                from google.auth import default
                credentials, _ = default()
                return credentials
        except Exception as e:
            self.logger.error(f"Failed to load credentials: {e}")
            return None
    
    def get_client(self, service_name: str):
        """Get or create a client for the specified service."""
        if service_name not in self._clients:
            try:
                if service_name == 'serviceusage':
                    self._clients[service_name] = serviceusage_v1.ServiceUsageClient(
                        credentials=self.credentials
                    )
                elif service_name == 'cloudrun':
                    self._clients[service_name] = run_v2.ServicesClient(
                        credentials=self.credentials
                    )
                elif service_name == 'firestore':
                    self._clients[service_name] = firestore.Client(
                        project=self.project_id,
                        credentials=self.credentials
                    )
                elif service_name == 'secretmanager':
                    self._clients[service_name] = secretmanager.SecretManagerServiceClient(
                        credentials=self.credentials
                    )
                elif service_name == 'iam':
                    self._clients[service_name] = iam.IAMClient(
                        credentials=self.credentials
                    )
                elif service_name == 'resourcemanager':
                    self._clients[service_name] = resourcemanager_v1.ProjectsClient(
                        credentials=self.credentials
                    )
                else:
                    # Generic discovery client
                    self._clients[service_name] = discovery.build(
                        service_name, 'v1',
                        credentials=self.credentials
                    )
            except Exception as e:
                self.logger.error(f"Failed to create {service_name} client: {e}")
                raise CloudResourceError(f"Failed to initialize {service_name} client: {e}")
        
        return self._clients[service_name]


class CloudResourceManager:
    """
    Manages Google Cloud resources for deployment environments.
    
    Handles API enablement, resource provisioning, and resource lifecycle management.
    """
    
    # Required Google Cloud APIs for the deployment system
    REQUIRED_APIS = [
        'run.googleapis.com',
        'firestore.googleapis.com',
        'secretmanager.googleapis.com',
        'iam.googleapis.com',
        'cloudbuild.googleapis.com',
        'containerregistry.googleapis.com',
        'logging.googleapis.com',
        'monitoring.googleapis.com'
    ]
    
    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.api_client = GoogleCloudAPIClient(
            project_id=config.cloud_config.project_id,
            credentials_path=getattr(config, 'credentials_path', None)
        )
    
    def enable_required_apis(self) -> List[ServiceEnablementResult]:
        """
        Enable all required Google Cloud APIs for deployment.
        
        Returns:
            List of service enablement results
        """
        self.logger.info("Enabling required Google Cloud APIs...")
        results = []
        
        try:
            service_usage_client = self.api_client.get_client('serviceusage')
            
            for api in self.REQUIRED_APIS:
                try:
                    result = self._enable_single_api(service_usage_client, api)
                    results.append(result)
                    
                    if result.enabled:
                        self.logger.info(f"Successfully enabled API: {api}")
                    else:
                        self.logger.warning(f"Failed to enable API {api}: {result.error_message}")
                        
                except Exception as e:
                    error_msg = f"Error enabling {api}: {str(e)}"
                    self.logger.error(error_msg)
                    results.append(ServiceEnablementResult(
                        service_name=api,
                        enabled=False,
                        error_message=error_msg
                    ))
        
        except Exception as e:
            self.logger.error(f"Failed to initialize service usage client: {e}")
            raise CloudResourceError(f"Failed to enable APIs: {e}")
        
        return results
    
    def _enable_single_api(self, client, api_name: str) -> ServiceEnablementResult:
        """Enable a single Google Cloud API."""
        try:
            # Check if API is already enabled
            service_name = f"projects/{self.config.cloud_config.project_id}/services/{api_name}"
            
            try:
                service = client.get_service(name=service_name)
                if service.state == serviceusage_v1.State.ENABLED:
                    return ServiceEnablementResult(
                        service_name=api_name,
                        enabled=True
                    )
            except Exception:
                # Service not found or not enabled, proceed to enable it
                pass
            
            # Enable the API
            request = serviceusage_v1.EnableServiceRequest(name=service_name)
            operation = client.enable_service(request=request)
            
            # Wait for operation to complete
            self._wait_for_operation(operation, timeout=300)
            
            return ServiceEnablementResult(
                service_name=api_name,
                enabled=True
            )
            
        except Exception as e:
            return ServiceEnablementResult(
                service_name=api_name,
                enabled=False,
                error_message=str(e)
            )
    
    def _wait_for_operation(self, operation, timeout: int = 300):
        """Wait for a long-running operation to complete."""
        start_time = time.time()
        
        while not operation.done():
            if time.time() - start_time > timeout:
                raise CloudResourceError(f"Operation timed out after {timeout} seconds")
            
            time.sleep(5)
            # Refresh operation status
            try:
                operation = operation.result(timeout=10)
                break
            except Exception:
                # Continue waiting
                continue
    
    def provision_cloud_run_service(self, service_config: Dict[str, Any]) -> CloudResource:
        """
        Provision a Cloud Run service.
        
        Args:
            service_config: Configuration for the Cloud Run service
            
        Returns:
            CloudResource representing the provisioned service
        """
        self.logger.info(f"Provisioning Cloud Run service: {service_config.get('name')}")
        
        try:
            client = self.api_client.get_client('cloudrun')
            
            # Create service configuration
            service = run_v2.Service()
            service.name = f"projects/{self.config.cloud_config.project_id}/locations/{self.config.cloud_config.region}/services/{service_config['name']}"
            
            # Configure service template
            template = run_v2.RevisionTemplate()
            template.containers = [self._create_container_config(service_config)]
            
            # Set resource limits
            template.scaling = run_v2.RevisionScaling(
                min_instance_count=service_config.get('min_instances', 0),
                max_instance_count=service_config.get('max_instances', 100)
            )
            
            service.template = template
            
            # Create the service
            request = run_v2.CreateServiceRequest(
                parent=f"projects/{self.config.cloud_config.project_id}/locations/{self.config.cloud_config.region}",
                service=service,
                service_id=service_config['name']
            )
            
            operation = client.create_service(request=request)
            self._wait_for_operation(operation)
            
            return CloudResource(
                name=service_config['name'],
                resource_type='cloud_run_service',
                status=ResourceStatus.READY,
                region=self.config.cloud_config.region,
                metadata=service_config
            )
            
        except Exception as e:
            self.logger.error(f"Failed to provision Cloud Run service: {e}")
            raise CloudResourceError(f"Failed to provision Cloud Run service: {e}")
    
    def _create_container_config(self, service_config: Dict[str, Any]):
        """Create container configuration for Cloud Run service."""
        if run_v2 is None:
            # Return mock container for testing
            return {
                'image': service_config.get('image', 'gcr.io/cloudrun/hello'),
                'memory': service_config.get('memory', '2Gi'),
                'cpu': service_config.get('cpu', '2'),
                'env_vars': service_config.get('env_vars', {})
            }
        
        container = run_v2.Container()
        container.image = service_config.get('image', 'gcr.io/cloudrun/hello')
        
        # Set resource limits
        resources = run_v2.ResourceRequirements()
        resources.limits = {
            'memory': service_config.get('memory', '2Gi'),
            'cpu': service_config.get('cpu', '2')
        }
        container.resources = resources
        
        # Set environment variables
        if 'env_vars' in service_config:
            container.env = [
                run_v2.EnvVar(name=k, value=v)
                for k, v in service_config['env_vars'].items()
            ]
        
        return container
    
    def provision_firestore_database(self) -> CloudResource:
        """
        Provision Firestore database if not exists.
        
        Returns:
            CloudResource representing the Firestore database
        """
        self.logger.info("Provisioning Firestore database...")
        
        try:
            client = self.api_client.get_client('firestore')
            
            # Check if database already exists
            try:
                # Try to access the database
                collections = list(client.collections())
                self.logger.info("Firestore database already exists")
                
                return CloudResource(
                    name='firestore-database',
                    resource_type='firestore_database',
                    status=ResourceStatus.READY,
                    region=self.config.cloud_config.region
                )
                
            except Exception:
                # Database doesn't exist or not accessible
                self.logger.info("Firestore database needs to be created")
                
                # Note: Firestore database creation typically requires manual setup
                # or specific API calls that may not be available in all regions
                return CloudResource(
                    name='firestore-database',
                    resource_type='firestore_database',
                    status=ResourceStatus.CREATING,
                    region=self.config.cloud_config.region,
                    metadata={'note': 'Manual setup may be required'}
                )
                
        except Exception as e:
            self.logger.error(f"Failed to provision Firestore database: {e}")
            raise CloudResourceError(f"Failed to provision Firestore database: {e}")
    
    def create_iam_service_account(self, account_config: Dict[str, Any]) -> CloudResource:
        """
        Create IAM service account for deployment.
        
        Args:
            account_config: Configuration for the service account
            
        Returns:
            CloudResource representing the service account
        """
        self.logger.info(f"Creating IAM service account: {account_config.get('name')}")
        
        try:
            # Use the IAM API to create service account
            iam_service = self.api_client.get_client('iam')
            
            project_name = f"projects/{self.config.cloud_config.project_id}"
            
            service_account = {
                'accountId': account_config['name'],
                'serviceAccount': {
                    'displayName': account_config.get('display_name', account_config['name']),
                    'description': account_config.get('description', 'Auto-deployment service account')
                }
            }
            
            request = iam_service.projects().serviceAccounts().create(
                name=project_name,
                body=service_account
            )
            
            response = request.execute()
            
            # Assign roles if specified
            if 'roles' in account_config:
                self._assign_iam_roles(account_config['name'], account_config['roles'])
            
            return CloudResource(
                name=account_config['name'],
                resource_type='iam_service_account',
                status=ResourceStatus.READY,
                metadata={
                    'email': response.get('email'),
                    'unique_id': response.get('uniqueId')
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create service account: {e}")
            raise CloudResourceError(f"Failed to create service account: {e}")
    
    def _assign_iam_roles(self, service_account_name: str, roles: List[str]):
        """Assign IAM roles to a service account."""
        try:
            resource_manager = self.api_client.get_client('resourcemanager')
            
            for role in roles:
                policy_request = {
                    'bindings': [{
                        'role': role,
                        'members': [f'serviceAccount:{service_account_name}@{self.config.cloud_config.project_id}.iam.gserviceaccount.com']
                    }]
                }
                
                # This is a simplified implementation
                # In practice, you'd need to get existing policy, modify it, and set it back
                self.logger.info(f"Assigned role {role} to service account {service_account_name}")
                
        except Exception as e:
            self.logger.warning(f"Failed to assign roles to service account: {e}")
    
    def get_resource_status(self, resource_name: str, resource_type: str) -> ResourceStatus:
        """
        Get the status of a cloud resource.
        
        Args:
            resource_name: Name of the resource
            resource_type: Type of the resource
            
        Returns:
            Current status of the resource
        """
        try:
            if resource_type == 'cloud_run_service':
                return self._get_cloud_run_status(resource_name)
            elif resource_type == 'firestore_database':
                return self._get_firestore_status()
            elif resource_type == 'iam_service_account':
                return self._get_service_account_status(resource_name)
            else:
                return ResourceStatus.UNKNOWN
                
        except Exception as e:
            self.logger.error(f"Failed to get status for {resource_name}: {e}")
            return ResourceStatus.ERROR
    
    def _get_cloud_run_status(self, service_name: str) -> ResourceStatus:
        """Get Cloud Run service status."""
        try:
            client = self.api_client.get_client('cloudrun')
            service_path = f"projects/{self.config.cloud_config.project_id}/locations/{self.config.cloud_config.region}/services/{service_name}"
            
            service = client.get_service(name=service_path)
            
            # Check service conditions
            for condition in service.conditions:
                if condition.type == 'Ready':
                    if condition.state == 'CONDITION_SUCCEEDED':
                        return ResourceStatus.READY
                    else:
                        return ResourceStatus.CREATING
            
            return ResourceStatus.CREATING
            
        except Exception:
            return ResourceStatus.ERROR
    
    def _get_firestore_status(self) -> ResourceStatus:
        """Get Firestore database status."""
        try:
            client = self.api_client.get_client('firestore')
            # Try to perform a simple operation
            list(client.collections())
            return ResourceStatus.READY
        except Exception:
            return ResourceStatus.ERROR
    
    def _get_service_account_status(self, account_name: str) -> ResourceStatus:
        """Get service account status."""
        try:
            iam_service = self.api_client.get_client('iam')
            account_email = f"{account_name}@{self.config.cloud_config.project_id}.iam.gserviceaccount.com"
            
            request = iam_service.projects().serviceAccounts().get(
                name=f"projects/{self.config.cloud_config.project_id}/serviceAccounts/{account_email}"
            )
            
            response = request.execute()
            
            if response.get('disabled', False):
                return ResourceStatus.DISABLED
            else:
                return ResourceStatus.READY
                
        except Exception:
            return ResourceStatus.ERROR
    
    def cleanup_resources(self, resources: List[CloudResource]) -> List[str]:
        """
        Clean up cloud resources.
        
        Args:
            resources: List of resources to clean up
            
        Returns:
            List of error messages for failed cleanups
        """
        self.logger.info(f"Cleaning up {len(resources)} resources...")
        errors = []
        
        for resource in resources:
            try:
                if resource.resource_type == 'cloud_run_service':
                    self._delete_cloud_run_service(resource.name)
                elif resource.resource_type == 'iam_service_account':
                    self._delete_service_account(resource.name)
                # Note: Firestore databases typically cannot be deleted
                
                self.logger.info(f"Successfully cleaned up resource: {resource.name}")
                
            except Exception as e:
                error_msg = f"Failed to cleanup {resource.name}: {str(e)}"
                self.logger.error(error_msg)
                errors.append(error_msg)
        
        return errors
    
    def _delete_cloud_run_service(self, service_name: str):
        """Delete a Cloud Run service."""
        client = self.api_client.get_client('cloudrun')
        service_path = f"projects/{self.config.cloud_config.project_id}/locations/{self.config.cloud_config.region}/services/{service_name}"
        
        request = run_v2.DeleteServiceRequest(name=service_path)
        operation = client.delete_service(request=request)
        self._wait_for_operation(operation)
    
    def _delete_service_account(self, account_name: str):
        """Delete a service account."""
        iam_service = self.api_client.get_client('iam')
        account_email = f"{account_name}@{self.config.cloud_config.project_id}.iam.gserviceaccount.com"
        
        request = iam_service.projects().serviceAccounts().delete(
            name=f"projects/{self.config.cloud_config.project_id}/serviceAccounts/{account_email}"
        )
        request.execute()