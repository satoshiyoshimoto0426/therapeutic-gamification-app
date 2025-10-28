"""
Tests for deployment reporter functionality.
"""

import asyncio
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from ..models import DeploymentRecord, DeploymentStatus, DeploymentPhase, ReportConfig
from ..deployment_reporter import DeploymentReporter
from ..progress_tracker import ProgressTracker
try:
    from ...notification.notification_manager import NotificationManager
except ImportError:
    # Mock for testing
    class NotificationManager:
        async def send_notification(self, **kwargs):
            pass
        async def test_channels(self):
            return []


class TestDeploymentReporter:
    """Test cases for DeploymentReporter class."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database file."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    @pytest.fixture
    def temp_reports_dir(self):
        """Create temporary reports directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def mock_notification_manager(self):
        """Create mock notification manager."""
        mock_manager = MagicMock(spec=NotificationManager)
        mock_manager.send_notification = AsyncMock()
        mock_manager.test_channels = AsyncMock(return_value=[])
        return mock_manager
    
    @pytest.fixture
    def deployment_reporter(self, mock_notification_manager, temp_db_path, temp_reports_dir):
        """Create test deployment reporter."""
        return DeploymentReporter(
            notification_manager=mock_notification_manager,
            history_db_path=temp_db_path,
            reports_dir=temp_reports_dir
        )
    
    @pytest.fixture
    def sample_deployment_config(self):
        """Create sample deployment configuration."""
        return {
            "memory": "2Gi",
            "cpu": "1",
            "min_instances": 1,
            "max_instances": 10
        }
    
    @pytest.fixture
    def sample_environment_config(self):
        """Create sample environment configuration."""
        return {
            "region": "us-central1",
            "project_id": "test-project",
            "service_name": "test-service"
        }
    
    def test_initialization(self, deployment_reporter, mock_notification_manager, temp_reports_dir):
        """Test deployment reporter initialization."""
        assert deployment_reporter.notification_manager == mock_notification_manager
        assert deployment_reporter.history_manager is not None
        assert deployment_reporter.report_generator is not None
        assert deployment_reporter.reports_dir == Path(temp_reports_dir)
        assert len(deployment_reporter.active_deployments) == 0
        assert deployment_reporter.auto_save_enabled is True
        assert deployment_reporter.auto_report_enabled is True
        assert deployment_reporter.notification_enabled is True
    
    def test_create_deployment_tracker(
        self,
        deployment_reporter,
        sample_deployment_config,
        sample_environment_config
    ):
        """Test creating deployment tracker."""
        deployment_id = "test-deployment-123"
        environment = "production"
        commit_sha = "abc123def456"
        image_tag = "myapp:v1.2.3"
        revision_name = "myapp-v123"
        
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment=environment,
            commit_sha=commit_sha,
            image_tag=image_tag,
            revision_name=revision_name,
            deployment_config=sample_deployment_config,
            environment_config=sample_environment_config
        )
        
        assert isinstance(tracker, ProgressTracker)
        assert tracker.deployment_record.deployment_id == deployment_id
        assert tracker.deployment_record.environment == environment
        assert tracker.deployment_record.commit_sha == commit_sha
        assert tracker.deployment_record.image_tag == image_tag
        assert tracker.deployment_record.revision_name == revision_name
        assert tracker.deployment_record.deployment_config == sample_deployment_config
        assert tracker.deployment_record.environment_config == sample_environment_config
        
        # Check that tracker is stored in active deployments
        assert deployment_id in deployment_reporter.active_deployments
        assert deployment_reporter.active_deployments[deployment_id] == tracker
    
    def test_get_deployment_tracker(self, deployment_reporter):
        """Test getting deployment tracker."""
        deployment_id = "test-deployment-123"
        
        # Create tracker
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="test",
            commit_sha="abc123",
            image_tag="test:latest"
        )
        
        # Get tracker
        retrieved_tracker = deployment_reporter.get_deployment_tracker(deployment_id)
        assert retrieved_tracker == tracker
        
        # Test non-existent tracker
        non_existent_tracker = deployment_reporter.get_deployment_tracker("non-existent")
        assert non_existent_tracker is None
    
    @pytest.mark.asyncio
    async def test_complete_deployment_success(self, deployment_reporter, mock_notification_manager):
        """Test completing deployment successfully."""
        deployment_id = "test-deployment-123"
        
        # Create tracker
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="production",
            commit_sha="abc123",
            image_tag="test:latest"
        )
        
        # Complete deployment
        success = await deployment_reporter.complete_deployment(
            deployment_id=deployment_id,
            success=True
        )
        
        assert success
        assert tracker.deployment_record.status == DeploymentStatus.COMPLETED
        assert deployment_id not in deployment_reporter.active_deployments
        
        # Verify notification was sent
        mock_notification_manager.send_notification.assert_called()
    
    @pytest.mark.asyncio
    async def test_complete_deployment_failure(self, deployment_reporter, mock_notification_manager):
        """Test completing deployment with failure."""
        deployment_id = "test-deployment-123"
        
        # Create tracker
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="production",
            commit_sha="abc123",
            image_tag="test:latest"
        )
        
        # Complete deployment with failure
        success = await deployment_reporter.complete_deployment(
            deployment_id=deployment_id,
            success=False
        )
        
        assert success
        assert tracker.deployment_record.status == DeploymentStatus.FAILED
        assert deployment_id not in deployment_reporter.active_deployments
        
        # Verify notification was sent
        mock_notification_manager.send_notification.assert_called()
    
    @pytest.mark.asyncio
    async def test_complete_deployment_not_found(self, deployment_reporter):
        """Test completing non-existent deployment."""
        success = await deployment_reporter.complete_deployment(
            deployment_id="non-existent",
            success=True
        )
        
        assert success is False
    
    @pytest.mark.asyncio
    async def test_generate_deployment_report(self, deployment_reporter, temp_reports_dir):
        """Test generating deployment report."""
        deployment_id = "test-deployment-123"
        
        # Create and complete deployment
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="production",
            commit_sha="abc123",
            image_tag="test:latest"
        )
        
        # Save to history first
        deployment_reporter.history_manager.save_deployment_record(tracker.deployment_record)
        
        # Generate report
        report_content = await deployment_reporter.generate_deployment_report(
            deployment_id=deployment_id,
            format="json",
            save_to_file=True
        )
        
        assert report_content is not None
        assert deployment_id in report_content
        
        # Check that report file was created
        report_files = list(Path(temp_reports_dir).glob(f"deployment_report_{deployment_id}_*.json"))
        assert len(report_files) > 0
    
    @pytest.mark.asyncio
    async def test_generate_summary_report(self, deployment_reporter, temp_reports_dir):
        """Test generating summary report."""
        # Create multiple deployments
        for i in range(3):
            deployment_id = f"test-deployment-{i}"
            tracker = deployment_reporter.create_deployment_tracker(
                deployment_id=deployment_id,
                environment="production",
                commit_sha=f"commit-{i}",
                image_tag=f"test:v{i}"
            )
            deployment_reporter.history_manager.save_deployment_record(tracker.deployment_record)
        
        # Generate summary report
        report_content = await deployment_reporter.generate_summary_report(
            environment="production",
            days=30,
            format="json",
            save_to_file=True
        )
        
        assert report_content is not None
        assert "summary" in report_content
        assert "deployments" in report_content
        
        # Check that report file was created
        report_files = list(Path(temp_reports_dir).glob("summary_report_production_*.json"))
        assert len(report_files) > 0
    
    def test_get_deployment_history(self, deployment_reporter):
        """Test getting deployment history."""
        # Create test deployments
        for i in range(5):
            deployment_id = f"test-deployment-{i}"
            tracker = deployment_reporter.create_deployment_tracker(
                deployment_id=deployment_id,
                environment="production" if i % 2 == 0 else "staging",
                commit_sha=f"commit-{i}",
                image_tag=f"test:v{i}"
            )
            deployment_reporter.history_manager.save_deployment_record(tracker.deployment_record)
        
        # Get history
        history = deployment_reporter.get_deployment_history(environment="production", days=30)
        assert len(history) == 3  # Records 0, 2, 4
        
        # Get all history
        all_history = deployment_reporter.get_deployment_history(days=30)
        assert len(all_history) == 5
    
    def test_get_deployment_statistics(self, deployment_reporter):
        """Test getting deployment statistics."""
        # Create test deployments
        for i in range(3):
            deployment_id = f"test-deployment-{i}"
            tracker = deployment_reporter.create_deployment_tracker(
                deployment_id=deployment_id,
                environment="production",
                commit_sha=f"commit-{i}",
                image_tag=f"test:v{i}"
            )
            if i == 0:  # Make first deployment failed
                tracker.deployment_record.status = DeploymentStatus.FAILED
                tracker.deployment_record.errors = ["Test error"]
            deployment_reporter.history_manager.save_deployment_record(tracker.deployment_record)
        
        # Get statistics
        stats = deployment_reporter.get_deployment_statistics(environment="production", days=30)
        
        assert stats['total_deployments'] == 3
        assert stats['successful_deployments'] == 2
        assert stats['failed_deployments'] == 1
    
    def test_get_active_deployments(self, deployment_reporter):
        """Test getting active deployments."""
        # Create active deployments
        for i in range(3):
            deployment_id = f"test-deployment-{i}"
            deployment_reporter.create_deployment_tracker(
                deployment_id=deployment_id,
                environment="production",
                commit_sha=f"commit-{i}",
                image_tag=f"test:v{i}"
            )
        
        active_deployments = deployment_reporter.get_active_deployments()
        
        assert len(active_deployments) == 3
        for i in range(3):
            deployment_id = f"test-deployment-{i}"
            assert deployment_id in active_deployments
            assert 'deployment_id' in active_deployments[deployment_id]
            assert 'status' in active_deployments[deployment_id]
    
    @pytest.mark.asyncio
    async def test_cleanup_old_records(self, deployment_reporter, mock_notification_manager):
        """Test cleaning up old records."""
        # Create old deployment
        old_deployment_id = "old-deployment"
        old_tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=old_deployment_id,
            environment="production",
            commit_sha="old-commit",
            image_tag="old:image"
        )
        old_tracker.deployment_record.start_time = datetime.utcnow() - timedelta(days=100)
        deployment_reporter.history_manager.save_deployment_record(old_tracker.deployment_record)
        
        # Cleanup
        deleted_count = await deployment_reporter.cleanup_old_records(days_to_keep=30)
        
        assert deleted_count == 1
        mock_notification_manager.send_notification.assert_called()
    
    def test_configuration_methods(self, deployment_reporter):
        """Test configuration methods."""
        # Test auto-save configuration
        deployment_reporter.configure_auto_save(False)
        assert deployment_reporter.auto_save_enabled is False
        
        deployment_reporter.configure_auto_save(True)
        assert deployment_reporter.auto_save_enabled is True
        
        # Test auto-report configuration
        deployment_reporter.configure_auto_report(False)
        assert deployment_reporter.auto_report_enabled is False
        
        deployment_reporter.configure_auto_report(True)
        assert deployment_reporter.auto_report_enabled is True
        
        # Test notifications configuration
        deployment_reporter.configure_notifications(False)
        assert deployment_reporter.notification_enabled is False
        
        deployment_reporter.configure_notifications(True)
        assert deployment_reporter.notification_enabled is True
    
    @pytest.mark.asyncio
    async def test_progress_callback_integration(self, deployment_reporter, mock_notification_manager):
        """Test that progress callbacks are properly integrated."""
        deployment_id = "test-deployment-123"
        
        # Create tracker
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="production",
            commit_sha="abc123",
            image_tag="test:latest"
        )
        
        # Start a phase to trigger progress callback
        await tracker.start_phase(DeploymentPhase.VALIDATION, 1, "Starting validation")
        
        # Give async callbacks time to execute
        await asyncio.sleep(0.1)
        
        # Verify that the deployment record was auto-saved (if enabled)
        if deployment_reporter.auto_save_enabled:
            saved_record = deployment_reporter.history_manager.get_deployment_record(deployment_id)
            assert saved_record is not None
    
    @pytest.mark.asyncio
    async def test_test_reporting_system(self, deployment_reporter, mock_notification_manager):
        """Test the reporting system test functionality."""
        # Mock successful test results
        mock_notification_manager.test_channels.return_value = [
            MagicMock(channel_name="test-channel", success=True)
        ]
        
        test_results = await deployment_reporter.test_reporting_system()
        
        assert test_results is not None
        assert 'timestamp' in test_results
        assert 'tests' in test_results
        assert 'overall_success' in test_results
        
        # Check individual test results
        assert 'notifications' in test_results['tests']
        assert 'history' in test_results['tests']
        assert 'report_generation' in test_results['tests']
    
    @pytest.mark.asyncio
    async def test_notification_sending(self, deployment_reporter, mock_notification_manager):
        """Test that notifications are sent at appropriate times."""
        deployment_id = "test-deployment-123"
        
        # Create tracker (should send start notification)
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="production",
            commit_sha="abc123",
            image_tag="test:latest"
        )
        
        # Give async notifications time to execute
        await asyncio.sleep(0.1)
        
        # Complete deployment (should send completion notification)
        await deployment_reporter.complete_deployment(deployment_id, success=True)
        
        # Verify notifications were sent
        assert mock_notification_manager.send_notification.call_count >= 2  # Start + completion


if __name__ == "__main__":
    pytest.main([__file__])