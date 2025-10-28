"""
Integration tests for deployment strategies.
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from base import DeploymentConfig, DeploymentStatus
from blue_green import BlueGreenDeploymentStrategy
from rolling_update import RollingUpdateDeploymentStrategy


class TestDeploymentStrategiesIntegration:
    """Integration tests for deployment strategies."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = DeploymentConfig(
            service_name="integration-test-service",
            project_id="test-project",
            region="us-central1",
            image_url="gcr.io/test-project/integration-test-service:latest",
            environment="production",
            memory="1Gi",
            cpu="1",
            min_instances=1,
            max_instances=10,
            timeout_seconds=300,
            health_check_path="/health",
            environment_variables={"ENV": "production", "LOG_LEVEL": "info"}
        )
    
    @patch('time.sleep')
    def test_blue_green_full_deployment_cycle(self, mock_sleep):
        """Test complete Blue-Green deployment cycle."""
        strategy = BlueGreenDeploymentStrategy(self.config)
        
        # Initial deployment
        deploy_result = strategy.deploy()
        assert deploy_result.status == DeploymentStatus.SUCCESS
        assert deploy_result.revision_name is not None
        assert deploy_result.traffic_allocation[deploy_result.revision_name] == 100
        
        # Store the deployed revision for rollback test
        deployed_revision = deploy_result.revision_name
        rollback_revision = deploy_result.rollback_revision
        
        # Test rollback
        rollback_result = strategy.rollback()
        assert rollback_result.status == DeploymentStatus.ROLLED_BACK
        assert rollback_result.revision_name == rollback_revision
        
        # Check deployment history
        history = strategy.get_deployment_history()
        assert len(history) == 2  # Deploy + Rollback
        assert history[0].status == DeploymentStatus.SUCCESS
        assert history[1].status == DeploymentStatus.ROLLED_BACK
    
    @patch('time.sleep')
    def test_rolling_update_full_deployment_cycle(self, mock_sleep):
        """Test complete Rolling Update deployment cycle."""
        strategy = RollingUpdateDeploymentStrategy(self.config)
        
        # Initial deployment
        deploy_result = strategy.deploy()
        assert deploy_result.status == DeploymentStatus.SUCCESS
        assert deploy_result.revision_name is not None
        assert deploy_result.traffic_allocation[deploy_result.revision_name] == 100
        
        # Store the deployed revision for rollback test
        deployed_revision = deploy_result.revision_name
        rollback_revision = deploy_result.rollback_revision
        
        # Test rollback
        rollback_result = strategy.rollback()
        assert rollback_result.status == DeploymentStatus.ROLLED_BACK
        assert rollback_result.revision_name == rollback_revision
        
        # Check deployment history
        history = strategy.get_deployment_history()
        assert len(history) == 2  # Deploy + Rollback
        assert history[0].status == DeploymentStatus.SUCCESS
        assert history[1].status == DeploymentStatus.ROLLED_BACK
    
    @patch('time.sleep')
    def test_strategy_comparison(self, mock_sleep):
        """Test comparison between Blue-Green and Rolling Update strategies."""
        blue_green = BlueGreenDeploymentStrategy(self.config)
        rolling_update = RollingUpdateDeploymentStrategy(self.config)
        
        # Deploy with both strategies
        bg_result = blue_green.deploy()
        ru_result = rolling_update.deploy()
        
        # Both should succeed
        assert bg_result.status == DeploymentStatus.SUCCESS
        assert ru_result.status == DeploymentStatus.SUCCESS
        
        # Check metadata differences
        assert bg_result.metadata["strategy"] == "blue-green"
        assert ru_result.metadata["strategy"] == "rolling-update"
        
        # Rolling update should have traffic steps in metadata
        assert "traffic_steps" in ru_result.metadata
        assert "blue_revision" in bg_result.metadata
        assert "green_revision" in bg_result.metadata
    
    def test_configuration_validation_across_strategies(self):
        """Test configuration validation works consistently across strategies."""
        # Test with invalid configuration
        invalid_config = DeploymentConfig(
            service_name="",  # Invalid
            project_id="test-project",
            region="us-central1",
            image_url="gcr.io/test-project/test-service:latest",
            environment="production",
            traffic_split_percentage=150  # Invalid
        )
        
        blue_green = BlueGreenDeploymentStrategy(invalid_config)
        rolling_update = RollingUpdateDeploymentStrategy(invalid_config)
        
        # Both strategies should fail validation
        bg_result = blue_green.deploy()
        ru_result = rolling_update.deploy()
        
        assert bg_result.status == DeploymentStatus.FAILED
        assert ru_result.status == DeploymentStatus.FAILED
        assert "deployment failed" in bg_result.message.lower()
        assert "deployment failed" in ru_result.message.lower()
    
    @patch('time.sleep')
    def test_multiple_deployments_history_tracking(self, mock_sleep):
        """Test deployment history tracking across multiple deployments."""
        strategy = BlueGreenDeploymentStrategy(self.config)
        
        # Perform multiple deployments
        for i in range(3):
            result = strategy.deploy()
            assert result.status == DeploymentStatus.SUCCESS
        
        # Check history
        history = strategy.get_deployment_history()
        assert len(history) == 3
        
        # All should be successful deployments
        for result in history:
            assert result.status == DeploymentStatus.SUCCESS
            assert result.metadata["strategy"] == "blue-green"
        
        # Test getting last successful deployment
        last_successful = strategy.get_last_successful_deployment()
        assert last_successful is not None
        assert last_successful == history[-1]  # Should be the most recent
    
    @patch('time.sleep')
    def test_rollback_to_specific_revision_across_strategies(self, mock_sleep):
        """Test rollback to specific revision works for both strategies."""
        target_revision = "specific-revision-12345"
        
        # Test Blue-Green rollback to specific revision
        bg_strategy = BlueGreenDeploymentStrategy(self.config)
        bg_rollback = bg_strategy.rollback(target_revision)
        assert bg_rollback.status == DeploymentStatus.ROLLED_BACK
        assert bg_rollback.revision_name == target_revision
        
        # Test Rolling Update rollback to specific revision
        ru_strategy = RollingUpdateDeploymentStrategy(self.config)
        ru_rollback = ru_strategy.rollback(target_revision)
        assert ru_rollback.status == DeploymentStatus.ROLLED_BACK
        assert ru_rollback.revision_name == target_revision
    
    def test_current_status_consistency(self):
        """Test that get_current_status returns consistent format across strategies."""
        blue_green = BlueGreenDeploymentStrategy(self.config)
        rolling_update = RollingUpdateDeploymentStrategy(self.config)
        
        bg_status = blue_green.get_current_status()
        ru_status = rolling_update.get_current_status()
        
        # Both should return successful status with consistent format
        assert bg_status.status == DeploymentStatus.SUCCESS
        assert ru_status.status == DeploymentStatus.SUCCESS
        assert bg_status.revision_name is not None
        assert ru_status.revision_name is not None
        assert bg_status.traffic_allocation is not None
        assert ru_status.traffic_allocation is not None
    
    @patch('time.sleep')
    def test_custom_rolling_update_traffic_steps(self, mock_sleep):
        """Test Rolling Update with custom traffic steps."""
        strategy = RollingUpdateDeploymentStrategy(self.config)
        
        # Set custom traffic steps
        custom_steps = [5, 15, 40, 70, 100]
        strategy.set_traffic_steps(custom_steps)
        
        # Deploy with custom steps
        result = strategy.deploy()
        
        assert result.status == DeploymentStatus.SUCCESS
        assert result.metadata["traffic_steps"] == custom_steps
    
    def test_error_handling_consistency(self):
        """Test that error handling is consistent across strategies."""
        # Create config that will cause deployment errors
        error_config = DeploymentConfig(
            service_name="error-test-service",
            project_id="",  # This will cause validation error
            region="us-central1",
            image_url="gcr.io/test-project/error-test-service:latest",
            environment="production"
        )
        
        blue_green = BlueGreenDeploymentStrategy(error_config)
        rolling_update = RollingUpdateDeploymentStrategy(error_config)
        
        bg_result = blue_green.deploy()
        ru_result = rolling_update.deploy()
        
        # Both should fail with similar error structure
        assert bg_result.status == DeploymentStatus.FAILED
        assert ru_result.status == DeploymentStatus.FAILED
        assert bg_result.error_details is not None
        assert ru_result.error_details is not None
        assert bg_result.timestamp is not None
        assert ru_result.timestamp is not None