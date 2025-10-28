"""
Tests for base deployment strategy.
"""

import pytest
from datetime import datetime
from unittest.mock import Mock

from base import (
    DeploymentStrategy, 
    DeploymentResult, 
    DeploymentStatus, 
    DeploymentConfig
)


class MockDeploymentStrategy(DeploymentStrategy):
    """Mock implementation for testing base class."""
    
    def deploy(self) -> DeploymentResult:
        return DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Mock deployment successful",
            timestamp=datetime.now()
        )
    
    def rollback(self, target_revision=None) -> DeploymentResult:
        return DeploymentResult(
            status=DeploymentStatus.ROLLED_BACK,
            message="Mock rollback successful",
            timestamp=datetime.now()
        )
    
    def get_current_status(self) -> DeploymentResult:
        return DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Mock service running",
            timestamp=datetime.now()
        )


class TestDeploymentConfig:
    """Test DeploymentConfig class."""
    
    def test_deployment_config_creation(self):
        """Test creating deployment configuration."""
        config = DeploymentConfig(
            service_name="test-service",
            project_id="test-project",
            region="us-central1",
            image_url="gcr.io/test-project/test-service:latest",
            environment="production"
        )
        
        assert config.service_name == "test-service"
        assert config.project_id == "test-project"
        assert config.region == "us-central1"
        assert config.image_url == "gcr.io/test-project/test-service:latest"
        assert config.environment == "production"
        assert config.memory == "2Gi"  # Default value
        assert config.cpu == "2"  # Default value
    
    def test_deployment_config_with_custom_values(self):
        """Test creating deployment configuration with custom values."""
        config = DeploymentConfig(
            service_name="test-service",
            project_id="test-project", 
            region="us-central1",
            image_url="gcr.io/test-project/test-service:latest",
            environment="staging",
            memory="1Gi",
            cpu="1",
            min_instances=0,
            max_instances=50,
            timeout_seconds=600,
            traffic_split_percentage=50,
            health_check_path="/api/health",
            environment_variables={"ENV": "staging", "DEBUG": "true"}
        )
        
        assert config.memory == "1Gi"
        assert config.cpu == "1"
        assert config.min_instances == 0
        assert config.max_instances == 50
        assert config.timeout_seconds == 600
        assert config.traffic_split_percentage == 50
        assert config.health_check_path == "/api/health"
        assert config.environment_variables == {"ENV": "staging", "DEBUG": "true"}


class TestDeploymentResult:
    """Test DeploymentResult class."""
    
    def test_deployment_result_creation(self):
        """Test creating deployment result."""
        timestamp = datetime.now()
        result = DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Deployment successful",
            timestamp=timestamp,
            revision_name="test-revision-123",
            traffic_allocation={"test-revision-123": 100}
        )
        
        assert result.status == DeploymentStatus.SUCCESS
        assert result.message == "Deployment successful"
        assert result.timestamp == timestamp
        assert result.revision_name == "test-revision-123"
        assert result.traffic_allocation == {"test-revision-123": 100}
    
    def test_deployment_result_with_error(self):
        """Test creating deployment result with error details."""
        result = DeploymentResult(
            status=DeploymentStatus.FAILED,
            message="Deployment failed",
            timestamp=datetime.now(),
            error_details="Connection timeout"
        )
        
        assert result.status == DeploymentStatus.FAILED
        assert result.message == "Deployment failed"
        assert result.error_details == "Connection timeout"


class TestDeploymentStrategy:
    """Test base DeploymentStrategy class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = DeploymentConfig(
            service_name="test-service",
            project_id="test-project",
            region="us-central1", 
            image_url="gcr.io/test-project/test-service:latest",
            environment="production"
        )
        self.strategy = MockDeploymentStrategy(self.config)
    
    def test_strategy_initialization(self):
        """Test strategy initialization."""
        assert self.strategy.config == self.config
        assert len(self.strategy._deployment_history) == 0
    
    def test_validate_config_success(self):
        """Test successful configuration validation."""
        assert self.strategy.validate_config() is True
    
    def test_validate_config_missing_required_field(self):
        """Test configuration validation with missing required field."""
        config = DeploymentConfig(
            service_name="",  # Missing required field
            project_id="test-project",
            region="us-central1",
            image_url="gcr.io/test-project/test-service:latest",
            environment="production"
        )
        strategy = MockDeploymentStrategy(config)
        
        with pytest.raises(ValueError, match="Required configuration field 'service_name' is missing"):
            strategy.validate_config()
    
    def test_validate_config_invalid_traffic_percentage(self):
        """Test configuration validation with invalid traffic percentage."""
        config = DeploymentConfig(
            service_name="test-service",
            project_id="test-project",
            region="us-central1",
            image_url="gcr.io/test-project/test-service:latest",
            environment="production",
            traffic_split_percentage=150  # Invalid percentage
        )
        strategy = MockDeploymentStrategy(config)
        
        with pytest.raises(ValueError, match="Traffic split percentage must be between 0 and 100"):
            strategy.validate_config()
    
    def test_add_to_history(self):
        """Test adding deployment result to history."""
        result = DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Test deployment",
            timestamp=datetime.now()
        )
        
        self.strategy.add_to_history(result)
        history = self.strategy.get_deployment_history()
        
        assert len(history) == 1
        assert history[0] == result
    
    def test_get_last_successful_deployment(self):
        """Test getting last successful deployment."""
        # Add failed deployment
        failed_result = DeploymentResult(
            status=DeploymentStatus.FAILED,
            message="Failed deployment",
            timestamp=datetime.now()
        )
        self.strategy.add_to_history(failed_result)
        
        # Add successful deployment
        success_result = DeploymentResult(
            status=DeploymentStatus.SUCCESS,
            message="Successful deployment",
            timestamp=datetime.now(),
            revision_name="success-revision"
        )
        self.strategy.add_to_history(success_result)
        
        # Add another failed deployment
        failed_result2 = DeploymentResult(
            status=DeploymentStatus.FAILED,
            message="Another failed deployment",
            timestamp=datetime.now()
        )
        self.strategy.add_to_history(failed_result2)
        
        last_successful = self.strategy.get_last_successful_deployment()
        assert last_successful == success_result
        assert last_successful.revision_name == "success-revision"
    
    def test_get_last_successful_deployment_none(self):
        """Test getting last successful deployment when none exists."""
        # Add only failed deployments
        failed_result = DeploymentResult(
            status=DeploymentStatus.FAILED,
            message="Failed deployment",
            timestamp=datetime.now()
        )
        self.strategy.add_to_history(failed_result)
        
        last_successful = self.strategy.get_last_successful_deployment()
        assert last_successful is None
    
    def test_abstract_methods_implemented(self):
        """Test that abstract methods are properly implemented in mock."""
        # Test deploy method
        deploy_result = self.strategy.deploy()
        assert deploy_result.status == DeploymentStatus.SUCCESS
        assert deploy_result.message == "Mock deployment successful"
        
        # Test rollback method
        rollback_result = self.strategy.rollback()
        assert rollback_result.status == DeploymentStatus.ROLLED_BACK
        assert rollback_result.message == "Mock rollback successful"
        
        # Test get_current_status method
        status_result = self.strategy.get_current_status()
        assert status_result.status == DeploymentStatus.SUCCESS
        assert status_result.message == "Mock service running"