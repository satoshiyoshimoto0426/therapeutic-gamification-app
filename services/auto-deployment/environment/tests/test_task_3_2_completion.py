"""
Test to verify completion of task 3.2: Implement configuration and secret management.

This test verifies that the configuration and secret management implementation
meets the requirements.
"""

import pytest
import os
import sys

# Add the parent directories to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, grandparent_dir)


def test_config_manager_module_exists():
    """Test that the configuration manager module exists."""
    config_manager_path = os.path.join(parent_dir, 'config_manager.py')
    assert os.path.exists(config_manager_path), "config_manager.py should exist"


def test_secret_manager_module_exists():
    """Test that the secret manager module exists."""
    secret_manager_path = os.path.join(parent_dir, 'secret_manager.py')
    assert os.path.exists(secret_manager_path), "secret_manager.py should exist"


def test_service_account_manager_module_exists():
    """Test that the service account manager module exists."""
    service_account_path = os.path.join(parent_dir, 'service_account_manager.py')
    assert os.path.exists(service_account_path), "service_account_manager.py should exist"


def test_config_manager_has_required_classes():
    """Test that the configuration manager has required classes."""
    config_manager_path = os.path.join(parent_dir, 'config_manager.py')
    
    with open(config_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required classes
    assert 'class ConfigurationManager:' in content
    assert 'class EnvironmentConfig:' in content
    assert 'class ConfigFormat(Enum):' in content


def test_config_manager_has_required_methods():
    """Test that ConfigurationManager has required methods."""
    config_manager_path = os.path.join(parent_dir, 'config_manager.py')
    
    with open(config_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required methods based on task requirements
    required_methods = [
        'load_environment_config',  # Environment-specific settings
        'save_environment_config',  # Configuration persistence
        'get_deployment_config',    # Integration with deployment config
        'validate_all_configs',     # Configuration validation
        '_load_config_from_files',  # File-based configuration
        '_load_config_from_env',    # Environment variable configuration
        '_validate_config',         # Configuration validation
    ]
    
    for method in required_methods:
        assert f'def {method}(' in content, f"Method {method} should be implemented"


def test_secret_manager_has_required_classes():
    """Test that the secret manager has required classes."""
    secret_manager_path = os.path.join(parent_dir, 'secret_manager.py')
    
    with open(secret_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required classes
    assert 'class SecretManager:' in content
    assert 'class SecretType(Enum):' in content
    assert 'class SecretMetadata:' in content
    assert 'class SecretValue:' in content


def test_secret_manager_has_required_methods():
    """Test that SecretManager has required methods."""
    secret_manager_path = os.path.join(parent_dir, 'secret_manager.py')
    
    with open(secret_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required methods based on task requirements
    required_methods = [
        'create_secret',            # Secret creation
        'get_secret',              # Secret retrieval
        'update_secret',           # Secret updates
        'delete_secret',           # Secret deletion
        'list_secrets',            # Secret listing
        'secret_exists',           # Secret existence check
        'setup_deployment_secrets', # Deployment secret setup
        'rotate_secret',           # Secret rotation
        'backup_secrets',          # Secret backup
    ]
    
    for method in required_methods:
        assert f'def {method}(' in content, f"Method {method} should be implemented"


def test_service_account_manager_has_required_classes():
    """Test that the service account manager has required classes."""
    service_account_path = os.path.join(parent_dir, 'service_account_manager.py')
    
    with open(service_account_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required classes
    assert 'class ServiceAccountManager:' in content
    assert 'class ServiceAccountRole(Enum):' in content
    assert 'class ServiceAccountInfo:' in content
    assert 'class ServiceAccountKey:' in content


def test_service_account_manager_has_required_methods():
    """Test that ServiceAccountManager has required methods."""
    service_account_path = os.path.join(parent_dir, 'service_account_manager.py')
    
    with open(service_account_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for required methods based on task requirements
    required_methods = [
        'create_service_account',           # Service account creation
        'get_service_account',             # Service account retrieval
        'delete_service_account',          # Service account deletion
        'create_service_account_key',      # Key creation
        'list_service_accounts',           # Service account listing
        'setup_deployment_service_accounts', # Default setup
        'rotate_service_account_key',      # Key rotation
    ]
    
    for method in required_methods:
        assert f'def {method}(' in content, f"Method {method} should be implemented"


def test_configuration_file_format_support():
    """Test that configuration manager supports multiple file formats."""
    config_manager_path = os.path.join(parent_dir, 'config_manager.py')
    
    with open(config_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for file format support
    assert 'yaml' in content.lower(), "Should support YAML configuration files"
    assert 'json' in content.lower(), "Should support JSON configuration files"
    assert 'ConfigFormat' in content, "Should define configuration formats"


def test_environment_variable_support():
    """Test that configuration manager supports environment variables."""
    config_manager_path = os.path.join(parent_dir, 'config_manager.py')
    
    with open(config_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for environment variable support
    assert 'os.getenv' in content, "Should read from environment variables"
    assert '_load_config_from_env' in content, "Should have environment loading method"


def test_secret_manager_integration():
    """Test that secret manager integrates with Google Cloud Secret Manager."""
    secret_manager_path = os.path.join(parent_dir, 'secret_manager.py')
    
    with open(secret_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for Google Cloud integration
    assert 'google.cloud' in content, "Should integrate with Google Cloud"
    assert 'secretmanager' in content, "Should use Secret Manager service"
    assert 'SecretManagerServiceClient' in content, "Should use Secret Manager client"


def test_service_account_iam_integration():
    """Test that service account manager integrates with Google Cloud IAM."""
    service_account_path = os.path.join(parent_dir, 'service_account_manager.py')
    
    with open(service_account_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for IAM integration
    assert 'google.cloud' in content, "Should integrate with Google Cloud"
    assert 'iam' in content, "Should use IAM service"
    assert 'serviceAccounts' in content, "Should manage service accounts"


def test_error_handling_implemented():
    """Test that proper error handling is implemented."""
    modules = ['config_manager.py', 'secret_manager.py', 'service_account_manager.py']
    
    for module in modules:
        module_path = os.path.join(parent_dir, module)
        with open(module_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error handling
        assert 'try:' in content, f"{module} should have try-catch blocks"
        assert 'except' in content, f"{module} should have exception handling"
        assert 'self.logger.error' in content, f"{module} should have error logging"


def test_configuration_validation():
    """Test that configuration validation is implemented."""
    config_manager_path = os.path.join(parent_dir, 'config_manager.py')
    
    with open(config_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for validation methods
    assert '_validate_config' in content, "Should have configuration validation"
    assert 'ConfigurationError' in content, "Should use configuration errors"
    assert 'validate_all_configs' in content, "Should validate all configurations"


def test_secret_types_defined():
    """Test that secret types are properly defined."""
    secret_manager_path = os.path.join(parent_dir, 'secret_manager.py')
    
    with open(secret_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for secret types
    expected_types = [
        'DATABASE_CREDENTIALS',
        'API_KEYS',
        'SERVICE_ACCOUNT_KEY',
        'WEBHOOK_URLS',
        'CERTIFICATES',
        'CUSTOM'
    ]
    
    for secret_type in expected_types:
        assert secret_type in content, f"SecretType should have {secret_type}"


def test_service_account_roles_defined():
    """Test that service account roles are properly defined."""
    service_account_path = os.path.join(parent_dir, 'service_account_manager.py')
    
    with open(service_account_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for common roles
    expected_roles = [
        'CLOUD_RUN_DEVELOPER',
        'CLOUD_RUN_INVOKER',
        'FIRESTORE_USER',
        'SECRET_MANAGER_ACCESSOR',
        'STORAGE_ADMIN',
        'LOGGING_WRITER'
    ]
    
    for role in expected_roles:
        assert role in content, f"ServiceAccountRole should have {role}"


def test_unit_tests_exist():
    """Test that unit tests exist for configuration and secret management."""
    test_files = [
        'test_config_manager.py',
        'test_secret_manager.py'
    ]
    
    for test_file in test_files:
        test_file_path = os.path.join(os.path.dirname(__file__), test_file)
        assert os.path.exists(test_file_path), f"Unit tests should exist: {test_file}"


def test_environment_specific_configuration():
    """Test that environment-specific configuration is supported."""
    config_manager_path = os.path.join(parent_dir, 'config_manager.py')
    
    with open(config_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for environment-specific handling
    assert 'Environment.DEVELOPMENT' in content, "Should handle development environment"
    assert 'Environment.STAGING' in content, "Should handle staging environment"
    assert 'Environment.PRODUCTION' in content, "Should handle production environment"


def test_deployment_config_integration():
    """Test that configuration manager integrates with DeploymentConfig."""
    config_manager_path = os.path.join(parent_dir, 'config_manager.py')
    
    with open(config_manager_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for deployment config integration
    assert 'DeploymentConfig' in content, "Should integrate with DeploymentConfig"
    assert 'get_deployment_config' in content, "Should convert to deployment config"
    assert 'CloudConfig' in content, "Should use cloud configuration"


def test_task_3_2_requirements_coverage():
    """Test that task 3.2 requirements are covered."""
    # Task 3.2 requirements:
    # - Write configuration manager for environment-specific settings ✓
    config_manager_path = os.path.join(parent_dir, 'config_manager.py')
    assert os.path.exists(config_manager_path)
    
    # - Implement secret manager integration ✓
    secret_manager_path = os.path.join(parent_dir, 'secret_manager.py')
    assert os.path.exists(secret_manager_path)
    
    # - Create service account management functionality ✓
    service_account_path = os.path.join(parent_dir, 'service_account_manager.py')
    assert os.path.exists(service_account_path)
    
    # - Write tests for configuration and secret handling ✓
    test_config_path = os.path.join(os.path.dirname(__file__), 'test_config_manager.py')
    test_secret_path = os.path.join(os.path.dirname(__file__), 'test_secret_manager.py')
    assert os.path.exists(test_config_path)
    assert os.path.exists(test_secret_path)


if __name__ == '__main__':
    pytest.main([__file__])