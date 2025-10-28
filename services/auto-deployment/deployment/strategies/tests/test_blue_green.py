"""
Tests for Blue-Green deployment strategy.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from blue_green import BlueGreenDeploymentStrategy
from base import DeploymentConfig, DeploymentStatus, DeploymentResult


class TestBlueGreenDeploymentStrategy:
    """Test Blue-Green deployment strategy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = DeploymentConfig(
            service_name="test-service",
            project_id="test-project",
            region="us-central1",
            image_url="gcr.io/test-project/test-service:latest",
            environment="production"
        )
        self.strategy = BlueGreenDeploymentStrategy(self.config)
    
    def test_initialization(self):
        """Test strategy initialization."""
        assert self.strategy.config == self.config
        assert self.strategy.current_revision is None
        assert self.strategy.green_revision is None
        assert self.strategy.blue_revision is None
    
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_successful_deployment(self, mock_sleep):
        """Test successful Blue-Green deployment."""
        # Mock current status to simulate existing blue revision
        mock_current_status = DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Current service running",
            timestamp=datetime.now(),
            revision_name="test-service-blue-123"
        )
        
        with patch.object(self.strategy, 'get_current_status', return_value=mock_current_status):
            result = self.strategy.deploy()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert "Blue-Green deployment completed successfully" in result.message
        assert result.revision_name is not None
        assert result.traffic_allocation[result.revision_name] == 100
        assert result.rollback_revision == "test-service-blue-123"
        assert result.metadata["strategy"] == "blue-green"
        assert "deployment_time" in result.metadata
        
        # Check that revisions are set correctly
        assert self.strategy.blue_revision == "test-service-blue-123"
        assert self.strategy.green_revision is not None
        assert self.strategy.current_revision == self.strategy.green_revision
    
    @patch('time.sleep')
    def test_deployment_with_health_check_failure(self, mock_sleep):
        """Test deployment with health check failure."""
        # Mock health check failure
        with patch.object(self.strategy, '_perform_health_checks', return_value=False):
            result = self.strategy.deploy()
        
        assert result.status == DeploymentStatus.FAILED
        assert "Health checks failed" in result.message
        assert "Green revision failed health checks" in result.error_details
    
    def test_deployment_with_validation_error(self):
        """Test deployment with configuration validation error."""
        # Create invalid config
        invalid_config = DeploymentConfig(
            service_name="",  # Invalid empty service name
            project_id="test-project",
            region="us-central1",
            image_url="gcr.io/test-project/test-service:latest",
            environment="production"
        )
        strategy = BlueGreenDeploymentStrategy(invalid_config)
        
        result = strategy.deploy()
        
        assert result.status == DeploymentStatus.FAILED
        assert "Blue-Green deployment failed" in result.message
        assert result.error_details is not None
    
    @patch('time.sleep')
    def test_successful_rollback(self, mock_sleep):
        """Test successful rollback to blue revision."""
        # Set up blue revision
        self.strategy.blue_revision = "test-service-blue-123"
        self.strategy.current_revision = "test-service-green-456"
        
        result = self.strategy.rollback()
        
        assert result.status == DeploymentStatus.ROLLED_BACK
        assert "Successfully rolled back to revision test-service-blue-123" in result.message
        assert result.revision_name == "test-service-blue-123"
        assert result.traffic_allocation["test-service-blue-123"] == 100
        assert result.metadata["strategy"] == "blue-green"
        assert self.strategy.current_revision == "test-service-blue-123"
    
    @patch('time.sleep')
    def test_rollback_to_specific_revision(self, mock_sleep):
        """Test rollback to specific target revision."""
        target_revision = "test-service-specific-789"
        
        result = self.strategy.rollback(target_revision)
        
        assert result.status == DeploymentStatus.ROLLED_BACK
        assert f"Successfully rolled back to revision {target_revision}" in result.message
        assert result.revision_name == target_revision
        assert result.traffic_allocation[target_revision] == 100
        assert self.strategy.current_revision == target_revision
    
    def test_rollback_without_target(self):
        """Test rollback without blue revision or target."""
        # No blue revision set and no deployment history
        result = self.strategy.rollback()
        
        assert result.status == DeploymentStatus.FAILED
        assert "No rollback target available" in result.message
        assert "No blue revision or rollback target specified" in result.error_details
    
    def test_rollback_with_deployment_history(self):
        """Test rollback using deployment history when no blue revision."""
        # Add successful deployment to history
        historical_result = DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Historical deployment",
            timestamp=datetime.now(),
            revision_name="test-service-historical-999",
            rollback_revision="test-service-rollback-888"
        )
        self.strategy.add_to_history(historical_result)
        
        with patch('time.sleep'):
            result = self.strategy.rollback()
        
        assert result.status == DeploymentStatus.ROLLED_BACK
        assert result.revision_name == "test-service-rollback-888"
    
    def test_get_current_status(self):
        """Test getting current deployment status."""
        result = self.strategy.get_current_status()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert "Service is running" in result.message
        assert result.revision_name is not None
        assert result.traffic_allocation is not None
    
    @patch('time.sleep')
    def test_deploy_green_revision(self, mock_sleep):
        """Test deploying green revision."""
        result = self.strategy._deploy_green_revision()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert "Green revision" in result.message
        assert "deployed successfully" in result.message
        assert result.revision_name is not None
        assert result.traffic_allocation[result.revision_name] == 0
        assert self.strategy.green_revision is not None
    
    def test_perform_health_checks(self):
        """Test health check performance."""
        with patch('time.sleep'):
            result = self.strategy._perform_health_checks()
        
        # Default implementation should return True
        assert result is True
    
    @patch('time.sleep')
    def test_switch_traffic_to_green(self, mock_sleep):
        """Test switching traffic to green revision."""
        self.strategy.green_revision = "test-service-green-123"
        
        result = self.strategy._switch_traffic_to_green()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert "Traffic switched to green revision" in result.message
        assert result.revision_name == "test-service-green-123"
        assert result.traffic_allocation["test-service-green-123"] == 100
    
    @patch('time.sleep')
    def test_switch_traffic_to_revision(self, mock_sleep):
        """Test switching traffic to specific revision."""
        revision_name = "test-service-specific-456"
        
        result = self.strategy._switch_traffic_to_revision(revision_name)
        
        assert result.status == DeploymentStatus.SUCCESS
        assert f"Traffic switched to revision {revision_name}" in result.message
        assert result.revision_name == revision_name
        assert result.traffic_allocation[revision_name] == 100
    
    def test_cleanup_failed_deployment(self):
        """Test cleanup of failed deployment."""
        result = self.strategy._cleanup_failed_deployment()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert "Failed green revision cleaned up" in result.message
    
    @patch('time.sleep')
    def test_deployment_history_tracking(self, mock_sleep):
        """Test that deployment results are added to history."""
        initial_history_length = len(self.strategy.get_deployment_history())
        
        # Perform deployment
        self.strategy.deploy()
        
        # Check history was updated
        history = self.strategy.get_deployment_history()
        assert len(history) == initial_history_length + 1
        assert history[-1].metadata["strategy"] == "blue-green"
    
    @patch('time.sleep')
    def test_rollback_history_tracking(self, mock_sleep):
        """Test that rollback results are added to history."""
        self.strategy.blue_revision = "test-service-blue-123"
        initial_history_length = len(self.strategy.get_deployment_history())
        
        # Perform rollback
        self.strategy.rollback()
        
        # Check history was updated
        history = self.strategy.get_deployment_history()
        assert len(history) == initial_history_length + 1
        assert history[-1].status == DeploymentStatus.ROLLED_BACK