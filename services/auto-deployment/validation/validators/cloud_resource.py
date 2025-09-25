"""
Cloud resource validator for pre-deployment checks.
"""

import subprocess
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List

from ..base import BaseValidator, ValidationResult, ValidationSeverity


logger = logging.getLogger(__name__)


class CloudResourceValidator(BaseValidator):
    """Validator for cloud resource availability and configuration."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.check_quotas = self.config.get('check_quotas', True)
        self.verify_permissions = self.config.get('verify_permissions', True)
        self.timeout_seconds = self.config.get('timeout_seconds', 60)
        self.project_id = self.config.get('project_id')
        self.region = self.config.get('region', 'us-central1')
        self.required_apis = self.config.get('required_apis', [
            'run.googleapis.com',
            'cloudbuild.googleapis.com',
            'containerregistry.googleapis.com',
            'secretmanager.googleapis.com'
        ])
        self.required_services = self.config.get('required_services', [
            'Cloud Run',
            'Cloud Build',
            'Container Registry',
            'Secret Manager'
        ])
    
    @property
    def description(self) -> str:
        return "Validates cloud resource availability, quotas, and API enablement"
    
    async def validate(self) -> ValidationResult:
        """Run cloud resource validation checks."""
        try:
            issues = []
            details = {}
            
            # Check if gcloud CLI is available
            gcloud_result = await self._check_gcloud_availability()
            if gcloud_result:
                issues.extend(gcloud_result.get('issues', []))
                details['gcloud'] = gcloud_result
                
                # If gcloud is not available, skip other checks
                if any(issue.get('type') == 'gcloud_missing' for issue in gcloud_result.get('issues', [])):
                    return self._error(
                        "Google Cloud CLI not available - cannot perform cloud resource validation",
                        details=details,
                        remediation_steps=[
                            "Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install",
                            "Run 'gcloud auth login' to authenticate",
                            "Set project with 'gcloud config set project PROJECT_ID'"
                        ]
                    )
            
            # Check project configuration
            project_result = await self._check_project_config()
            if project_result:
                issues.extend(project_result.get('issues', []))
                details['project'] = project_result
            
            # Check API enablement
            api_result = await self._check_api_enablement()
            if api_result:
                issues.extend(api_result.get('issues', []))
                details['apis'] = api_result
            
            # Check quotas if enabled
            if self.check_quotas:
                quota_result = await self._check_quotas()
                if quota_result:
                    issues.extend(quota_result.get('issues', []))
                    details['quotas'] = quota_result
            
            # Check permissions if enabled
            if self.verify_permissions:
                permission_result = await self._check_permissions()
                if permission_result:
                    issues.extend(permission_result.get('issues', []))
                    details['permissions'] = permission_result
            
            # Determine overall result
            if not issues:
                return self._success(
                    "All cloud resource checks passed",
                    details=details
                )
            
            # Categorize issues by severity
            critical_issues = [i for i in issues if i.get('severity') == 'critical']
            error_issues = [i for i in issues if i.get('severity') == 'error']
            warning_issues = [i for i in issues if i.get('severity') == 'warning']
            
            if critical_issues:
                return self._critical(
                    f"Critical cloud resource issues found: {len(critical_issues)} critical, "
                    f"{len(error_issues)} errors, {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            elif error_issues:
                return self._error(
                    f"Cloud resource issues found: {len(error_issues)} errors, "
                    f"{len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            else:
                return self._warning(
                    f"Cloud resource warnings found: {len(warning_issues)} warnings",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
                
        except Exception as e:
            logger.error(f"Cloud resource validation failed: {e}")
            return self._error(
                f"Cloud resource validation failed: {str(e)}",
                details={'error': str(e)},
                remediation_steps=[
                    "Check that Google Cloud CLI is installed and configured",
                    "Verify network connectivity to Google Cloud APIs",
                    "Review validator configuration"
                ]
            )
    
    async def _check_gcloud_availability(self) -> Optional[Dict[str, Any]]:
        """Check if gcloud CLI is available and configured."""
        try:
            # Check if gcloud is installed
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    'gcloud', 'version',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                ),
                timeout=10
            )
            stdout, stderr = await result.communicate()
            
            issues = []
            
            if result.returncode != 0:
                issues.append({
                    'type': 'gcloud_error',
                    'severity': 'error',
                    'message': f'gcloud command failed: {stderr.decode()}'
                })
            
            # Check authentication
            auth_result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    'gcloud', 'auth', 'list', '--format=json',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                ),
                timeout=10
            )
            auth_stdout, auth_stderr = await auth_result.communicate()
            
            if auth_result.returncode == 0:
                try:
                    auth_data = json.loads(auth_stdout.decode())
                    active_accounts = [acc for acc in auth_data if acc.get('status') == 'ACTIVE']
                    if not active_accounts:
                        issues.append({
                            'type': 'gcloud_not_authenticated',
                            'severity': 'error',
                            'message': 'No active gcloud authentication found'
                        })
                except json.JSONDecodeError:
                    issues.append({
                        'type': 'gcloud_auth_check_error',
                        'severity': 'warning',
                        'message': 'Could not parse gcloud auth status'
                    })
            else:
                issues.append({
                    'type': 'gcloud_auth_error',
                    'severity': 'error',
                    'message': f'gcloud auth check failed: {auth_stderr.decode()}'
                })
            
            return {
                'gcloud_available': result.returncode == 0,
                'version_info': stdout.decode() if result.returncode == 0 else None,
                'issues': issues
            }
            
        except FileNotFoundError:
            return {
                'gcloud_available': False,
                'issues': [{
                    'type': 'gcloud_missing',
                    'severity': 'critical',
                    'message': 'Google Cloud CLI (gcloud) not found'
                }]
            }
        except asyncio.TimeoutError:
            return {
                'gcloud_available': False,
                'issues': [{
                    'type': 'gcloud_timeout',
                    'severity': 'error',
                    'message': 'gcloud command timed out'
                }]
            }
        except Exception as e:
            logger.error(f"gcloud availability check failed: {e}")
            return {
                'gcloud_available': False,
                'issues': [{
                    'type': 'gcloud_check_error',
                    'severity': 'error',
                    'message': f'gcloud availability check failed: {str(e)}'
                }]
            }
    
    async def _check_project_config(self) -> Optional[Dict[str, Any]]:
        """Check project configuration."""
        try:
            # Get current project
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    'gcloud', 'config', 'get-value', 'project',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                ),
                timeout=10
            )
            stdout, stderr = await result.communicate()
            
            issues = []
            current_project = None
            
            if result.returncode == 0:
                current_project = stdout.decode().strip()
                if not current_project or current_project == '(unset)':
                    issues.append({
                        'type': 'no_project_set',
                        'severity': 'error',
                        'message': 'No Google Cloud project is set'
                    })
                elif self.project_id and current_project != self.project_id:
                    issues.append({
                        'type': 'wrong_project',
                        'severity': 'warning',
                        'message': f'Current project {current_project} differs from configured project {self.project_id}'
                    })
            else:
                issues.append({
                    'type': 'project_check_error',
                    'severity': 'error',
                    'message': f'Could not get current project: {stderr.decode()}'
                })
            
            return {
                'current_project': current_project,
                'configured_project': self.project_id,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Project config check failed: {e}")
            return {
                'current_project': None,
                'issues': [{
                    'type': 'project_check_error',
                    'severity': 'error',
                    'message': f'Project config check failed: {str(e)}'
                }]
            }
    
    async def _check_api_enablement(self) -> Optional[Dict[str, Any]]:
        """Check if required APIs are enabled."""
        try:
            # Get enabled services
            result = await asyncio.wait_for(
                asyncio.create_subprocess_exec(
                    'gcloud', 'services', 'list', '--enabled', '--format=json',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                ),
                timeout=30
            )
            stdout, stderr = await result.communicate()
            
            issues = []
            enabled_apis = []
            
            if result.returncode == 0:
                try:
                    services_data = json.loads(stdout.decode())
                    enabled_apis = [service.get('name', '') for service in services_data]
                    
                    # Check required APIs
                    for required_api in self.required_apis:
                        if required_api not in enabled_apis:
                            issues.append({
                                'type': 'api_not_enabled',
                                'severity': 'error',
                                'message': f'Required API not enabled: {required_api}',
                                'api': required_api
                            })
                            
                except json.JSONDecodeError:
                    issues.append({
                        'type': 'api_list_parse_error',
                        'severity': 'error',
                        'message': 'Could not parse enabled services list'
                    })
            else:
                issues.append({
                    'type': 'api_list_error',
                    'severity': 'error',
                    'message': f'Could not list enabled services: {stderr.decode()}'
                })
            
            return {
                'enabled_apis': enabled_apis,
                'required_apis': self.required_apis,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"API enablement check failed: {e}")
            return {
                'enabled_apis': [],
                'issues': [{
                    'type': 'api_check_error',
                    'severity': 'error',
                    'message': f'API enablement check failed: {str(e)}'
                }]
            }
    
    async def _check_quotas(self) -> Optional[Dict[str, Any]]:
        """Check resource quotas."""
        try:
            # This is a simplified quota check
            # In a real implementation, you would check specific quotas for Cloud Run, etc.
            
            issues = []
            quota_info = {}
            
            # Check Cloud Run quotas (simplified)
            try:
                result = await asyncio.wait_for(
                    asyncio.create_subprocess_exec(
                        'gcloud', 'run', 'services', 'list', '--region', self.region, '--format=json',
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    ),
                    timeout=20
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode == 0:
                    try:
                        services_data = json.loads(stdout.decode())
                        service_count = len(services_data)
                        quota_info['cloud_run_services'] = service_count
                        
                        # Simple check - warn if approaching typical limits
                        if service_count > 80:  # Assuming 100 service limit
                            issues.append({
                                'type': 'quota_warning',
                                'severity': 'warning',
                                'message': f'High number of Cloud Run services: {service_count}',
                                'service': 'Cloud Run',
                                'current_usage': service_count
                            })
                            
                    except json.JSONDecodeError:
                        logger.warning("Could not parse Cloud Run services list")
                        
            except Exception as e:
                logger.warning(f"Could not check Cloud Run quotas: {e}")
            
            return {
                'quota_info': quota_info,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Quota check failed: {e}")
            return {
                'quota_info': {},
                'issues': [{
                    'type': 'quota_check_error',
                    'severity': 'warning',
                    'message': f'Quota check failed: {str(e)}'
                }]
            }
    
    async def _check_permissions(self) -> Optional[Dict[str, Any]]:
        """Check required permissions."""
        try:
            issues = []
            permissions_info = {}
            
            # Check basic permissions by trying to list resources
            required_permissions = [
                ('Cloud Run', 'gcloud', 'run', 'services', 'list', '--region', self.region),
                ('Cloud Build', 'gcloud', 'builds', 'list', '--limit=1'),
                ('Secret Manager', 'gcloud', 'secrets', 'list', '--limit=1')
            ]
            
            for service_name, *command in required_permissions:
                try:
                    result = await asyncio.wait_for(
                        asyncio.create_subprocess_exec(
                            *command,
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        ),
                        timeout=15
                    )
                    stdout, stderr = await result.communicate()
                    
                    if result.returncode == 0:
                        permissions_info[service_name] = 'accessible'
                    else:
                        error_msg = stderr.decode().lower()
                        if 'permission' in error_msg or 'forbidden' in error_msg or 'unauthorized' in error_msg:
                            issues.append({
                                'type': 'permission_denied',
                                'severity': 'error',
                                'message': f'Insufficient permissions for {service_name}',
                                'service': service_name,
                                'error': stderr.decode()
                            })
                            permissions_info[service_name] = 'permission_denied'
                        else:
                            permissions_info[service_name] = 'error'
                            
                except asyncio.TimeoutError:
                    issues.append({
                        'type': 'permission_check_timeout',
                        'severity': 'warning',
                        'message': f'Permission check for {service_name} timed out',
                        'service': service_name
                    })
                    permissions_info[service_name] = 'timeout'
                    
                except Exception as e:
                    logger.warning(f"Permission check for {service_name} failed: {e}")
                    permissions_info[service_name] = 'error'
            
            return {
                'permissions_info': permissions_info,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return {
                'permissions_info': {},
                'issues': [{
                    'type': 'permission_check_error',
                    'severity': 'error',
                    'message': f'Permission check failed: {str(e)}'
                }]
            }
    
    def _get_remediation_steps(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate remediation steps based on issues found."""
        steps = []
        
        # gcloud issues
        gcloud_issues = [i for i in issues if i.get('type', '').startswith('gcloud')]
        if gcloud_issues:
            steps.append("Install and configure Google Cloud CLI: https://cloud.google.com/sdk/docs/install")
            steps.append("Run 'gcloud auth login' to authenticate")
            steps.append("Set project with 'gcloud config set project PROJECT_ID'")
        
        # Project issues
        project_issues = [i for i in issues if i.get('type') in ['no_project_set', 'wrong_project']]
        if project_issues:
            steps.append("Set the correct Google Cloud project: gcloud config set project PROJECT_ID")
        
        # API issues
        api_issues = [i for i in issues if i.get('type') == 'api_not_enabled']
        if api_issues:
            steps.append("Enable required APIs:")
            for issue in api_issues:
                api = issue.get('api', '')
                if api:
                    steps.append(f"  gcloud services enable {api}")
        
        # Permission issues
        permission_issues = [i for i in issues if i.get('type') == 'permission_denied']
        if permission_issues:
            steps.append("Grant required permissions to your account or service account")
            steps.append("Contact your Google Cloud administrator for access")
        
        # Quota issues
        quota_issues = [i for i in issues if i.get('type') == 'quota_warning']
        if quota_issues:
            steps.append("Review resource usage and clean up unused resources")
            steps.append("Request quota increases if needed")
        
        if not steps:
            steps.append("Review cloud resource configuration and ensure all services are properly set up")
        
        return steps