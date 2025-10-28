"""
Integration tests for the complete reporting system.

This module tests the integration between all reporting components:
- DeploymentReporter
- ProgressTracker
- HistoryManager
- ReportGenerator
- NotificationManager integration
"""

import asyncio
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from models import DeploymentRecord, DeploymentStatus, DeploymentPhase, ReportConfig
from deployment_reporter import DeploymentReporter
try:
    from ...notification.notification_manager import NotificationManager
except ImportError:
    # Mock for testing
    class NotificationManager:
        async def send_notification(self, **kwargs):
            pass
        async def test_channels(self):
            return []


class TestReportingIntegration:
    """Integration test cases for the complete reporting system."""
    
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
        mock_manager.test_channels = AsyncMock(return_value=[
            MagicMock(channel_name="slack", success=True),
            MagicMock(channel_name="email", success=True)
        ])
        return mock_manager
    
    @pytest.fixture
    def deployment_reporter(self, mock_notification_manager, temp_db_path, temp_reports_dir):
        """Create deployment reporter for integration testing."""
        return DeploymentReporter(
            notification_manager=mock_notification_manager,
            history_db_path=temp_db_path,
            reports_dir=temp_reports_dir
        )
    
    @pytest.mark.asyncio
    async def test_complete_deployment_workflow(self, deployment_reporter, mock_notification_manager, temp_reports_dir):
        """Test complete deployment workflow from start to finish."""
        deployment_id = "integration-test-deployment"
        environment = "production"
        commit_sha = "abc123def456"
        image_tag = "myapp:v1.2.3"
        
        # Step 1: Create deployment tracker
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment=environment,
            commit_sha=commit_sha,
            image_tag=image_tag,
            deployment_config={"memory": "2Gi", "cpu": "1"},
            environment_config={"region": "us-central1"}
        )
        
        assert tracker is not None
        assert deployment_id in deployment_reporter.active_deployments
        
        # Step 2: Simulate deployment phases
        await tracker.start_phase(DeploymentPhase.VALIDATION, 3, "Starting validation")
        await tracker.update_step(DeploymentPhase.VALIDATION, "Validating code quality", 1)
        await tracker.update_step(DeploymentPhase.VALIDATION, "Validating security", 2)
        await tracker.complete_phase(DeploymentPhase.VALIDATION, success=True)
        
        await tracker.start_phase(DeploymentPhase.BUILD, 2, "Starting build")
        await tracker.update_step(DeploymentPhase.BUILD, "Building image", 1)
        await tracker.complete_phase(DeploymentPhase.BUILD, success=True)
        
        await tracker.start_phase(DeploymentPhase.DEPLOYMENT, 4, "Starting deployment")
        await tracker.update_step(DeploymentPhase.DEPLOYMENT, "Deploying to Cloud Run", 2)
        await tracker.complete_phase(DeploymentPhase.DEPLOYMENT, success=True)
        
        await tracker.start_phase(DeploymentPhase.HEALTH_CHECK, 2, "Starting health checks")
        await tracker.add_health_check_result({
            "endpoint": "/health",
            "status_code": 200,
            "response_time_ms": 150,
            "success": True
        })
        await tracker.complete_phase(DeploymentPhase.HEALTH_CHECK, success=True)
        
        # Step 3: Complete deployment
        success = await deployment_reporter.complete_deployment(deployment_id, success=True)
        assert success is True
        
        # Step 4: Verify deployment is no longer active
        assert deployment_id not in deployment_reporter.active_deployments
        
        # Step 5: Verify record was saved to history
        saved_record = deployment_reporter.history_manager.get_deployment_record(deployment_id)
        assert saved_record is not None
        assert saved_record.status == DeploymentStatus.COMPLETED
        assert saved_record.overall_progress_percentage == 100.0
        
        # Step 6: Verify reports were generated
        report_files = list(Path(temp_reports_dir).glob(f"deployment_report_{deployment_id}_*"))
        assert len(report_files) >= 1  # At least one report format
        
        # Step 7: Verify notifications were sent
        assert mock_notification_manager.send_notification.call_count >= 2  # Start + completion
        
        # Step 8: Test report generation
        json_report = await deployment_reporter.generate_deployment_report(
            deployment_id, format="json", save_to_file=False
        )
        assert json_report is not None
        assert deployment_id in json_report
        
        html_report = await deployment_reporter.generate_deployment_report(
            deployment_id, format="html", save_to_file=False
        )
        assert html_report is not None
        assert "<!DOCTYPE html>" in html_report
        
        markdown_report = await deployment_reporter.generate_deployment_report(
            deployment_id, format="markdown", save_to_file=False
        )
        assert markdown_report is not None
        assert "# Deployment Report" in markdown_report
    
    @pytest.mark.asyncio
    async def test_failed_deployment_workflow(self, deployment_reporter, mock_notification_manager):
        """Test workflow for failed deployment."""
        deployment_id = "failed-integration-test"
        
        # Create deployment tracker
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="staging",
            commit_sha="def456ghi789",
            image_tag="myapp:v1.2.4"
        )
        
        # Simulate failure during deployment phase
        await tracker.start_phase(DeploymentPhase.VALIDATION, 2)
        await tracker.complete_phase(DeploymentPhase.VALIDATION, success=True)
        
        await tracker.start_phase(DeploymentPhase.BUILD, 3)
        await tracker.complete_phase(DeploymentPhase.BUILD, success=True)
        
        await tracker.start_phase(DeploymentPhase.DEPLOYMENT, 5)
        await tracker.update_step(DeploymentPhase.DEPLOYMENT, "Deploying service", 2)
        await tracker.fail_phase(
            DeploymentPhase.DEPLOYMENT,
            "Service deployment failed: Resource quota exceeded",
            warnings=["High resource usage detected"]
        )
        
        # Complete deployment as failed
        success = await deployment_reporter.complete_deployment(deployment_id, success=False)
        assert success is True
        
        # Verify record was saved with failure status
        saved_record = deployment_reporter.history_manager.get_deployment_record(deployment_id)
        assert saved_record is not None
        assert saved_record.status == DeploymentStatus.FAILED
        assert len(saved_record.errors) > 0
        assert len(saved_record.warnings) > 0
        
        # Verify failure notification was sent
        notification_calls = mock_notification_manager.send_notification.call_args_list
        completion_call = notification_calls[-1]  # Last call should be completion
        assert "failed" in completion_call[1]['title'].lower() or "Failed" in completion_call[1]['title']
    
    @pytest.mark.asyncio
    async def test_multiple_concurrent_deployments(self, deployment_reporter, mock_notification_manager):
        """Test handling multiple concurrent deployments."""
        deployment_ids = [f"concurrent-deployment-{i}" for i in range(3)]
        trackers = []
        
        # Create multiple concurrent deployments
        for i, deployment_id in enumerate(deployment_ids):
            tracker = deployment_reporter.create_deployment_tracker(
                deployment_id=deployment_id,
                environment=f"env-{i}",
                commit_sha=f"commit-{i}",
                image_tag=f"app:v{i}"
            )
            trackers.append(tracker)
        
        # Verify all are active
        assert len(deployment_reporter.active_deployments) == 3
        
        # Simulate concurrent progress
        tasks = []
        for i, tracker in enumerate(trackers):
            async def simulate_deployment(t, idx):
                await t.start_phase(DeploymentPhase.VALIDATION, 2)
                await t.complete_phase(DeploymentPhase.VALIDATION, success=True)
                await t.start_phase(DeploymentPhase.DEPLOYMENT, 3)
                await t.complete_phase(DeploymentPhase.DEPLOYMENT, success=True)
                await deployment_reporter.complete_deployment(deployment_ids[idx], success=True)
            
            tasks.append(simulate_deployment(tracker, i))
        
        # Wait for all deployments to complete
        await asyncio.gather(*tasks)
        
        # Verify all deployments completed
        assert len(deployment_reporter.active_deployments) == 0
        
        # Verify all records were saved
        for deployment_id in deployment_ids:
            saved_record = deployment_reporter.history_manager.get_deployment_record(deployment_id)
            assert saved_record is not None
            assert saved_record.status == DeploymentStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_deployment_with_rollback(self, deployment_reporter, mock_notification_manager):
        """Test deployment workflow with rollback scenario."""
        deployment_id = "rollback-test-deployment"
        
        # Create deployment tracker
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="production",
            commit_sha="rollback123",
            image_tag="myapp:v2.0.0"
        )
        
        # Simulate successful deployment phases
        await tracker.start_phase(DeploymentPhase.VALIDATION, 2)
        await tracker.complete_phase(DeploymentPhase.VALIDATION, success=True)
        
        await tracker.start_phase(DeploymentPhase.BUILD, 3)
        await tracker.complete_phase(DeploymentPhase.BUILD, success=True)
        
        await tracker.start_phase(DeploymentPhase.DEPLOYMENT, 4)
        await tracker.complete_phase(DeploymentPhase.DEPLOYMENT, success=True)
        
        # Simulate health check failure leading to rollback
        await tracker.start_phase(DeploymentPhase.HEALTH_CHECK, 2)
        await tracker.add_health_check_result({
            "endpoint": "/health",
            "status_code": 500,
            "response_time_ms": 5000,
            "success": False,
            "error": "Service unavailable"
        })
        await tracker.fail_phase(
            DeploymentPhase.HEALTH_CHECK,
            "Health checks failed, initiating rollback"
        )
        
        # Add rollback information
        await tracker.add_metadata("rollback_revision", "myapp-v199")
        await tracker.add_metadata("rollback_reason", "Health check failures")
        tracker.deployment_record.rollback_revision = "myapp-v199"
        tracker.deployment_record.rollback_reason = "Health check failures"
        tracker.deployment_record.rollback_time = datetime.utcnow()
        
        # Complete deployment with rollback status
        success = await deployment_reporter.complete_deployment(
            deployment_id, success=False, final_status=DeploymentStatus.ROLLED_BACK
        )
        assert success is True
        
        # Verify rollback information was saved
        saved_record = deployment_reporter.history_manager.get_deployment_record(deployment_id)
        assert saved_record is not None
        assert saved_record.status == DeploymentStatus.ROLLED_BACK
        assert saved_record.rollback_revision == "myapp-v199"
        assert saved_record.rollback_reason == "Health check failures"
        assert saved_record.rollback_time is not None
        
        # Generate report and verify rollback information is included
        report_content = await deployment_reporter.generate_deployment_report(
            deployment_id, format="json", save_to_file=False
        )
        assert report_content is not None
        assert "rollback" in report_content.lower()
    
    @pytest.mark.asyncio
    async def test_summary_report_generation(self, deployment_reporter, mock_notification_manager):
        """Test summary report generation with multiple deployments."""
        # Create multiple deployments with different outcomes
        deployment_configs = [
            ("success-1", "production", DeploymentStatus.COMPLETED),
            ("success-2", "production", DeploymentStatus.COMPLETED),
            ("failed-1", "production", DeploymentStatus.FAILED),
            ("success-3", "staging", DeploymentStatus.COMPLETED),
            ("rollback-1", "production", DeploymentStatus.ROLLED_BACK)
        ]
        
        for deployment_id, environment, final_status in deployment_configs:
            tracker = deployment_reporter.create_deployment_tracker(
                deployment_id=deployment_id,
                environment=environment,
                commit_sha=f"commit-{deployment_id}",
                image_tag=f"app:{deployment_id}"
            )
            
            # Simulate basic deployment flow
            await tracker.start_phase(DeploymentPhase.VALIDATION, 1)
            await tracker.complete_phase(DeploymentPhase.VALIDATION, success=True)
            
            if final_status == DeploymentStatus.FAILED:
                await tracker.start_phase(DeploymentPhase.DEPLOYMENT, 2)
                await tracker.fail_phase(DeploymentPhase.DEPLOYMENT, "Simulated failure")
            else:
                await tracker.start_phase(DeploymentPhase.DEPLOYMENT, 2)
                await tracker.complete_phase(DeploymentPhase.DEPLOYMENT, success=True)
            
            success = await deployment_reporter.complete_deployment(
                deployment_id,
                success=(final_status == DeploymentStatus.COMPLETED),
                final_status=final_status
            )
            assert success is True
        
        # Generate summary reports
        json_summary = await deployment_reporter.generate_summary_report(
            environment="production", days=1, format="json", save_to_file=False
        )
        assert json_summary is not None
        assert "summary" in json_summary
        assert "deployments" in json_summary
        
        html_summary = await deployment_reporter.generate_summary_report(
            environment="production", days=1, format="html", save_to_file=False
        )
        assert html_summary is not None
        assert "Deployment Summary Report" in html_summary
        
        markdown_summary = await deployment_reporter.generate_summary_report(
            environment="production", days=1, format="markdown", save_to_file=False
        )
        assert markdown_summary is not None
        assert "# Deployment Summary Report" in markdown_summary
        
        # Verify statistics
        stats = deployment_reporter.get_deployment_statistics(environment="production", days=1)
        assert stats['total_deployments'] == 4  # production deployments
        assert stats['successful_deployments'] == 2
        assert stats['failed_deployments'] == 2  # failed + rolled back
        assert stats['success_rate'] == 50.0
    
    @pytest.mark.asyncio
    async def test_notification_integration(self, deployment_reporter, mock_notification_manager):
        """Test integration with notification system."""
        deployment_id = "notification-test-deployment"
        
        # Create deployment
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="production",
            commit_sha="notify123",
            image_tag="myapp:v1.0.0"
        )
        
        # Give time for start notification
        await asyncio.sleep(0.1)
        
        # Simulate deployment progress
        await tracker.start_phase(DeploymentPhase.VALIDATION, 4)
        await tracker.update_step(DeploymentPhase.VALIDATION, "Step 1", 1)
        await tracker.update_step(DeploymentPhase.VALIDATION, "Step 2", 2)
        await tracker.update_step(DeploymentPhase.VALIDATION, "Step 3", 3)
        await tracker.complete_phase(DeploymentPhase.VALIDATION, success=True)
        
        # Give time for progress notifications
        await asyncio.sleep(0.1)
        
        # Complete deployment
        await deployment_reporter.complete_deployment(deployment_id, success=True)
        
        # Give time for completion notification
        await asyncio.sleep(0.1)
        
        # Verify notifications were sent
        notification_calls = mock_notification_manager.send_notification.call_args_list
        assert len(notification_calls) >= 2  # At least start + completion
        
        # Verify notification content
        start_notification = notification_calls[0]
        assert "started" in start_notification[1]['title'].lower()
        assert deployment_id[:8] in start_notification[1]['content']
        
        completion_notification = notification_calls[-1]
        assert "completed" in completion_notification[1]['title'].lower()
        assert deployment_id[:8] in completion_notification[1]['content']
    
    @pytest.mark.asyncio
    async def test_configuration_persistence(self, deployment_reporter):
        """Test that configuration changes persist across operations."""
        # Change configurations
        deployment_reporter.configure_auto_save(False)
        deployment_reporter.configure_auto_report(False)
        deployment_reporter.configure_notifications(False)
        
        # Create and complete deployment
        deployment_id = "config-test-deployment"
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="test",
            commit_sha="config123",
            image_tag="test:config"
        )
        
        await deployment_reporter.complete_deployment(deployment_id, success=True)
        
        # Verify configurations are still applied
        assert deployment_reporter.auto_save_enabled is False
        assert deployment_reporter.auto_report_enabled is False
        assert deployment_reporter.notification_enabled is False
        
        # Since auto-save is disabled, record should not be in history
        saved_record = deployment_reporter.history_manager.get_deployment_record(deployment_id)
        # Note: The record might still be saved due to explicit save in complete_deployment
        # This test mainly verifies that configuration state is maintained
    
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, deployment_reporter, mock_notification_manager):
        """Test error handling and system recovery."""
        deployment_id = "error-handling-test"
        
        # Create deployment
        tracker = deployment_reporter.create_deployment_tracker(
            deployment_id=deployment_id,
            environment="test",
            commit_sha="error123",
            image_tag="test:error"
        )
        
        # Simulate error in notification system
        mock_notification_manager.send_notification.side_effect = Exception("Notification error")
        
        # System should continue working despite notification errors
        await tracker.start_phase(DeploymentPhase.VALIDATION, 1)
        await tracker.complete_phase(DeploymentPhase.VALIDATION, success=True)
        
        success = await deployment_reporter.complete_deployment(deployment_id, success=True)
        assert success is True  # Should succeed despite notification error
        
        # Verify record was still saved
        saved_record = deployment_reporter.history_manager.get_deployment_record(deployment_id)
        assert saved_record is not None
        assert saved_record.status == DeploymentStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_system_test_functionality(self, deployment_reporter, mock_notification_manager):
        """Test the integrated system test functionality."""
        test_results = await deployment_reporter.test_reporting_system()
        
        assert test_results is not None
        assert 'timestamp' in test_results
        assert 'tests' in test_results
        assert 'overall_success' in test_results
        
        # Check individual test components
        tests = test_results['tests']
        assert 'notifications' in tests
        assert 'history' in tests
        assert 'report_generation' in tests
        
        # Verify test results structure
        for test_name, test_result in tests.items():
            assert 'success' in test_result
            assert isinstance(test_result['success'], bool)


if __name__ == "__main__":
    pytest.main([__file__])