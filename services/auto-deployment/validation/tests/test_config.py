"""
Tests for validation configuration.
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path

from ..config import ValidationConfig, DEFAULT_CONFIG


class TestValidationConfig:
    """Test ValidationConfig class."""
    
    def test_default_initialization(self):
        """Test default configuration initialization."""
        config = ValidationConfig()
        
        assert config.enabled is True
        assert config.fail_fast is False
        assert config.parallel_execution is True
        assert config.timeout_seconds == 300
        assert isinstance(config.validator_configs, dict)
        assert isinstance(config.enabled_categories, list)
        assert isinstance(config.environment_configs, dict)
    
    def test_get_validator_config(self):
        """Test getting validator-specific configuration."""
        config = ValidationConfig()
        config.validator_configs = {
            "TestValidator": {"enabled": True, "param": "value"}
        }
        
        validator_config = config.get_validator_config("TestValidator")
        assert validator_config == {"enabled": True, "param": "value"}
        
        # Test non-existent validator
        empty_config = config.get_validator_config("NonExistentValidator")
        assert empty_config == {}
    
    def test_get_environment_config(self):
        """Test getting environment-specific configuration."""
        config = ValidationConfig()
        config.environment_configs = {
            "production": {"strict": True}
        }
        
        env_config = config.get_environment_config("production")
        assert env_config == {"strict": True}
        
        # Test non-existent environment
        empty_config = config.get_environment_config("nonexistent")
        assert empty_config == {}
    
    def test_is_validator_enabled(self):
        """Test validator enabled check."""
        config = ValidationConfig()
        config.validator_configs = {
            "EnabledValidator": {"enabled": True},
            "DisabledValidator": {"enabled": False}
        }
        
        assert config.is_validator_enabled("EnabledValidator") is True
        assert config.is_validator_enabled("DisabledValidator") is False
        assert config.is_validator_enabled("DefaultValidator") is True  # Default is enabled
    
    def test_is_category_enabled(self):
        """Test category enabled check."""
        config = ValidationConfig()
        config.enabled_categories = ["security", "code_quality"]
        
        assert config.is_category_enabled("security") is True
        assert config.is_category_enabled("code_quality") is True
        assert config.is_category_enabled("disabled_category") is False
    
    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = ValidationConfig(
            enabled=True,
            fail_fast=True,
            timeout_seconds=600
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["enabled"] is True
        assert config_dict["fail_fast"] is True
        assert config_dict["timeout_seconds"] == 600
        assert "validator_configs" in config_dict
        assert "enabled_categories" in config_dict
        assert "environment_configs" in config_dict
    
    def test_from_json_file(self):
        """Test loading configuration from JSON file."""
        config_data = {
            "enabled": False,
            "fail_fast": True,
            "timeout_seconds": 600,
            "validator_configs": {
                "TestValidator": {"enabled": True}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = ValidationConfig.from_file(temp_path)
            
            assert config.enabled is False
            assert config.fail_fast is True
            assert config.timeout_seconds == 600
            assert config.validator_configs == {"TestValidator": {"enabled": True}}
        finally:
            Path(temp_path).unlink()
    
    def test_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        config_data = {
            "enabled": False,
            "fail_fast": True,
            "timeout_seconds": 600,
            "validator_configs": {
                "TestValidator": {"enabled": True}
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            temp_path = f.name
        
        try:
            config = ValidationConfig.from_file(temp_path)
            
            assert config.enabled is False
            assert config.fail_fast is True
            assert config.timeout_seconds == 600
            assert config.validator_configs == {"TestValidator": {"enabled": True}}
        finally:
            Path(temp_path).unlink()
    
    def test_from_nonexistent_file(self):
        """Test loading configuration from non-existent file."""
        config = ValidationConfig.from_file("nonexistent.json")
        
        # Should return default configuration
        assert config.enabled is True
        assert config.fail_fast is False
        assert config.parallel_execution is True
    
    def test_save_to_json_file(self):
        """Test saving configuration to JSON file."""
        config = ValidationConfig(
            enabled=False,
            fail_fast=True,
            timeout_seconds=600
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        
        try:
            config.save_to_file(temp_path)
            
            # Load and verify
            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["enabled"] is False
            assert saved_data["fail_fast"] is True
            assert saved_data["timeout_seconds"] == 600
        finally:
            Path(temp_path).unlink()
    
    def test_save_to_yaml_file(self):
        """Test saving configuration to YAML file."""
        config = ValidationConfig(
            enabled=False,
            fail_fast=True,
            timeout_seconds=600
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        
        try:
            config.save_to_file(temp_path)
            
            # Load and verify
            with open(temp_path, 'r') as f:
                saved_data = yaml.safe_load(f)
            
            assert saved_data["enabled"] is False
            assert saved_data["fail_fast"] is True
            assert saved_data["timeout_seconds"] == 600
        finally:
            Path(temp_path).unlink()
    
    def test_unsupported_file_format(self):
        """Test handling unsupported file formats."""
        # Create a temporary file with unsupported extension
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("test content")
            temp_path = f.name
        
        try:
            with pytest.raises(ValueError, match="Unsupported config file format"):
                ValidationConfig.from_file(temp_path)
        finally:
            Path(temp_path).unlink()
        
        config = ValidationConfig()
        with pytest.raises(ValueError, match="Unsupported config file format"):
            config.save_to_file("config.txt")


class TestDefaultConfig:
    """Test default configuration."""
    
    def test_default_config_structure(self):
        """Test that default configuration has expected structure."""
        assert DEFAULT_CONFIG.enabled is True
        assert isinstance(DEFAULT_CONFIG.validator_configs, dict)
        assert isinstance(DEFAULT_CONFIG.enabled_categories, list)
        assert isinstance(DEFAULT_CONFIG.environment_configs, dict)
        
        # Check that common validators are configured
        assert "CodeQualityValidator" in DEFAULT_CONFIG.validator_configs
        assert "SecurityValidator" in DEFAULT_CONFIG.validator_configs
        assert "CloudResourceValidator" in DEFAULT_CONFIG.validator_configs
        assert "AuthenticationValidator" in DEFAULT_CONFIG.validator_configs
        
        # Check that common categories are enabled
        assert "code_quality" in DEFAULT_CONFIG.enabled_categories
        assert "security" in DEFAULT_CONFIG.enabled_categories
        assert "cloud_resources" in DEFAULT_CONFIG.enabled_categories
        
        # Check environment configurations
        assert "development" in DEFAULT_CONFIG.environment_configs
        assert "staging" in DEFAULT_CONFIG.environment_configs
        assert "production" in DEFAULT_CONFIG.environment_configs