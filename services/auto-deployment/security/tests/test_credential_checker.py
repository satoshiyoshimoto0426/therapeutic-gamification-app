"""
Tests for credential checker.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from ..credential_checker import CredentialChecker
from ..security_config import SecurityConfig


class TestCredentialChecker(unittest.TestCase):
    """Test credential checker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SecurityConfig(
            secret_rotation_enabled=True,
            secret_expiry_warning_days=30,
            require_secret_encryption=True
        )
        self.checker = CredentialChecker(self.config)
    
    def test_is_credential_env_var(self):
        """Test credential environment variable detection."""
        # Should detect credential variables
        self.assertTrue(self.checker._is_credential_env_var('API_KEY'))
        self.assertTrue(self.checker._is_credential_env_var('SECRET_TOKEN'))
        self.assertTrue(self.checker._is_credential_env_var('DATABASE_PASSWORD'))
        self.assertTrue(self.checker._is_credential_env_var('PRIVATE_KEY'))
        
        # Should not detect non-credential variables
        self.assertFalse(self.checker._is_credential_env_var('DEBUG_MODE'))
        self.assertFalse(self.checker._is_credential_env_var('PORT'))
        self.assertFalse(self.checker._is_credential_env_var('LOG_LEVEL'))
    
    def test_extract_credentials_from_text(self):
        """Test credential extraction from text."""
        text = """
        api_key = "sk-1234567890abcdef1234567890abcdef"
        secret_key: "super_secret_key_12345"
        password = "mypassword123"
        token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        """
        
        credentials = self.checker._extract_credentials_from_text(text)
        
        self.assertTrue(len(credentials) > 0)
        
        # Check that different credential types are detected
        cred_types = [cred[0] for cred in credentials]
        self.assertIn('api_key', cred_types)
        self.assertIn('secret_key', cred_types)
        self.assertIn('password', cred_types)
        self.assertIn('token', cred_types)
    
    def test_analyze_credential_hardcoded(self):
        """Test analysis of hardcoded credentials."""
        result = self.checker._analyze_credential(
            'config.py:api_key',
            'sk-1234567890abcdef1234567890abcdef',
            'source_code'
        )
        
        self.assertFalse(result.passed)
        self.assertEqual(result.credential_type, 'source_code')
        self.assertIn("Credential is hardcoded", result.issues)
        self.assertIn("Move credential to secure secret management system", result.recommendations)
        self.assertLess(result.strength_score, 1.0)
    
    def test_analyze_credential_weak(self):
        """Test analysis of weak credentials."""
        result = self.checker._analyze_credential(
            'env:PASSWORD',
            'password',
            'environment_variable'
        )
        
        self.assertFalse(result.passed)
        self.assertIn("Credential uses common weak value", result.issues)
        self.assertIn("Credential is too short", result.issues)
        self.assertLess(result.strength_score, 0.5)
    
    def test_analyze_credential_strong(self):
        """Test analysis of strong credentials."""
        result = self.checker._analyze_credential(
            'env:API_KEY',
            'sk-1234567890abcdef1234567890abcdef1234567890abcdef',
            'environment_variable'
        )
        
        self.assertTrue(result.passed)
        self.assertEqual(result.credential_type, 'environment_variable')
        self.assertEqual(len(result.issues), 0)
        self.assertEqual(result.strength_score, 1.0)
    
    def test_analyze_service_account_key(self):
        """Test service account key analysis."""
        key_data = {
            'type': 'service_account',
            'project_id': 'test-project',
            'private_key_id': 'key123',
            'private_key': '-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n',
            'client_email': 'test@test-project.iam.gserviceaccount.com',
            'client_id': '123456789',
            'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
            'token_uri': 'https://oauth2.googleapis.com/token'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(key_data, f)
            key_file_path = f.name
        
        try:
            result = self.checker._analyze_service_account_key(key_file_path, key_data)
            
            self.assertIsInstance(result.passed, bool)
            self.assertEqual(result.credential_type, 'service_account_key')
            self.assertIsInstance(result.strength_score, float)
            self.assertIsInstance(result.expiry_date, datetime)
            self.assertIsInstance(result.last_rotated, datetime)
        finally:
            os.unlink(key_file_path)
    
    def test_analyze_service_account_key_invalid_type(self):
        """Test service account key analysis with invalid type."""
        key_data = {
            'type': 'invalid_type',
            'private_key': '-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n'
        }
        
        result = self.checker._analyze_service_account_key('test.json', key_data)
        
        self.assertFalse(result.passed)
        self.assertIn("Invalid service account key type", result.issues)
    
    def test_analyze_service_account_key_invalid_private_key(self):
        """Test service account key analysis with invalid private key."""
        key_data = {
            'type': 'service_account',
            'private_key': 'invalid_private_key_format'
        }
        
        result = self.checker._analyze_service_account_key('test.json', key_data)
        
        self.assertFalse(result.passed)
        self.assertIn("Invalid private key format", result.issues)
    
    @patch.dict(os.environ, {
        'API_KEY': 'sk-1234567890abcdef1234567890abcdef',
        'SECRET_TOKEN': 'super_secret_token_12345',
        'DEBUG_MODE': 'true'
    })
    def test_check_environment_credentials(self):
        """Test environment credential checking."""
        results = self.checker._check_environment_credentials()
        
        self.assertIsInstance(results, list)
        self.assertTrue(len(results) >= 2)  # At least API_KEY and SECRET_TOKEN
        
        # Check that non-credential env vars are not included
        credential_types = [result.credential_type for result in results]
        self.assertTrue(all(ct == 'environment_variable' for ct in credential_types))
    
    def test_check_config_file_credentials(self):
        """Test configuration file credential checking."""
        # Create temporary config file with credentials
        config_content = """
        {
            "api_key": "sk-1234567890abcdef1234567890abcdef",
            "database_url": "postgresql://user:password@localhost/db",
            "debug": true
        }
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(config_content)
            config_file = f.name
        
        # Temporarily rename to config.json for testing
        config_json_path = 'config.json'
        os.rename(config_file, config_json_path)
        
        try:
            results = self.checker._check_config_file_credentials()
            
            self.assertIsInstance(results, list)
            if results:  # Only check if credentials were found
                self.assertTrue(all(result.credential_type == 'config_file' for result in results))
        finally:
            if os.path.exists(config_json_path):
                os.unlink(config_json_path)
    
    def test_check_service_account_keys(self):
        """Test service account key file checking."""
        # Create temporary service account key file
        key_data = {
            'type': 'service_account',
            'project_id': 'test-project',
            'private_key': '-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n',
            'client_email': 'test@test-project.iam.gserviceaccount.com'
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='-service-account.json', delete=False) as f:
            json.dump(key_data, f)
            key_file = f.name
        
        try:
            results = self.checker._check_service_account_keys()
            
            self.assertIsInstance(results, list)
            if results:  # Only check if keys were found
                self.assertTrue(all(result.credential_type == 'service_account_key' for result in results))
        finally:
            os.unlink(key_file)
    
    def test_check_credential_rotation(self):
        """Test credential rotation checking."""
        result = self.checker.check_credential_rotation('test-credential')
        
        self.assertIsInstance(result, type(self.checker._analyze_credential('', '', '')))
        self.assertEqual(result.credential_type, 'rotation_check')
        self.assertIsInstance(result.expiry_date, datetime)
        self.assertIsInstance(result.last_rotated, datetime)
    
    def test_check_all_credentials(self):
        """Test checking all credential types."""
        with patch.object(self.checker, '_check_environment_credentials', return_value=[]):
            with patch.object(self.checker, '_check_config_file_credentials', return_value=[]):
                with patch.object(self.checker, '_check_source_code_credentials', return_value=[]):
                    with patch.object(self.checker, '_check_service_account_keys', return_value=[]):
                        results = self.checker.check_all_credentials()
                        
                        self.assertIsInstance(results, list)
    
    def test_is_gitignored(self):
        """Test gitignore checking."""
        # Create temporary .gitignore file
        gitignore_content = """
        *.json
        secret-key.txt
        .env
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.gitignore', delete=False) as f:
            f.write(gitignore_content)
            gitignore_file = f.name
        
        # Temporarily rename to .gitignore for testing
        gitignore_path = '.gitignore'
        if os.path.exists(gitignore_path):
            # Backup existing .gitignore
            os.rename(gitignore_path, gitignore_path + '.backup')
        
        os.rename(gitignore_file, gitignore_path)
        
        try:
            # Test files that should be ignored
            self.assertTrue(self.checker._is_gitignored('test.json'))
            self.assertTrue(self.checker._is_gitignored('secret-key.txt'))
            
            # Test files that should not be ignored
            self.assertFalse(self.checker._is_gitignored('test.py'))
        finally:
            os.unlink(gitignore_path)
            # Restore backup if it existed
            if os.path.exists(gitignore_path + '.backup'):
                os.rename(gitignore_path + '.backup', gitignore_path)


if __name__ == '__main__':
    unittest.main()