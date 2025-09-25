"""
Unit tests for SecretManager.

Tests Google Cloud Secret Manager integration and secret management functionality.
"""

import pytest
import json
import base64
from unittest.mock import Mock, patch, MagicMock

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, grandparent_dir)

from secret_manager import SecretManager, SecretType, SecretMetadata, SecretValue
from config import DeploymentConfig, CloudConfig, Environment
from exceptions import CloudResourceError, SecurityError


class TestSecretManager:
    """Test cases for SecretManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.cloud_config = CloudConfig(
            project_id="test-project",
            region="us-central1",
            service_name="test-service"
        )
        self.deployment_config = DeploymentConfig(
            environment=Environment.DEVELOPMENT,
            cloud_config=self.cloud_config
        )
    
    @patch('secret_manager.secretmanager')
    def test_initialization_with_mock_client(self, mock_secretmanager):
        """Test SecretManager initialization with mocked client."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        secret_manager = SecretManager(self.deployment_config)
        
        assert secret_manager.config == self.deployment_config
        assert secret_manager.project_id == "test-project"
        assert secret_manager.client == mock_client
        assert hasattr(secret_manager, 'logger')
        assert hasattr(secret_manager, 'SYSTEM_SECRETS')
    
    def test_initialization_without_client(self):
        """Test SecretManager initialization without Google Cloud SDK."""
        with patch('secret_manager.secretmanager', None):
            secret_manager = SecretManager(self.deployment_config)
            assert secret_manager.client is None
    
    def test_system_secrets_defined(self):
        """Test that system secrets are properly defined."""
        with patch('secret_manager.secretmanager'):
            secret_manager = SecretManager(self.deployment_config)
            
            expected_secrets = [
                "slack-webhook-url",
                "github-token",
                "database-url",
                "service-account-key",
                "jwt-secret",
                "encryption-key"
            ]
            
            for secret_name in expected_secrets:
                assert secret_name in secret_manager.SYSTEM_SECRETS
                assert isinstance(secret_manager.SYSTEM_SECRETS[secret_name], SecretType)
    
    @patch('secret_manager.secretmanager')
    def test_create_secret_string_value(self, mock_secretmanager):
        """Test creating a secret with string value."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock the create_secret response
        mock_secret = Mock()
        mock_secret.name = "projects/test-project/secrets/development-test-secret"
        mock_client.create_secret.return_value = mock_secret
        
        # Mock the add_secret_version response
        mock_version = Mock()
        mock_version.name = "projects/test-project/secrets/development-test-secret/versions/1"
        mock_client.add_secret_version.return_value = mock_version
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.create_secret(
            "test-secret",
            "secret-value",
            SecretType.API_KEYS,
            "Test secret"
        )
        
        assert isinstance(result, SecretMetadata)
        assert result.name == "test-secret"
        assert result.secret_type == SecretType.API_KEYS
        assert result.description == "Test secret"
        assert result.version == "1"
        
        # Verify client calls
        mock_client.create_secret.assert_called_once()
        mock_client.add_secret_version.assert_called_once()
    
    @patch('secret_manager.secretmanager')
    def test_create_secret_dict_value(self, mock_secretmanager):
        """Test creating a secret with dictionary value."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock responses
        mock_secret = Mock()
        mock_secret.name = "projects/test-project/secrets/development-test-secret"
        mock_client.create_secret.return_value = mock_secret
        
        mock_version = Mock()
        mock_version.name = "projects/test-project/secrets/development-test-secret/versions/1"
        mock_client.add_secret_version.return_value = mock_version
        
        secret_manager = SecretManager(self.deployment_config)
        
        secret_dict = {"username": "admin", "password": "secret123"}
        
        result = secret_manager.create_secret(
            "db-credentials",
            secret_dict,
            SecretType.DATABASE_CREDENTIALS
        )
        
        assert isinstance(result, SecretMetadata)
        assert result.name == "db-credentials"
        assert result.secret_type == SecretType.DATABASE_CREDENTIALS
        
        # Verify that the dictionary was JSON-encoded
        call_args = mock_client.add_secret_version.call_args
        payload_data = call_args[1]['request'].payload.data
        decoded_data = json.loads(payload_data.decode('utf-8'))
        assert decoded_data == secret_dict
    
    @patch('secret_manager.secretmanager')
    @patch('secret_manager.gcp_exceptions')
    def test_create_secret_already_exists(self, mock_exceptions, mock_secretmanager):
        """Test creating a secret that already exists."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock AlreadyExists exception
        mock_exceptions.AlreadyExists = Exception
        mock_client.create_secret.side_effect = mock_exceptions.AlreadyExists("Secret already exists")
        
        secret_manager = SecretManager(self.deployment_config)
        
        # Mock update_secret method
        with patch.object(secret_manager, 'update_secret') as mock_update:
            mock_update.return_value = SecretMetadata(
                name="existing-secret",
                secret_type=SecretType.API_KEYS
            )
            
            result = secret_manager.create_secret(
                "existing-secret",
                "new-value",
                SecretType.API_KEYS
            )
            
            assert isinstance(result, SecretMetadata)
            mock_update.assert_called_once()
    
    @patch('secret_manager.secretmanager')
    def test_get_secret_string_value(self, mock_secretmanager):
        """Test retrieving a secret with string value."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock access_secret_version response
        mock_response = Mock()
        mock_response.payload.data = b"secret-string-value"
        mock_response.name = "projects/test-project/secrets/development-test-secret/versions/1"
        mock_client.access_secret_version.return_value = mock_response
        
        # Mock get_secret response
        mock_secret_info = Mock()
        mock_secret_info.labels = {"secret_type": "api_keys", "environment": "development"}
        mock_secret_info.annotations = {"description": "Test secret"}
        mock_client.get_secret.return_value = mock_secret_info
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.get_secret("test-secret")
        
        assert isinstance(result, SecretValue)
        assert result.value == "secret-string-value"
        assert result.is_binary is False
        assert result.metadata.name == "test-secret"
        assert result.metadata.secret_type == SecretType.API_KEYS
        assert result.metadata.description == "Test secret"
        assert result.metadata.version == "1"
    
    @patch('secret_manager.secretmanager')
    def test_get_secret_json_value(self, mock_secretmanager):
        """Test retrieving a secret with JSON value."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock access_secret_version response with JSON data
        secret_dict = {"username": "admin", "password": "secret123"}
        json_data = json.dumps(secret_dict).encode('utf-8')
        
        mock_response = Mock()
        mock_response.payload.data = json_data
        mock_response.name = "projects/test-project/secrets/development-db-creds/versions/1"
        mock_client.access_secret_version.return_value = mock_response
        
        # Mock get_secret response
        mock_secret_info = Mock()
        mock_secret_info.labels = {"secret_type": "database_credentials", "environment": "development"}
        mock_secret_info.annotations = {"description": "Database credentials"}
        mock_client.get_secret.return_value = mock_secret_info
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.get_secret("db-creds")
        
        assert isinstance(result, SecretValue)
        assert result.value == secret_dict
        assert result.is_binary is False
        assert result.metadata.secret_type == SecretType.DATABASE_CREDENTIALS
    
    @patch('secret_manager.secretmanager')
    @patch('secret_manager.gcp_exceptions')
    def test_get_secret_not_found(self, mock_exceptions, mock_secretmanager):
        """Test retrieving a non-existent secret."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock NotFound exception
        mock_exceptions.NotFound = Exception
        mock_client.access_secret_version.side_effect = mock_exceptions.NotFound("Secret not found")
        
        secret_manager = SecretManager(self.deployment_config)
        
        with pytest.raises(SecurityError, match="Secret not found"):
            secret_manager.get_secret("non-existent-secret")
    
    @patch('secret_manager.secretmanager')
    def test_update_secret(self, mock_secretmanager):
        """Test updating an existing secret."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock add_secret_version response
        mock_version = Mock()
        mock_version.name = "projects/test-project/secrets/development-test-secret/versions/2"
        mock_client.add_secret_version.return_value = mock_version
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.update_secret(
            "test-secret",
            "updated-value",
            SecretType.API_KEYS,
            "Updated description"
        )
        
        assert isinstance(result, SecretMetadata)
        assert result.name == "test-secret"
        assert result.secret_type == SecretType.API_KEYS
        assert result.description == "Updated description"
        assert result.version == "2"
        
        mock_client.add_secret_version.assert_called_once()
    
    @patch('secret_manager.secretmanager')
    def test_delete_secret(self, mock_secretmanager):
        """Test deleting a secret."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.delete_secret("test-secret")
        
        assert result is True
        mock_client.delete_secret.assert_called_once()
    
    @patch('secret_manager.secretmanager')
    @patch('secret_manager.gcp_exceptions')
    def test_delete_secret_not_found(self, mock_exceptions, mock_secretmanager):
        """Test deleting a non-existent secret."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock NotFound exception
        mock_exceptions.NotFound = Exception
        mock_client.delete_secret.side_effect = mock_exceptions.NotFound("Secret not found")
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.delete_secret("non-existent-secret")
        
        assert result is False
    
    @patch('secret_manager.secretmanager')
    def test_list_secrets(self, mock_secretmanager):
        """Test listing secrets."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock list_secrets response
        mock_secret1 = Mock()
        mock_secret1.name = "projects/test-project/secrets/development-secret1"
        mock_secret1.labels = {"secret_type": "api_keys", "environment": "development"}
        mock_secret1.annotations = {"description": "First secret"}
        mock_secret1.create_time = None
        
        mock_secret2 = Mock()
        mock_secret2.name = "projects/test-project/secrets/development-secret2"
        mock_secret2.labels = {"secret_type": "database_credentials", "environment": "development"}
        mock_secret2.annotations = {"description": "Second secret"}
        mock_secret2.create_time = None
        
        # Mock secret from different environment (should be filtered out)
        mock_secret3 = Mock()
        mock_secret3.name = "projects/test-project/secrets/production-secret3"
        mock_secret3.labels = {"secret_type": "api_keys", "environment": "production"}
        mock_secret3.annotations = {"description": "Production secret"}
        mock_secret3.create_time = None
        
        mock_client.list_secrets.return_value = [mock_secret1, mock_secret2, mock_secret3]
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.list_secrets()
        
        assert len(result) == 2  # Only development secrets
        assert all(isinstance(secret, SecretMetadata) for secret in result)
        assert result[0].name == "development-secret1"
        assert result[1].name == "development-secret2"
    
    @patch('secret_manager.secretmanager')
    def test_list_secrets_filtered_by_type(self, mock_secretmanager):
        """Test listing secrets filtered by type."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock list_secrets response
        mock_secret1 = Mock()
        mock_secret1.name = "projects/test-project/secrets/development-api-key"
        mock_secret1.labels = {"secret_type": "api_keys", "environment": "development"}
        mock_secret1.annotations = {}
        mock_secret1.create_time = None
        
        mock_secret2 = Mock()
        mock_secret2.name = "projects/test-project/secrets/development-db-creds"
        mock_secret2.labels = {"secret_type": "database_credentials", "environment": "development"}
        mock_secret2.annotations = {}
        mock_secret2.create_time = None
        
        mock_client.list_secrets.return_value = [mock_secret1, mock_secret2]
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.list_secrets(SecretType.API_KEYS)
        
        assert len(result) == 1
        assert result[0].secret_type == SecretType.API_KEYS
    
    @patch('secret_manager.secretmanager')
    def test_secret_exists_true(self, mock_secretmanager):
        """Test checking if a secret exists (true case)."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock successful get_secret call
        mock_secret = Mock()
        mock_client.get_secret.return_value = mock_secret
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.secret_exists("existing-secret")
        
        assert result is True
        mock_client.get_secret.assert_called_once()
    
    @patch('secret_manager.secretmanager')
    @patch('secret_manager.gcp_exceptions')
    def test_secret_exists_false(self, mock_exceptions, mock_secretmanager):
        """Test checking if a secret exists (false case)."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock NotFound exception
        mock_exceptions.NotFound = Exception
        mock_client.get_secret.side_effect = mock_exceptions.NotFound("Secret not found")
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.secret_exists("non-existent-secret")
        
        assert result is False
    
    def test_normalize_secret_name(self):
        """Test secret name normalization."""
        with patch('secret_manager.secretmanager'):
            secret_manager = SecretManager(self.deployment_config)
            
            # Test basic normalization
            assert secret_manager._normalize_secret_name("test-secret") == "development-test-secret"
            
            # Test invalid characters
            assert secret_manager._normalize_secret_name("test@secret!") == "development-test-secret-"
            
            # Test name starting with number
            assert secret_manager._normalize_secret_name("123secret") == "development-secret-123secret"
            
            # Test long name truncation
            long_name = "a" * 300
            normalized = secret_manager._normalize_secret_name(long_name)
            assert len(normalized) <= 255
            assert normalized.startswith("development-")
    
    @patch('secret_manager.secretmanager')
    @patch.dict(os.environ, {
        'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/test',
        'GITHUB_TOKEN': 'ghp_test_token',
        'DATABASE_URL': 'postgresql://user:pass@host:5432/db'
    })
    def test_setup_deployment_secrets(self, mock_secretmanager):
        """Test setting up deployment secrets from environment variables."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock create_secret responses
        mock_secret = Mock()
        mock_secret.name = "projects/test-project/secrets/development-slack-webhook-url"
        mock_client.create_secret.return_value = mock_secret
        
        mock_version = Mock()
        mock_version.name = "projects/test-project/secrets/development-slack-webhook-url/versions/1"
        mock_client.add_secret_version.return_value = mock_version
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.setup_deployment_secrets()
        
        assert len(result) == 3  # Three environment variables were set
        assert "slack-webhook-url" in result
        assert "github-token" in result
        assert "database-url" in result
        
        # Verify create_secret was called for each secret
        assert mock_client.create_secret.call_count == 3
    
    @patch('secret_manager.secretmanager')
    def test_rotate_secret(self, mock_secretmanager):
        """Test rotating a secret."""
        mock_client = Mock()
        mock_secretmanager.SecretManagerServiceClient.return_value = mock_client
        
        # Mock update_secret
        mock_version = Mock()
        mock_version.name = "projects/test-project/secrets/development-test-secret/versions/2"
        mock_client.add_secret_version.return_value = mock_version
        
        secret_manager = SecretManager(self.deployment_config)
        
        result = secret_manager.rotate_secret("test-secret", "new-rotated-value")
        
        assert isinstance(result, SecretMetadata)
        assert result.name == "test-secret"
        mock_client.add_secret_version.assert_called_once()


class TestSecretMetadata:
    """Test cases for SecretMetadata dataclass."""
    
    def test_secret_metadata_creation(self):
        """Test creating SecretMetadata."""
        metadata = SecretMetadata(
            name="test-secret",
            secret_type=SecretType.API_KEYS,
            description="Test secret",
            labels={"env": "test"},
            version="1"
        )
        
        assert metadata.name == "test-secret"
        assert metadata.secret_type == SecretType.API_KEYS
        assert metadata.description == "Test secret"
        assert metadata.labels == {"env": "test"}
        assert metadata.version == "1"


class TestSecretValue:
    """Test cases for SecretValue dataclass."""
    
    def test_secret_value_creation(self):
        """Test creating SecretValue."""
        metadata = SecretMetadata(
            name="test-secret",
            secret_type=SecretType.API_KEYS
        )
        
        secret_value = SecretValue(
            value="secret-data",
            metadata=metadata,
            is_binary=False
        )
        
        assert secret_value.value == "secret-data"
        assert secret_value.metadata == metadata
        assert secret_value.is_binary is False


if __name__ == '__main__':
    pytest.main([__file__])