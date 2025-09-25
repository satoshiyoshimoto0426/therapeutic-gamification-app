"""
Environment-specific requirement validator for pre-deployment checks.
"""

import os
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Set

from ..base import BaseValidator, ValidationResult, ValidationSeverity


logger = logging.getLogger(__name__)


class EnvironmentValidator(BaseValidator):
    """Validator for environment-specific requirements and configuration."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.environment = self.config.get('environment', 'development')
        self.check_secrets = self.config.get('check_secrets', True)
        self.check_env_vars = self.config.get('check_env_vars', True)
        self.check_config_files = self.config.get('check_config_files', True)
        self.timeout_seconds = self.config.get('timeout_seconds', 30)
        
        # Environment-specific requirements
        self.env_requirements = self.config.get('env_requirements', {
            'development': {
                'required_env_vars': ['GOOGLE_CLOUD_PROJECT'],
                'optional_env_vars': ['DEBUG', 'LOG_LEVEL'],
                'required_secrets': [],
                'config_files': ['firebase_config/firestore.rules'],
                'min_resources': {'memory': '1Gi', 'cpu': '1'}
            },
            'staging': {
                'required_env_vars': ['GOOGLE_CLOUD_PROJECT', 'ENVIRONMENT'],
                'optional_env_vars': ['DEBUG', 'LOG_LEVEL', 'MONITORING_ENABLED'],
                'required_secrets': ['database-url', 'api-keys'],
                'config_files': ['firebase_config/firestore.rules', 'firebase_config/firestore.indexes.json'],
                'min_resources': {'memory': '2Gi', 'cpu': '1'}
            },
            'production': {
                'required_env_vars': ['GOOGLE_CLOUD_PROJECT', 'ENVIRONMENT'],
                'optional_env_vars': ['LOG_LEVEL', 'MONITORING_ENABLED'],
                'required_secrets': ['database-url', 'api-keys', 'auth-secrets'],
                'config_files': [
                    'firebase_config/firestore.rules',
                    'firebase_config/firestore.indexes.json',
                    'infrastructure/production/cloud-run.yaml'
                ],
                'min_resources': {'memory': '4Gi', 'cpu': '2'},
                'security_requirements': {
                    'https_only': True,
                    'cors_restricted': True,
                    'rate_limiting': True
                }
            }
        })
    
    @property
    def description(self) -> str:
        return f"Validates environment-specific requirements for {self.environment}"
    
    async def validate(self) -> ValidationResult:
        """Run environment-specific validation checks."""
        try:
            issues = []
            details = {}
            
            # Get environment requirements
            env_reqs = self.env_requirements.get(self.environment, {})
            if not env_reqs:
                return self._warning(
                    f"No specific requirements defined for environment: {self.environment}",
                    details={'environment': self.environment}
                )
            
            # Check environment variables
            if self.check_env_vars:
                env_var_result = await self._check_environment_variables(env_reqs)
                if env_var_result:
                    issues.extend(env_var_result.get('issues', []))
                    details['environment_variables'] = env_var_result
            
            # Check secrets
            if self.check_secrets:
                secrets_result = await self._check_secrets(env_reqs)
                if secrets_result:
                    issues.extend(secrets_result.get('issues', []))
                    details['secrets'] = secrets_result
            
            # Check configuration files
            if self.check_config_files:
                config_result = await self._check_config_files(env_reqs)
                if config_result:
                    issues.extend(config_result.get('issues', []))
                    details['config_files'] = config_result
            
            # Check resource requirements
            resource_result = await self._check_resource_requirements(env_reqs)
            if resource_result:
                issues.extend(resource_result.get('issues', []))
                details['resources'] = resource_result
            
            # Check security requirements for production
            if self.environment == 'production':
                security_result = await self._check_security_requirements(env_reqs)
                if security_result:
                    issues.extend(security_result.get('issues', []))
                    details['security'] = security_result
            
            # Determine overall result
            if not issues:
                return self._success(
                    f"All environment requirements for {self.environment} are satisfied",
                    details=details
                )
            
            # Categorize issues by severity
            critical_issues = [i for i in issues if i.get('severity') == 'critical']
            error_issues = [i for i in issues if i.get('severity') == 'error']
            warning_issues = [i for i in issues if i.get('severity') == 'warning']
            
            if critical_issues:
                return self._critical(
                    f"Critical environment issues for {self.environment}: {len(critical_issues)} critical, "
                    f"{len(error_issues)} errors, {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues, env_reqs)
                )
            elif error_issues:
                return self._error(
                    f"Environment issues for {self.environment}: {len(error_issues)} errors, "
                    f"{len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues, env_reqs)
                )
            else:
                return self._warning(
                    f"Environment warnings for {self.environment}: {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues, env_reqs)
                )
                
        except Exception as e:
            logger.error(f"Environment validation failed: {e}")
            return self._error(
                f"Environment validation failed: {str(e)}",
                details={'error': str(e), 'environment': self.environment},
                remediation_steps=[
                    "Check environment configuration",
                    "Verify all required files and variables are present",
                    "Review validator configuration"
                ]
            )
    
    async def _check_environment_variables(self, env_reqs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check required and optional environment variables."""
        try:
            issues = []
            env_var_status = {}
            
            required_vars = env_reqs.get('required_env_vars', [])
            optional_vars = env_reqs.get('optional_env_vars', [])
            
            # Check required environment variables
            for var_name in required_vars:
                value = os.environ.get(var_name)
                if not value:
                    issues.append({
                        'type': 'missing_required_env_var',
                        'severity': 'error',
                        'message': f'Required environment variable not set: {var_name}',
                        'variable': var_name
                    })
                    env_var_status[var_name] = 'missing'
                else:
                    env_var_status[var_name] = 'present'
            
            # Check optional environment variables
            for var_name in optional_vars:
                value = os.environ.get(var_name)
                if not value:
                    env_var_status[var_name] = 'missing_optional'
                else:
                    env_var_status[var_name] = 'present'
            
            # Environment-specific validations
            if self.environment == 'production':
                # Production should not have DEBUG=True
                debug_value = os.environ.get('DEBUG', '').lower()
                if debug_value in ['true', '1', 'yes']:
                    issues.append({
                        'type': 'debug_enabled_in_production',
                        'severity': 'error',
                        'message': 'DEBUG mode should not be enabled in production',
                        'variable': 'DEBUG'
                    })
            
            return {
                'required_vars': required_vars,
                'optional_vars': optional_vars,
                'env_var_status': env_var_status,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Environment variable check failed: {e}")
            return {
                'env_var_status': {},
                'issues': [{
                    'type': 'env_var_check_error',
                    'severity': 'error',
                    'message': f'Environment variable check failed: {str(e)}'
                }]
            }
    
    async def _check_secrets(self, env_reqs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check required secrets in Secret Manager."""
        try:
            issues = []
            secret_status = {}
            
            required_secrets = env_reqs.get('required_secrets', [])
            
            if not required_secrets:
                return {
                    'required_secrets': [],
                    'secret_status': {},
                    'issues': []
                }
            
            # Check if gcloud is available for secret checking
            try:
                result = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        'gcloud', 'secrets', 'list', '--format=json',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    ),
                    timeout=self.timeout_seconds
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    try:
                        secrets_data = json.loads(stdout.decode())
                        existing_secrets = {secret.get('name', '').split('/')[-1] for secret in secrets_data}
                        
                        # Check each required secret
                        for secret_name in required_secrets:
                            if secret_name in existing_secrets:
                                secret_status[secret_name] = 'exists'
                            else:
                                issues.append({
                                    'type': 'missing_secret',
                                    'severity': 'error',
                                    'message': f'Required secret not found: {secret_name}',
                                    'secret': secret_name
                                })
                                secret_status[secret_name] = 'missing'
                                
                    except json.JSONDecodeError:
                        issues.append({
                            'type': 'secret_list_parse_error',
                            'severity': 'error',
                            'message': 'Could not parse secrets list'
                        })
                else:
                    issues.append({
                        'type': 'secret_list_error',
                        'severity': 'error',
                        'message': f'Could not list secrets: {stderr.decode()}'
                    })
                    
            except FileNotFoundError:
                issues.append({
                    'type': 'gcloud_not_available',
                    'severity': 'error',
                    'message': 'gcloud CLI not available for secret checking'
                })
            except asyncio.TimeoutError:
                issues.append({
                    'type': 'secret_check_timeout',
                    'severity': 'warning',
                    'message': 'Secret check timed out'
                })
            
            return {
                'required_secrets': required_secrets,
                'secret_status': secret_status,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Secret check failed: {e}")
            return {
                'secret_status': {},
                'issues': [{
                    'type': 'secret_check_error',
                    'severity': 'error',
                    'message': f'Secret check failed: {str(e)}'
                }]
            }
    
    async def _check_config_files(self, env_reqs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check required configuration files."""
        try:
            issues = []
            file_status = {}
            
            required_files = env_reqs.get('config_files', [])
            
            for file_path in required_files:
                path = Path(file_path)
                if path.exists():
                    if path.is_file():
                        # Check if file is readable and not empty
                        try:
                            if path.stat().st_size == 0:
                                issues.append({
                                    'type': 'empty_config_file',
                                    'severity': 'warning',
                                    'message': f'Configuration file is empty: {file_path}',
                                    'file': file_path
                                })
                                file_status[file_path] = 'empty'
                            else:
                                file_status[file_path] = 'exists'
                                
                                # Validate specific file types
                                if file_path.endswith('.json'):
                                    await self._validate_json_file(path, issues, file_path)
                                elif file_path.endswith('.yaml') or file_path.endswith('.yml'):
                                    await self._validate_yaml_file(path, issues, file_path)
                                    
                        except Exception as e:
                            issues.append({
                                'type': 'config_file_read_error',
                                'severity': 'error',
                                'message': f'Cannot read configuration file {file_path}: {str(e)}',
                                'file': file_path
                            })
                            file_status[file_path] = 'read_error'
                    else:
                        issues.append({
                            'type': 'config_path_not_file',
                            'severity': 'error',
                            'message': f'Configuration path is not a file: {file_path}',
                            'file': file_path
                        })
                        file_status[file_path] = 'not_file'
                else:
                    issues.append({
                        'type': 'missing_config_file',
                        'severity': 'error',
                        'message': f'Required configuration file not found: {file_path}',
                        'file': file_path
                    })
                    file_status[file_path] = 'missing'
            
            return {
                'required_files': required_files,
                'file_status': file_status,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Config file check failed: {e}")
            return {
                'file_status': {},
                'issues': [{
                    'type': 'config_file_check_error',
                    'severity': 'error',
                    'message': f'Config file check failed: {str(e)}'
                }]
            }
    
    async def _validate_json_file(self, path: Path, issues: List[Dict[str, Any]], file_path: str):
        """Validate JSON configuration file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                json.load(f)
        except json.JSONDecodeError as e:
            issues.append({
                'type': 'invalid_json_config',
                'severity': 'error',
                'message': f'Invalid JSON in configuration file {file_path}: {str(e)}',
                'file': file_path
            })
        except Exception as e:
            issues.append({
                'type': 'json_validation_error',
                'severity': 'error',
                'message': f'Error validating JSON file {file_path}: {str(e)}',
                'file': file_path
            })
    
    async def _validate_yaml_file(self, path: Path, issues: List[Dict[str, Any]], file_path: str):
        """Validate YAML configuration file."""
        try:
            import yaml
            with open(path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
        except ImportError:
            # YAML validation is optional if PyYAML is not installed
            pass
        except yaml.YAMLError as e:
            issues.append({
                'type': 'invalid_yaml_config',
                'severity': 'error',
                'message': f'Invalid YAML in configuration file {file_path}: {str(e)}',
                'file': file_path
            })
        except Exception as e:
            issues.append({
                'type': 'yaml_validation_error',
                'severity': 'error',
                'message': f'Error validating YAML file {file_path}: {str(e)}',
                'file': file_path
            })
    
    async def _check_resource_requirements(self, env_reqs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check minimum resource requirements."""
        try:
            issues = []
            resource_info = {}
            
            min_resources = env_reqs.get('min_resources', {})
            
            if not min_resources:
                return {
                    'min_resources': {},
                    'resource_info': {},
                    'issues': []
                }
            
            # For now, we'll just validate the format and store the requirements
            # In a real implementation, you might check against current resource allocation
            
            required_memory = min_resources.get('memory')
            required_cpu = min_resources.get('cpu')
            
            if required_memory:
                resource_info['required_memory'] = required_memory
                # Validate memory format (e.g., "2Gi", "1024Mi")
                if not self._validate_memory_format(required_memory):
                    issues.append({
                        'type': 'invalid_memory_format',
                        'severity': 'error',
                        'message': f'Invalid memory format: {required_memory}',
                        'resource': 'memory'
                    })
            
            if required_cpu:
                resource_info['required_cpu'] = required_cpu
                # Validate CPU format (e.g., "1", "2", "0.5")
                if not self._validate_cpu_format(required_cpu):
                    issues.append({
                        'type': 'invalid_cpu_format',
                        'severity': 'error',
                        'message': f'Invalid CPU format: {required_cpu}',
                        'resource': 'cpu'
                    })
            
            return {
                'min_resources': min_resources,
                'resource_info': resource_info,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Resource requirement check failed: {e}")
            return {
                'resource_info': {},
                'issues': [{
                    'type': 'resource_check_error',
                    'severity': 'error',
                    'message': f'Resource requirement check failed: {str(e)}'
                }]
            }
    
    async def _check_security_requirements(self, env_reqs: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check security requirements for production environment."""
        try:
            issues = []
            security_info = {}
            
            security_reqs = env_reqs.get('security_requirements', {})
            
            if not security_reqs:
                return {
                    'security_requirements': {},
                    'security_info': {},
                    'issues': []
                }
            
            # Check HTTPS requirement
            if security_reqs.get('https_only'):
                security_info['https_only'] = True
                # In a real implementation, you would check the actual service configuration
                
            # Check CORS restriction requirement
            if security_reqs.get('cors_restricted'):
                security_info['cors_restricted'] = True
                # Check if CORS is properly configured (this would require checking actual config)
                
            # Check rate limiting requirement
            if security_reqs.get('rate_limiting'):
                security_info['rate_limiting'] = True
                # Check if rate limiting is configured
                
            # For now, we'll just note the requirements
            # In a real implementation, you would validate against actual service configuration
            
            return {
                'security_requirements': security_reqs,
                'security_info': security_info,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Security requirement check failed: {e}")
            return {
                'security_info': {},
                'issues': [{
                    'type': 'security_check_error',
                    'severity': 'error',
                    'message': f'Security requirement check failed: {str(e)}'
                }]
            }
    
    def _validate_memory_format(self, memory: str) -> bool:
        """Validate memory format (e.g., '2Gi', '1024Mi')."""
        import re
        pattern = r'^\d+(\.\d+)?(Mi|Gi|Ti|Ki|M|G|T|K)?$'
        return bool(re.match(pattern, memory))
    
    def _validate_cpu_format(self, cpu: str) -> bool:
        """Validate CPU format (e.g., '1', '2', '0.5')."""
        try:
            float(cpu)
            return True
        except ValueError:
            return False
    
    def _get_remediation_steps(self, issues: List[Dict[str, Any]], env_reqs: Dict[str, Any]) -> List[str]:
        """Generate remediation steps based on issues found."""
        steps = []
        
        # Environment variable issues
        env_var_issues = [i for i in issues if i.get('type') in ['missing_required_env_var', 'debug_enabled_in_production']]
        if env_var_issues:
            steps.append("Set required environment variables:")
            for issue in env_var_issues:
                var_name = issue.get('variable', '')
                if var_name:
                    if issue.get('type') == 'debug_enabled_in_production':
                        steps.append(f"  export {var_name}=false")
                    else:
                        steps.append(f"  export {var_name}=<appropriate_value>")
        
        # Secret issues
        secret_issues = [i for i in issues if i.get('type') == 'missing_secret']
        if secret_issues:
            steps.append("Create required secrets in Google Secret Manager:")
            for issue in secret_issues:
                secret_name = issue.get('secret', '')
                if secret_name:
                    steps.append(f"  gcloud secrets create {secret_name} --data-file=<secret_file>")
        
        # Config file issues
        config_issues = [i for i in issues if i.get('type') in ['missing_config_file', 'empty_config_file', 'invalid_json_config', 'invalid_yaml_config']]
        if config_issues:
            steps.append("Fix configuration files:")
            for issue in config_issues:
                file_path = issue.get('file', '')
                if file_path:
                    if issue.get('type') == 'missing_config_file':
                        steps.append(f"  Create missing file: {file_path}")
                    elif issue.get('type') == 'empty_config_file':
                        steps.append(f"  Add content to empty file: {file_path}")
                    else:
                        steps.append(f"  Fix syntax errors in: {file_path}")
        
        # Resource issues
        resource_issues = [i for i in issues if i.get('type') in ['invalid_memory_format', 'invalid_cpu_format']]
        if resource_issues:
            steps.append("Fix resource specification format:")
            steps.append("  Memory format: '2Gi', '1024Mi', etc.")
            steps.append("  CPU format: '1', '2', '0.5', etc.")
        
        if not steps:
            steps.append(f"Review environment configuration for {self.environment}")
            steps.append("Ensure all required resources and settings are properly configured")
        
        return steps