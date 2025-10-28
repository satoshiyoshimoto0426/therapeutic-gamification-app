"""
Tests for Cloud Run client functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from google.api_core import exceptions as gcp_exceptions

from cloud_run_client import (
    CloudRunClient, 
    CloudRunService, 
    DeploymentResult
)


class TestCloudRunClient:
    """Test cases for CloudRunClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.project_id = "test-project"
        self.region = "us-central1"
        self.client = CloudRunClient(self.project_id, self.region)
    
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.ServicesClient')
    def test_init(self, mock_services_client):
        """Test client initialization."""
        client = CloudRunClient("test-project", "us-central1")
        assert client.project_id == "test-project"
        assert client.region == "us-central1"
        assert client.parent == "projects/test-project/locations/us-central1"
        mock_services_client.assert_called_once()
    
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.ServicesClient')
    def test_deploy_service_new_service(self, mock_services_client):
        """Test deploying a new service."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_services_client.return_value = mock_client_instance
        mock_client_instance.get_service.side_effect = gcp_exceptions.NotFound("Service not found")
        
        # Mock operation result
        mock_operation = Mock()
        mock_result = Mock()
        mock_result.uri = "https://test-service-url.com"
        mock_result.latest_ready_revision_name = "test-service-001"
        mock_result.spec.traffic = []
        mock_operation.result.return_value = mock_result
        mock_client_instance.create_service.return_value = mock_operation
        
        # Create client and service config
        client = CloudRunClient(self.project_id, self.region)
        service_config = CloudRunService(
            name="test-service",
            project_id=self.project_id,
            region=self.region,
            image="gcr.io/test-project/test-image:latest"
        )
        
        # Execute deployment
        result = client.deploy_service(service_config)
        
        # Verify results
        assert result.success is True
        assert result.service_name == "test-service"
        assert result.revision_name == "test-service-001"
        assert result.url == "https://test-service-url.com"
        assert result.error_message is None
        
        # Verify create_service was called
        mock_client_instance.create_service.assert_called_once()
    
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.ServicesClient')
    def test_deploy_service_update_existing(self, mock_services_client):
        """Test updating an existing service."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_services_client.return_value = mock_client_instance
        
        # Mock existing service
        mock_existing_service = Mock()
        mock_client_instance.get_service.return_value = mock_existing_service
        
        # Mock operation result
        mock_operation = Mock()
        mock_result = Mock()
        mock_result.uri = "https://test-service-url.com"
        mock_result.latest_ready_revision_name = "test-service-002"
        mock_result.spec.traffic = []
        mock_operation.result.return_value = mock_result
        mock_client_instance.update_service.return_value = mock_operation
        
        # Create client and service config
        client = CloudRunClient(self.project_id, self.region)
        service_config = CloudRunService(
            name="test-service",
            project_id=self.project_id,
            region=self.region,
            image="gcr.io/test-project/test-image:v2"
        )
        
        # Execute deployment
        result = client.deploy_service(service_config)
        
        # Verify results
        assert result.success is True
        assert result.service_name == "test-service"
        assert result.revision_name == "test-service-002"
        assert result.url == "https://test-service-url.com"
        
        # Verify update_service was called
        mock_client_instance.update_service.assert_called_once()
    
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.ServicesClient')
    def test_deploy_service_failure(self, mock_services_client):
        """Test deployment failure handling."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_services_client.return_value = mock_client_instance
        mock_client_instance.get_service.side_effect = gcp_exceptions.NotFound("Service not found")
        mock_client_instance.create_service.side_effect = gcp_exceptions.GoogleAPIError("Deployment failed")
        
        # Create client and service config
        client = CloudRunClient(self.project_id, self.region)
        service_config = CloudRunService(
            name="test-service",
            project_id=self.project_id,
            region=self.region,
            image="gcr.io/test-project/test-image:latest"
        )
        
        # Execute deployment
        result = client.deploy_service(service_config)
        
        # Verify failure handling
        assert result.success is False
        assert result.service_name == "test-service"
        assert result.error_message == "Deployment failed"
    
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.ServicesClient')
    def test_get_service(self, mock_services_client):
        """Test getting service details."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_services_client.return_value = mock_client_instance
        mock_service = Mock()
        mock_client_instance.get_service.return_value = mock_service
        
        # Create client
        client = CloudRunClient(self.project_id, self.region)
        
        # Get service
        result = client.get_service("test-service")
        
        # Verify result
        assert result == mock_service
        mock_client_instance.get_service.assert_called_once_with(
            name="projects/test-project/locations/us-central1/services/test-service"
        )
    
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.ServicesClient')
    def test_get_service_not_found(self, mock_services_client):
        """Test getting non-existent service."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_services_client.return_value = mock_client_instance
        mock_client_instance.get_service.side_effect = gcp_exceptions.NotFound("Service not found")
        
        # Create client
        client = CloudRunClient(self.project_id, self.region)
        
        # Get service
        result = client.get_service("non-existent-service")
        
        # Verify result
        assert result is None
    
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.ServicesClient')
    def test_list_services(self, mock_services_client):
        """Test listing services."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_services_client.return_value = mock_client_instance
        
        mock_service1 = Mock()
        mock_service1.name = "projects/test-project/locations/us-central1/services/service1"
        mock_service2 = Mock()
        mock_service2.name = "projects/test-project/locations/us-central1/services/service2"
        
        mock_client_instance.list_services.return_value = [mock_service1, mock_service2]
        
        # Create client
        client = CloudRunClient(self.project_id, self.region)
        
        # List services
        result = client.list_services()
        
        # Verify result
        assert result == ["service1", "service2"]
        mock_client_instance.list_services.assert_called_once_with(
            parent="projects/test-project/locations/us-central1"
        )
    
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.ServicesClient')
    def test_delete_service(self, mock_services_client):
        """Test deleting a service."""
        # Setup mocks
        mock_client_instance = Mock()
        mock_services_client.return_value = mock_client_instance
        mock_operation = Mock()
        mock_operation.result.return_value = None
        mock_client_instance.delete_service.return_value = mock_operation
        
        # Create client
        client = CloudRunClient(self.project_id, self.region)
        
        # Delete service
        result = client.delete_service("test-service")
        
        # Verify result
        assert result is True
        mock_client_instance.delete_service.assert_called_once_with(
            name="projects/test-project/locations/us-central1/services/test-service"
        )
    
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.RevisionsClient')
    @patch('services.auto_deployment.deployment.cloud_run.cloud_run_client.run_v2.ServicesClient')
    def test_get_service_revisions(self, mock_services_client, mock_revisions_client):
        """Test getting service revisions."""
        # Setup mocks
        mock_revisions_instance = Mock()
        mock_revisions_client.return_value = mock_revisions_instance
        
        mock_revision1 = Mock()
        mock_revision1.name = "projects/test-project/locations/us-central1/services/test-service/revisions/rev1"
        mock_revision2 = Mock()
        mock_revision2.name = "projects/test-project/locations/us-central1/services/test-service/revisions/rev2"
        
        mock_revisions_instance.list_revisions.return_value = [mock_revision1, mock_revision2]
        
        # Create client
        client = CloudRunClient(self.project_id, self.region)
        
        # Get revisions
        result = client.get_service_revisions("test-service")
        
        # Verify result
        assert result == ["rev1", "rev2"]
        mock_revisions_instance.list_revisions.assert_called_once_with(
            parent="projects/test-project/locations/us-central1/services/test-service"
        )


class TestCloudRunService:
    """Test cases for CloudRunService dataclass."""
    
    def test_cloud_run_service_creation(self):
        """Test CloudRunService creation with defaults."""
        service = CloudRunService(
            name="test-service",
            project_id="test-project",
            region="us-central1",
            image="gcr.io/test-project/test-image:latest"
        )
        
        assert service.name == "test-service"
        assert service.project_id == "test-project"
        assert service.region == "us-central1"
        assert service.image == "gcr.io/test-project/test-image:latest"
        assert service.memory == "2Gi"
        assert service.cpu == "2"
        assert service.min_instances == 1
        assert service.max_instances == 100
        assert service.port == 8080
        assert service.env_vars == {}
        assert service.service_account is None
    
    def test_cloud_run_service_with_custom_values(self):
        """Test CloudRunService creation with custom values."""
        env_vars = {"ENV": "production", "DEBUG": "false"}
        service = CloudRunService(
            name="prod-service",
            project_id="prod-project",
            region="us-east1",
            image="gcr.io/prod-project/prod-image:v1.0.0",
            memory="4Gi",
            cpu="4",
            min_instances=2,
            max_instances=50,
            port=3000,
            env_vars=env_vars,
            service_account="prod-service-account@prod-project.iam.gserviceaccount.com"
        )
        
        assert service.name == "prod-service"
        assert service.memory == "4Gi"
        assert service.cpu == "4"
        assert service.min_instances == 2
        assert service.max_instances == 50
        assert service.port == 3000
        assert service.env_vars == env_vars
        assert service.service_account == "prod-service-account@prod-project.iam.gserviceaccount.com"


class TestDeploymentResult:
    """Test cases for DeploymentResult dataclass."""
    
    def test_deployment_result_success(self):
        """Test successful deployment result."""
        result = DeploymentResult(
            success=True,
            service_name="test-service",
            revision_name="test-service-001",
            url="https://test-service-url.com",
            traffic_allocation={"test-service-001": 100}
        )
        
        assert result.success is True
        assert result.service_name == "test-service"
        assert result.revision_name == "test-service-001"
        assert result.url == "https://test-service-url.com"
        assert result.traffic_allocation == {"test-service-001": 100}
        assert result.error_message is None
    
    def test_deployment_result_failure(self):
        """Test failed deployment result."""
        result = DeploymentResult(
            success=False,
            service_name="test-service",
            revision_name="",
            url="",
            traffic_allocation={},
            error_message="Deployment failed due to invalid configuration"
        )
        
        assert result.success is False
        assert result.service_name == "test-service"
        assert result.revision_name == ""
        assert result.url == ""
        assert result.traffic_allocation == {}
        assert result.error_message == "Deployment failed due to invalid configuration"