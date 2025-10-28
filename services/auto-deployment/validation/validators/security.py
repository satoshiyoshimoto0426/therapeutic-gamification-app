"""
Security validator for pre-deployment checks.
"""

import subprocess
import json
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Set
import hashlib

import sys
import os

# Add validation directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
validation_dir = os.path.dirname(current_dir)
if validation_dir not in sys.path:
    sys.path.insert(0, validation_dir)

from base import BaseValidator, ValidationResult, ValidationSeverity


logger = logging.getLogger(__name__)


class SecurityValidator(BaseValidator):
    """Validator for security checks including vulnerability scanning and dependency analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.run_vulnerability_scan = self.config.get('run_vulnerability_scan', True)
        self.check_dependencies = self.config.get('check_dependencies', True)
        self.severity_threshold = self.config.get('severity_threshold', 'medium')
        self.project_root = Path(self.config.get('project_root', '.'))
        self.exclude_patterns = self.config.get('exclude_patterns', [
            '*/tests/*', '*/test_*', '*/__pycache__/*', '*/node_modules/*'
        ])
        self.secret_patterns = self._get_secret_patterns()
    
    @property
    def description(self) -> str:
        return "Validates security through vulnerability scanning, dependency checks, and secret detection"
    
    async def validate(self) -> ValidationResult:
        """Run security validation checks."""
        try:
            issues = []
            details = {}
            
            # Check for secrets in code
            secret_result = await self._check_secrets()
            if secret_result:
                issues.extend(secret_result.get('issues', []))
                details['secrets'] = secret_result
            
            # Run vulnerability scan if enabled
            if self.run_vulnerability_scan:
                vuln_result = await self._run_vulnerability_scan()
                if vuln_result:
                    issues.extend(vuln_result.get('issues', []))
                    details['vulnerabilities'] = vuln_result
            
            # Check dependencies if enabled
            if self.check_dependencies:
                dep_result = await self._check_dependencies()
                if dep_result:
                    issues.extend(dep_result.get('issues', []))
                    details['dependencies'] = dep_result
            
            # Check for insecure configurations
            config_result = await self._check_insecure_configurations()
            if config_result:
                issues.extend(config_result.get('issues', []))
                details['configurations'] = config_result
            
            # Determine overall result
            if not issues:
                return self._success(
                    "All security checks passed",
                    details=details
                )
            
            # Categorize issues by severity
            critical_issues = [i for i in issues if i.get('severity') == 'critical']
            high_issues = [i for i in issues if i.get('severity') == 'high']
            medium_issues = [i for i in issues if i.get('severity') == 'medium']
            low_issues = [i for i in issues if i.get('severity') == 'low']
            
            if critical_issues:
                return self._critical(
                    f"Critical security vulnerabilities found: {len(critical_issues)} critical, "
                    f"{len(high_issues)} high, {len(medium_issues)} medium, {len(low_issues)} low",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            elif high_issues or (medium_issues and self.severity_threshold in ['low', 'medium']):
                return self._error(
                    f"Security vulnerabilities found: {len(high_issues)} high, "
                    f"{len(medium_issues)} medium, {len(low_issues)} low",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
            else:
                return self._warning(
                    f"Low-severity security issues found: {len(medium_issues)} medium, "
                    f"{len(low_issues)} low",
                    details=details,
                    remediation_steps=self._get_remediation_steps(issues)
                )
                
        except Exception as e:
            logger.error(f"Security validation failed: {e}")
            return self._error(
                f"Security validation failed: {str(e)}",
                details={'error': str(e)},
                remediation_steps=[
                    "Check that security scanning tools are installed (bandit, safety)",
                    "Ensure the project structure is correct",
                    "Review validator configuration"
                ]
            )
    
    async def _check_secrets(self) -> Optional[Dict[str, Any]]:
        """Check for hardcoded secrets in the codebase."""
        try:
            issues = []
            files_scanned = 0
            
            # Scan Python files for secrets
            for py_file in self.project_root.rglob('*.py'):
                if self._should_exclude_file(py_file):
                    continue
                
                files_scanned += 1
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        line_number = 0
                        
                        for line in content.split('\n'):
                            line_number += 1
                            for pattern_name, pattern in self.secret_patterns.items():
                                matches = re.finditer(pattern, line, re.IGNORECASE)
                                for match in matches:
                                    issues.append({
                                        'type': 'secret_detected',
                                        'severity': 'critical',
                                        'message': f'Potential {pattern_name} detected',
                                        'file': str(py_file.relative_to(self.project_root)),
                                        'line': line_number,
                                        'pattern': pattern_name,
                                        'matched_text': match.group()[:20] + '...' if len(match.group()) > 20 else match.group()
                                    })
                                    
                except Exception as e:
                    logger.warning(f"Could not scan file {py_file}: {e}")
            
            return {
                'files_scanned': files_scanned,
                'secrets_found': len(issues),
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Secret scanning failed: {e}")
            return {
                'files_scanned': 0,
                'secrets_found': 0,
                'issues': [{
                    'type': 'secret_scan_error',
                    'severity': 'error',
                    'message': f'Secret scanning failed: {str(e)}'
                }]
            }
    
    async def _run_vulnerability_scan(self) -> Optional[Dict[str, Any]]:
        """Run vulnerability scanning using bandit."""
        try:
            # Run bandit security scanner
            result = subprocess.run([
                'python', '-m', 'bandit', '-r', str(self.project_root),
                '-f', 'json', '--skip', 'B101'  # Skip assert_used test
            ], capture_output=True, text=True)
            
            issues = []
            
            if result.stdout:
                try:
                    bandit_output = json.loads(result.stdout)
                    
                    for issue in bandit_output.get('results', []):
                        severity = self._map_bandit_severity(issue.get('issue_severity', 'LOW'))
                        issues.append({
                            'type': 'vulnerability',
                            'severity': severity,
                            'message': issue.get('issue_text', ''),
                            'file': issue.get('filename', ''),
                            'line': issue.get('line_number', 0),
                            'test_id': issue.get('test_id', ''),
                            'test_name': issue.get('test_name', ''),
                            'confidence': issue.get('issue_confidence', 'UNDEFINED')
                        })
                        
                except json.JSONDecodeError:
                    logger.warning("Could not parse bandit JSON output")
                    if result.returncode != 0:
                        issues.append({
                            'type': 'vulnerability_scan_error',
                            'severity': 'warning',
                            'message': 'Vulnerability scan completed with warnings'
                        })
            
            return {
                'total_issues': len(issues),
                'issues': issues
            }
            
        except FileNotFoundError:
            logger.warning("bandit not found, skipping vulnerability scan")
            return {
                'total_issues': 0,
                'issues': [{
                    'type': 'tool_missing',
                    'severity': 'warning',
                    'message': 'bandit not installed, skipping vulnerability scanning'
                }]
            }
        except Exception as e:
            logger.error(f"Vulnerability scanning failed: {e}")
            return {
                'total_issues': 1,
                'issues': [{
                    'type': 'vulnerability_scan_error',
                    'severity': 'error',
                    'message': f'Vulnerability scanning failed: {str(e)}'
                }]
            }
    
    async def _check_dependencies(self) -> Optional[Dict[str, Any]]:
        """Check dependencies for known vulnerabilities using safety."""
        try:
            # Run safety check
            result = subprocess.run([
                'python', '-m', 'safety', 'check', '--json'
            ], capture_output=True, text=True)
            
            issues = []
            
            if result.stdout:
                try:
                    safety_output = json.loads(result.stdout)
                    
                    for vuln in safety_output:
                        severity = self._map_safety_severity(vuln)
                        issues.append({
                            'type': 'dependency_vulnerability',
                            'severity': severity,
                            'message': f"Vulnerable dependency: {vuln.get('package', 'unknown')} {vuln.get('installed_version', '')}",
                            'package': vuln.get('package', ''),
                            'installed_version': vuln.get('installed_version', ''),
                            'vulnerability_id': vuln.get('vulnerability_id', ''),
                            'advisory': vuln.get('advisory', ''),
                            'more_info_url': vuln.get('more_info_url', '')
                        })
                        
                except json.JSONDecodeError:
                    if result.returncode != 0 and result.stderr:
                        issues.append({
                            'type': 'dependency_check_error',
                            'severity': 'warning',
                            'message': f'Dependency check failed: {result.stderr}'
                        })
            
            return {
                'total_vulnerabilities': len(issues),
                'issues': issues
            }
            
        except FileNotFoundError:
            logger.warning("safety not found, skipping dependency vulnerability check")
            return {
                'total_vulnerabilities': 0,
                'issues': [{
                    'type': 'tool_missing',
                    'severity': 'warning',
                    'message': 'safety not installed, skipping dependency vulnerability checks'
                }]
            }
        except Exception as e:
            logger.error(f"Dependency vulnerability check failed: {e}")
            return {
                'total_vulnerabilities': 1,
                'issues': [{
                    'type': 'dependency_check_error',
                    'severity': 'error',
                    'message': f'Dependency vulnerability check failed: {str(e)}'
                }]
            }
    
    async def _check_insecure_configurations(self) -> Optional[Dict[str, Any]]:
        """Check for insecure configurations."""
        try:
            issues = []
            
            # Check for debug mode in production files
            for config_file in self.project_root.rglob('*.py'):
                if self._should_exclude_file(config_file):
                    continue
                
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        line_number = 0
                        
                        for line in content.split('\n'):
                            line_number += 1
                            line_lower = line.lower().strip()
                            
                            # Check for debug mode
                            if 'debug' in line_lower and ('true' in line_lower or '= true' in line_lower):
                                issues.append({
                                    'type': 'insecure_config',
                                    'severity': 'medium',
                                    'message': 'Debug mode may be enabled',
                                    'file': str(config_file.relative_to(self.project_root)),
                                    'line': line_number,
                                    'details': 'Debug mode should be disabled in production'
                                })
                            
                            # Check for insecure SSL settings
                            if 'ssl_verify' in line_lower and 'false' in line_lower:
                                issues.append({
                                    'type': 'insecure_config',
                                    'severity': 'high',
                                    'message': 'SSL verification disabled',
                                    'file': str(config_file.relative_to(self.project_root)),
                                    'line': line_number,
                                    'details': 'SSL verification should not be disabled'
                                })
                                
                except Exception as e:
                    logger.warning(f"Could not scan config file {config_file}: {e}")
            
            return {
                'total_issues': len(issues),
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Configuration security check failed: {e}")
            return {
                'total_issues': 1,
                'issues': [{
                    'type': 'config_check_error',
                    'severity': 'error',
                    'message': f'Configuration security check failed: {str(e)}'
                }]
            }
    
    def _get_secret_patterns(self) -> Dict[str, str]:
        """Get regex patterns for detecting secrets."""
        return {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'password': r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']([^"\']{8,})["\']',
            'secret_key': r'(?i)(secret[_-]?key|secretkey)\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})["\']?',
            'private_key': r'-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----',
            'aws_access_key': r'(?i)(aws[_-]?access[_-]?key[_-]?id|access[_-]?key)\s*[:=]\s*["\']?(AKIA[0-9A-Z]{16})["\']?',
            'aws_secret_key': r'(?i)(aws[_-]?secret[_-]?access[_-]?key|secret[_-]?key)\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?',
            'github_token': r'(?i)(github[_-]?token|gh[_-]?token)\s*[:=]\s*["\']?(ghp_[a-zA-Z0-9]{36}|gho_[a-zA-Z0-9]{36})["\']?',
            'jwt_token': r'(?i)(jwt[_-]?token|bearer[_-]?token)\s*[:=]\s*["\']?(eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+)["\']?'
        }
    
    def _should_exclude_file(self, file_path: Path) -> bool:
        """Check if file should be excluded from scanning."""
        file_str = str(file_path)
        for pattern in self.exclude_patterns:
            if pattern.replace('*', '') in file_str:
                return True
        return False
    
    def _map_bandit_severity(self, bandit_severity: str) -> str:
        """Map bandit severity to our severity levels."""
        severity_map = {
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low'
        }
        return severity_map.get(bandit_severity.upper(), 'medium')
    
    def _map_safety_severity(self, vuln: Dict[str, Any]) -> str:
        """Map safety vulnerability to severity level."""
        # Safety doesn't provide severity, so we infer from advisory text
        advisory = vuln.get('advisory', '').lower()
        if any(word in advisory for word in ['critical', 'remote code execution', 'rce']):
            return 'critical'
        elif any(word in advisory for word in ['high', 'sql injection', 'xss', 'csrf']):
            return 'high'
        elif any(word in advisory for word in ['medium', 'denial of service', 'dos']):
            return 'medium'
        else:
            return 'medium'  # Default to medium for safety vulnerabilities
    
    def _get_remediation_steps(self, issues: List[Dict[str, Any]]) -> List[str]:
        """Generate remediation steps based on issues found."""
        steps = []
        
        # Secret issues
        secret_issues = [i for i in issues if i.get('type') == 'secret_detected']
        if secret_issues:
            steps.append("Remove hardcoded secrets from code and use environment variables or secret management")
            steps.append("Add secrets to .gitignore to prevent future commits")
            steps.append("Rotate any exposed credentials immediately")
        
        # Vulnerability issues
        vuln_issues = [i for i in issues if i.get('type') == 'vulnerability']
        if vuln_issues:
            steps.append("Fix security vulnerabilities identified by bandit")
            steps.append("Review and update code to follow security best practices")
        
        # Dependency issues
        dep_issues = [i for i in issues if i.get('type') == 'dependency_vulnerability']
        if dep_issues:
            steps.append("Update vulnerable dependencies to secure versions")
            steps.append("Run: pip install --upgrade <package_name> for each vulnerable package")
            steps.append("Consider using pip-audit for ongoing dependency monitoring")
        
        # Configuration issues
        config_issues = [i for i in issues if i.get('type') == 'insecure_config']
        if config_issues:
            steps.append("Fix insecure configuration settings")
            steps.append("Ensure debug mode is disabled in production")
            steps.append("Enable SSL verification for all external connections")
        
        # Tool missing issues
        missing_tools = [i for i in issues if i.get('type') == 'tool_missing']
        if missing_tools:
            steps.append("Install missing security tools: pip install bandit safety")
        
        if not steps:
            steps.append("Review security configuration and ensure all tools are properly set up")
        
        return steps