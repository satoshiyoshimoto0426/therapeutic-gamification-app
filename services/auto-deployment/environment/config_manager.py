"""
Configuration Manager for auto-deployment system.

Handles environment-specific settings, configuration loading,
and configuration validation for deployment environments.
"""

import os
import json
import yaml
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import DeploymentConfig, Environment, CloudConfig
from exceptions import ConfigurationError


class ConfigFormat(Enum):
    """Supported configuration file formats."""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"


@dataclass
class EnvironmentConfig:
    """Environment-specific configuration."""
    name: str
    project_id: str
    region: str
    service_name: str
    
    # Resource limits
    memory: str = "2Gi"
    cpu: str = "2"
    min_instances: int = 1
    max_instances: int = 100
    
    # Environment variables
    env_vars: Dict[str, str] = None
    
    # Security settings
    enable_security_scan: bool = True
    min_test_coverage: float = 0.8
    
    # Notification settings
    slack_webhook_url: Optional[str] = None
    email_recipients: List[str] = None
    
    def __post_init__(self):
        if self.env_vars is None:
            self.env_vars = {}
        if self.email_recipients is None:
            self.email_recipients = []


class ConfigurationManager:
    """
    Manages environment-specific configuration for auto-deployment.
    
    Handles loading, validation, and merging of configuration from
    multiple sources including files, environment variables, and defaults.
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else Path.cwd() / ".kiro" / "deployment"
        self.logger = logging.getLogger(__name__)
        self._config_cache: Dict[str, EnvironmentConfig] = {}
        
        # Ensure config directory exists
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_environment_config(self, environment: Environment) -> EnvironmentConfig:
        """
        Load configuration for a specific environment.
        
        Args:
            environment: Target environment
            
        Returns:
            Environment-specific configuration
        """
        env_name = environment.value
        
        if env_name not in self._config_cache:
            self.logger.info(f"Loading configuration for environment: {env_name}")
            self._config_cache[env_name] = self._build_environment_config(environment)
        
        return self._config_cache[env_name]
    
    def _build_environment_config(self, environment: Environment) -> EnvironmentConfig:
        """Build environment configuration from multiple sources."""
        # Start with default configuration
        config = self._get_default_config(environment)
        
        # Load from configuration files
        file_config = self._load_config_from_files(environment)
        if file_config:
            config = self._merge_configs(config, file_config)
        
        # Override with environment variables
        env_config = self._load_config_from_env(environment)
        if env_config:
            config = self._merge_configs(config, env_config)
        
        # Validate final configuration
        self._validate_config(config)
        
        return config
    
    def _get_default_config(self, environment: Environment) -> EnvironmentConfig:
        """Get default configuration for environment."""
        base_config = EnvironmentConfig(
            name=environment.value,
            project_id=os.getenv("GCP_PROJECT_ID", "therapeutic-gamification-app"),
            region=os.getenv("GCP_REGION", "asia-northeast1"),
            service_name=os.getenv("SERVICE_NAME", "therapeutic-gamification-app")
        )
        
        # Environment-specific defaults
        if environment == Environment.PRODUCTION:
            base_config.min_instances = 5
            base_config.max_instances = 1000
            base_config.memory = "4Gi"
            base_config.cpu = "4"
            base_config.min_test_coverage = 0.9
        elif environment == Environment.STAGING:
            base_config.min_instances = 1
            base_config.max_instances = 10
            base_config.memory = "2Gi"
            base_config.cpu = "2"
            base_config.min_test_coverage = 0.8
        elif environment == Environment.DEVELOPMENT:
            base_config.min_instances = 0
            base_config.max_instances = 5
            base_config.memory = "1Gi"
            base_config.cpu = "1"
            base_config.enable_security_scan = False
            base_config.min_test_coverage = 0.7
        
        return base_config
    
    def _load_config_from_files(self, environment: Environment) -> Optional[Dict[str, Any]]:
        """Load configuration from files."""
        env_name = environment.value
        config_data = {}
        
        # Try different file formats
        config_files = [
            self.config_dir / f"{env_name}.yaml",
            self.config_dir / f"{env_name}.yml",
            self.config_dir / f"{env_name}.json",
            self.config_dir / "config.yaml",
            self.config_dir / "config.yml",
            self.config_dir / "config.json"
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    self.logger.info(f"Loading configuration from: {config_file}")
                    file_data = self._load_config_file(config_file)
                    
                    # Extract environment-specific section if it exists
                    if env_name in file_data:
                        config_data.update(file_data[env_name])
                    else:
                        config_data.update(file_data)
                    
                except Exception as e:
                    self.logger.error(f"Failed to load config from {config_file}: {e}")
        
        return config_data if config_data else None
    
    def _load_config_file(self, config_file: Path) -> Dict[str, Any]:
        """Load configuration from a specific file."""
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix.lower() in ['.yaml', '.yml']:
                return yaml.safe_load(f) or {}
            elif config_file.suffix.lower() == '.json':
                return json.load(f) or {}
            else:
                raise ConfigurationError(f"Unsupported config file format: {config_file.suffix}")
    
    def _load_config_from_env(self, environment: Environment) -> Optional[Dict[str, Any]]:
        """Load configuration from environment variables."""
        env_name = environment.value.upper()
        config_data = {}
        
        # Environment-specific variables
        env_vars = {
            f"{env_name}_PROJECT_ID": "project_id",
            f"{env_name}_REGION": "region",
            f"{env_name}_SERVICE_NAME": "service_name",
            f"{env_name}_MEMORY": "memory",
            f"{env_name}_CPU": "cpu",
            f"{env_name}_MIN_INSTANCES": "min_instances",
            f"{env_name}_MAX_INSTANCES": "max_instances",
            f"{env_name}_MIN_TEST_COVERAGE": "min_test_coverage",
            f"{env_name}_SLACK_WEBHOOK_URL": "slack_webhook_url",
            f"{env_name}_ENABLE_SECURITY_SCAN": "enable_security_scan"
        }
        
        # Generic variables (fallback)
        generic_vars = {
            "GCP_PROJECT_ID": "project_id",
            "GCP_REGION": "region",
            "SERVICE_NAME": "service_name",
            "MEMORY": "memory",
            "CPU": "cpu",
            "MIN_INSTANCES": "min_instances",
            "MAX_INSTANCES": "max_instances",
            "MIN_TEST_COVERAGE": "min_test_coverage",
            "SLACK_WEBHOOK_URL": "slack_webhook_url",
            "ENABLE_SECURITY_SCAN": "enable_security_scan"
        }
        
        # Load environment-specific variables first
        for env_var, config_key in env_vars.items():
            value = os.getenv(env_var)
            if value is not None:
                config_data[config_key] = self._convert_env_value(value, config_key)
        
        # Load generic variables if environment-specific not found
        for env_var, config_key in generic_vars.items():
            if config_key not in config_data:
                value = os.getenv(env_var)
                if value is not None:
                    config_data[config_key] = self._convert_env_value(value, config_key)
        
        # Load environment variables for the service
        env_vars_dict = {}
        for key, value in os.environ.items():
            if key.startswith(f"{env_name}_ENV_") or key.startswith("APP_"):
                env_key = key.replace(f"{env_name}_ENV_", "").replace("APP_", "")
                env_vars_dict[env_key] = value
        
        if env_vars_dict:
            config_data["env_vars"] = env_vars_dict
        
        return config_data if config_data else None
    
    def _convert_env_value(self, value: str, config_key: str) -> Any:
        """Convert environment variable value to appropriate type."""
        # Boolean values
        if config_key in ["enable_security_scan"]:
            return value.lower() in ["true", "1", "yes", "on"]
        
        # Integer values
        if config_key in ["min_instances", "max_instances"]:
            try:
                return int(value)
            except ValueError:
                self.logger.error(f"Invalid integer value for {config_key}: {value}")
                return value
        
        # Float values
        if config_key in ["min_test_coverage"]:
            try:
                return float(value)
            except ValueError:
                self.logger.error(f"Invalid float value for {config_key}: {value}")
                return value
        
        # String values (default)
        return value
    
    def _merge_configs(self, base_config: EnvironmentConfig, override_data: Dict[str, Any]) -> EnvironmentConfig:
        """Merge configuration data into base configuration."""
        # Convert base config to dict
        config_dict = asdict(base_config)
        
        # Update with override data
        for key, value in override_data.items():
            if key in config_dict:
                if key == "env_vars" and isinstance(config_dict[key], dict) and isinstance(value, dict):
                    # Merge environment variables
                    config_dict[key].update(value)
                elif key == "email_recipients" and isinstance(value, str):
                    # Convert comma-separated string to list
                    config_dict[key] = [email.strip() for email in value.split(",")]
                else:
                    config_dict[key] = value
            else:
                self.logger.error(f"Unknown configuration key: {key}")
        
        # Create new config object
        return EnvironmentConfig(**config_dict)
    
    def _validate_config(self, config: EnvironmentConfig) -> None:
        """Validate configuration values."""
        errors = []
        
        # Required fields
        if not config.project_id:
            errors.append("project_id is required")
        
        if not config.region:
            errors.append("region is required")
        
        if not config.service_name:
            errors.append("service_name is required")
        
        # Numeric validations
        if config.min_instances < 0:
            errors.append("min_instances must be >= 0")
        
        if config.max_instances <= config.min_instances:
            errors.append("max_instances must be > min_instances")
        
        if not (0.0 <= config.min_test_coverage <= 1.0):
            errors.append("min_test_coverage must be between 0.0 and 1.0")
        
        # Resource validations
        if not self._validate_memory_format(config.memory):
            errors.append(f"Invalid memory format: {config.memory}")
        
        if not self._validate_cpu_format(config.cpu):
            errors.append(f"Invalid CPU format: {config.cpu}")
        
        if errors:
            raise ConfigurationError(f"Configuration validation failed: {'; '.join(errors)}")
    
    def _validate_memory_format(self, memory: str) -> bool:
        """Validate memory format (e.g., '2Gi', '512Mi')."""
        import re
        pattern = r'^\d+(\.\d+)?(Mi|Gi|Ti)$'
        return bool(re.match(pattern, memory))
    
    def _validate_cpu_format(self, cpu: str) -> bool:
        """Validate CPU format (e.g., '2', '0.5', '1000m')."""
        import re
        # Allow integer, decimal, or millicpu format
        patterns = [
            r'^\d+$',  # Integer (e.g., '2')
            r'^\d+\.\d+$',  # Decimal (e.g., '0.5')
            r'^\d+m$'  # Millicpu (e.g., '1000m')
        ]
        return any(re.match(pattern, cpu) for pattern in patterns)
    
    def save_environment_config(self, environment: Environment, config: EnvironmentConfig) -> None:
        """
        Save environment configuration to file.
        
        Args:
            environment: Target environment
            config: Configuration to save
        """
        env_name = environment.value
        config_file = self.config_dir / f"{env_name}.yaml"
        
        try:
            # Convert to dict and remove None values
            config_dict = asdict(config)
            config_dict = {k: v for k, v in config_dict.items() if v is not None}
            
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config_dict, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Configuration saved to: {config_file}")
            
            # Update cache
            self._config_cache[env_name] = config
            
        except Exception as e:
            raise ConfigurationError(f"Failed to save configuration: {e}")
    
    def list_available_configs(self) -> List[str]:
        """List available configuration files."""
        configs = []
        
        for config_file in self.config_dir.glob("*.yaml"):
            if config_file.stem not in ["config"]:
                configs.append(config_file.stem)
        
        for config_file in self.config_dir.glob("*.json"):
            if config_file.stem not in ["config"]:
                configs.append(config_file.stem)
        
        return sorted(list(set(configs)))
    
    def get_deployment_config(self, environment: Environment) -> DeploymentConfig:
        """
        Convert environment config to deployment config.
        
        Args:
            environment: Target environment
            
        Returns:
            DeploymentConfig object
        """
        env_config = self.load_environment_config(environment)
        
        # Create cloud config
        cloud_config = CloudConfig(
            project_id=env_config.project_id,
            region=env_config.region,
            service_name=env_config.service_name,
            memory=env_config.memory,
            cpu=env_config.cpu,
            min_instances=env_config.min_instances,
            max_instances=env_config.max_instances
        )
        
        # Create deployment config
        deployment_config = DeploymentConfig(
            environment=environment,
            cloud_config=cloud_config
        )
        
        # Update security config
        deployment_config.security_config.enable_security_scan = env_config.enable_security_scan
        deployment_config.security_config.min_test_coverage = env_config.min_test_coverage
        
        # Update notification config
        deployment_config.notification_config.slack_webhook_url = env_config.slack_webhook_url
        deployment_config.notification_config.email_recipients = env_config.email_recipients
        
        return deployment_config
    
    def clear_cache(self) -> None:
        """Clear configuration cache."""
        self._config_cache.clear()
        self.logger.info("Configuration cache cleared")
    
    def validate_all_configs(self) -> Dict[str, List[str]]:
        """
        Validate all available configurations.
        
        Returns:
            Dictionary mapping environment names to validation errors
        """
        results = {}
        
        for env_name in self.list_available_configs():
            try:
                environment = Environment(env_name)
                self.load_environment_config(environment)
                results[env_name] = []  # No errors
            except ValueError:
                results[env_name] = [f"Invalid environment name: {env_name}"]
            except ConfigurationError as e:
                results[env_name] = [str(e)]
            except Exception as e:
                results[env_name] = [f"Unexpected error: {e}"]
        
        return results

# Alias for backward compatibility
ConfigManager = ConfigurationManager
