"""
Tests for Cloud Run deployment orchestrator.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ..cloud_run_deployer import (
    CloudRunDeployer,
    DeploymentConfig,
    DeploymentStatus,
    DeploymentStrategy
)
from ..cloud_run_client import CloudRunService, DeploymentResult
from ..traffic_manager import TrafficUpdateResult
from ..revision_manager import RevisionInfo, RevisionStatus, RevisionCleanupResult


class TestCloudRunDeployer:
    """Test cases for CloudRunDeployer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.project_id = "test-project"
        self.region = "us-central1"
        
        # Create deployer with mocked dependencies
        with patch('services.auto_deployment.deployment.cloud_run.cloud_run_deployer.CloudRunClient'), \
             patch('services.auto_deployment.deployment.cloud_run.cloud_run_deployer.TrafficManager'), \
             patch('services.auto_deployment.deployment.cloud_run.cloud_run_deployer.RevisionManager'):
            
            self.deployer = CloudRunDeployer(self.project_id, self.region)
            
            # Setup mocks
            self.mock_client = self.deployer.client
            self.mock_traffic_manager = self.deployer.traffic_manager
            self.mock_revision_manager = self.deployer.revision_manager
    
    def test_init(self):
        """Test deployer initialization."""
        with patch('services.auto_deployment.deployment.cloud_run.cloud_run_deployer.CloudRunClient') as mock_client_class, \
             patch('services.auto_deployment.deployment.cloud_run.cloud_run_deployer.TrafficManager') as mock_traffic_class, \
             patch('services.auto_deployment.deployment.cloud_run.cloud_run_deployer.RevisionManager') as mock_revision_class:
            
            deployer = CloudRunDeployer("test-project", "us-central1")
            
            assert deployer.project_id == "test-project"
            assert deployer.region == "us-central1"
            
            # Verify dependencies were created
            mock_client_class.assert_called_once_with("test-project", "us-central1")
            mock_traffic_class.assert_called_once()
            mock_revision_class.assert_called_once()
    
    def test_deploy_immediate_strategy_success(self):
        """Test successful deployment with immediate strategy."""
        # Setup service config
        service_config = CloudRunService(
            name="test-service",
            project_id=self.project_id,
            region=self.region,
            image="gcr.io/test-project/test-image:latest"
        )
        
        config = DeploymentConfig(
            service_config=service_config,
            strategy=DeploymentStrategy.IMMEDIATE
        )
        
        # Mock stable revision
        stable_revision = RevisionInfo(
            name="old-rev",
            service_name="test-service",
            image="gcr.io/test-project/test-image:old",
            created_time=datetime.now(),
            status=RevisionStatus.SERVING,
            traffic_percentage=100
        )
        self.mock_revision_manager.get_stable_revision.return_value = stable_revision
        
        # Mock successful deployment
        deployment_result = DeploymentResult(
            success=True,
            service_name="test-service",
            revision_name="new-rev",
            url="https://test-service-url.com",
            traffic_allocation={"new-rev": 100}
        )
        self.mock_client.deploy_service.return_value = deployment_result
        
        # Mock successful traffic update
        traffic_result = TrafficUpdateResult(
            success=True,
            current_traffic={"new-rev": 100}
        )
        self.mock_traffic_manager.update_traffic.return_value = traffic_result
        
        # Mock successful cleanup
        cleanup_result = RevisionCleanupResult(
            success=True,
            cleaned_revisions=["very-old-rev"]
        )
        self.mock_revision_manager.cleanup_old_revisions.return_value = cleanup_result
        
        # Execute deployment
        result = self.deployer.deploy(config)
        
        # Verify results
        assert result.success is True
        assert result.service_name == "test-service"
        assert result.new_revision == "new-rev"
        assert result.previous_revision == "old-rev"
        assert result.traffic_allocation == {"new-rev": 100}
        assert result.deployment_strategy == DeploymentStrategy.IMMEDIATE
        assert result.rollback_available is True
        
        # Verify method calls
        self.mock_client.deploy_service.assert_called_once_with(service_config)
        self.mock_traffic_manager.update_traffic.assert_called_once()
        self.mock_revision_manager.cleanup_old_revisions.assert_called_once()
    
    def test_deploy_canary_strategy_success(self):
        """Test successful deployment with canary strategy."""
        # Setup service config
        service_config = CloudRunService(
            name="test-service",
            project_id=self.project_id,
            region=self.region,
            image="gcr.io/test-project/test-image:latest"
        )
        
        config = DeploymentConfig(
            service_config=service_config,
            strategy=DeploymentStrategy.CANARY,
            canary_percentage=20,
            monitoring_duration=60
        )
        
        # Mock stable revision
        stable_revision = RevisionInfo(
            name="old-rev",
            service_name="test-service",
            image="gcr.io/test-project/test-image:old",
            created_time=datetime.now(),
            status=RevisionStatus.SERVING,
            traffic_percentage=100
        )
        self.mock_revision_manager.get_stable_revision.return_value = stable_revision
        
        # Mock successful deployment
        deployment_result = DeploymentResult(
            success=True,
            service_name="test-service",
            revision_name="new-rev",
            url="https://test-service-url.com",
            traffic_allocation={"new-rev": 100}
        )
        self.mock_client.deploy_service.return_value = deployment_result
        
        # Mock successful canary deployment
        traffic_result = TrafficUpdateResult(
            success=True,
            current_traffic={"new-rev": 100}
        )
        self.mock_traffic_manager.execute_canary_deployment.return_value = traffic_result
        
        # Mock cleanup
        self.mock_revision_manager.cleanup_old_revisions.return_value = RevisionCleanupResult(
            success=True, cleaned_revisions=[]
        )
        
        # Execute deployment
        result = self.deployer.deploy(config)
        
        # Verify results
        assert result.success is True
        assert result.deployment_strategy == DeploymentStrategy.CANARY
        
        # Verify canary deployment was called with correct parameters
        self.mock_traffic_manager.execute_canary_deployment.assert_called_once_with(
            "test-service", "new-rev", "old-rev", 20, 60
        )
    
    def test_deploy_blue_green_strategy_success(self):
        """Test successful deployment with blue-green strategy."""
        # Setup service config
        service_config = CloudRunService(
            name="test-service",
            project_id=self.project_id,
            region=self.region,
            image="gcr.io/test-project/test-image:latest"
        )
        
        config = DeploymentConfig(
            service_config=service_config,
            strategy=DeploymentStrategy.BLUE_GREEN
        )
        
        # Mock stable revision
        stable_revision = RevisionInfo(
            name="blue-rev",
            service_name="test-service",
            image="gcr.io/test-project/test-image:blue",
            created_time=datetime.now(),
            status=RevisionStatus.SERVING,
            traffic_percentage=100
        )
        self.mock_revision_manager.get_stable_revision.return_value = stable_revision
        
        # Mock successful deployment
        deployment_result = DeploymentResult(
            success=True,
            service_name="test-service",
            revision_name="green-rev",
            url="https://test-service-url.com",
            traffic_allocation={"green-rev": 100}
        )
        self.mock_client.deploy_service.return_value = deployment_result
        
        # Mock successful blue-green deployment
        traffic_result = TrafficUpdateResult(
            success=True,
            current_traffic={"green-rev": 100, "blue-rev": 0}
        )
        self.mock_traffic_manager.execute_blue_green_deployment.return_value = traffic_result
        
        # Mock cleanup
        self.mock_revision_manager.cleanup_old_revisions.return_value = RevisionCleanupResult(
            success=True, cleaned_revisions=[]
        )
        
        # Execute deployment
        result = self.deployer.deploy(config)
        
        # Verify results
        assert result.success is True
        assert result.deployment_strategy == DeploymentStrategy.BLUE_GREEN
        
        # Verify blue-green deployment was called with correct parameters
        self.mock_traffic_manager.execute_blue_green_deployment.assert_called_once_with(
            "test-service", "blue-rev", "green-rev", switch_to_green=True
        )
    
    def test_deploy_service_deployment_failure(self):
        """Test deployment failure during service deployment."""
        # Setup service config
        service_config = CloudRunService(
            name="test-service",
            project_id=self.project_id,
            region=self.region,
            image="gcr.io/test-project/test-image:latest"
        )
        
        config = DeploymentConfig(service_config=service_config)
        
        # Mock no stable revision
        self.mock_revision_manager.get_stable_revision.return_value = None
        
        # Mock failed deployment
        deployment_result = DeploymentResult(
            success=False,
            service_name="test-service",
            revision_name="",
            url="",
            traffic_allocation={},
            error_message="Service deployment failed"
        )
        self.mock_client.deploy_service.return_value = deployment_result
        
        # Execute deployment
        result = self.deployer.deploy(config)
        
        # Verify failure
        assert result.success is False
        assert result.error_message == "Service deployment failed"
        assert result.rollback_available is False
        
        # Verify traffic manager was not called
        self.mock_traffic_manager.update_traffic.assert_not_called()
    
    def test_deploy_traffic_update_failure(self):
        """Test deployment failure during traffic update."""
        # Setup service config
        service_config = CloudRunService(
            name="test-service",
            project_id=self.project_id,
            region=self.region,
            image="gcr.io/test-project/test-image:latest"
        )
        
        config = DeploymentConfig(service_config=service_config)
        
        # Mock stable revision
        stable_revision = RevisionInfo(
            name="old-rev",
            service_name="test-service",
            image="gcr.io/test-project/test-image:old",
            created_time=datetime.now(),
            status=RevisionStatus.SERVING,
            traffic_percentage=100
        )
        self.mock_revision_manager.get_stable_revision.return_value = stable_revision
        
        # Mock successful service deployment
        deployment_result = DeploymentResult(
            success=True,
            service_name="test-service",
            revision_name="new-rev",
            url="https://test-service-url.com",
            traffic_allocation={"new-rev": 100}
        )
        self.mock_client.deploy_service.return_value = deployment_result
        
        # Mock failed traffic update
        traffic_result = TrafficUpdateResult(
            success=False,
            current_traffic={},
            error_message="Traffic update failed"
        )
        self.mock_traffic_manager.update_traffic.return_value = traffic_result
        
        # Execute deployment
        result = self.deployer.deploy(config)
        
        # Verify failure
        assert result.success is False
        assert result.error_message == "Traffic update failed"
        assert result.new_revision == "new-rev"
        assert result.rollback_available is True
    
    def test_deploy_no_cleanup(self):
        """Test deployment without revision cleanup."""
        # Setup service config
        service_config = CloudRunService(
            name="test-service",
            project_id=self.project_id,
            region=self.region,
            image="gcr.io/test-project/test-image:latest"
        )
        
        config = DeploymentConfig(
            service_config=service_config,
            cleanup_old_revisions=False
        )
        
        # Mock no stable revision
        self.mock_revision_manager.get_stable_revision.return_value = None
        
        # Mock successful deployment
        deployment_result = DeploymentResult(
            success=True,
            service_name="test-service",
            revision_name="new-rev",
            url="https://test-service-url.com",
            traffic_allocation={"new-rev": 100}
        )
        self.mock_client.deploy_service.return_value = deployment_result
        
        # Mock successful traffic update
        traffic_result = TrafficUpdateResult(
            success=True,
            current_traffic={"new-rev": 100}
        )
        self.mock_traffic_manager.update_traffic.return_value = traffic_result
        
        # Execute deployment
        result = self.deployer.deploy(config)
        
        # Verify results
        assert result.success is True
        
        # Verify cleanup was not called
        self.mock_revision_manager.cleanup_old_revisions.assert_not_called()
    
    def test_rollback_with_target_revision(self):
        """Test rollback to specific revision."""
        # Mock successful rollback
        rollback_result = TrafficUpdateResult(
            success=True,
            current_traffic={"target-rev": 100}
        )
        self.mock_traffic_manager.rollback_traffic.return_value = rollback_result
        
        # Execute rollback
        result = self.deployer.rollback("test-service", "target-rev")
        
        # Verify results
        assert result.success is True
        assert result.service_name == "test-service"
        assert result.new_revision == "target-rev"
        assert result.traffic_allocation == {"target-rev": 100}
        
        # Verify rollback was called with correct parameters
        self.mock_traffic_manager.rollback_traffic.assert_called_once_with("test-service", "target-rev")
    
    def test_rollback_automatic_revision_selection(self):
        """Test rollback with automatic revision selection."""
        # Mock revision list with serving revisions
        serving_rev1 = RevisionInfo(
            name="current-rev",
            service_name="test-service",
            image="gcr.io/test-project/test-image:current",
            created_time=datetime.now(),
            status=RevisionStatus.SERVING,
            traffic_percentage=100
        )
        
        serving_rev2 = RevisionInfo(
            name="previous-rev",
            service_name="test-service",
            image="gcr.io/test-project/test-image:previous",
            created_time=datetime.now(),
            status=RevisionStatus.SERVING,
            traffic_percentage=0
        )
        
        self.mock_revision_manager.list_revisions.return_value = [serving_rev1, serving_rev2]
        
        # Mock successful rollback
        rollback_result = TrafficUpdateResult(
            success=True,
            current_traffic={"previous-rev": 100}
        )
        self.mock_traffic_manager.rollback_traffic.return_value = rollback_result
        
        # Execute rollback without target revision
        result = self.deployer.rollback("test-service")
        
        # Verify results
        assert result.success is True
        assert result.new_revision == "previous-rev"
        
        # Verify rollback was called with automatically selected revision
        self.mock_traffic_manager.rollback_traffic.assert_called_once_with("test-service", "previous-rev")
    
    def test_rollback_no_suitable_revision(self):
        """Test rollback when no suitable revision is found."""
        # Mock revision list with only one serving revision
        serving_rev = RevisionInfo(
            name="current-rev",
            service_name="test-service",
            image="gcr.io/test-project/test-image:current",
            created_time=datetime.now(),
            status=RevisionStatus.SERVING,
            traffic_percentage=100
        )
        
        self.mock_revision_manager.list_revisions.return_value = [serving_rev]
        
        # Execute rollback
        result = self.deployer.rollback("test-service")
        
        # Verify failure
        assert result.success is False
        assert "No suitable revision found for rollback" in result.error_message
    
    def test_get_deployment_status(self):
        """Test getting deployment status."""
        # Mock service
        mock_service = Mock()
        mock_service.uri = "https://test-service-url.com"
        self.mock_client.get_service.return_value = mock_service
        
        # Mock revisions
        rev1 = RevisionInfo(
            name="rev1",
            service_name="test-service",
            image="gcr.io/test-project/test-image:v1",
            created_time=datetime.now(),
            status=RevisionStatus.SERVING,
            traffic_percentage=100
        )
        
        rev2 = RevisionInfo(
            name="rev2",
            service_name="test-service",
            image="gcr.io/test-project/test-image:v2",
            created_time=datetime.now(),
            status=RevisionStatus.INACTIVE,
            traffic_percentage=0
        )
        
        self.mock_revision_manager.list_revisions.return_value = [rev1, rev2]
        
        # Mock traffic allocation
        self.mock_traffic_manager.get_current_traffic.return_value = {"rev1": 100}
        
        # Get deployment status
        result = self.deployer.get_deployment_status("test-service")
        
        # Verify results
        assert result["service_name"] == "test-service"
        assert result["service_url"] == "https://test-service-url.com"
        assert result["total_revisions"] == 2
        assert result["serving_revisions"] == 1
        assert result["traffic_allocation"] == {"rev1": 100}
        assert result["latest_revision"] == "rev1"
        assert result["stable_revision"] == "rev1"
        assert len(result["revisions"]) == 2
    
    def test_get_deployment_status_service_not_found(self):
        """Test getting deployment status for non-existent service."""
        self.mock_client.get_service.return_value = None
        
        result = self.deployer.get_deployment_status("non-existent-service")
        
        assert "error" in result
        assert "Service non-existent-service not found" in result["error"]


class TestDeploymentConfig:
    """Test cases for DeploymentConfig dataclass."""
    
    def test_deployment_config_creation(self):
        """Test DeploymentConfig creation with defaults."""
        service_config = CloudRunService(
            name="test-service",
            project_id="test-project",
            region="us-central1",
            image="gcr.io/test-project/test-image:latest"
        )
        
        config = DeploymentConfig(service_config=service_config)
        
        assert config.service_config == service_config
        assert config.strategy == DeploymentStrategy.IMMEDIATE
        assert config.canary_percentage == 10
        assert config.monitoring_duration == 300
        assert config.cleanup_old_revisions is True
        assert config.keep_revision_count == 5
        assert config.keep_revision_days == 30
    
    def test_deployment_config_custom_values(self):
        """Test DeploymentConfig creation with custom values."""
        service_config = CloudRunService(
            name="test-service",
            project_id="test-project",
            region="us-central1",
            image="gcr.io/test-project/test-image:latest"
        )
        
        config = DeploymentConfig(
            service_config=service_config,
            strategy=DeploymentStrategy.CANARY,
            canary_percentage=20,
            monitoring_duration=600,
            cleanup_old_revisions=False,
            keep_revision_count=10,
            keep_revision_days=60
        )
        
        assert config.strategy == DeploymentStrategy.CANARY
        assert config.canary_percentage == 20
        assert config.monitoring_duration == 600
        assert config.cleanup_old_revisions is False
        assert config.keep_revision_count == 10
        assert config.keep_revision_days == 60


class TestDeploymentStatus:
    """Test cases for DeploymentStatus dataclass."""
    
    def test_deployment_status_success(self):
        """Test successful deployment status."""
        status = DeploymentStatus(
            success=True,
            service_name="test-service",
            new_revision="new-rev",
            previous_revision="old-rev",
            traffic_allocation={"new-rev": 100},
            deployment_strategy=DeploymentStrategy.IMMEDIATE,
            rollback_available=True
        )
        
        assert status.success is True
        assert status.service_name == "test-service"
        assert status.new_revision == "new-rev"
        assert status.previous_revision == "old-rev"
        assert status.traffic_allocation == {"new-rev": 100}
        assert status.deployment_strategy == DeploymentStrategy.IMMEDIATE
        assert status.error_message is None
        assert status.rollback_available is True
    
    def test_deployment_status_failure(self):
        """Test failed deployment status."""
        status = DeploymentStatus(
            success=False,
            service_name="test-service",
            new_revision="",
            previous_revision=None,
            traffic_allocation={},
            deployment_strategy=DeploymentStrategy.IMMEDIATE,
            error_message="Deployment failed",
            rollback_available=False
        )
        
        assert status.success is False
        assert status.service_name == "test-service"
        assert status.new_revision == ""
        assert status.previous_revision is None
        assert status.traffic_allocation == {}
        assert status.deployment_strategy == DeploymentStrategy.IMMEDIATE
        assert status.error_message == "Deployment failed"
        assert status.rollback_available is False