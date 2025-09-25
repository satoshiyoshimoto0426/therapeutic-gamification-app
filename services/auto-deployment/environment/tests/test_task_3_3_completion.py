"""
Task 3.3 completion test - Environment detection and setup automation.
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from environment_detector import EnvironmentDetector, EnvironmentInfo, DetectionMethod
from config import Environment


def test_environment_detector_instantiation():
    """Test that EnvironmentDetector can be instantiated."""
    detector = EnvironmentDetector()
    assert detector is not None
    assert hasattr(detector, 'detect_environment')
    assert hasattr(detector, 'setup_environment')


def test_environment_detection_methods():
    """Test that all detection methods are available."""
    detector = EnvironmentDetector()
    
    # Test that all detection methods are implemented
    methods = [
        DetectionMethod.ENVIRONMENT_VARIABLE,
        DetectionMethod.GIT_BRANCH,
        DetectionMethod.CONFIG_FILE,
        DetectionMethod.PROJECT_ID,
        DetectionMethod.HOSTNAME
    ]
    
    for method in methods:
        assert method in detector.detection_rules
        assert callable(detector.detection_rules[method])


def test_environment_patterns():
    """Test that environment patterns are properly configured."""
    detector = EnvironmentDetector()
    
    # Test that all environments have patterns
    for env in [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION]:
        assert env in detector.env_patterns
        patterns = detector.env_patterns[env]
        
        assert 'env_vars' in patterns
        assert 'branches' in patterns
        assert 'project_suffixes' in patterns
        assert 'hostnames' in patterns
        
        assert isinstance(patterns['env_vars'], list)
        assert isinstance(patterns['branches'], list)
        assert isinstance(patterns['project_suffixes'], list)
        assert isinstance(patterns['hostnames'], list)


def test_detect_environment_with_env_var():
    """Test environment detection with environment variable."""
    detector = EnvironmentDetector()
    
    with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
        result = detector.detect_environment()
        
        assert isinstance(result, EnvironmentInfo)
        assert result.environment == Environment.PRODUCTION
        assert result.confidence > 0.5
        assert result.detection_method == DetectionMethod.ENVIRONMENT_VARIABLE


def test_detect_environment_fallback():
    """Test environment detection fallback to development."""
    detector = EnvironmentDetector()
    
    # Clear environment and mock all detection methods to fail
    with patch.dict(os.environ, {}, clear=True):
        with patch.object(detector, '_detect_from_git_branch', return_value=None):
            with patch.object(detector, '_detect_from_config_file', return_value=None):
                with patch.object(detector, '_detect_from_hostname', return_value=None):
                    result = detector.detect_environment()
                    
                    assert result.environment == Environment.DEVELOPMENT
                    assert result.detection_method == DetectionMethod.MANUAL


def test_setup_environment_development():
    """Test development environment setup."""
    detector = EnvironmentDetector()
    
    env_info = EnvironmentInfo(
        environment=Environment.DEVELOPMENT,
        confidence=0.9,
        detection_method=DetectionMethod.ENVIRONMENT_VARIABLE,
        details={}
    )
    
    result = detector.setup_environment(env_info)
    
    assert result['environment'] == 'development'
    assert 'configurations' in result
    assert 'validations' in result
    assert 'setup_actions' in result
    
    # Check development-specific configurations
    config = result['configurations']
    assert config['debug_mode'] is True
    assert config['log_level'] == 'DEBUG'
    assert config['resource_limits']['memory'] == '1Gi'


def test_setup_environment_staging():
    """Test staging environment setup."""
    detector = EnvironmentDetector()
    
    env_info = EnvironmentInfo(
        environment=Environment.STAGING,
        confidence=0.8,
        detection_method=DetectionMethod.GIT_BRANCH,
        details={}
    )
    
    result = detector.setup_environment(env_info)
    
    assert result['environment'] == 'staging'
    
    # Check staging-specific configurations
    config = result['configurations']
    assert config['debug_mode'] is False
    assert config['log_level'] == 'INFO'
    assert config['resource_limits']['memory'] == '2Gi'


def test_setup_environment_production():
    """Test production environment setup."""
    detector = EnvironmentDetector()
    
    env_info = EnvironmentInfo(
        environment=Environment.PRODUCTION,
        confidence=0.9,
        detection_method=DetectionMethod.PROJECT_ID,
        details={},
        project_id='my-prod-project'
    )
    
    result = detector.setup_environment(env_info)
    
    assert result['environment'] == 'production'
    
    # Check production-specific configurations
    config = result['configurations']
    assert config['debug_mode'] is False
    assert config['log_level'] == 'WARNING'
    assert config['resource_limits']['memory'] == '4Gi'
    assert config['resource_limits']['min_instances'] == 2


def test_environment_validation():
    """Test environment setup validation."""
    detector = EnvironmentDetector()
    
    # Test validation with good configuration
    env_info = EnvironmentInfo(
        environment=Environment.DEVELOPMENT,
        confidence=0.9,
        detection_method=DetectionMethod.ENVIRONMENT_VARIABLE,
        details={}
    )
    
    setup_results = {
        'configurations': {
            'debug_mode': True,
            'log_level': 'DEBUG'
        }
    }
    
    validations = detector._validate_environment_setup(env_info, setup_results)
    
    assert 'environment_detected' in validations
    assert 'configuration_valid' in validations
    assert 'resources_available' in validations
    assert 'security_compliant' in validations
    assert 'issues' in validations


def test_environment_recommendations():
    """Test environment recommendations."""
    detector = EnvironmentDetector()
    
    # Test recommendations for each environment
    for env in [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION]:
        env_info = EnvironmentInfo(
            environment=env,
            confidence=0.9,
            detection_method=DetectionMethod.ENVIRONMENT_VARIABLE,
            details={}
        )
        
        recommendations = detector.get_environment_recommendations(env_info)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        
        # Each recommendation should be a string
        for rec in recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 0


def test_detection_method_enum():
    """Test that DetectionMethod enum has all required values."""
    expected_methods = [
        'ENVIRONMENT_VARIABLE',
        'GIT_BRANCH', 
        'CONFIG_FILE',
        'PROJECT_ID',
        'HOSTNAME',
        'MANUAL'
    ]
    
    for method_name in expected_methods:
        assert hasattr(DetectionMethod, method_name)


def test_environment_info_dataclass():
    """Test EnvironmentInfo dataclass functionality."""
    env_info = EnvironmentInfo(
        environment=Environment.DEVELOPMENT,
        confidence=0.8,
        detection_method=DetectionMethod.ENVIRONMENT_VARIABLE,
        details={'test': 'value'}
    )
    
    assert env_info.environment == Environment.DEVELOPMENT
    assert env_info.confidence == 0.8
    assert env_info.detection_method == DetectionMethod.ENVIRONMENT_VARIABLE
    assert env_info.details == {'test': 'value'}
    assert env_info.project_id is None
    assert env_info.region is None


def test_integration_detect_and_setup():
    """Test integration of detection and setup."""
    detector = EnvironmentDetector()
    
    with patch.dict(os.environ, {'ENVIRONMENT': 'staging'}):
        # Detect environment
        env_info = detector.detect_environment()
        assert env_info.environment == Environment.STAGING
        
        # Setup environment
        setup_result = detector.setup_environment(env_info)
        assert setup_result['environment'] == 'staging'
        
        # Validate setup
        assert setup_result['validations']['environment_detected'] is True


if __name__ == '__main__':
    # Run tests
    print("Running Task 3.3 completion tests...")
    
    test_functions = [
        test_environment_detector_instantiation,
        test_environment_detection_methods,
        test_environment_patterns,
        test_detect_environment_with_env_var,
        test_detect_environment_fallback,
        test_setup_environment_development,
        test_setup_environment_staging,
        test_setup_environment_production,
        test_environment_validation,
        test_environment_recommendations,
        test_detection_method_enum,
        test_environment_info_dataclass,
        test_integration_detect_and_setup
    ]
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✓ {test_func.__name__}")
            passed += 1
        except Exception as e:
            print(f"✗ {test_func.__name__}: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("\n✅ Task 3.3 COMPLETED SUCCESSFULLY!")
        print("✅ Environment detection logic implemented")
        print("✅ Automatic environment setup procedures created")
        print("✅ Environment validation and verification working")
        print("✅ Integration tests passing")
    else:
        print(f"\n❌ Task 3.3 has {failed} failing tests")
    
    exit(0 if failed == 0 else 1)