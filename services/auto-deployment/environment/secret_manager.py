"""
Secret Manager for auto-deployment system.

Handles Google Cloud Secret Manager integration, secret creation,
retrieval, and management for deployment environments.
"""

import logging
import json
import base64
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

try:
    from google.cloud import secretmanager
    from google.oauth2 import service_account
    from google.api_core import exceptions as gcp_exceptions
except ImportError:
    # Mock imports for testing environments without Google Cloud SDK
    secretmanager = None
    service_account = None
    gcp_exceptions = None

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import DeploymentConfig
from exceptions import CloudResourceError, SecurityError


class SecretType(Enum):
    """Types of secrets managed by the system."""
    DATABASE_CREDENTIALS = "database_credentials"
    API_KEYS = "api_keys"
    SERVICE_ACCOUNT_KEY = "service_account_key"
    WEBHOOK_URLS = "webhook_urls"
    CERTIFICATES = "certificates"
    CUSTOM = "custom"


@dataclass
class SecretMetadata:
    """Metadata for a secret."""
    name: str
    secret_type: SecretType
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    version: Optional[str] = None


@dataclass
class SecretValue:
    """Container for secret value and metadata."""
    value: Union[str, bytes, Dict[str, Any]]
    metadata: SecretMetadata
    is_binary: bool = False


class SecretManager:
    """
    Manages secrets using Google Cloud Secret Manager.
    
    Provides functionality to create, retrieve, update, and delete secrets
    with proper encryption and access control.
    """
    
    def __init__(self, config: DeploymentConfig, credentials_path: Optional[str] = None):
        self.config = config
        self.project_id = config.cloud_config.project_id
        self.credentials_path = credentials_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize Secret Manager client
        self.client = self._initialize_client()
        
        # Common secret names for the deployment system
        self.SYSTEM_SECRETS = {
            "slack-webhook-url": SecretType.WEBHOOK_URLS,
            "github-token": SecretType.API_KEYS,
            "database-url": SecretType.DATABASE_CREDENTIALS,
            "service-account-key": SecretType.SERVICE_ACCOUNT_KEY,
            "jwt-secret": SecretType.API_KEYS,
            "encryption-key": SecretType.API_KEYS
        }
    
    def _initialize_client(self):
        """Initialize Google Cloud Secret Manager client."""
        if secretmanager is None:
            self.logger.warning("Google Cloud Secret Manager not available")
            return None
        
        try:
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                return secretmanager.SecretManagerServiceClient(credentials=credentials)
            else:
                return secretmanager.SecretManagerServiceClient()
        except Exception as e:
            self.logger.error(f"Failed to initialize Secret Manager client: {e}")
            raise CloudResourceError(f"Failed to initialize Secret Manager: {e}")
    
    def create_secret(
        self,
        secret_name: str,
        secret_value: Union[str, bytes, Dict[str, Any]],
        secret_type: SecretType = SecretType.CUSTOM,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> SecretMetadata:
        """
        Create a new secret in Google Cloud Secret Manager.
        
        Args:
            secret_name: Name of the secret
            secret_value: Value to store
            secret_type: Type of secret
            description: Optional description
            labels: Optional labels for the secret
            
        Returns:
            SecretMetadata for the created secret
        """
        if self.client is None:
            raise CloudResourceError("Secret Manager client not available")
        
        try:
            self.logger.info(f"Creating secret: {secret_name}")
            
            # Prepare secret value
            if isinstance(secret_value, dict):
                secret_data = json.dumps(secret_value).encode('utf-8')
            elif isinstance(secret_value, str):
                secret_data = secret_value.encode('utf-8')
            else:
                secret_data = secret_value
            
            # Create secret
            parent = f"projects/{self.project_id}"
            secret_id = self._normalize_secret_name(secret_name)
            
            # Prepare labels
            secret_labels = labels or {}
            secret_labels.update({
                "environment": self.config.environment.value,
                "secret_type": secret_type.value,
                "managed_by": "auto-deployment"
            })
            
            # Create the secret
            secret = secretmanager.Secret(
                labels=secret_labels
            )
            
            if description:
                secret.annotations = {"description": description}
            
            create_secret_request = secretmanager.CreateSecretRequest(
                parent=parent,
                secret_id=secret_id,
                secret=secret
            )
            
            created_secret = self.client.create_secret(request=create_secret_request)
            
            # Add the secret version
            add_version_request = secretmanager.AddSecretVersionRequest(
                parent=created_secret.name,
                payload=secretmanager.SecretPayload(data=secret_data)
            )
            
            version = self.client.add_secret_version(request=add_version_request)
            
            self.logger.info(f"Secret created successfully: {secret_name}")
            
            return SecretMetadata(
                name=secret_name,
                secret_type=secret_type,
                description=description,
                labels=secret_labels,
                version=version.name.split("/")[-1]
            )
            
        except gcp_exceptions.AlreadyExists:
            self.logger.warning(f"Secret already exists: {secret_name}")
            # Update the existing secret instead
            return self.update_secret(secret_name, secret_value, secret_type, description, labels)
        except Exception as e:
            self.logger.error(f"Failed to create secret {secret_name}: {e}")
            raise SecurityError(f"Failed to create secret: {e}")
    
    def get_secret(self, secret_name: str, version: str = "latest") -> SecretValue:
        """
        Retrieve a secret value from Google Cloud Secret Manager.
        
        Args:
            secret_name: Name of the secret
            version: Version of the secret to retrieve
            
        Returns:
            SecretValue containing the secret data and metadata
        """
        if self.client is None:
            raise CloudResourceError("Secret Manager client not available")
        
        try:
            self.logger.debug(f"Retrieving secret: {secret_name}")
            
            secret_id = self._normalize_secret_name(secret_name)
            name = f"projects/{self.project_id}/secrets/{secret_id}/versions/{version}"
            
            # Get the secret version
            response = self.client.access_secret_version(request={"name": name})
            
            # Decode the secret value
            secret_data = response.payload.data
            
            # Try to decode as JSON first, then as string
            try:
                secret_value = json.loads(secret_data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError):
                try:
                    secret_value = secret_data.decode('utf-8')
                    is_binary = False
                except UnicodeDecodeError:
                    secret_value = secret_data
                    is_binary = True
            else:
                is_binary = False
            
            # Get secret metadata
            secret_info = self.client.get_secret(
                request={"name": f"projects/{self.project_id}/secrets/{secret_id}"}
            )
            
            metadata = SecretMetadata(
                name=secret_name,
                secret_type=SecretType(secret_info.labels.get("secret_type", "custom")),
                description=secret_info.annotations.get("description"),
                labels=dict(secret_info.labels),
                version=response.name.split("/")[-1]
            )
            
            return SecretValue(
                value=secret_value,
                metadata=metadata,
                is_binary=is_binary
            )
            
        except gcp_exceptions.NotFound:
            raise SecurityError(f"Secret not found: {secret_name}")
        except Exception as e:
            self.logger.error(f"Failed to retrieve secret {secret_name}: {e}")
            raise SecurityError(f"Failed to retrieve secret: {e}")
    
    def update_secret(
        self,
        secret_name: str,
        secret_value: Union[str, bytes, Dict[str, Any]],
        secret_type: Optional[SecretType] = None,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> SecretMetadata:
        """
        Update an existing secret with a new value.
        
        Args:
            secret_name: Name of the secret
            secret_value: New value to store
            secret_type: Optional new type
            description: Optional new description
            labels: Optional new labels
            
        Returns:
            SecretMetadata for the updated secret
        """
        if self.client is None:
            raise CloudResourceError("Secret Manager client not available")
        
        try:
            self.logger.info(f"Updating secret: {secret_name}")
            
            secret_id = self._normalize_secret_name(secret_name)
            secret_path = f"projects/{self.project_id}/secrets/{secret_id}"
            
            # Prepare secret value
            if isinstance(secret_value, dict):
                secret_data = json.dumps(secret_value).encode('utf-8')
            elif isinstance(secret_value, str):
                secret_data = secret_value.encode('utf-8')
            else:
                secret_data = secret_value
            
            # Add new version
            add_version_request = secretmanager.AddSecretVersionRequest(
                parent=secret_path,
                payload=secretmanager.SecretPayload(data=secret_data)
            )
            
            version = self.client.add_secret_version(request=add_version_request)
            
            # Update metadata if provided
            if secret_type or description or labels:
                secret_info = self.client.get_secret(request={"name": secret_path})
                
                update_mask = []
                
                if labels:
                    secret_info.labels.clear()
                    secret_info.labels.update(labels)
                    secret_info.labels.update({
                        "environment": self.config.environment.value,
                        "managed_by": "auto-deployment"
                    })
                    if secret_type:
                        secret_info.labels["secret_type"] = secret_type.value
                    update_mask.append("labels")
                
                if description:
                    secret_info.annotations["description"] = description
                    update_mask.append("annotations")
                
                if update_mask:
                    update_request = secretmanager.UpdateSecretRequest(
                        secret=secret_info,
                        update_mask={"paths": update_mask}
                    )
                    self.client.update_secret(request=update_request)
            
            self.logger.info(f"Secret updated successfully: {secret_name}")
            
            return SecretMetadata(
                name=secret_name,
                secret_type=secret_type or SecretType.CUSTOM,
                description=description,
                labels=labels,
                version=version.name.split("/")[-1]
            )
            
        except gcp_exceptions.NotFound:
            # Secret doesn't exist, create it
            return self.create_secret(secret_name, secret_value, secret_type or SecretType.CUSTOM, description, labels)
        except Exception as e:
            self.logger.error(f"Failed to update secret {secret_name}: {e}")
            raise SecurityError(f"Failed to update secret: {e}")
    
    def delete_secret(self, secret_name: str) -> bool:
        """
        Delete a secret from Google Cloud Secret Manager.
        
        Args:
            secret_name: Name of the secret to delete
            
        Returns:
            True if successful
        """
        if self.client is None:
            raise CloudResourceError("Secret Manager client not available")
        
        try:
            self.logger.info(f"Deleting secret: {secret_name}")
            
            secret_id = self._normalize_secret_name(secret_name)
            name = f"projects/{self.project_id}/secrets/{secret_id}"
            
            self.client.delete_secret(request={"name": name})
            
            self.logger.info(f"Secret deleted successfully: {secret_name}")
            return True
            
        except gcp_exceptions.NotFound:
            self.logger.warning(f"Secret not found for deletion: {secret_name}")
            return False
        except Exception as e:
            self.logger.error(f"Failed to delete secret {secret_name}: {e}")
            raise SecurityError(f"Failed to delete secret: {e}")
    
    def list_secrets(self, secret_type: Optional[SecretType] = None) -> List[SecretMetadata]:
        """
        List all secrets in the project.
        
        Args:
            secret_type: Optional filter by secret type
            
        Returns:
            List of SecretMetadata objects
        """
        if self.client is None:
            raise CloudResourceError("Secret Manager client not available")
        
        try:
            self.logger.debug("Listing secrets")
            
            parent = f"projects/{self.project_id}"
            secrets = []
            
            for secret in self.client.list_secrets(request={"parent": parent}):
                # Filter by environment
                if secret.labels.get("environment") != self.config.environment.value:
                    continue
                
                # Filter by secret type if specified
                if secret_type and secret.labels.get("secret_type") != secret_type.value:
                    continue
                
                metadata = SecretMetadata(
                    name=secret.name.split("/")[-1],
                    secret_type=SecretType(secret.labels.get("secret_type", "custom")),
                    description=secret.annotations.get("description"),
                    labels=dict(secret.labels),
                    created_at=secret.create_time.isoformat() if secret.create_time else None
                )
                
                secrets.append(metadata)
            
            return secrets
            
        except Exception as e:
            self.logger.error(f"Failed to list secrets: {e}")
            raise SecurityError(f"Failed to list secrets: {e}")
    
    def secret_exists(self, secret_name: str) -> bool:
        """
        Check if a secret exists.
        
        Args:
            secret_name: Name of the secret
            
        Returns:
            True if secret exists
        """
        if self.client is None:
            return False
        
        try:
            secret_id = self._normalize_secret_name(secret_name)
            name = f"projects/{self.project_id}/secrets/{secret_id}"
            
            self.client.get_secret(request={"name": name})
            return True
            
        except gcp_exceptions.NotFound:
            return False
        except Exception as e:
            self.logger.error(f"Error checking secret existence {secret_name}: {e}")
            return False
    
    def setup_deployment_secrets(self) -> Dict[str, SecretMetadata]:
        """
        Set up common secrets required for deployment.
        
        Returns:
            Dictionary mapping secret names to their metadata
        """
        self.logger.info("Setting up deployment secrets")
        
        created_secrets = {}
        
        # Get secrets from environment variables or prompt
        secret_values = self._get_deployment_secret_values()
        
        for secret_name, secret_type in self.SYSTEM_SECRETS.items():
            if secret_name in secret_values:
                try:
                    metadata = self.create_secret(
                        secret_name,
                        secret_values[secret_name],
                        secret_type,
                        description=f"Auto-deployment {secret_type.value}"
                    )
                    created_secrets[secret_name] = metadata
                except Exception as e:
                    self.logger.warning(f"Failed to create secret {secret_name}: {e}")
        
        return created_secrets
    
    def _get_deployment_secret_values(self) -> Dict[str, str]:
        """Get secret values from environment variables."""
        secret_values = {}
        
        # Map environment variables to secret names
        env_var_mapping = {
            "SLACK_WEBHOOK_URL": "slack-webhook-url",
            "GITHUB_TOKEN": "github-token",
            "DATABASE_URL": "database-url",
            "SERVICE_ACCOUNT_KEY": "service-account-key",
            "JWT_SECRET": "jwt-secret",
            "ENCRYPTION_KEY": "encryption-key"
        }
        
        for env_var, secret_name in env_var_mapping.items():
            value = os.getenv(env_var)
            if value:
                secret_values[secret_name] = value
        
        return secret_values
    
    def _normalize_secret_name(self, secret_name: str) -> str:
        """
        Normalize secret name to comply with Google Cloud Secret Manager naming rules.
        
        Args:
            secret_name: Original secret name
            
        Returns:
            Normalized secret name
        """
        # Replace invalid characters with hyphens
        import re
        normalized = re.sub(r'[^a-zA-Z0-9_-]', '-', secret_name)
        
        # Ensure it starts with a letter
        if not normalized[0].isalpha():
            normalized = f"secret-{normalized}"
        
        # Ensure it's not too long (max 255 characters)
        if len(normalized) > 255:
            normalized = normalized[:255]
        
        # Add environment prefix to avoid conflicts
        env_prefix = self.config.environment.value
        if not normalized.startswith(f"{env_prefix}-"):
            normalized = f"{env_prefix}-{normalized}"
        
        return normalized.lower()
    
    def rotate_secret(self, secret_name: str, new_value: Union[str, bytes, Dict[str, Any]]) -> SecretMetadata:
        """
        Rotate a secret by creating a new version and optionally disabling old versions.
        
        Args:
            secret_name: Name of the secret to rotate
            new_value: New secret value
            
        Returns:
            SecretMetadata for the new version
        """
        self.logger.info(f"Rotating secret: {secret_name}")
        
        # Update with new value
        metadata = self.update_secret(secret_name, new_value)
        
        # TODO: Implement old version cleanup if needed
        # This could involve disabling old versions after a grace period
        
        return metadata
    
    def backup_secrets(self, output_file: str, encrypt: bool = True) -> None:
        """
        Backup secrets to an encrypted file.
        
        Args:
            output_file: Path to output file
            encrypt: Whether to encrypt the backup
        """
        self.logger.info(f"Backing up secrets to: {output_file}")
        
        secrets = self.list_secrets()
        backup_data = {}
        
        for secret_metadata in secrets:
            try:
                secret_value = self.get_secret(secret_metadata.name)
                backup_data[secret_metadata.name] = {
                    "value": secret_value.value if not secret_value.is_binary else base64.b64encode(secret_value.value).decode(),
                    "metadata": {
                        "secret_type": secret_metadata.secret_type.value,
                        "description": secret_metadata.description,
                        "labels": secret_metadata.labels,
                        "is_binary": secret_value.is_binary
                    }
                }
            except Exception as e:
                self.logger.warning(f"Failed to backup secret {secret_metadata.name}: {e}")
        
        # Save backup
        with open(output_file, 'w', encoding='utf-8') as f:
            if encrypt:
                # TODO: Implement encryption
                self.logger.warning("Encryption not implemented, saving as plain JSON")
            
            json.dump(backup_data, f, indent=2)
        
        self.logger.info(f"Backup completed: {len(backup_data)} secrets saved")