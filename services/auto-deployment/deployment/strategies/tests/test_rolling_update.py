"""
Tests for Rolling Update deployment strategy.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from rolling_update import RollingUpdateDeploymentStrategy
from base import DeploymentConfig, DeploymentStatus, DeploymentResult


class TestRollingUpdateDeploymentStrategy:
    """Test Rolling Update deployment strategy."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = DeploymentConfig(
            service_name="test-service",
            project_id="test-project",
            region="us-central1",
            image_url="gcr.io/test-project/test-service:latest",
            environment="production"
        )
        self.strategy = RollingUpdateDeploymentStrategy(self.config)
    
    def test_initialization(self):
        """Test strategy initialization."""
        assert self.strategy.config == self.config
        assert self.strategy.current_revision is None
        assert self.strategy.new_revision is None
        assert self.strategy.old_revision is None
        assert self.strategy.traffic_steps == [10, 25, 50, 75, 100]
    
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_successful_deployment(self, mock_sleep):
        """Test successful Rolling Update deployment."""
        # Mock current status to simulate existing revision
        mock_current_status = DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Current service running",
            timestamp=datetime.now(),
            revision_name="test-service-old-123"
        )
        
        with patch.object(self.strategy, 'get_current_status', return_value=mock_current_status):
            result = self.strategy.deploy()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert "Rolling update deployment completed successfully" in result.message
        assert result.revision_name is not None
        assert result.traffic_allocation[result.revision_name] == 100
        assert result.rollback_revision == "test-service-old-123"
        assert result.metadata["strategy"] == "rolling-update"
        assert "deployment_time" in result.metadata
        assert result.metadata["traffic_steps"] == [10, 25, 50, 75, 100]
        
        # Check that revisions are set correctly
        assert self.strategy.old_revision == "test-service-old-123"
        assert self.strategy.new_revision is not None
        assert self.strategy.current_revision == self.strategy.new_revision
    
    @patch('time.sleep')
    def test_deployment_with_traffic_update_failure(self, mock_sleep):
        """Test deployment with traffic update failure."""
        # Mock traffic update failure
        failed_traffic_result = DeploymentResult(
            status=DeploymentStatus.FAILED,
            message="Traffic update failed",
            timestamp=datetime.now(),
            error_details="Network error"
        )
        
        with patch.object(self.strategy, '_update_traffic_allocation', return_value=failed_traffic_result):
            result = self.strategy.deploy()
        
        assert result.status == DeploymentStatus.FAILED
        assert "Traffic update failed at 10%, rolled back" in result.message
        assert "Network error" in result.error_details
    
    @patch('time.sleep')
    def test_deployment_with_health_check_failure(self, mock_sleep):
        """Test deployment with health check failure."""
        # Mock health check failure at specific traffic level
        with patch.object(self.strategy, '_perform_health_checks_at_traffic_level', return_value=False):
            result = self.strategy.deploy()
        
        assert result.status == DeploymentStatus.FAILED
        assert "Health checks failed at 10% traffic, rolled back" in result.message
        assert "Health checks failed at traffic level 10%" in result.error_details
    
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
        strategy = RollingUpdateDeploymentStrategy(invalid_config)
        
        result = strategy.deploy()
        
        assert result.status == DeploymentStatus.FAILED
        assert "Rolling update deployment failed" in result.message
        assert result.error_details is not None
    
    @patch('time.sleep')
    def test_successful_rollback(self, mock_sleep):
        """Test successful rollback to old revision."""
        # Set up old revision
        self.strategy.old_revision = "test-service-old-123"
        self.strategy.current_revision = "test-service-new-456"
        
        result = self.strategy.rollback()
        
        assert result.status == DeploymentStatus.ROLLED_BACK
        assert "Successfully rolled back to revision test-service-old-123" in result.message
        assert result.revision_name == "test-service-old-123"
        assert result.traffic_allocation["test-service-old-123"] == 100
        assert result.metadata["strategy"] == "rolling-update"
        assert self.strategy.current_revision == "test-service-old-123"
    
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
        """Test rollback without old revision or target."""
        # No old revision set and no deployment history
        result = self.strategy.rollback()
        
        assert result.status == DeploymentStatus.FAILED
        assert "No rollback target available" in result.message
        assert "No previous revision or rollback target specified" in result.error_details
    
    def test_rollback_with_deployment_history(self):
        """Test rollback using deployment history when no old revision."""
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
    def test_deploy_new_revision(self, mock_sleep):
        """Test deploying new revision."""
        self.strategy.old_revision = "test-service-old-123"
        
        result = self.strategy._deploy_new_revision()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert "New revision" in result.message
        assert "deployed with 10% traffic" in result.message
        assert result.revision_name is not None
        assert result.traffic_allocation[result.revision_name] == 10
        assert result.traffic_allocation["test-service-old-123"] == 90
        assert self.strategy.new_revision is not None
    
    @patch('time.sleep')
    def test_deploy_new_revision_no_old_revision(self, mock_sleep):
        """Test deploying new revision when no old revision exists."""
        result = self.strategy._deploy_new_revision()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert result.traffic_allocation[result.revision_name] == 100
    
    @patch('time.sleep')
    def test_perform_gradual_rollout_success(self, mock_sleep):
        """Test successful gradual rollout."""
        self.strategy.new_revision = "test-service-new-123"
        
        result = self.strategy._perform_gradual_rollout()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert "Gradual rollout completed successfully" in result.message
        assert result.revision_name == "test-service-new-123"
        assert result.traffic_allocation["test-service-new-123"] == 100
    
    @patch('time.sleep')
    def test_update_traffic_allocation(self, mock_sleep):
        """Test updating traffic allocation."""
        self.strategy.new_revision = "test-service-new-123"
        self.strategy.old_revision = "test-service-old-456"
        
        result = self.strategy._update_traffic_allocation(25)
        
        assert result.status == DeploymentStatus.SUCCESS
        assert "Traffic updated: 25% to new revision" in result.message
        assert result.revision_name == "test-service-new-123"
        assert result.traffic_allocation["test-service-new-123"] == 25
        assert result.traffic_allocation["test-service-old-456"] == 75
    
    @patch('time.sleep')
    def test_update_traffic_allocation_100_percent(self, mock_sleep):
        """Test updating traffic allocation to 100%."""
        self.strategy.new_revision = "test-service-new-123"
        self.strategy.old_revision = "test-service-old-456"
        
        result = self.strategy._update_traffic_allocation(100)
        
        assert result.status == DeploymentStatus.SUCCESS
        assert result.traffic_allocation["test-service-new-123"] == 100
        # Old revision should not be in traffic allocation when new revision gets 100%
        assert "test-service-old-456" not in result.traffic_allocation
    
    def test_perform_health_checks_at_traffic_level(self):
        """Test health checks at different traffic levels."""
        with patch('time.sleep'):
            # Test at low traffic level
            result_low = self.strategy._perform_health_checks_at_traffic_level(10)
            assert result_low is True
            
            # Test at high traffic level
            result_high = self.strategy._perform_health_checks_at_traffic_level(75)
            assert result_high is True
    
    @patch('time.sleep')
    def test_perform_immediate_rollback(self, mock_sleep):
        """Test immediate rollback to target revision."""
        target_revision = "test-service-rollback-123"
        
        result = self.strategy._perform_immediate_rollback(target_revision)
        
        assert result.status == DeploymentStatus.SUCCESS
        assert f"Immediate rollback to {target_revision} completed" in result.message
        assert result.revision_name == target_revision
        assert result.traffic_allocation[target_revision] == 100
    
    def test_set_traffic_steps_valid(self):
        """Test setting valid traffic steps."""
        custom_steps = [5, 20, 50, 100]
        self.strategy.set_traffic_steps(custom_steps)
        
        assert self.strategy.traffic_steps == [5, 20, 50, 100]
    
    def test_set_traffic_steps_without_100(self):
        """Test setting traffic steps without 100% (should be added automatically)."""
        custom_steps = [15, 30, 60]
        self.strategy.set_traffic_steps(custom_steps)
        
        assert self.strategy.traffic_steps == [15, 30, 60, 100]
    
    def test_set_traffic_steps_unsorted(self):
        """Test setting unsorted traffic steps (should be sorted)."""
        custom_steps = [50, 10, 100, 25]
        self.strategy.set_traffic_steps(custom_steps)
        
        assert self.strategy.traffic_steps == [10, 25, 50, 100]
    
    def test_set_traffic_steps_invalid_values(self):
        """Test setting invalid traffic steps."""
        with pytest.raises(ValueError, match="Traffic steps must be between 0 and 100"):
            self.strategy.set_traffic_steps([10, 150, 50])  # 150 is invalid
        
        with pytest.raises(ValueError, match="Traffic steps must be between 0 and 100"):
            self.strategy.set_traffic_steps([-10, 50, 100])  # -10 is invalid
        
        with pytest.raises(ValueError, match="Traffic steps must be between 0 and 100"):
            self.strategy.set_traffic_steps([])  # Empty list is invalid
    
    @patch('time.sleep')
    def test_deployment_history_tracking(self, mock_sleep):
        """Test that deployment results are added to history."""
        initial_history_length = len(self.strategy.get_deployment_history())
        
        # Perform deployment
        self.strategy.deploy()
        
        # Check history was updated
        history = self.strategy.get_deployment_history()
        assert len(history) == initial_history_length + 1
        assert history[-1].metadata["strategy"] == "rolling-update"
    
    @patch('time.sleep')
    def test_rollback_history_tracking(self, mock_sleep):
        """Test that rollback results are added to history."""
        self.strategy.old_revision = "test-service-old-123"
        initial_history_length = len(self.strategy.get_deployment_history())
        
        # Perform rollback
        self.strategy.rollback()
        
        # Check history was updated
        history = self.strategy.get_deployment_history()
        assert len(history) == initial_history_length + 1
        assert history[-1].status == DeploymentStatus.ROLLED_BACK