"""
Credential security checker.
"""

import os
import json
import re
import hashlib
import base64
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .models import CredentialResult
from .security_config import SecurityConfig


class CredentialChecker:
    """Checks credential security and compliance."""
    
    def __init__(self, config: SecurityConfig):
        """Initialize credential checker."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Common patterns for credential detection
        self.credential_patterns = {
            'api_key': [
                r'api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
                r'apikey["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
            ],
            'secret_key': [
                r'secret[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
                r'secretkey["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
            ],
            'password': [
                r'password["\']?\s*[:=]\s*["\']?([^\s"\']{8,})',
                r'passwd["\']?\s*[:=]\s*["\']?([^\s"\']{8,})',
            ],
            'token': [
                r'token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
                r'access[_-]?token["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_-]{20,})',
            ],
            'private_key': [
                r'-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----',
                r'private[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9+/=]{100,})',
            ],
            'database_url': [
                r'database[_-]?url["\']?\s*[:=]\s*["\']?((?:postgresql|mysql|mongodb)://[^\s"\']+)',
                r'db[_-]?url["\']?\s*[:=]\s*["\']?((?:postgresql|mysql|mongodb)://[^\s"\']+)',
            ]
        }
    
    def check_all_credentials(self) -> List[CredentialResult]:
        """Check all credential types."""
        results = []
        
        # Check environment variables
        results.extend(self._check_environment_credentials())
        
        # Check configuration files
        results.extend(self._check_config_file_credentials())
        
        # Check source code
        results.extend(self._check_source_code_credentials())
        
        # Check service account keys
        results.extend(self._check_service_account_keys())
        
        return results
    
    def _check_environment_credentials(self) -> List[CredentialResult]:
        """Check environment variables for credentials."""
        results = []
        
        for key, value in os.environ.items():
            if self._is_credential_env_var(key):
                result = self._analyze_credential(key, value, 'environment_variable')
                results.append(result)
        
        return results
    
    def _check_config_file_credentials(self) -> List[CredentialResult]:
        """Check configuration files for hardcoded credentials."""
        results = []
        config_files = [
            '.env',
            'config.json',
            'config.yaml',
            'config.yml',
            'settings.json',
            'app.config'
        ]
        
        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        content = f.read()
                    
                    credentials = self._extract_credentials_from_text(content)
                    for cred_type, cred_value in credentials:
                        result = self._analyze_credential(
                            f"{config_file}:{cred_type}",
                            cred_value,
                            'config_file'
                        )
                        results.append(result)
                        
                except Exception as e:
                    self.logger.warning(f"Could not read config file {config_file}: {e}")
        
        return results
    
    def _check_source_code_credentials(self) -> List[CredentialResult]:
        """Check source code for hardcoded credentials."""
        results = []
        
        # Check common source code directories
        source_dirs = ['src', 'services', 'lib', 'app']
        
        for source_dir in source_dirs:
            if os.path.exists(source_dir):
                for root, dirs, files in os.walk(source_dir):
                    for file in files:
                        if file.endswith(('.py', '.js', '.ts', '.java', '.go', '.rb')):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                
                                credentials = self._extract_credentials_from_text(content)
                                for cred_type, cred_value in credentials:
                                    result = self._analyze_credential(
                                        f"{file_path}:{cred_type}",
                                        cred_value,
                                        'source_code'
                                    )
                                    results.append(result)
                                    
                            except Exception as e:
                                self.logger.warning(f"Could not read source file {file_path}: {e}")
        
        return results
    
    def _check_service_account_keys(self) -> List[CredentialResult]:
        """Check service account key files."""
        results = []
        
        # Look for service account key files
        key_patterns = ['*service-account*.json', '*credentials*.json', '*key*.json']
        
        for root, dirs, files in os.walk('.'):
            for file in files:
                if any(pattern.replace('*', '') in file.lower() for pattern in key_patterns):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = json.load(f)
                        
                        if 'private_key' in content and 'client_email' in content:
                            result = self._analyze_service_account_key(file_path, content)
                            results.append(result)
                            
                    except Exception as e:
                        self.logger.warning(f"Could not read key file {file_path}: {e}")
        
        return results
    
    def _is_credential_env_var(self, key: str) -> bool:
        """Check if environment variable name suggests it contains credentials."""
        credential_keywords = [
            'key', 'secret', 'password', 'token', 'auth', 'credential',
            'api', 'private', 'cert', 'ssl', 'tls'
        ]
        
        key_lower = key.lower()
        return any(keyword in key_lower for keyword in credential_keywords)
    
    def _extract_credentials_from_text(self, text: str) -> List[tuple]:
        """Extract potential credentials from text."""
        credentials = []
        
        for cred_type, patterns in self.credential_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    if match.groups():
                        credentials.append((cred_type, match.group(1)))
                    else:
                        credentials.append((cred_type, match.group(0)))
        
        return credentials
    
    def _analyze_credential(self, identifier: str, value: str, cred_type: str) -> CredentialResult:
        """Analyze a credential for security issues."""
        issues = []
        recommendations = []
        strength_score = 1.0
        
        # Check if credential is hardcoded
        if cred_type in ['config_file', 'source_code']:
            issues.append("Credential is hardcoded")
            recommendations.append("Move credential to secure secret management system")
            strength_score -= 0.5
        
        # Check credential strength
        if len(value) < 20:
            issues.append("Credential is too short")
            recommendations.append("Use longer, more complex credentials")
            strength_score -= 0.2
        
        # Check for common weak patterns
        if value.lower() in ['password', '123456', 'admin', 'secret']:
            issues.append("Credential uses common weak value")
            recommendations.append("Use strong, unique credentials")
            strength_score -= 0.4
        
        # Check for base64 encoding (potential credential)
        try:
            decoded = base64.b64decode(value)
            if len(decoded) > 10:
                issues.append("Credential appears to be base64 encoded")
                recommendations.append("Ensure encoded credentials are properly secured")
        except:
            pass
        
        # Check expiry (mock implementation)
        expiry_date = None
        last_rotated = None
        
        # For service account keys, check creation date
        if 'service-account' in identifier.lower():
            # Mock: assume keys should be rotated every 90 days
            last_rotated = datetime.now() - timedelta(days=30)  # Mock
            expiry_date = last_rotated + timedelta(days=90)
            
            if expiry_date < datetime.now() + timedelta(days=self.config.secret_expiry_warning_days):
                issues.append("Credential is expiring soon")
                recommendations.append("Rotate credential before expiry")
                strength_score -= 0.1
        
        passed = len(issues) == 0
        
        return CredentialResult(
            passed=passed,
            credential_type=cred_type,
            issues=issues,
            recommendations=recommendations,
            expiry_date=expiry_date,
            last_rotated=last_rotated,
            strength_score=max(0.0, strength_score)
        )
    
    def _analyze_service_account_key(self, file_path: str, key_data: Dict) -> CredentialResult:
        """Analyze service account key security."""
        issues = []
        recommendations = []
        strength_score = 1.0
        
        # Check if key file is in version control
        if os.path.exists('.git') and not self._is_gitignored(file_path):
            issues.append("Service account key file not in .gitignore")
            recommendations.append("Add service account key files to .gitignore")
            strength_score -= 0.3
        
        # Check key type
        if key_data.get('type') != 'service_account':
            issues.append("Invalid service account key type")
            recommendations.append("Use proper service account keys")
            strength_score -= 0.2
        
        # Check private key format
        private_key = key_data.get('private_key', '')
        if not private_key.startswith('-----BEGIN PRIVATE KEY-----'):
            issues.append("Invalid private key format")
            recommendations.append("Ensure private key is in proper PEM format")
            strength_score -= 0.2
        
        # Mock: Check key age (in real implementation, would check creation date)
        last_rotated = datetime.now() - timedelta(days=45)  # Mock
        expiry_date = last_rotated + timedelta(days=90)
        
        if expiry_date < datetime.now() + timedelta(days=self.config.secret_expiry_warning_days):
            issues.append("Service account key is expiring soon")
            recommendations.append("Rotate service account key")
            strength_score -= 0.1
        
        passed = len(issues) == 0
        
        return CredentialResult(
            passed=passed,
            credential_type='service_account_key',
            issues=issues,
            recommendations=recommendations,
            expiry_date=expiry_date,
            last_rotated=last_rotated,
            strength_score=max(0.0, strength_score)
        )
    
    def _is_gitignored(self, file_path: str) -> bool:
        """Check if file is in .gitignore."""
        try:
            if os.path.exists('.gitignore'):
                with open('.gitignore', 'r') as f:
                    gitignore_content = f.read()
                
                # Simple check - in real implementation would use proper gitignore parsing
                filename = os.path.basename(file_path)
                return filename in gitignore_content or '*.json' in gitignore_content
        except:
            pass
        
        return False
    
    def check_credential_rotation(self, credential_id: str) -> CredentialResult:
        """Check if credential needs rotation."""
        # Mock implementation - in real system would check actual rotation dates
        issues = []
        recommendations = []
        
        # Mock: assume credential was last rotated 60 days ago
        last_rotated = datetime.now() - timedelta(days=60)
        next_rotation = last_rotated + timedelta(days=self.config.key_rotation_days)
        
        if next_rotation < datetime.now():
            issues.append("Credential rotation is overdue")
            recommendations.append("Rotate credential immediately")
        elif next_rotation < datetime.now() + timedelta(days=self.config.secret_expiry_warning_days):
            issues.append("Credential rotation is due soon")
            recommendations.append("Schedule credential rotation")
        
        passed = len(issues) == 0
        strength_score = 1.0 if passed else 0.5
        
        return CredentialResult(
            passed=passed,
            credential_type='rotation_check',
            issues=issues,
            recommendations=recommendations,
            expiry_date=next_rotation,
            last_rotated=last_rotated,
            strength_score=strength_score
        )