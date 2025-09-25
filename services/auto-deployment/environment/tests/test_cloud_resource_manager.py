"""
Unit tests for CloudResourceManager.

Tests the Google Cloud API client wrapper, service enablement automation,
and resource provisioning logic.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import dataclass
from typing import Dict, Any

import sys
import os

# Add the parent directories to the path to enable imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, grandparent_dir)

from cloud_resource_manager import (
    CloudResourceManager,
    GoogleCloudAPIClient,
    CloudResource,
    ResourceStatus,
    ServiceEnablementResult
)
from config import DeploymentConfig
from exceptions import CloudResourceError


@dataclass
class MockCloudConfig:
    """Mock cloud configuration for testing."""
    project_id: str = "test-project"
    region: str = "us-central1"
    service_name: str = "test-service"

@dataclass
class MockDeploymentConfig:
    """Mock deployment configuration for testing."""
    cloud_config: MockCloudConfig = None
    environment: str = "test"
    
    def __post_init__(self):
        if self.cloud_config is None:
            self.cloud_config = MockCloudConfig()


class TestGoogleCloudAPIClient:
    """Test cases for GoogleCloudAPIClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.project_id = "test-project"
        self.credentials_path = "/path/to/credentials.json"
    
    @patch('services.auto_deployment.environment.cloud_resource_manager.service_account')
    def test_load_credentials_with_file(self, mock_service_account):
        """Test loading credentials from file."""
        mock_credentials = Mock()
        mock_service_account.Credentials.from_service_account_file.return_value = mock_credentials
        
        client = GoogleCloudAPIClient(self.project_id, self.credentials_path)
        
        assert client.credentials == mock_credentials
        mock_service_account.Credentials.from_service_account_file.assert_called_once_with(
            self.credentials_path
        )
    
    @patch('services.auto_deployment.environment.cloud_resource_manager.default')
    def test_load_credentials_default(self, mock_default):
        """Test loading default credentials."""
        mock_credentials = Mock()
        mock_default.return_value = (mock_credentials, None)
        
        client = GoogleCloudAPIClient(self.project_id)
        
        assert client.credentials == mock_credentials
        mock_default.assert_called_once()
    
    @patch('services.auto_deployment.environment.cloud_resource_manager.serviceusage_v1')
    def test_get_client_serviceusage(self, mock_serviceusage):
        """Test getting service usage client."""
        mock_client = Mock()
        mock_serviceusage.ServiceUsageClient.return_value = mock_client
        
        with patch.object(GoogleCloudAPIClient, '_load_credentials', return_value=Mock()):
            client = GoogleCloudAPIClient(self.project_id)
            result = client.get_client('serviceusage')
        
        assert result == mock_client
        mock_serviceusage.ServiceUsageClient.assert_called_once()
    
    def test_get_client_caching(self):
        """Test that clients are cached properly."""
        with patch.object(GoogleCloudAPIClient, '_load_credentials', return_value=Mock()):
            with patch('services.auto_deployment.environment.cloud_resource_manager.serviceusage_v1') as mock_serviceusage:
                mock_client = Mock()
                mock_serviceusage.ServiceUsageClient.return_value = mock_client
                
                client = GoogleCloudAPIClient(self.project_id)
                
                # First call should create client
                result1 = client.get_client('serviceusage')
                # Second call should return cached client
                result2 = client.get_client('serviceusage')
                
                assert result1 == result2 == mock_client
                # Should only be called once due to caching
                mock_serviceusage.ServiceUsageClient.assert_called_once()


class TestCloudResourceManager:
    """Test cases for CloudResourceManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = MockDeploymentConfig()
        self.manager = CloudResourceManager(self.config)
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_enable_required_apis_success(self, mock_get_client):
        """Test successful API enablement."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock service already enabled
        mock_service = Mock()
        mock_service.state = 1  # ENABLED state
        mock_client.get_service.return_value = mock_service
        
        results = self.manager.enable_required_apis()
        
        assert len(results) == len(self.manager.REQUIRED_APIS)
        for result in results:
            assert isinstance(result, ServiceEnablementResult)
            assert result.enabled is True
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_enable_required_apis_needs_enabling(self, mock_get_client):
        """Test API enablement when service needs to be enabled."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock service not found (needs enabling)
        mock_client.get_service.side_effect = Exception("Service not found")
        
        # Mock successful enablement
        mock_operation = Mock()
        mock_operation.done.return_value = True
        mock_client.enable_service.return_value = mock_operation
        
        with patch.object(self.manager, '_wait_for_operation'):
            results = self.manager.enable_required_apis()
        
        assert len(results) == len(self.manager.REQUIRED_APIS)
        for result in results:
            assert isinstance(result, ServiceEnablementResult)
            assert result.enabled is True
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_provision_cloud_run_service(self, mock_get_client):
        """Test Cloud Run service provisioning."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        mock_operation = Mock()
        mock_operation.done.return_value = True
        mock_client.create_service.return_value = mock_operation
        
        service_config = {
            'name': 'test-service',
            'image': 'gcr.io/test/image',
            'memory': '1Gi',
            'cpu': '1',
            'min_instances': 0,
            'max_instances': 10,
            'env_vars': {'ENV': 'test'}
        }
        
        with patch.object(self.manager, '_wait_for_operation'):
            result = self.manager.provision_cloud_run_service(service_config)
        
        assert isinstance(result, CloudResource)
        assert result.name == 'test-service'
        assert result.resource_type == 'cloud_run_service'
        assert result.status == ResourceStatus.READY
        assert result.region == self.config.cloud_config.region
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_provision_firestore_database_exists(self, mock_get_client):
        """Test Firestore database provisioning when database exists."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock database exists
        mock_client.collections.return_value = []
        
        result = self.manager.provision_firestore_database()
        
        assert isinstance(result, CloudResource)
        assert result.name == 'firestore-database'
        assert result.resource_type == 'firestore_database'
        assert result.status == ResourceStatus.READY
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_provision_firestore_database_needs_creation(self, mock_get_client):
        """Test Firestore database provisioning when database needs creation."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock database doesn't exist
        mock_client.collections.side_effect = Exception("Database not found")
        
        result = self.manager.provision_firestore_database()
        
        assert isinstance(result, CloudResource)
        assert result.name == 'firestore-database'
        assert result.resource_type == 'firestore_database'
        assert result.status == ResourceStatus.CREATING
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_create_iam_service_account(self, mock_get_client):
        """Test IAM service account creation."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock IAM service
        mock_iam_service = Mock()
        mock_projects = Mock()
        mock_service_accounts = Mock()
        mock_create = Mock()
        
        mock_client.return_value = mock_iam_service
        mock_iam_service.projects.return_value = mock_projects
        mock_projects.serviceAccounts.return_value = mock_service_accounts
        mock_service_accounts.create.return_value = mock_create
        
        mock_response = {
            'email': 'test-account@test-project.iam.gserviceaccount.com',
            'uniqueId': '123456789'
        }
        mock_create.execute.return_value = mock_response
        
        account_config = {
            'name': 'test-account',
            'display_name': 'Test Account',
            'description': 'Test service account',
            'roles': ['roles/run.developer']
        }
        
        with patch.object(self.manager, '_assign_iam_roles'):
            result = self.manager.create_iam_service_account(account_config)
        
        assert isinstance(result, CloudResource)
        assert result.name == 'test-account'
        assert result.resource_type == 'iam_service_account'
        assert result.status == ResourceStatus.READY
        assert result.metadata['email'] == mock_response['email']
    
    def test_get_resource_status_unknown_type(self):
        """Test getting status for unknown resource type."""
        result = self.manager.get_resource_status('test', 'unknown_type')
        assert result == ResourceStatus.UNKNOWN
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_get_cloud_run_status_ready(self, mock_get_client):
        """Test getting Cloud Run service status when ready."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock service with ready condition
        mock_service = Mock()
        mock_condition = Mock()
        mock_condition.type = 'Ready'
        mock_condition.state = 'CONDITION_SUCCEEDED'
        mock_service.conditions = [mock_condition]
        mock_client.get_service.return_value = mock_service
        
        result = self.manager._get_cloud_run_status('test-service')
        assert result == ResourceStatus.READY
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_get_cloud_run_status_creating(self, mock_get_client):
        """Test getting Cloud Run service status when creating."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock service with non-ready condition
        mock_service = Mock()
        mock_condition = Mock()
        mock_condition.type = 'Ready'
        mock_condition.state = 'CONDITION_PENDING'
        mock_service.conditions = [mock_condition]
        mock_client.get_service.return_value = mock_service
        
        result = self.manager._get_cloud_run_status('test-service')
        assert result == ResourceStatus.CREATING
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_cleanup_resources(self, mock_get_client):
        """Test resource cleanup."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock successful deletion
        mock_operation = Mock()
        mock_operation.done.return_value = True
        mock_client.delete_service.return_value = mock_operation
        
        resources = [
            CloudResource(
                name='test-service',
                resource_type='cloud_run_service',
                status=ResourceStatus.READY
            )
        ]
        
        with patch.object(self.manager, '_wait_for_operation'):
            errors = self.manager.cleanup_resources(resources)
        
        assert len(errors) == 0
        mock_client.delete_service.assert_called_once()
    
    @patch.object(GoogleCloudAPIClient, 'get_client')
    def test_cleanup_resources_with_errors(self, mock_get_client):
        """Test resource cleanup with errors."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client
        
        # Mock deletion failure
        mock_client.delete_service.side_effect = Exception("Deletion failed")
        
        resources = [
            CloudResource(
                name='test-service',
                resource_type='cloud_run_service',
                status=ResourceStatus.READY
            )
        ]
        
        errors = self.manager.cleanup_resources(resources)
        
        assert len(errors) == 1
        assert "Deletion failed" in errors[0]
    
    def test_wait_for_operation_timeout(self):
        """Test operation timeout handling."""
        mock_operation = Mock()
        mock_operation.done.return_value = False
        
        with pytest.raises(CloudResourceError, match="Operation timed out"):
            self.manager._wait_for_operation(mock_operation, timeout=1)
    
    def test_wait_for_operation_success(self):
        """Test successful operation completion."""
        mock_operation = Mock()
        mock_operation.done.return_value = True
        
        # Should not raise any exception
        self.manager._wait_for_operation(mock_operation, timeout=10)


class TestIntegration:
    """Integration tests for cloud resource manager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = MockDeploymentConfig()
    
    @patch('services.auto_deployment.environment.cloud_resource_manager.serviceusage_v1')
    @patch('services.auto_deployment.environment.cloud_resource_manager.run_v2')
    def test_full_resource_provisioning_flow(self, mock_run_v2, mock_serviceusage):
        """Test complete resource provisioning workflow."""
        # Mock API enablement
        mock_service_client = Mock()
        mock_serviceusage.ServiceUsageClient.return_value = mock_service_client
        
        mock_service = Mock()
        mock_service.state = 1  # ENABLED
        mock_service_client.get_service.return_value = mock_service
        
        # Mock Cloud Run provisioning
        mock_run_client = Mock()
        mock_run_v2.ServicesClient.return_value = mock_run_client
        
        mock_operation = Mock()
        mock_operation.done.return_value = True
        mock_run_client.create_service.return_value = mock_operation
        
        with patch.object(GoogleCloudAPIClient, '_load_credentials', return_value=Mock()):
            manager = CloudResourceManager(self.config)
            
            # Enable APIs
            api_results = manager.enable_required_apis()
            assert all(result.enabled for result in api_results)
            
            # Provision Cloud Run service
            service_config = {
                'name': 'test-service',
                'image': 'gcr.io/test/image'
            }
            
            with patch.object(manager, '_wait_for_operation'):
                resource = manager.provision_cloud_run_service(service_config)
            
            assert resource.status == ResourceStatus.READY
            assert resource.name == 'test-service'


if __name__ == '__main__':
    pytest.main([__file__])