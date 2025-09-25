"""
Service Account Manager for auto-deployment system.

Handles Google Cloud IAM service account creation, management,
and key generation for deployment environments.
"""

import logging
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

try:
    from google.cloud import iam
    from google.cloud import resourcemanager_v1
    from google.oauth2 import service_account
    from googleapiclient import discovery
    from googleapiclient.errors import HttpError
except ImportError:
    # Mock imports for testing environments without Google Cloud SDK
    iam = None
    resourcemanager_v1 = None
    service_account = None
    discovery = None
    HttpError = Exception

import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import DeploymentConfig, Environment
from exceptions import CloudResourceError, SecurityError


class ServiceAccountRole(Enum):
    """Common service account roles for deployment."""
    CLOUD_RUN_DEVELOPER = "roles/run.developer"
    CLOUD_RUN_INVOKER = "roles/run.invoker"
    FIRESTORE_USER = "roles/datastore.user"
    SECRET_MANAGER_ACCESSOR = "roles/secretmanager.secretAccessor"
    STORAGE_ADMIN = "roles/storage.admin"
    LOGGING_WRITER = "roles/logging.logWriter"
    MONITORING_WRITER = "roles/monitoring.metricWriter"
    CLOUD_BUILD_EDITOR = "roles/cloudbuild.builds.editor"
    SERVICE_ACCOUNT_USER = "roles/iam.serviceAccountUser"


@dataclass
class ServiceAccountInfo:
    """Information about a service account."""
    name: str
    email: str
    display_name: str
    description: Optional[str] = None
    unique_id: Optional[str] = None
    project_id: Optional[str] = None
    roles: Optional[List[str]] = None
    key_id: Optional[str] = None
    created_at: Optional[str] = None


@dataclass
class ServiceAccountKey:
    """Service account key information."""
    key_id: str
    key_type: str
    private_key_data: str
    service_account_email: str
    created_at: Optional[str] = None


class ServiceAccountManager:
    """
    Manages Google Cloud IAM service accounts for deployment.
    
    Provides functionality to create, configure, and manage service accounts
    with appropriate roles and permissions for the deployment system.
    """
    
    def __init__(self, config: DeploymentConfig, credentials_path: Optional[str] = None):
        self.config = config
        self.project_id = config.cloud_config.project_id
        self.credentials_path = credentials_path
        self.logger = logging.getLogger(__name__)
        
        # Initialize IAM client
        self.iam_client = self._initialize_iam_client()
        self.resource_manager = self._initialize_resource_manager()
        
        # Default service accounts for deployment
        self.DEFAULT_SERVICE_ACCOUNTS = {
            "deployment-runner": {
                "display_name": "Auto-Deployment Runner",
                "description": "Service account for running automated deployments",
                "roles": [
                    ServiceAccountRole.CLOUD_RUN_DEVELOPER.value,
                    ServiceAccountRole.CLOUD_BUILD_EDITOR.value,
                    ServiceAccountRole.STORAGE_ADMIN.value,
                    ServiceAccountRole.LOGGING_WRITER.value
                ]
            },
            "app-runtime": {
                "display_name": "Application Runtime",
                "description": "Service account for the running application",
                "roles": [
                    ServiceAccountRole.FIRESTORE_USER.value,
                    ServiceAccountRole.SECRET_MANAGER_ACCESSOR.value,
                    ServiceAccountRole.LOGGING_WRITER.value,
                    ServiceAccountRole.MONITORING_WRITER.value
                ]
            }
        }
    
    def _initialize_iam_client(self):
        """Initialize Google Cloud IAM client."""
        if iam is None:
            self.logger.warning("Google Cloud IAM not available")
            return None
        
        try:
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                return discovery.build('iam', 'v1', credentials=credentials)
            else:
                return discovery.build('iam', 'v1')
        except Exception as e:
            self.logger.error(f"Failed to initialize IAM client: {e}")
            raise CloudResourceError(f"Failed to initialize IAM client: {e}")
    
    def _initialize_resource_manager(self):
        """Initialize Google Cloud Resource Manager client."""
        if resourcemanager_v1 is None:
            self.logger.warning("Google Cloud Resource Manager not available")
            return None
        
        try:
            if self.credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                return discovery.build('cloudresourcemanager', 'v1', credentials=credentials)
            else:
                return discovery.build('cloudresourcemanager', 'v1')
        except Exception as e:
            self.logger.error(f"Failed to initialize Resource Manager client: {e}")
            raise CloudResourceError(f"Failed to initialize Resource Manager client: {e}")
    
    def create_service_account(
        self,
        account_name: str,
        display_name: str,
        description: Optional[str] = None,
        roles: Optional[List[str]] = None
    ) -> ServiceAccountInfo:
        """
        Create a new service account.
        
        Args:
            account_name: Name of the service account
            display_name: Display name for the service account
            description: Optional description
            roles: Optional list of roles to assign
            
        Returns:
            ServiceAccountInfo for the created service account
        """
        if self.iam_client is None:
            raise CloudResourceError("IAM client not available")
        
        try:
            self.logger.info(f"Creating service account: {account_name}")
            
            # Normalize account name
            normalized_name = self._normalize_account_name(account_name)
            
            # Create service account
            service_account_body = {
                'accountId': normalized_name,
                'serviceAccount': {
                    'displayName': display_name,
                    'description': description or f"Service account for {account_name}"
                }
            }
            
            request = self.iam_client.projects().serviceAccounts().create(
                name=f'projects/{self.project_id}',
                body=service_account_body
            )
            
            response = request.execute()
            
            service_account_email = response['email']
            
            # Assign roles if provided
            if roles:
                self._assign_roles(service_account_email, roles)
            
            self.logger.info(f"Service account created successfully: {service_account_email}")
            
            return ServiceAccountInfo(
                name=normalized_name,
                email=service_account_email,
                display_name=display_name,
                description=description,
                unique_id=response.get('uniqueId'),
                project_id=self.project_id,
                roles=roles,
                created_at=response.get('creationTime')
            )
            
        except HttpError as e:
            if e.resp.status == 409:
                self.logger.warning(f"Service account already exists: {account_name}")
                # Return existing service account info
                return self.get_service_account(account_name)
            else:
                self.logger.error(f"Failed to create service account {account_name}: {e}")
                raise SecurityError(f"Failed to create service account: {e}")
        except Exception as e:
            self.logger.error(f"Failed to create service account {account_name}: {e}")
            raise SecurityError(f"Failed to create service account: {e}")
    
    def get_service_account(self, account_name: str) -> ServiceAccountInfo:
        """
        Get information about a service account.
        
        Args:
            account_name: Name of the service account
            
        Returns:
            ServiceAccountInfo for the service account
        """
        if self.iam_client is None:
            raise CloudResourceError("IAM client not available")
        
        try:
            normalized_name = self._normalize_account_name(account_name)
            service_account_email = f"{normalized_name}@{self.project_id}.iam.gserviceaccount.com"
            
            request = self.iam_client.projects().serviceAccounts().get(
                name=f'projects/{self.project_id}/serviceAccounts/{service_account_email}'
            )
            
            response = request.execute()
            
            # Get assigned roles
            roles = self._get_service_account_roles(service_account_email)
            
            return ServiceAccountInfo(
                name=normalized_name,
                email=response['email'],
                display_name=response.get('displayName', ''),
                description=response.get('description'),
                unique_id=response.get('uniqueId'),
                project_id=self.project_id,
                roles=roles,
                created_at=response.get('creationTime')
            )
            
        except HttpError as e:
            if e.resp.status == 404:
                raise SecurityError(f"Service account not found: {account_name}")
            else:
                raise SecurityError(f"Failed to get service account: {e}")
        except Exception as e:
            self.logger.error(f"Failed to get service account {account_name}: {e}")
            raise SecurityError(f"Failed to get service account: {e}")
    
    def delete_service_account(self, account_name: str) -> bool:
        """
        Delete a service account.
        
        Args:
            account_name: Name of the service account to delete
            
        Returns:
            True if successful
        """
        if self.iam_client is None:
            raise CloudResourceError("IAM client not available")
        
        try:
            self.logger.info(f"Deleting service account: {account_name}")
            
            normalized_name = self._normalize_account_name(account_name)
            service_account_email = f"{normalized_name}@{self.project_id}.iam.gserviceaccount.com"
            
            request = self.iam_client.projects().serviceAccounts().delete(
                name=f'projects/{self.project_id}/serviceAccounts/{service_account_email}'
            )
            
            request.execute()
            
            self.logger.info(f"Service account deleted successfully: {service_account_email}")
            return True
            
        except HttpError as e:
            if e.resp.status == 404:
                self.logger.warning(f"Service account not found for deletion: {account_name}")
                return False
            else:
                self.logger.error(f"Failed to delete service account {account_name}: {e}")
                raise SecurityError(f"Failed to delete service account: {e}")
        except Exception as e:
            self.logger.error(f"Failed to delete service account {account_name}: {e}")
            raise SecurityError(f"Failed to delete service account: {e}")
    
    def create_service_account_key(self, account_name: str) -> ServiceAccountKey:
        """
        Create a new key for a service account.
        
        Args:
            account_name: Name of the service account
            
        Returns:
            ServiceAccountKey with the private key data
        """
        if self.iam_client is None:
            raise CloudResourceError("IAM client not available")
        
        try:
            self.logger.info(f"Creating key for service account: {account_name}")
            
            normalized_name = self._normalize_account_name(account_name)
            service_account_email = f"{normalized_name}@{self.project_id}.iam.gserviceaccount.com"
            
            request = self.iam_client.projects().serviceAccounts().keys().create(
                name=f'projects/{self.project_id}/serviceAccounts/{service_account_email}',
                body={'keyAlgorithm': 'KEY_ALG_RSA_2048'}
            )
            
            response = request.execute()
            
            self.logger.info(f"Service account key created successfully")
            
            return ServiceAccountKey(
                key_id=response['name'].split('/')[-1],
                key_type=response.get('keyType', 'USER_MANAGED'),
                private_key_data=response['privateKeyData'],
                service_account_email=service_account_email,
                created_at=response.get('validAfterTime')
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create service account key for {account_name}: {e}")
            raise SecurityError(f"Failed to create service account key: {e}")
    
    def list_service_accounts(self) -> List[ServiceAccountInfo]:
        """
        List all service accounts in the project.
        
        Returns:
            List of ServiceAccountInfo objects
        """
        if self.iam_client is None:
            raise CloudResourceError("IAM client not available")
        
        try:
            self.logger.debug("Listing service accounts")
            
            request = self.iam_client.projects().serviceAccounts().list(
                name=f'projects/{self.project_id}'
            )
            
            response = request.execute()
            
            service_accounts = []
            
            for account in response.get('accounts', []):
                # Filter for deployment-related accounts
                if self._is_deployment_account(account['email']):
                    roles = self._get_service_account_roles(account['email'])
                    
                    service_accounts.append(ServiceAccountInfo(
                        name=account['email'].split('@')[0],
                        email=account['email'],
                        display_name=account.get('displayName', ''),
                        description=account.get('description'),
                        unique_id=account.get('uniqueId'),
                        project_id=self.project_id,
                        roles=roles,
                        created_at=account.get('creationTime')
                    ))
            
            return service_accounts
            
        except Exception as e:
            self.logger.error(f"Failed to list service accounts: {e}")
            raise SecurityError(f"Failed to list service accounts: {e}")
    
    def setup_deployment_service_accounts(self) -> Dict[str, ServiceAccountInfo]:
        """
        Set up default service accounts required for deployment.
        
        Returns:
            Dictionary mapping account names to ServiceAccountInfo
        """
        self.logger.info("Setting up deployment service accounts")
        
        created_accounts = {}
        
        for account_name, config in self.DEFAULT_SERVICE_ACCOUNTS.items():
            try:
                # Add environment prefix to account name
                env_account_name = f"{self.config.environment.value}-{account_name}"
                
                account_info = self.create_service_account(
                    env_account_name,
                    config["display_name"],
                    config["description"],
                    config["roles"]
                )
                
                created_accounts[account_name] = account_info
                
            except Exception as e:
                self.logger.warning(f"Failed to create service account {account_name}: {e}")
        
        return created_accounts
    
    def _assign_roles(self, service_account_email: str, roles: List[str]) -> None:
        """Assign IAM roles to a service account."""
        if self.resource_manager is None:
            self.logger.warning("Resource Manager not available, skipping role assignment")
            return
        
        try:
            # Get current IAM policy
            request = self.resource_manager.projects().getIamPolicy(
                resource=self.project_id,
                body={}
            )
            
            policy = request.execute()
            
            # Add service account to roles
            bindings = policy.get('bindings', [])
            
            for role in roles:
                # Find existing binding for this role
                binding = None
                for b in bindings:
                    if b['role'] == role:
                        binding = b
                        break
                
                if binding is None:
                    # Create new binding
                    binding = {
                        'role': role,
                        'members': []
                    }
                    bindings.append(binding)
                
                # Add service account to members
                member = f"serviceAccount:{service_account_email}"
                if member not in binding['members']:
                    binding['members'].append(member)
            
            # Update policy
            policy['bindings'] = bindings
            
            set_request = self.resource_manager.projects().setIamPolicy(
                resource=self.project_id,
                body={'policy': policy}
            )
            
            set_request.execute()
            
            self.logger.info(f"Assigned roles to {service_account_email}: {roles}")
            
        except Exception as e:
            self.logger.error(f"Failed to assign roles to {service_account_email}: {e}")
            raise SecurityError(f"Failed to assign roles: {e}")
    
    def _get_service_account_roles(self, service_account_email: str) -> List[str]:
        """Get roles assigned to a service account."""
        if self.resource_manager is None:
            return []
        
        try:
            request = self.resource_manager.projects().getIamPolicy(
                resource=self.project_id,
                body={}
            )
            
            policy = request.execute()
            roles = []
            
            member = f"serviceAccount:{service_account_email}"
            
            for binding in policy.get('bindings', []):
                if member in binding.get('members', []):
                    roles.append(binding['role'])
            
            return roles
            
        except Exception as e:
            self.logger.warning(f"Failed to get roles for {service_account_email}: {e}")
            return []
    
    def _normalize_account_name(self, account_name: str) -> str:
        """
        Normalize service account name to comply with Google Cloud naming rules.
        
        Args:
            account_name: Original account name
            
        Returns:
            Normalized account name
        """
        import re
        
        # Replace invalid characters with hyphens
        normalized = re.sub(r'[^a-zA-Z0-9-]', '-', account_name)
        
        # Ensure it starts with a letter
        if not normalized[0].isalpha():
            normalized = f"sa-{normalized}"
        
        # Ensure it's not too long (max 30 characters for service account ID)
        if len(normalized) > 30:
            normalized = normalized[:30]
        
        # Remove trailing hyphens
        normalized = normalized.rstrip('-')
        
        return normalized.lower()
    
    def _is_deployment_account(self, email: str) -> bool:
        """Check if a service account is related to deployment."""
        deployment_keywords = [
            'deployment', 'deploy', 'runner', 'app', 'runtime',
            self.config.environment.value
        ]
        
        email_lower = email.lower()
        return any(keyword in email_lower for keyword in deployment_keywords)
    
    def rotate_service_account_key(self, account_name: str, old_key_id: Optional[str] = None) -> ServiceAccountKey:
        """
        Rotate a service account key by creating a new one and optionally deleting the old one.
        
        Args:
            account_name: Name of the service account
            old_key_id: Optional ID of the old key to delete
            
        Returns:
            ServiceAccountKey for the new key
        """
        self.logger.info(f"Rotating key for service account: {account_name}")
        
        # Create new key
        new_key = self.create_service_account_key(account_name)
        
        # Delete old key if provided
        if old_key_id:
            try:
                self._delete_service_account_key(account_name, old_key_id)
                self.logger.info(f"Old key deleted: {old_key_id}")
            except Exception as e:
                self.logger.warning(f"Failed to delete old key {old_key_id}: {e}")
        
        return new_key
    
    def _delete_service_account_key(self, account_name: str, key_id: str) -> None:
        """Delete a service account key."""
        if self.iam_client is None:
            raise CloudResourceError("IAM client not available")
        
        normalized_name = self._normalize_account_name(account_name)
        service_account_email = f"{normalized_name}@{self.project_id}.iam.gserviceaccount.com"
        
        request = self.iam_client.projects().serviceAccounts().keys().delete(
            name=f'projects/{self.project_id}/serviceAccounts/{service_account_email}/keys/{key_id}'
        )
        
        request.execute()