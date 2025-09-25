"""
Configuration management for the validation framework.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import yaml
import json
from pathlib import Path


@dataclass
class ValidationConfig:
    """Configuration for validation framework."""
    
    # Global validation settings
    enabled: bool = True
    fail_fast: bool = False
    parallel_execution: bool = True
    timeout_seconds: int = 300
    
    # Validator-specific configurations
    validator_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    # Validation categories to run
    enabled_categories: List[str] = field(default_factory=lambda: [
        'code_quality',
        'security',
        'dependencies',
        'cloud_resources',
        'authentication'
    ])
    
    # Environment-specific settings
    environment_configs: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, config_path: str) -> 'ValidationConfig':
        """Load configuration from a file."""
        path = Path(config_path)
        
        if not path.exists():
            return cls()
        
        # Check file format before opening
        if path.suffix.lower() not in ['.yaml', '.yml', '.json']:
            raise ValueError(f"Unsupported config file format: {path.suffix}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix.lower() == '.json':
                data = json.load(f)
        
        return cls(**data)
    
    def get_validator_config(self, validator_name: str) -> Dict[str, Any]:
        """Get configuration for a specific validator."""
        return self.validator_configs.get(validator_name, {})
    
    def get_environment_config(self, environment: str) -> Dict[str, Any]:
        """Get configuration for a specific environment."""
        return self.environment_configs.get(environment, {})
    
    def is_validator_enabled(self, validator_name: str) -> bool:
        """Check if a validator is enabled."""
        validator_config = self.get_validator_config(validator_name)
        return validator_config.get('enabled', True)
    
    def is_category_enabled(self, category: str) -> bool:
        """Check if a validation category is enabled."""
        return category in self.enabled_categories
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'enabled': self.enabled,
            'fail_fast': self.fail_fast,
            'parallel_execution': self.parallel_execution,
            'timeout_seconds': self.timeout_seconds,
            'validator_configs': self.validator_configs,
            'enabled_categories': self.enabled_categories,
            'environment_configs': self.environment_configs
        }
    
    def save_to_file(self, config_path: str) -> None:
        """Save configuration to a file."""
        path = Path(config_path)
        
        # Check file format before opening
        if path.suffix.lower() not in ['.yaml', '.yml', '.json']:
            raise ValueError(f"Unsupported config file format: {path.suffix}")
        
        data = self.to_dict()
        
        with open(path, 'w', encoding='utf-8') as f:
            if path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(data, f, default_flow_style=False)
            elif path.suffix.lower() == '.json':
                json.dump(data, f, indent=2)


# Default configuration template
DEFAULT_CONFIG = ValidationConfig(
    enabled=True,
    fail_fast=False,
    parallel_execution=True,
    timeout_seconds=300,
    validator_configs={
        'CodeQualityValidator': {
            'enabled': True,
            'min_test_coverage': 0.8,
            'run_linting': True,
            'run_type_checking': True
        },
        'SecurityValidator': {
            'enabled': True,
            'run_vulnerability_scan': True,
            'check_dependencies': True,
            'severity_threshold': 'medium'
        },
        'CloudResourceValidator': {
            'enabled': True,
            'check_quotas': True,
            'verify_permissions': True,
            'timeout_seconds': 60
        },
        'AuthenticationValidator': {
            'enabled': True,
            'verify_service_accounts': True,
            'check_api_keys': True
        }
    },
    enabled_categories=[
        'code_quality',
        'security', 
        'dependencies',
        'cloud_resources',
        'authentication'
    ],
    environment_configs={
        'development': {
            'strict_validation': False,
            'allow_warnings': True
        },
        'staging': {
            'strict_validation': True,
            'allow_warnings': True
        },
        'production': {
            'strict_validation': True,
            'allow_warnings': False,
            'require_manual_approval': True
        }
    }
)