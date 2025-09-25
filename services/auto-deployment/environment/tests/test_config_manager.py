"""
Unit tests for ConfigurationManager.

Tests configuration loading, validation, and environment-specific settings.
"""

import pytest
import os
import tempfile
import yaml
import json
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, grandparent_dir)

from config_manager import ConfigurationManager, EnvironmentConfig, ConfigFormat
from config import Environment, DeploymentConfig
from exceptions import ConfigurationError


class TestConfigurationManager:
    """Test cases for ConfigurationManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigurationManager(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test ConfigurationManager initialization."""
        assert self.config_manager.config_dir == Path(self.temp_dir)
        assert os.path.exists(self.temp_dir)
        assert hasattr(self.config_manager, 'logger')
        assert hasattr(self.config_manager, '_config_cache')
    
    def test_get_default_config_development(self):
        """Test default configuration for development environment."""
        config = self.config_manager._get_default_config(Environment.DEVELOPMENT)
        
        assert config.name == "development"
        assert config.min_instances == 0
        assert config.max_instances == 5
        assert config.memory == "1Gi"
        assert config.cpu == "1"
        assert config.enable_security_scan is False
        assert config.min_test_coverage == 0.7
    
    def test_get_default_config_staging(self):
        """Test default configuration for staging environment."""
        config = self.config_manager._get_default_config(Environment.STAGING)
        
        assert config.name == "staging"
        assert config.min_instances == 1
        assert config.max_instances == 10
        assert config.memory == "2Gi"
        assert config.cpu == "2"
        assert config.enable_security_scan is True
        assert config.min_test_coverage == 0.8
    
    def test_get_default_config_production(self):
        """Test default configuration for production environment."""
        config = self.config_manager._get_default_config(Environment.PRODUCTION)
        
        assert config.name == "production"
        assert config.min_instances == 5
        assert config.max_instances == 1000
        assert config.memory == "4Gi"
        assert config.cpu == "4"
        assert config.enable_security_scan is True
        assert config.min_test_coverage == 0.9
    
    def test_load_config_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        # Create test YAML file
        config_data = {
            "development": {
                "project_id": "test-project-dev",
                "region": "us-west1",
                "memory": "512Mi",
                "min_instances": 0,
                "max_instances": 3
            }
        }
        
        config_file = Path(self.temp_dir) / "development.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(config_data, f)
        
        # Load configuration
        result = self.config_manager._load_config_from_files(Environment.DEVELOPMENT)
        
        assert result is not None
        assert result["project_id"] == "test-project-dev"
        assert result["region"] == "us-west1"
        assert result["memory"] == "512Mi"
        assert result["min_instances"] == 0
        assert result["max_instances"] == 3
    
    def test_load_config_from_json_file(self):
        """Test loading configuration from JSON file."""
        # Create test JSON file
        config_data = {
            "staging": {
                "project_id": "test-project-staging",
                "service_name": "test-service",
                "cpu": "1.5"
            }
        }
        
        config_file = Path(self.temp_dir) / "staging.json"
        with open(config_file, 'w') as f:
            json.dump(config_data, f)
        
        # Load configuration
        result = self.config_manager._load_config_from_files(Environment.STAGING)
        
        assert result is not None
        assert result["project_id"] == "test-project-staging"
        assert result["service_name"] == "test-service"
        assert result["cpu"] == "1.5"
    
    @patch.dict(os.environ, {
        'DEVELOPMENT_PROJECT_ID': 'env-project-dev',
        'DEVELOPMENT_REGION': 'europe-west1',
        'DEVELOPMENT_MIN_INSTANCES': '0',
        'DEVELOPMENT_MAX_INSTANCES': '2',
        'DEVELOPMENT_ENABLE_SECURITY_SCAN': 'false'
    })
    def test_load_config_from_env_variables(self):
        """Test loading configuration from environment variables."""
        result = self.config_manager._load_config_from_env(Environment.DEVELOPMENT)
        
        assert result is not None
        assert result["project_id"] == "env-project-dev"
        assert result["region"] == "europe-west1"
        assert result["min_instances"] == 0
        assert result["max_instances"] == 2
        assert result["enable_security_scan"] is False
    
    @patch.dict(os.environ, {
        'GCP_PROJECT_ID': 'fallback-project',
        'GCP_REGION': 'asia-east1'
    })
    def test_load_config_from_generic_env_variables(self):
        """Test loading configuration from generic environment variables."""
        result = self.config_manager._load_config_from_env(Environment.DEVELOPMENT)
        
        assert result is not None
        assert result["project_id"] == "fallback-project"
        assert result["region"] == "asia-east1"
    
    def test_convert_env_value_boolean(self):
        """Test environment value conversion for boolean types."""
        assert self.config_manager._convert_env_value("true", "enable_security_scan") is True
        assert self.config_manager._convert_env_value("false", "enable_security_scan") is False
        assert self.config_manager._convert_env_value("1", "enable_security_scan") is True
        assert self.config_manager._convert_env_value("0", "enable_security_scan") is False
        assert self.config_manager._convert_env_value("yes", "enable_security_scan") is True
        assert self.config_manager._convert_env_value("no", "enable_security_scan") is False
    
    def test_convert_env_value_integer(self):
        """Test environment value conversion for integer types."""
        assert self.config_manager._convert_env_value("5", "min_instances") == 5
        assert self.config_manager._convert_env_value("100", "max_instances") == 100
        
        # Test invalid integer
        result = self.config_manager._convert_env_value("invalid", "min_instances")
        assert result == "invalid"  # Should return original value on error
    
    def test_convert_env_value_float(self):
        """Test environment value conversion for float types."""
        assert self.config_manager._convert_env_value("0.8", "min_test_coverage") == 0.8
        assert self.config_manager._convert_env_value("0.95", "min_test_coverage") == 0.95
        
        # Test invalid float
        result = self.config_manager._convert_env_value("invalid", "min_test_coverage")
        assert result == "invalid"  # Should return original value on error
    
    def test_merge_configs(self):
        """Test configuration merging."""
        base_config = EnvironmentConfig(
            name="test",
            project_id="base-project",
            region="us-central1",
            service_name="base-service",
            memory="1Gi",
            env_vars={"BASE_VAR": "base_value"}
        )
        
        override_data = {
            "project_id": "override-project",
            "memory": "2Gi",
            "min_instances": 2,
            "env_vars": {"OVERRIDE_VAR": "override_value"},
            "email_recipients": "user1@example.com,user2@example.com"
        }
        
        result = self.config_manager._merge_configs(base_config, override_data)
        
        assert result.project_id == "override-project"
        assert result.memory == "2Gi"
        assert result.min_instances == 2
        assert result.region == "us-central1"  # Should keep base value
        assert result.env_vars["BASE_VAR"] == "base_value"
        assert result.env_vars["OVERRIDE_VAR"] == "override_value"
        assert result.email_recipients == ["user1@example.com", "user2@example.com"]
    
    def test_validate_config_success(self):
        """Test successful configuration validation."""
        config = EnvironmentConfig(
            name="test",
            project_id="valid-project",
            region="us-central1",
            service_name="valid-service",
            memory="2Gi",
            cpu="2",
            min_instances=1,
            max_instances=10,
            min_test_coverage=0.8
        )
        
        # Should not raise any exception
        self.config_manager._validate_config(config)
    
    def test_validate_config_missing_required_fields(self):
        """Test configuration validation with missing required fields."""
        config = EnvironmentConfig(
            name="test",
            project_id="",  # Empty project ID
            region="us-central1",
            service_name="valid-service"
        )
        
        with pytest.raises(ConfigurationError, match="project_id is required"):
            self.config_manager._validate_config(config)
    
    def test_validate_config_invalid_instances(self):
        """Test configuration validation with invalid instance counts."""
        config = EnvironmentConfig(
            name="test",
            project_id="valid-project",
            region="us-central1",
            service_name="valid-service",
            min_instances=10,
            max_instances=5  # max < min
        )
        
        with pytest.raises(ConfigurationError, match="max_instances must be > min_instances"):
            self.config_manager._validate_config(config)
    
    def test_validate_config_invalid_test_coverage(self):
        """Test configuration validation with invalid test coverage."""
        config = EnvironmentConfig(
            name="test",
            project_id="valid-project",
            region="us-central1",
            service_name="valid-service",
            min_test_coverage=1.5  # > 1.0
        )
        
        with pytest.raises(ConfigurationError, match="min_test_coverage must be between 0.0 and 1.0"):
            self.config_manager._validate_config(config)
    
    def test_validate_memory_format(self):
        """Test memory format validation."""
        assert self.config_manager._validate_memory_format("1Gi") is True
        assert self.config_manager._validate_memory_format("512Mi") is True
        assert self.config_manager._validate_memory_format("2.5Gi") is True
        assert self.config_manager._validate_memory_format("1Ti") is True
        
        assert self.config_manager._validate_memory_format("1G") is False
        assert self.config_manager._validate_memory_format("invalid") is False
        assert self.config_manager._validate_memory_format("") is False
    
    def test_validate_cpu_format(self):
        """Test CPU format validation."""
        assert self.config_manager._validate_cpu_format("1") is True
        assert self.config_manager._validate_cpu_format("2") is True
        assert self.config_manager._validate_cpu_format("0.5") is True
        assert self.config_manager._validate_cpu_format("1000m") is True
        assert self.config_manager._validate_cpu_format("500m") is True
        
        assert self.config_manager._validate_cpu_format("1.5.0") is False
        assert self.config_manager._validate_cpu_format("invalid") is False
        assert self.config_manager._validate_cpu_format("") is False
    
    def test_save_environment_config(self):
        """Test saving environment configuration to file."""
        config = EnvironmentConfig(
            name="test",
            project_id="test-project",
            region="us-central1",
            service_name="test-service",
            memory="2Gi",
            cpu="2"
        )
        
        self.config_manager.save_environment_config(Environment.DEVELOPMENT, config)
        
        # Check that file was created
        config_file = Path(self.temp_dir) / "development.yaml"
        assert config_file.exists()
        
        # Check file content
        with open(config_file, 'r') as f:
            saved_data = yaml.safe_load(f)
        
        assert saved_data["project_id"] == "test-project"
        assert saved_data["region"] == "us-central1"
        assert saved_data["service_name"] == "test-service"
        assert saved_data["memory"] == "2Gi"
        assert saved_data["cpu"] == "2"
    
    def test_list_available_configs(self):
        """Test listing available configuration files."""
        # Create test config files
        (Path(self.temp_dir) / "development.yaml").touch()
        (Path(self.temp_dir) / "staging.json").touch()
        (Path(self.temp_dir) / "production.yaml").touch()
        (Path(self.temp_dir) / "config.yaml").touch()  # Should be ignored
        
        configs = self.config_manager.list_available_configs()
        
        assert "development" in configs
        assert "staging" in configs
        assert "production" in configs
        assert "config" not in configs
    
    def test_get_deployment_config(self):
        """Test converting environment config to deployment config."""
        # Create a test environment config
        env_config = EnvironmentConfig(
            name="test",
            project_id="test-project",
            region="us-west1",
            service_name="test-service",
            memory="4Gi",
            cpu="4",
            min_instances=2,
            max_instances=20,
            enable_security_scan=True,
            min_test_coverage=0.85,
            slack_webhook_url="https://hooks.slack.com/test",
            email_recipients=["admin@example.com"]
        )
        
        # Mock the load_environment_config method
        with patch.object(self.config_manager, 'load_environment_config', return_value=env_config):
            deployment_config = self.config_manager.get_deployment_config(Environment.DEVELOPMENT)
        
        assert isinstance(deployment_config, DeploymentConfig)
        assert deployment_config.environment == Environment.DEVELOPMENT
        assert deployment_config.cloud_config.project_id == "test-project"
        assert deployment_config.cloud_config.region == "us-west1"
        assert deployment_config.cloud_config.service_name == "test-service"
        assert deployment_config.cloud_config.memory == "4Gi"
        assert deployment_config.cloud_config.cpu == "4"
        assert deployment_config.cloud_config.min_instances == 2
        assert deployment_config.cloud_config.max_instances == 20
        assert deployment_config.security_config.enable_security_scan is True
        assert deployment_config.security_config.min_test_coverage == 0.85
        assert deployment_config.notification_config.slack_webhook_url == "https://hooks.slack.com/test"
        assert deployment_config.notification_config.email_recipients == ["admin@example.com"]
    
    def test_clear_cache(self):
        """Test clearing configuration cache."""
        # Add something to cache
        self.config_manager._config_cache["test"] = Mock()
        assert len(self.config_manager._config_cache) > 0
        
        # Clear cache
        self.config_manager.clear_cache()
        assert len(self.config_manager._config_cache) == 0
    
    def test_validate_all_configs(self):
        """Test validating all available configurations."""
        # Create valid config file
        valid_config = {
            "project_id": "valid-project",
            "region": "us-central1",
            "service_name": "valid-service"
        }
        
        with open(Path(self.temp_dir) / "development.yaml", 'w') as f:
            yaml.dump(valid_config, f)
        
        # Create invalid config file
        invalid_config = {
            "project_id": "",  # Invalid
            "region": "us-central1",
            "service_name": "invalid-service"
        }
        
        with open(Path(self.temp_dir) / "staging.yaml", 'w') as f:
            yaml.dump(invalid_config, f)
        
        results = self.config_manager.validate_all_configs()
        
        assert "development" in results
        assert "staging" in results
        assert len(results["development"]) == 0  # No errors
        assert len(results["staging"]) > 0  # Has errors


if __name__ == '__main__':
    pytest.main([__file__])