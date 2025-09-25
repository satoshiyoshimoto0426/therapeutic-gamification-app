"""
Validator factory for creating and configuring validators.
"""

import logging
from typing import Dict, Any, Optional, List

from ..framework import ValidationFramework
from ..config import ValidationConfig
from .code_quality import CodeQualityValidator
from .security import SecurityValidator
from .dependency import DependencyValidator
from .cloud_resource import CloudResourceValidator
from .authentication import AuthenticationValidator
from .environment import EnvironmentValidator


logger = logging.getLogger(__name__)


class ValidatorFactory:
    """Factory for creating and configuring validators."""
    
    # Registry of available validator classes
    VALIDATOR_CLASSES = {
        'code_quality': CodeQualityValidator,
        'security': SecurityValidator,
        'dependency': DependencyValidator,
        'cloud_resource': CloudResourceValidator,
        'authentication': AuthenticationValidator,
        'environment': EnvironmentValidator
    }
    
    @classmethod
    def create_framework(
        self,
        config: Optional[ValidationConfig] = None,
        environment: Optional[str] = None
    ) -> ValidationFramework:
        """
        Create a validation framework with all validators registered.
        
        Args:
            config: Optional validation configuration
            environment: Target environment (development, staging, production)
            
        Returns:
            Configured ValidationFramework instance
        """
        framework = ValidationFramework(config)
        
        # Register all available validators
        for validator_name, validator_class in self.VALIDATOR_CLASSES.items():
            try:
                # Get environment-specific configuration
                validator_config = self._get_validator_config(
                    validator_name, 
                    environment, 
                    config
                )
                
                framework.register_validator_class(validator_class, validator_config)
                logger.info(f"Registered validator: {validator_name}")
                
            except Exception as e:
                logger.error(f"Failed to register validator {validator_name}: {e}")
        
        return framework
    
    @classmethod
    def create_cloud_validators_framework(
        self,
        config: Optional[ValidationConfig] = None,
        environment: Optional[str] = None
    ) -> ValidationFramework:
        """
        Create a validation framework with only cloud-related validators.
        
        This is useful for task 2.3 specifically.
        
        Args:
            config: Optional validation configuration
            environment: Target environment
            
        Returns:
            ValidationFramework with cloud validators
        """
        framework = ValidationFramework(config)
        
        # Register only cloud-related validators
        cloud_validators = [
            'cloud_resource',
            'authentication', 
            'environment'
        ]
        
        for validator_name in cloud_validators:
            if validator_name in self.VALIDATOR_CLASSES:
                validator_class = self.VALIDATOR_CLASSES[validator_name]
                try:
                    validator_config = self._get_validator_config(
                        validator_name,
                        environment,
                        config
                    )
                    
                    framework.register_validator_class(validator_class, validator_config)
                    logger.info(f"Registered cloud validator: {validator_name}")
                    
                except Exception as e:
                    logger.error(f"Failed to register cloud validator {validator_name}: {e}")
        
        return framework
    
    @classmethod
    def create_validator(
        self,
        validator_name: str,
        config: Optional[Dict[str, Any]] = None,
        environment: Optional[str] = None
    ) -> Optional[Any]:
        """
        Create a single validator instance.
        
        Args:
            validator_name: Name of the validator to create
            config: Optional validator configuration
            environment: Target environment
            
        Returns:
            Validator instance or None if not found
        """
        if validator_name not in self.VALIDATOR_CLASSES:
            logger.error(f"Unknown validator: {validator_name}")
            return None
        
        validator_class = self.VALIDATOR_CLASSES[validator_name]
        
        try:
            validator_config = config or self._get_default_config(validator_name, environment)
            return validator_class(validator_config)
            
        except Exception as e:
            logger.error(f"Failed to create validator {validator_name}: {e}")
            return None
    
    @classmethod
    def _get_validator_config(
        self,
        validator_name: str,
        environment: Optional[str],
        global_config: Optional[ValidationConfig]
    ) -> Dict[str, Any]:
        """Get configuration for a specific validator."""
        config = {}
        
        # Start with default configuration
        default_config = self._get_default_config(validator_name, environment)
        config.update(default_config)
        
        # Apply global configuration if available
        if global_config:
            validator_config = global_config.get_validator_config(validator_name)
            if validator_config:
                config.update(validator_config)
        
        # Apply environment-specific overrides
        if environment:
            env_config = self._get_environment_config(validator_name, environment)
            config.update(env_config)
        
        return config
    
    @classmethod
    def _get_default_config(
        self,
        validator_name: str,
        environment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get default configuration for a validator."""
        base_config = {
            'timeout_seconds': 60,
            'enabled': True
        }
        
        # Validator-specific defaults
        if validator_name == 'cloud_resource':
            base_config.update({
                'check_quotas': True,
                'verify_permissions': True,
                'region': 'us-central1',
                'required_apis': [
                    'run.googleapis.com',
                    'cloudbuild.googleapis.com',
                    'containerregistry.googleapis.com',
                    'secretmanager.googleapis.com'
                ]
            })
        
        elif validator_name == 'authentication':
            base_config.update({
                'verify_service_accounts': True,
                'check_api_keys': True,
                'check_environment_vars': True,
                'check_github_auth': True,
                'required_credentials': [
                    'GOOGLE_APPLICATION_CREDENTIALS',
                    'GOOGLE_CLOUD_PROJECT'
                ]
            })
        
        elif validator_name == 'environment':
            base_config.update({
                'environment': environment or 'development',
                'check_secrets': True,
                'check_env_vars': True,
                'check_config_files': True
            })
        
        elif validator_name == 'code_quality':
            base_config.update({
                'min_test_coverage': 0.8,
                'run_linting': True,
                'run_type_checking': True
            })
        
        elif validator_name == 'security':
            base_config.update({
                'run_vulnerability_scan': True,
                'check_dependencies': True,
                'scan_secrets': True
            })
        
        elif validator_name == 'dependency':
            base_config.update({
                'check_compatibility': True,
                'check_vulnerabilities': True,
                'update_available': True
            })
        
        return base_config
    
    @classmethod
    def _get_environment_config(
        self,
        validator_name: str,
        environment: str
    ) -> Dict[str, Any]:
        """Get environment-specific configuration overrides."""
        config = {}
        
        if environment == 'production':
            if validator_name == 'cloud_resource':
                config.update({
                    'check_quotas': True,
                    'verify_permissions': True,
                    'timeout_seconds': 120  # More time for production checks
                })
            
            elif validator_name == 'authentication':
                config.update({
                    'verify_service_accounts': True,
                    'check_api_keys': True,
                    'timeout_seconds': 90
                })
            
            elif validator_name == 'environment':
                config.update({
                    'check_secrets': True,
                    'check_env_vars': True,
                    'check_config_files': True
                })
            
            elif validator_name == 'security':
                config.update({
                    'run_vulnerability_scan': True,
                    'fail_on_high_severity': True
                })
        
        elif environment == 'development':
            # More lenient settings for development
            if validator_name == 'cloud_resource':
                config.update({
                    'check_quotas': False,
                    'verify_permissions': False
                })
            
            elif validator_name == 'security':
                config.update({
                    'fail_on_high_severity': False
                })
        
        return config
    
    @classmethod
    def get_available_validators(self) -> List[str]:
        """Get list of available validator names."""
        return list(self.VALIDATOR_CLASSES.keys())
    
    @classmethod
    def get_cloud_validators(self) -> List[str]:
        """Get list of cloud-related validator names."""
        return ['cloud_resource', 'authentication', 'environment']