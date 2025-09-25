"""
Tests for environment detector.
"""

import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import json

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from environment_detector import EnvironmentDetector, EnvironmentInfo, DetectionMethod
from config import Environment


class TestEnvironmentDetector:
    """Test cases for EnvironmentDetector."""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance for testing."""
        return EnvironmentDetector()
    
    def test_detect_from_env_var_development(self, detector):
        """Test environment detection from environment variable - development."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            result = detector._detect_from_env_var()
            
            assert result is not None
            assert result.environment == Environment.DEVELOPMENT
            assert result.confidence == 0.9
            assert result.detection_method == DetectionMethod.ENVIRONMENT_VARIABLE
            assert result.details['variable'] == 'ENVIRONMENT'
            assert result.details['value'] == 'development'
    
    def test_detect_from_env_var_production(self, detector):
        """Test environment detection from environment variable - production."""
        with patch.dict(os.environ, {'ENV': 'production'}):
            result = detector._detect_from_env_var()
            
            assert result is not None
            assert result.environment == Environment.PRODUCTION
            assert result.confidence == 0.9
            assert result.detection_method == DetectionMethod.ENVIRONMENT_VARIABLE
    
    def test_detect_from_env_var_staging(self, detector):
        """Test environment detection from environment variable - staging."""
        with patch.dict(os.environ, {'NODE_ENV': 'staging'}):
            result = detector._detect_from_env_var()
            
            assert result is not None
            assert result.environment == Environment.STAGING
            assert result.confidence == 0.9
            assert result.detection_method == DetectionMethod.ENVIRONMENT_VARIABLE
    
    def test_detect_from_env_var_none(self, detector):
        """Test environment detection when no relevant env vars are set."""
        with patch.dict(os.environ, {}, clear=True):
            result = detector._detect_from_env_var()
            assert result is None
    
    @patch('subprocess.run')
    def test_detect_from_git_branch_main(self, mock_run, detector):
        """Test environment detection from git branch - main."""
        mock_run.return_value = Mock(returncode=0, stdout='main\n')
        
        result = detector._detect_from_git_branch()
        
        assert result is not None
        assert result.environment == Environment.PRODUCTION
        assert result.confidence == 0.8
        assert result.detection_method == DetectionMethod.GIT_BRANCH
        assert result.details['branch'] == 'main'
    
    @patch('subprocess.run')
    def test_detect_from_git_branch_develop(self, mock_run, detector):
        """Test environment detection from git branch - develop."""
        mock_run.return_value = Mock(returncode=0, stdout='develop\n')
        
        result = detector._detect_from_git_branch()
        
        assert result is not None
        assert result.environment == Environment.DEVELOPMENT
        assert result.confidence == 0.8
        assert result.detection_method == DetectionMethod.GIT_BRANCH
    
    @patch('subprocess.run')
    def test_detect_from_git_branch_feature(self, mock_run, detector):
        """Test environment detection from git branch - feature branch."""
        mock_run.return_value = Mock(returncode=0, stdout='feature/new-feature\n')
        
        result = detector._detect_from_git_branch()
        
        assert result is not None
        assert result.environment == Environment.DEVELOPMENT
        assert result.confidence == 0.8
        assert result.detection_method == DetectionMethod.GIT_BRANCH
    
    @patch('subprocess.run')
    def test_detect_from_git_branch_error(self, mock_run, detector):
        """Test environment detection when git command fails."""
        mock_run.return_value = Mock(returncode=1, stdout='', stderr='Not a git repository')
        
        result = detector._detect_from_git_branch()
        assert result is None
    
    def test_detect_from_config_file_json(self, detector):
        """Test environment detection from JSON config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({'environment': 'staging'}, f)
            config_path = f.name
        
        try:
            # Mock Path.exists to return True for our temp file
            with patch('pathlib.Path.exists') as mock_exists:
                mock_exists.return_value = True
                with patch('builtins.open', mock_open_json({'environment': 'staging'})):
                    with patch('pathlib.Path.__str__', return_value='deployment.json'):
                        result = detector._detect_from_config_file()
                        
                        assert result is not None
                        assert result.environment == Environment.STAGING
                        assert result.confidence == 0.7
                        assert result.detection_method == DetectionMethod.CONFIG_FILE
        finally:
            os.unlink(config_path)
    
    def test_detect_from_project_id_dev(self, detector):
        """Test environment detection from project ID - development."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'my-project-dev'}):
            result = detector._detect_from_project_id()
            
            assert result is not None
            assert result.environment == Environment.DEVELOPMENT
            assert result.confidence == 0.8
            assert result.detection_method == DetectionMethod.PROJECT_ID
            assert result.project_id == 'my-project-dev'
    
    def test_detect_from_project_id_prod(self, detector):
        """Test environment detection from project ID - production."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'my-project-prod'}):
            result = detector._detect_from_project_id()
            
            assert result is not None
            assert result.environment == Environment.PRODUCTION
            assert result.confidence == 0.8
            assert result.detection_method == DetectionMethod.PROJECT_ID
    
    def test_detect_from_project_id_clean_name(self, detector):
        """Test environment detection from clean project ID (assumes production)."""
        with patch.dict(os.environ, {'GOOGLE_CLOUD_PROJECT': 'my-clean-project'}):
            result = detector._detect_from_project_id()
            
            assert result is not None
            assert result.environment == Environment.PRODUCTION
            assert result.confidence == 0.6
            assert result.detection_method == DetectionMethod.PROJECT_ID
    
    def test_detect_from_project_id_none(self, detector):
        """Test environment detection when no project ID is set."""
        with patch.dict(os.environ, {}, clear=True):
            result = detector._detect_from_project_id()
            assert result is None
    
    @patch('socket.gethostname')
    def test_detect_from_hostname_dev(self, mock_hostname, detector):
        """Test environment detection from hostname - development."""
        mock_hostname.return_value = 'dev-server-01'
        
        result = detector._detect_from_hostname()
        
        assert result is not None
        assert result.environment == Environment.DEVELOPMENT
        assert result.confidence == 0.6
        assert result.detection_method == DetectionMethod.HOSTNAME
    
    @patch('socket.gethostname')
    def test_detect_from_hostname_localhost(self, mock_hostname, detector):
        """Test environment detection from hostname - localhost."""
        mock_hostname.return_value = 'localhost'
        
        result = detector._detect_from_hostname()
        
        assert result is not None
        assert result.environment == Environment.DEVELOPMENT
        assert result.confidence == 0.6
        assert result.detection_method == DetectionMethod.HOSTNAME
    
    @patch('socket.gethostname')
    def test_detect_from_hostname_error(self, mock_hostname, detector):
        """Test environment detection when hostname lookup fails."""
        mock_hostname.side_effect = Exception("Network error")
        
        result = detector._detect_from_hostname()
        assert result is None
    
    def test_detect_environment_multiple_methods(self, detector):
        """Test environment detection with multiple methods."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production', 'GOOGLE_CLOUD_PROJECT': 'test-dev'}):
            result = detector.detect_environment()
            
            # Should choose the method with highest confidence (env var = 0.9 > project_id = 0.8)
            assert result.environment == Environment.PRODUCTION
            assert result.confidence == 0.9
            assert result.detection_method == DetectionMethod.ENVIRONMENT_VARIABLE
    
    def test_detect_environment_no_methods_succeed(self, detector):
        """Test environment detection when no methods succeed."""
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(detector, '_detect_from_git_branch', return_value=None):
                with patch.object(detector, '_detect_from_config_file', return_value=None):
                    with patch.object(detector, '_detect_from_hostname', return_value=None):
                        result = detector.detect_environment()
                        
                        # Should default to development
                        assert result.environment == Environment.DEVELOPMENT
                        assert result.confidence == 0.1
                        assert result.detection_method == DetectionMethod.MANUAL
    
    def test_setup_development_environment(self, detector):
        """Test development environment setup."""
        env_info = EnvironmentInfo(
            environment=Environment.DEVELOPMENT,
            confidence=0.9,
            detection_method=DetectionMethod.ENVIRONMENT_VARIABLE,
            details={}
        )
        
        result = detector.setup_environment(env_info)
        
        assert result['environment'] == 'development'
        assert result['configurations']['debug_mode'] is True
        assert result['configurations']['log_level'] == 'DEBUG'
        assert result['configurations']['resource_limits']['memory'] == '1Gi'
        assert 'Enable debug logging' in result['setup_actions']
    
    def test_setup_staging_environment(self, detector):
        """Test staging environment setup."""
        env_info = EnvironmentInfo(
            environment=Environment.STAGING,
            confidence=0.8,
            detection_method=DetectionMethod.GIT_BRANCH,
            details={}
        )
        
        result = detector.setup_environment(env_info)
        
        assert result['environment'] == 'staging'
        assert result['configurations']['debug_mode'] is False
        assert result['configurations']['log_level'] == 'INFO'
        assert result['configurations']['resource_limits']['memory'] == '2Gi'
        assert 'Configure production-like settings' in result['setup_actions']
    
    def test_setup_production_environment(self, detector):
        """Test production environment setup."""
        env_info = EnvironmentInfo(
            environment=Environment.PRODUCTION,
            confidence=0.8,
            detection_method=DetectionMethod.PROJECT_ID,
            details={},
            project_id='my-prod-project'
        )
        
        result = detector.setup_environment(env_info)
        
        assert result['environment'] == 'production'
        assert result['configurations']['debug_mode'] is False
        assert result['configurations']['log_level'] == 'WARNING'
        assert result['configurations']['resource_limits']['memory'] == '4Gi'
        assert result['configurations']['resource_limits']['min_instances'] == 2
        assert 'Configure production settings' in result['setup_actions']
    
    def test_validate_environment_setup_low_confidence(self, detector):
        """Test environment setup validation with low confidence."""
        env_info = EnvironmentInfo(
            environment=Environment.DEVELOPMENT,
            confidence=0.3,  # Low confidence
            detection_method=DetectionMethod.MANUAL,
            details={}
        )
        
        setup_results = {'configurations': {}}
        validations = detector._validate_environment_setup(env_info, setup_results)
        
        assert len(validations['issues']) > 0
        assert any(issue['type'] == 'low_confidence' for issue in validations['issues'])
    
    def test_validate_environment_setup_debug_in_production(self, detector):
        """Test environment setup validation with debug in production."""
        env_info = EnvironmentInfo(
            environment=Environment.PRODUCTION,
            confidence=0.9,
            detection_method=DetectionMethod.ENVIRONMENT_VARIABLE,
            details={}
        )
        
        setup_results = {
            'configurations': {
                'debug_mode': True  # This should trigger a validation error
            }
        }
        
        validations = detector._validate_environment_setup(env_info, setup_results)
        
        assert validations['security_compliant'] is False
        assert any(issue['type'] == 'debug_in_production' for issue in validations['issues'])
    
    def test_get_environment_recommendations_low_confidence(self, detector):
        """Test getting recommendations for low confidence detection."""
        env_info = EnvironmentInfo(
            environment=Environment.DEVELOPMENT,
            confidence=0.5,  # Low confidence
            detection_method=DetectionMethod.HOSTNAME,
            details={}
        )
        
        recommendations = detector.get_environment_recommendations(env_info)
        
        assert len(recommendations) > 0
        assert any('ENVIRONMENT variable' in rec for rec in recommendations)
    
    def test_get_environment_recommendations_production(self, detector):
        """Test getting recommendations for production environment."""
        env_info = EnvironmentInfo(
            environment=Environment.PRODUCTION,
            confidence=0.9,
            detection_method=DetectionMethod.ENVIRONMENT_VARIABLE,
            details={}
        )
        
        recommendations = detector.get_environment_recommendations(env_info)
        
        assert len(recommendations) > 0
        assert any('Secret Manager' in rec for rec in recommendations)
        assert any('monitoring' in rec for rec in recommendations)
    
    def test_get_environment_recommendations_development(self, detector):
        """Test getting recommendations for development environment."""
        env_info = EnvironmentInfo(
            environment=Environment.DEVELOPMENT,
            confidence=0.9,
            detection_method=DetectionMethod.ENVIRONMENT_VARIABLE,
            details={}
        )
        
        recommendations = detector.get_environment_recommendations(env_info)
        
        assert len(recommendations) > 0
        assert any('local' in rec or 'development' in rec for rec in recommendations)


def mock_open_json(data):
    """Helper to mock open() for JSON files."""
    from unittest.mock import mock_open
    return mock_open(read_data=json.dumps(data))


if __name__ == '__main__':
    pytest.main([__file__])