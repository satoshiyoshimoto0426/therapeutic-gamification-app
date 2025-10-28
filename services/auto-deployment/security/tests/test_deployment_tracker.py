"""
Tests for deployment tracker.
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from deployment_tracker import DeploymentTracker, DeploymentStatus, DeploymentStage
from audit_logger import AuditLogger, AuditContext
from security_config import SecurityConfig


class TestDeploymentTracker(unittest.TestCase):
    """Test deployment tracker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = SecurityConfig(audit_logging=True)
        self.audit_logger = AuditLogger(self.config)
        self.tracker = DeploymentTracker(self.config, self.audit_logger)
        self.context = AuditContext(
            user_id="test_user",
            session_id="test_session",
            ip_address="192.168.1.1",
            environment="test"
        )
    
    def test_start_deployment(self):
        """Test starting a new deployment."""
        deployment_id = self.tracker.start_deployment(
            environment="production",
            commit_sha="abc123",
            image_tag="v1.0.0",
            user_id="test_user",
            metadata={"branch": "main"},
            context=self.context
        )
        
        self.assertIsInstance(deployment_id, str)
        self.assertIn(deployment_id, self.tracker._deployments)
        self.assertIn(deployment_id, self.tracker._active_deployments)
        
        # Check deployment record
        deployment = self.tracker._deployments[deployment_id]
        self.assertEqual(deployment.environment, "production")
        self.assertEqual(deployment.commit_sha, "abc123")
        self.assertEqual(deployment.image_tag, "v1.0.0")
        self.assertEqual(deployment.user_id, "test_user")
        self.assertEqual(deployment.status, DeploymentStatus.PENDING)
        self.assertEqual(deployment.metadata["branch"], "main")
        self.assertTrue(len(deployment.actions) > 0)
    
    def test_track_action(self):
        """Test tracking deployment actions."""
        deployment_id = self.tracker.start_deployment(
            environment="production",
            commit_sha="abc123",
            image_tag="v1.0.0",
            user_id="test_user",
            context=self.context
        )
        
        action_id = self.tracker.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.BUILD,
            action="build_image",
            status=DeploymentStatus.BUILDING,
            details={"dockerfile": "Dockerfile"},
            user_id="test_user",
            duration_seconds=60.5,
            context=self.context
        )
        
        self.assertIsInstance(action_id, str)
        
        # Check deployment record was updated
        deployment = self.tracker._deployments[deployment_id]
        self.assertEqual(deployment.status, DeploymentStatus.BUILDING)
        self.assertTrue(len(deployment.actions) >= 2)  # Start + build actions
        
        # Check the build action
        build_action = deployment.actions[-1]
        self.assertEqual(build_action.action_id, action_id)
        self.assertEqual(build_action.stage, DeploymentStage.BUILD)
        self.assertEqual(build_action.action, "build_image")
        self.assertEqual(build_action.status, DeploymentStatus.BUILDING)
        self.assertEqual(build_action.duration_seconds, 60.5)
        self.assertEqual(build_action.details["dockerfile"], "Dockerfile")
    
    def test_track_action_invalid_deployment(self):
        """Test tracking action for invalid deployment."""
        with self.assertRaises(ValueError):
            self.tracker.track_action(
                deployment_id="invalid-id",
                stage=DeploymentStage.BUILD,
                action="build_image",
                status=DeploymentStatus.BUILDING
            )
    
    def test_complete_deployment_success(self):
        """Test completing a deployment successfully."""
        deployment_id = self.tracker.start_deployment(
            environment="production",
            commit_sha="abc123",
            image_tag="v1.0.0",
            user_id="test_user",
            context=self.context
        )
        
        self.tracker.complete_deployment(
            deployment_id=deployment_id,
            success=True,
            details={"final_url": "https://app.example.com"},
            context=self.context
        )
        
        # Check deployment status
        deployment = self.tracker._deployments[deployment_id]
        self.assertEqual(deployment.status, DeploymentStatus.COMPLETED)
        self.assertNotIn(deployment_id, self.tracker._active_deployments)
        
        # Check completion action was added
        completion_action = deployment.actions[-1]
        self.assertEqual(completion_action.action, "complete_deployment")
        self.assertEqual(completion_action.status, DeploymentStatus.COMPLETED)
        self.assertTrue(completion_action.details["success"])
        self.assertIsInstance(completion_action.duration_seconds, float)
    
    def test_complete_deployment_failure(self):
        """Test completing a deployment with failure."""
        deployment_id = self.tracker.start_deployment(
            environment="production",
            commit_sha="abc123",
            image_tag="v1.0.0",
            user_id="test_user",
            context=self.context
        )
        
        self.tracker.complete_deployment(
            deployment_id=deployment_id,
            success=False,
            details={"error_message": "Build failed"},
            context=self.context
        )
        
        # Check deployment status
        deployment = self.tracker._deployments[deployment_id]
        self.assertEqual(deployment.status, DeploymentStatus.FAILED)
        
        # Check completion action
        completion_action = deployment.actions[-1]
        self.assertEqual(completion_action.status, DeploymentStatus.FAILED)
        self.assertFalse(completion_action.details["success"])
    
    def test_complete_deployment_invalid_id(self):
        """Test completing deployment with invalid ID."""
        with self.assertRaises(ValueError):
            self.tracker.complete_deployment(
                deployment_id="invalid-id",
                success=True
            )
    
    def test_rollback_deployment(self):
        """Test rolling back a deployment."""
        deployment_id = self.tracker.start_deployment(
            environment="production",
            commit_sha="abc123",
            image_tag="v1.0.0",
            user_id="test_user",
            context=self.context
        )
        
        self.tracker.rollback_deployment(
            deployment_id=deployment_id,
            reason="Health check failed",
            target_revision="v0.9.0",
            context=self.context
        )
        
        # Check deployment status
        deployment = self.tracker._deployments[deployment_id]
        self.assertEqual(deployment.status, DeploymentStatus.ROLLED_BACK)
        
        # Check rollback action
        rollback_action = deployment.actions[-1]
        self.assertEqual(rollback_action.action, "rollback_deployment")
        self.assertEqual(rollback_action.status, DeploymentStatus.ROLLED_BACK)
        self.assertEqual(rollback_action.details["reason"], "Health check failed")
        self.assertEqual(rollback_action.details["target_revision"], "v0.9.0")
    
    def test_rollback_deployment_invalid_id(self):
        """Test rolling back deployment with invalid ID."""
        with self.assertRaises(ValueError):
            self.tracker.rollback_deployment(
                deployment_id="invalid-id",
                reason="Test rollback"
            )
    
    def test_get_deployment(self):
        """Test getting deployment by ID."""
        deployment_id = self.tracker.start_deployment(
            environment="production",
            commit_sha="abc123",
            image_tag="v1.0.0",
            user_id="test_user",
            context=self.context
        )
        
        deployment = self.tracker.get_deployment(deployment_id)
        
        self.assertIsNotNone(deployment)
        self.assertEqual(deployment.deployment_id, deployment_id)
        self.assertEqual(deployment.environment, "production")
        
        # Test non-existent deployment
        non_existent = self.tracker.get_deployment("invalid-id")
        self.assertIsNone(non_existent)
    
    def test_get_deployments_no_filter(self):
        """Test getting all deployments without filters."""
        # Create test deployments
        dep1 = self.tracker.start_deployment("prod", "abc123", "v1.0.0", "user1", context=self.context)
        dep2 = self.tracker.start_deployment("staging", "def456", "v1.1.0", "user2", context=self.context)
        
        deployments = self.tracker.get_deployments()
        
        self.assertEqual(len(deployments), 2)
        deployment_ids = [d.deployment_id for d in deployments]
        self.assertIn(dep1, deployment_ids)
        self.assertIn(dep2, deployment_ids)
    
    def test_get_deployments_with_filters(self):
        """Test getting deployments with filters."""
        # Create test deployments
        dep1 = self.tracker.start_deployment("prod", "abc123", "v1.0.0", "user1", context=self.context)
        dep2 = self.tracker.start_deployment("staging", "def456", "v1.1.0", "user2", context=self.context)
        
        # Complete one deployment
        self.tracker.complete_deployment(dep1, success=True, context=self.context)
        
        # Filter by environment
        prod_deployments = self.tracker.get_deployments(environment="prod")
        self.assertEqual(len(prod_deployments), 1)
        self.assertEqual(prod_deployments[0].deployment_id, dep1)
        
        # Filter by status
        completed_deployments = self.tracker.get_deployments(status=DeploymentStatus.COMPLETED)
        self.assertEqual(len(completed_deployments), 1)
        self.assertEqual(completed_deployments[0].deployment_id, dep1)
        
        # Filter by user
        user1_deployments = self.tracker.get_deployments(user_id="user1")
        self.assertEqual(len(user1_deployments), 1)
        self.assertEqual(user1_deployments[0].deployment_id, dep1)
        
        # Filter with limit
        limited_deployments = self.tracker.get_deployments(limit=1)
        self.assertEqual(len(limited_deployments), 1)
    
    def test_get_deployments_time_filter(self):
        """Test getting deployments with time filters."""
        now = datetime.now(timezone.utc)
        past = now - timedelta(hours=1)
        future = now + timedelta(hours=1)
        
        # Create test deployment
        dep1 = self.tracker.start_deployment("prod", "abc123", "v1.0.0", "user1", context=self.context)
        
        # Filter by start time
        deployments_after_past = self.tracker.get_deployments(start_time=past)
        self.assertEqual(len(deployments_after_past), 1)
        
        # Filter by end time
        deployments_before_future = self.tracker.get_deployments(end_time=future)
        self.assertEqual(len(deployments_before_future), 1)
        
        # Filter by time range
        deployments_in_range = self.tracker.get_deployments(start_time=past, end_time=future)
        self.assertEqual(len(deployments_in_range), 1)
    
    def test_get_deployment_actions(self):
        """Test getting deployment actions."""
        deployment_id = self.tracker.start_deployment(
            environment="production",
            commit_sha="abc123",
            image_tag="v1.0.0",
            user_id="test_user",
            context=self.context
        )
        
        # Add some actions
        self.tracker.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.BUILD,
            action="build_image",
            status=DeploymentStatus.BUILDING,
            context=self.context
        )
        
        self.tracker.track_action(
            deployment_id=deployment_id,
            stage=DeploymentStage.DEPLOY,
            action="deploy_service",
            status=DeploymentStatus.DEPLOYING,
            context=self.context
        )
        
        # Get all actions
        all_actions = self.tracker.get_deployment_actions(deployment_id)
        self.assertEqual(len(all_actions), 3)  # Start + build + deploy
        
        # Get actions by stage
        build_actions = self.tracker.get_deployment_actions(deployment_id, stage=DeploymentStage.BUILD)
        self.assertEqual(len(build_actions), 1)
        self.assertEqual(build_actions[0].action, "build_image")
        
        # Test non-existent deployment
        no_actions = self.tracker.get_deployment_actions("invalid-id")
        self.assertEqual(len(no_actions), 0)
    
    def test_get_deployment_statistics(self):
        """Test getting deployment statistics."""
        # Create test deployments
        dep1 = self.tracker.start_deployment("prod", "abc123", "v1.0.0", "user1", context=self.context)
        dep2 = self.tracker.start_deployment("staging", "def456", "v1.1.0", "user2", context=self.context)
        dep3 = self.tracker.start_deployment("prod", "ghi789", "v1.2.0", "user1", context=self.context)
        
        # Complete some deployments
        self.tracker.complete_deployment(dep1, success=True, context=self.context)
        self.tracker.complete_deployment(dep2, success=False, context=self.context)
        
        stats = self.tracker.get_deployment_statistics()
        
        self.assertEqual(stats['total_deployments'], 3)
        self.assertEqual(stats['successful_deployments'], 1)
        self.assertEqual(stats['failed_deployments'], 1)
        self.assertAlmostEqual(stats['success_rate'], 1/3, places=2)
        self.assertIsInstance(stats['average_duration_seconds'], float)
        
        # Check environment breakdown
        self.assertEqual(stats['deployments_by_environment']['prod'], 2)
        self.assertEqual(stats['deployments_by_environment']['staging'], 1)
        
        # Check status breakdown
        self.assertEqual(stats['deployments_by_status']['completed'], 1)
        self.assertEqual(stats['deployments_by_status']['failed'], 1)
        self.assertEqual(stats['deployments_by_status']['pending'], 1)
    
    def test_get_deployment_statistics_empty(self):
        """Test getting statistics with no deployments."""
        stats = self.tracker.get_deployment_statistics()
        
        self.assertEqual(stats['total_deployments'], 0)
        self.assertEqual(stats['successful_deployments'], 0)
        self.assertEqual(stats['failed_deployments'], 0)
        self.assertEqual(stats['success_rate'], 0.0)
        self.assertEqual(stats['average_duration_seconds'], 0.0)
        self.assertEqual(stats['deployments_by_environment'], {})
        self.assertEqual(stats['deployments_by_status'], {})
    
    def test_export_deployment_history_json(self):
        """Test exporting deployment history to JSON."""
        # Create test deployment
        dep1 = self.tracker.start_deployment("prod", "abc123", "v1.0.0", "user1", context=self.context)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            export_file = f.name
        
        try:
            self.tracker.export_deployment_history(export_file, format='json')
            
            # Verify file was created and contains data
            self.assertTrue(os.path.exists(export_file))
            
            with open(export_file, 'r') as f:
                data = json.load(f)
            
            self.assertIsInstance(data, list)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]['deployment_id'], dep1)
            self.assertIn('actions', data[0])
        finally:
            if os.path.exists(export_file):
                os.unlink(export_file)
    
    def test_export_deployment_history_csv(self):
        """Test exporting deployment history to CSV."""
        # Create test deployment
        dep1 = self.tracker.start_deployment("prod", "abc123", "v1.0.0", "user1", context=self.context)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            export_file = f.name
        
        try:
            self.tracker.export_deployment_history(export_file, format='csv')
            
            # Verify file was created and contains data
            self.assertTrue(os.path.exists(export_file))
            
            with open(export_file, 'r') as f:
                content = f.read()
            
            self.assertIn('deployment_id', content)  # Header should be present
            self.assertIn(dep1, content)  # Deployment ID should be in content
        finally:
            if os.path.exists(export_file):
                os.unlink(export_file)
    
    def test_export_deployment_history_invalid_format(self):
        """Test exporting deployment history with invalid format."""
        with self.assertRaises(ValueError):
            self.tracker.export_deployment_history('test.txt', format='invalid')
    
    def test_cleanup_old_deployments(self):
        """Test cleanup of old deployments."""
        # Create test deployment
        dep1 = self.tracker.start_deployment("prod", "abc123", "v1.0.0", "user1", context=self.context)
        initial_count = len(self.tracker._deployments)
        
        # Cleanup with very short retention (should remove all deployments)
        self.tracker.cleanup_old_deployments(retention_days=0)
        
        # Should have fewer deployments
        final_count = len(self.tracker._deployments)
        self.assertLess(final_count, initial_count)
    
    def test_status_to_audit_result(self):
        """Test status to audit result conversion."""
        # Test success status
        success_result = self.tracker._status_to_audit_result(DeploymentStatus.COMPLETED)
        self.assertEqual(success_result.value, "success")
        
        # Test failure status
        failure_result = self.tracker._status_to_audit_result(DeploymentStatus.FAILED)
        self.assertEqual(failure_result.value, "failure")
        
        # Test warning status
        warning_result = self.tracker._status_to_audit_result(DeploymentStatus.ROLLED_BACK)
        self.assertEqual(warning_result.value, "warning")
        
        # Test info status
        info_result = self.tracker._status_to_audit_result(DeploymentStatus.PENDING)
        self.assertEqual(info_result.value, "info")


if __name__ == '__main__':
    unittest.main()