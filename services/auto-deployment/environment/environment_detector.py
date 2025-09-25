"""
Environment Detection and Setup Automation for auto-deployment system.

Handles automatic detection of deployment environments (dev/staging/production),
environment setup procedures, and environment validation.
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import Environment, DeploymentConfig
from exceptions import EnvironmentError, ConfigurationError


class DetectionMethod(Enum):
    """Methods for environment detection."""
    ENVIRONMENT_VARIABLE = "env_var"
    GIT_BRANCH = "git_branch"
    CONFIG_FILE = "config_file"
    PROJECT_ID = "project_id"
    HOSTNAME = "hostname"
    MANUAL = "manual"


@dataclass
class EnvironmentInfo:
    """Information about detected environment."""
    environment: Environment
    confidence: float  # 0.0 to 1.0
    detection_method: DetectionMethod
    details: Dict[str, Any]
    project_id: Optional[str] = None
    region: Optional[str] = None


class EnvironmentDetector:
    """Detects and sets up deployment environments automatically."""
    
    def __init__(self, config: Optional[DeploymentConfig] = None):
        self.config = config or DeploymentConfig(Environment.DEVELOPMENT)
        self.logger = logging.getLogger(__name__)
        
        # Environment detection rules
        self.detection_rules = {
            DetectionMethod.ENVIRONMENT_VARIABLE: self._detect_from_env_var,
            DetectionMethod.GIT_BRANCH: self._detect_from_git_branch,
            DetectionMethod.CONFIG_FILE: self._detect_from_config_file,
            DetectionMethod.PROJECT_ID: self._detect_from_project_id,
            DetectionMethod.HOSTNAME: self._detect_from_hostname,
        }
        
        # Environment-specific patterns
        self.env_patterns = {
            Environment.DEVELOPMENT: {
                'env_vars': ['dev', 'development', 'local'],
                'branches': ['dev', 'develop', 'development', 'feature/*'],
                'project_suffixes': ['-dev', '-development'],
                'hostnames': ['localhost', '127.0.0.1', 'dev-*']
            },
            Environment.STAGING: {
                'env_vars': ['staging', 'stage', 'test'],
                'branches': ['staging', 'stage', 'release/*'],
                'project_suffixes': ['-staging', '-stage', '-test'],
                'hostnames': ['staging-*', 'stage-*', 'test-*']
            },
            Environment.PRODUCTION: {
                'env_vars': ['production', 'prod', 'live'],
                'branches': ['main', 'master', 'production', 'prod'],
                'project_suffixes': ['-prod', '-production', ''],
                'hostnames': ['prod-*', 'production-*']
            }
        }
    
    def detect_environment(self, 
                          methods: Optional[List[DetectionMethod]] = None) -> EnvironmentInfo:
        """
        Detect the current deployment environment.
        
        Args:
            methods: List of detection methods to use. If None, uses all methods.
            
        Returns:
            EnvironmentInfo with detected environment and confidence score.
        """
        if methods is None:
            methods = list(self.detection_rules.keys())
        
        detections = []
        
        for method in methods:
            try:
                detection_func = self.detection_rules[method]
                result = detection_func()
                if result:
                    detections.append(result)
                    self.logger.debug(f"Detection method {method.value} found: {result}")
            except Exception as e:
                self.logger.warning(f"Detection method {method.value} failed: {e}")
        
        if not detections:
            # Default to development if no detection succeeds
            return EnvironmentInfo(
                environment=Environment.DEVELOPMENT,
                confidence=0.1,
                detection_method=DetectionMethod.MANUAL,
                details={'reason': 'No detection method succeeded, defaulting to development'}
            )
        
        # Choose the detection with highest confidence
        best_detection = max(detections, key=lambda x: x.confidence)
        
        self.logger.info(f"Detected environment: {best_detection.environment.value} "
                        f"(confidence: {best_detection.confidence:.2f}, "
                        f"method: {best_detection.detection_method.value})")
        
        return best_detection
    
    def _detect_from_env_var(self) -> Optional[EnvironmentInfo]:
        """Detect environment from environment variables."""
        # Check common environment variables
        env_vars_to_check = [
            'ENVIRONMENT',
            'ENV',
            'DEPLOYMENT_ENV',
            'NODE_ENV',
            'FLASK_ENV',
            'DJANGO_SETTINGS_MODULE'
        ]
        
        for var_name in env_vars_to_check:
            value = os.environ.get(var_name, '').lower()
            if not value:
                continue
                
            for env, patterns in self.env_patterns.items():
                for pattern in patterns['env_vars']:
                    if pattern in value:
                        return EnvironmentInfo(
                            environment=env,
                            confidence=0.9,
                            detection_method=DetectionMethod.ENVIRONMENT_VARIABLE,
                            details={
                                'variable': var_name,
                                'value': value,
                                'pattern': pattern
                            }
                        )
        
        return None
    
    def _detect_from_git_branch(self) -> Optional[EnvironmentInfo]:
        """Detect environment from Git branch name."""
        try:
            import subprocess
            
            # Get current Git branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return None
                
            branch_name = result.stdout.strip().lower()
            
            for env, patterns in self.env_patterns.items():
                for pattern in patterns['branches']:
                    if pattern.endswith('/*'):
                        # Handle wildcard patterns
                        prefix = pattern[:-2]
                        if branch_name.startswith(prefix):
                            return EnvironmentInfo(
                                environment=env,
                                confidence=0.8,
                                detection_method=DetectionMethod.GIT_BRANCH,
                                details={
                                    'branch': branch_name,
                                    'pattern': pattern
                                }
                            )
                    elif pattern == branch_name:
                        return EnvironmentInfo(
                            environment=env,
                            confidence=0.8,
                            detection_method=DetectionMethod.GIT_BRANCH,
                            details={
                                'branch': branch_name,
                                'pattern': pattern
                            }
                        )
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return None
    
    def _detect_from_config_file(self) -> Optional[EnvironmentInfo]:
        """Detect environment from configuration files."""
        config_files = [
            'deployment.json',
            'environment.json',
            '.env',
            'config.yaml',
            'app.yaml'
        ]
        
        for config_file in config_files:
            config_path = Path(config_file)
            if not config_path.exists():
                continue
                
            try:
                if config_file.endswith('.json'):
                    with open(config_path, 'r') as f:
                        config_data = json.load(f)
                elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    import yaml
                    with open(config_path, 'r') as f:
                        config_data = yaml.safe_load(f)
                elif config_file == '.env':
                    config_data = {}
                    with open(config_path, 'r') as f:
                        for line in f:
                            if '=' in line and not line.strip().startswith('#'):
                                key, value = line.strip().split('=', 1)
                                config_data[key] = value
                else:
                    continue
                
                # Look for environment indicators in config
                env_indicators = ['environment', 'env', 'stage', 'deployment_env']
                for indicator in env_indicators:
                    if indicator in config_data:
                        env_value = str(config_data[indicator]).lower()
                        
                        for env, patterns in self.env_patterns.items():
                            for pattern in patterns['env_vars']:
                                if pattern in env_value:
                                    return EnvironmentInfo(
                                        environment=env,
                                        confidence=0.7,
                                        detection_method=DetectionMethod.CONFIG_FILE,
                                        details={
                                            'file': str(config_path),
                                            'key': indicator,
                                            'value': env_value,
                                            'pattern': pattern
                                        }
                                    )
                
            except Exception as e:
                self.logger.debug(f"Failed to parse config file {config_file}: {e}")
                continue
        
        return None
    
    def _detect_from_project_id(self) -> Optional[EnvironmentInfo]:
        """Detect environment from Google Cloud project ID."""
        project_id = (
            os.environ.get('GOOGLE_CLOUD_PROJECT') or
            os.environ.get('GCP_PROJECT') or
            os.environ.get('GCLOUD_PROJECT')
        )
        
        if not project_id:
            return None
        
        project_id_lower = project_id.lower()
        
        for env, patterns in self.env_patterns.items():
            for suffix in patterns['project_suffixes']:
                if suffix and project_id_lower.endswith(suffix):
                    return EnvironmentInfo(
                        environment=env,
                        confidence=0.8,
                        detection_method=DetectionMethod.PROJECT_ID,
                        details={
                            'project_id': project_id,
                            'suffix': suffix
                        },
                        project_id=project_id
                    )
        
        # If no suffix matches, assume production for clean project names
        if not any(suffix in project_id_lower for patterns in self.env_patterns.values() 
                  for suffix in patterns['project_suffixes'] if suffix):
            return EnvironmentInfo(
                environment=Environment.PRODUCTION,
                confidence=0.6,
                detection_method=DetectionMethod.PROJECT_ID,
                details={
                    'project_id': project_id,
                    'reason': 'No environment suffix found, assuming production'
                },
                project_id=project_id
            )
        
        return None
    
    def _detect_from_hostname(self) -> Optional[EnvironmentInfo]:
        """Detect environment from hostname."""
        import socket
        
        try:
            hostname = socket.gethostname().lower()
            
            for env, patterns in self.env_patterns.items():
                for pattern in patterns['hostnames']:
                    if pattern.endswith('*'):
                        # Handle wildcard patterns
                        prefix = pattern[:-1]
                        if hostname.startswith(prefix):
                            return EnvironmentInfo(
                                environment=env,
                                confidence=0.6,
                                detection_method=DetectionMethod.HOSTNAME,
                                details={
                                    'hostname': hostname,
                                    'pattern': pattern
                                }
                            )
                    elif pattern == hostname:
                        return EnvironmentInfo(
                            environment=env,
                            confidence=0.6,
                            detection_method=DetectionMethod.HOSTNAME,
                            details={
                                'hostname': hostname,
                                'pattern': pattern
                            }
                        )
            
        except Exception as e:
            self.logger.debug(f"Failed to get hostname: {e}")
        
        return None
    
    def setup_environment(self, env_info: EnvironmentInfo) -> Dict[str, Any]:
        """
        Set up the detected environment with appropriate configurations.
        
        Args:
            env_info: Environment information from detection
            
        Returns:
            Dictionary with setup results and configurations
        """
        self.logger.info(f"Setting up environment: {env_info.environment.value}")
        
        setup_results = {
            'environment': env_info.environment.value,
            'project_id': env_info.project_id,
            'region': env_info.region,
            'configurations': {},
            'validations': {},
            'setup_actions': []
        }
        
        try:
            # Environment-specific setup
            if env_info.environment == Environment.DEVELOPMENT:
                setup_results.update(self._setup_development_environment(env_info))
            elif env_info.environment == Environment.STAGING:
                setup_results.update(self._setup_staging_environment(env_info))
            elif env_info.environment == Environment.PRODUCTION:
                setup_results.update(self._setup_production_environment(env_info))
            
            # Validate environment setup
            validation_results = self._validate_environment_setup(env_info, setup_results)
            setup_results['validations'] = validation_results
            
            self.logger.info(f"Environment setup completed for {env_info.environment.value}")
            
        except Exception as e:
            self.logger.error(f"Environment setup failed: {e}")
            setup_results['error'] = str(e)
            raise EnvironmentError(f"Failed to setup environment: {e}")
        
        return setup_results
    
    def _setup_development_environment(self, env_info: EnvironmentInfo) -> Dict[str, Any]:
        """Setup development environment."""
        return {
            'configurations': {
                'debug_mode': True,
                'log_level': 'DEBUG',
                'auto_reload': True,
                'resource_limits': {
                    'memory': '1Gi',
                    'cpu': '1',
                    'min_instances': 0,
                    'max_instances': 10
                }
            },
            'setup_actions': [
                'Enable debug logging',
                'Set minimal resource limits',
                'Configure auto-reload'
            ]
        }
    
    def _setup_staging_environment(self, env_info: EnvironmentInfo) -> Dict[str, Any]:
        """Setup staging environment."""
        return {
            'configurations': {
                'debug_mode': False,
                'log_level': 'INFO',
                'auto_reload': False,
                'resource_limits': {
                    'memory': '2Gi',
                    'cpu': '1',
                    'min_instances': 1,
                    'max_instances': 50
                }
            },
            'setup_actions': [
                'Configure production-like settings',
                'Set moderate resource limits',
                'Enable monitoring'
            ]
        }
    
    def _setup_production_environment(self, env_info: EnvironmentInfo) -> Dict[str, Any]:
        """Setup production environment."""
        return {
            'configurations': {
                'debug_mode': False,
                'log_level': 'WARNING',
                'auto_reload': False,
                'resource_limits': {
                    'memory': '4Gi',
                    'cpu': '2',
                    'min_instances': 2,
                    'max_instances': 100
                }
            },
            'setup_actions': [
                'Configure production settings',
                'Set high resource limits',
                'Enable comprehensive monitoring',
                'Configure security policies'
            ]
        }
    
    def _validate_environment_setup(self, 
                                   env_info: EnvironmentInfo, 
                                   setup_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that environment setup is correct."""
        validations = {
            'environment_detected': True,
            'configuration_valid': True,
            'resources_available': True,
            'security_compliant': True,
            'issues': []
        }
        
        # Validate environment detection confidence
        if env_info.confidence < 0.5:
            validations['issues'].append({
                'type': 'low_confidence',
                'message': f'Environment detection confidence is low: {env_info.confidence:.2f}',
                'severity': 'warning'
            })
        
        # Validate production environment requirements
        if env_info.environment == Environment.PRODUCTION:
            if setup_results.get('configurations', {}).get('debug_mode', False):
                validations['security_compliant'] = False
                validations['issues'].append({
                    'type': 'debug_in_production',
                    'message': 'Debug mode should not be enabled in production',
                    'severity': 'error'
                })
        
        # Validate project ID format
        if env_info.project_id:
            if not env_info.project_id.replace('-', '').replace('_', '').isalnum():
                validations['configuration_valid'] = False
                validations['issues'].append({
                    'type': 'invalid_project_id',
                    'message': f'Project ID format may be invalid: {env_info.project_id}',
                    'severity': 'warning'
                })
        
        return validations
    
    def get_environment_recommendations(self, env_info: EnvironmentInfo) -> List[str]:
        """Get recommendations for the detected environment."""
        recommendations = []
        
        if env_info.confidence < 0.7:
            recommendations.append(
                "Consider setting the ENVIRONMENT variable explicitly for more reliable detection"
            )
        
        if env_info.environment == Environment.PRODUCTION:
            recommendations.extend([
                "Ensure all secrets are stored in Google Secret Manager",
                "Enable comprehensive monitoring and alerting",
                "Configure backup and disaster recovery procedures",
                "Review security policies and access controls"
            ])
        elif env_info.environment == Environment.STAGING:
            recommendations.extend([
                "Use production-like data for realistic testing",
                "Configure monitoring to match production setup",
                "Test deployment procedures regularly"
            ])
        else:  # Development
            recommendations.extend([
                "Use local or development databases to avoid affecting production data",
                "Enable debug logging for easier troubleshooting",
                "Consider using development-specific service accounts"
            ])
        
        return recommendations