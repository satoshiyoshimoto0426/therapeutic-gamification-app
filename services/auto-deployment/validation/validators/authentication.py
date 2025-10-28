"""
Authentication validator for pre-deployment checks.
"""

import subprocess
import json
import logging
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List

current_dir = os.path.dirname(os.path.abspath(__file__))
validation_dir = os.path.dirname(current_dir)
if validation_dir not in sys.path:
    sys.path.insert(0, validation_dir)

from base import BaseValidator, ValidationResult, ValidationSeverity


logger = logging.getLogger(__name__)


class AuthenticationValidator(BaseValidator):
    """Validator for authentication credentials, service accounts, and API access."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.verify_service_accounts = self.config.get('verify_service_accounts', True)
        self.check_api_keys = self.config.get('check_api_keys', True)
        self.check_environment_vars = self.config.get('check_environment_vars', True)
        self.timeout_seconds = self.config.get('timeout_seconds', 30)
        self.project_id = self.config.get('project_id')
        
        # Required credentials
        self.required_credentials = self.config.get('required_credentials', [
            'GOOGLE_APPLICATION_CREDENTIALS',
            'GOOGLE_CLOUD_PROJECT'
        ])
        
        # GitHub-related authentication
        self.check_github_auth = self.config.get('check_github_auth', True)
        self.github_token_var = self.config.get('github_token_var', 'GITHUB_TOKEN')
    
    @property
    def description(self) -> str:
        return "Validates authentication credentials, service accounts, and API access"
    
    async def validate(self) -> ValidationResult:
        """Run authentication and authorization validation checks."""
        try:
            issues = []
            details = {}
            
            # Check Google Cloud authentication
            gcloud_auth_result = await self._check_gcloud_authentication()
            if gcloud_auth_result:
                issues.extend(gcloud_auth_result.get('issues', []))
                details['gcloud_auth'] = gcloud_auth_result
            
            # Check API keys and credentials
            if self.check_api_keys:
                api_key_result = await self._check_api_credentials()
                if api_key_result:
                    issues.extend(api_key_result.get('issues', []))
                    details['api_credentials'] = api_key_result
            
            # Check environment variables for credentials
            if self.check_environment_vars:
                env_cred_result = await self._check_credential_environment_vars()
                if env_cred_result:
                    issues.extend(env_cred_result.get('issues', []))
                    details['credential_env_vars'] = env_cred_result
            
            # Check GitHub authentication if enabled
            if self.check_github_auth:
                github_auth_result = await self._check_github_authentication()
                if github_auth_result:
                    issues.extend(github_auth_result.get('issues', []))
                    details['github_auth'] = github_auth_result
            
            # Determine overall result
            if not issues:
                return self._success(
                    "All authentication and authorization checks passed",
                    details=details
                )
            
            # Categorize issues by severity
            critical_issues = [i for i in issues if i.get('severity') == 'critical']
            error_issues = [i for i in issues if i.get('severity') == 'error']
            warning_issues = [i for i in issues if i.get('severity') == 'warning']
            
            if critical_issues:
                return self._critical(
                    f"Critical authentication issues found: {len(critical_issues)} critical, "
                    f"{len(error_issues)} errors, {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            elif error_issues:
                return self._error(
                    f"Authentication issues found: {len(error_issues)} errors, "
                    f"{len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            else:
                return self._warning(
                    f"Authentication warnings found: {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
                
        except Exception as e:
            logger.error(f"Authentication validation failed: {e}")
            return self._error(
                f"Authentication validation failed: {str(e)}",
                details={'error': str(e)},
                remediation_steps=[
                    "Check authentication configuration",
                    "Verify all credentials are properly set",
                    "Review validator configuration"
                ]
            )
    
    async def _check_gcloud_authentication(self) -> Optional[Dict[str, Any]]:
        """Check Google Cloud CLI authentication status."""
        try:
            issues = []
            auth_info = {}
            
            # Check if gcloud is available
            try:
                result = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        'gcloud', 'auth', 'list', '--format=json',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    ),
                    timeout=self.timeout_seconds
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    try:
                        auth_data = json.loads(stdout.decode())
                        active_accounts = [acc for acc in auth_data if acc.get('status') == 'ACTIVE']
                        
                        if not active_accounts:
                            issues.append({
                                'type': 'no_active_auth',
                                'severity': 'critical',
                                'message': 'No active Google Cloud authentication found'
                            })
                            auth_info['active_accounts'] = []
                        else:
                            auth_info['active_accounts'] = [acc.get('account') for acc in active_accounts]
                                    
                    except json.JSONDecodeError:
                        issues.append({
                            'type': 'auth_parse_error',
                            'severity': 'error',
                            'message': 'Could not parse gcloud auth list output'
                        })
                else:
                    issues.append({
                        'type': 'auth_list_error',
                        'severity': 'error',
                        'message': f'gcloud auth list failed: {stderr.decode()}'
                    })
                    
            except FileNotFoundError:
                issues.append({
                    'type': 'gcloud_not_found',
                    'severity': 'critical',
                    'message': 'Google Cloud CLI (gcloud) not found'
                })
                auth_info['gcloud_available'] = False
            except asyncio.TimeoutError:
                issues.append({
                    'type': 'auth_check_timeout',
                    'severity': 'error',
                    'message': 'gcloud auth check timed out'
                })
            
            return {
                'auth_info': auth_info,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"gcloud authentication check failed: {e}")
            return {
                'auth_info': {},
                'issues': [{
                    'type': 'auth_check_error',
                    'severity': 'error',
                    'message': f'gcloud authentication check failed: {str(e)}'
                }]
            }
    
    async def _check_api_credentials(self) -> Optional[Dict[str, Any]]:
        """Check API credentials and keys."""
        try:
            issues = []
            credential_info = {}
            
            # Check for Google Application Credentials file
            google_creds_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if google_creds_path:
                creds_path = Path(google_creds_path)
                if creds_path.exists():
                    try:
                        with open(creds_path, 'r') as f:
                            creds_data = json.load(f)
                            
                        credential_info['google_credentials_file'] = {
                            'path': google_creds_path,
                            'type': creds_data.get('type'),
                            'project_id': creds_data.get('project_id'),
                            'client_email': creds_data.get('client_email')
                        }
                        
                        # Validate credential file structure
                        required_fields = ['type', 'project_id', 'private_key', 'client_email']
                        missing_fields = [field for field in required_fields if not creds_data.get(field)]
                        
                        if missing_fields:
                            issues.append({
                                'type': 'incomplete_credentials_file',
                                'severity': 'error',
                                'message': f'Credentials file missing required fields: {missing_fields}',
                                'missing_fields': missing_fields
                            })
                            
                    except json.JSONDecodeError:
                        issues.append({
                            'type': 'invalid_credentials_file',
                            'severity': 'error',
                            'message': f'Invalid JSON in credentials file: {google_creds_path}'
                        })
                    except Exception as e:
                        issues.append({
                            'type': 'credentials_file_read_error',
                            'severity': 'error',
                            'message': f'Could not read credentials file: {str(e)}'
                        })
                else:
                    issues.append({
                        'type': 'credentials_file_not_found',
                        'severity': 'error',
                        'message': f'Credentials file not found: {google_creds_path}'
                    })
            else:
                credential_info['google_credentials_file'] = None
                
            return {
                'credential_info': credential_info,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"API credentials check failed: {e}")
            return {
                'credential_info': {},
                'issues': [{
                    'type': 'api_credentials_check_error',
                    'severity': 'error',
                    'message': f'API credentials check failed: {str(e)}'
                }]
            }
    
    async def _check_credential_environment_vars(self) -> Optional[Dict[str, Any]]:
        """Check credential-related environment variables."""
        try:
            issues = []
            env_var_status = {}
            
            for var_name in self.required_credentials:
                value = os.environ.get(var_name)
                if not value:
                    issues.append({
                        'type': 'missing_credential_env_var',
                        'severity': 'error',
                        'message': f'Required credential environment variable not set: {var_name}',
                        'variable': var_name
                    })
                    env_var_status[var_name] = 'missing'
                else:
                    env_var_status[var_name] = 'present'
            
            return {
                'required_credentials': self.required_credentials,
                'env_var_status': env_var_status,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Credential environment variable check failed: {e}")
            return {
                'env_var_status': {},
                'issues': [{
                    'type': 'credential_env_var_check_error',
                    'severity': 'error',
                    'message': f'Credential environment variable check failed: {str(e)}'
                }]
            }
    
    async def _check_github_authentication(self) -> Optional[Dict[str, Any]]:
        """Check GitHub authentication for CI/CD integration."""
        try:
            issues = []
            github_info = {}
            
            # Check GitHub token environment variable
            github_token = os.environ.get(self.github_token_var)
            if not github_token:
                issues.append({
                    'type': 'missing_github_token',
                    'severity': 'warning',
                    'message': f'GitHub token not found in environment variable: {self.github_token_var}'
                })
                github_info['token_available'] = False
            else:
                github_info['token_available'] = True
                
                # Basic token format validation
                if not github_token.startswith(('ghp_', 'github_pat_')):
                    issues.append({
                        'type': 'invalid_github_token_format',
                        'severity': 'warning',
                        'message': 'GitHub token format may be invalid (should start with ghp_ or github_pat_)'
                    })
            
            return {
                'github_info': github_info,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"GitHub authentication check failed: {e}")
            return {
                'github_info': {},
                'issues': [{
                    'type': 'github_auth_check_error',
                    'severity': 'error',
                    'message': f'GitHub authentication check failed: {str(e)}'
                }]
            }
    
    def _get_remediation_steps(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate remediation steps based on identified issues."""
        remediation_steps = []
        issue_types = {issue.get('type') for issue in issues}
        
        if 'gcloud_not_found' in issue_types:
            remediation_steps.append("Install Google Cloud CLI (gcloud)")
            
        if 'no_active_auth' in issue_types:
            remediation_steps.append("Run 'gcloud auth login' to authenticate")
            
        if 'missing_credential_env_var' in issue_types:
            remediation_steps.append("Set required environment variables (GOOGLE_APPLICATION_CREDENTIALS, GOOGLE_CLOUD_PROJECT)")
            
        if 'credentials_file_not_found' in issue_types:
            remediation_steps.append("Verify the credentials file path and ensure the file exists")
            
        if 'missing_github_token' in issue_types:
            remediation_steps.append("Set GITHUB_TOKEN environment variable with a valid GitHub token")
            
        if not remediation_steps:
            remediation_steps.append("Review authentication configuration and credentials")
            
        return remediation_steps
