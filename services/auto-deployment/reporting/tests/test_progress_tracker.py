"""
Tests for progress tracker functionality.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from models import DeploymentRecord, DeploymentPhase, ProgressStatus, DeploymentStatus
from progress_tracker import ProgressTracker


class TestProgressTracker:
    """Test cases for ProgressTracker class."""
    
    @pytest.fixture
    def deployment_record(self):
        """Create test deployment record."""
        return DeploymentRecord(
            deployment_id="test-deployment-123",
            environment="test",
            commit_sha="abc123",
            image_tag="test:latest"
        )
    
    @pytest.fixture
    def progress_tracker(self, deployment_record):
        """Create test progress tracker."""
        return ProgressTracker(deployment_record)
    
    def test_initialization(self, progress_tracker, deployment_record):
        """Test progress tracker initialization."""
        assert progress_tracker.deployment_record == deployment_record
        assert len(progress_tracker.progress_callbacks) == 0
        assert len(progress_tracker.phase_callbacks) == 0
        
        # Check that all phases are initialized
        for phase in DeploymentPhase:
            assert phase in progress_tracker.deployment_record.phases
            assert progress_tracker.deployment_record.phases[phase].status == ProgressStatus.NOT_STARTED
    
    def test_add_callbacks(self, progress_tracker):
        """Test adding progress and phase callbacks."""
        progress_callback = MagicMock()
        phase_callback = MagicMock()
        
        progress_tracker.add_progress_callback(progress_callback)
        progress_tracker.add_phase_callback(DeploymentPhase.VALIDATION, phase_callback)
        
        assert progress_callback in progress_tracker.progress_callbacks
        assert phase_callback in progress_tracker.phase_callbacks[DeploymentPhase.VALIDATION]
    
    @pytest.mark.asyncio
    async def test_start_phase(self, progress_tracker):
        """Test starting a deployment phase."""
        phase = DeploymentPhase.VALIDATION
        total_steps = 5
        description = "Starting validation"
        
        await progress_tracker.start_phase(phase, total_steps, description)
        
        phase_progress = progress_tracker.deployment_record.phases[phase]
        assert phase_progress.status == ProgressStatus.IN_PROGRESS
        assert phase_progress.total_steps == total_steps
        assert phase_progress.current_step == description
        assert phase_progress.start_time is not None
        assert progress_tracker.deployment_record.current_phase == phase
    
    @pytest.mark.asyncio
    async def test_update_step(self, progress_tracker):
        """Test updating step in a phase."""
        phase = DeploymentPhase.VALIDATION
        
        # Start phase first
        await progress_tracker.start_phase(phase, 5)
        
        # Update step
        step_description = "Validating code quality"
        completed_steps = 2
        
        await progress_tracker.update_step(phase, step_description, completed_steps)
        
        phase_progress = progress_tracker.deployment_record.phases[phase]
        assert phase_progress.current_step == step_description
        assert phase_progress.completed_steps == completed_steps
        assert phase_progress.progress_percentage == 40.0  # 2/5 * 100
    
    @pytest.mark.asyncio
    async def test_complete_phase_success(self, progress_tracker):
        """Test completing a phase successfully."""
        phase = DeploymentPhase.VALIDATION
        
        # Start phase first
        await progress_tracker.start_phase(phase, 3)
        
        # Complete phase
        await progress_tracker.complete_phase(phase, success=True)
        
        phase_progress = progress_tracker.deployment_record.phases[phase]
        assert phase_progress.status == ProgressStatus.COMPLETED
        assert phase_progress.end_time is not None
        assert phase_progress.progress_percentage == 100.0
        assert phase_progress.completed_steps == 3
        assert phase_progress.duration_seconds is not None
    
    @pytest.mark.asyncio
    async def test_complete_phase_failure(self, progress_tracker):
        """Test completing a phase with failure."""
        phase = DeploymentPhase.VALIDATION
        error_message = "Validation failed"
        warnings = ["Warning 1", "Warning 2"]
        
        # Start phase first
        await progress_tracker.start_phase(phase, 3)
        
        # Complete phase with failure
        await progress_tracker.complete_phase(phase, success=False, error_message=error_message, warnings=warnings)
        
        phase_progress = progress_tracker.deployment_record.phases[phase]
        assert phase_progress.status == ProgressStatus.FAILED
        assert phase_progress.error_message == error_message
        assert phase_progress.warnings == warnings
        
        # Check that errors are added to deployment record
        assert f"{phase.value}: {error_message}" in progress_tracker.deployment_record.errors
        assert f"{phase.value}: Warning 1" in progress_tracker.deployment_record.warnings
        assert f"{phase.value}: Warning 2" in progress_tracker.deployment_record.warnings
    
    @pytest.mark.asyncio
    async def test_fail_phase(self, progress_tracker):
        """Test failing a phase."""
        phase = DeploymentPhase.DEPLOYMENT
        error_message = "Deployment failed"
        
        await progress_tracker.fail_phase(phase, error_message)
        
        phase_progress = progress_tracker.deployment_record.phases[phase]
        assert phase_progress.status == ProgressStatus.FAILED
        assert phase_progress.error_message == error_message
    
    @pytest.mark.asyncio
    async def test_skip_phase(self, progress_tracker):
        """Test skipping a phase."""
        phase = DeploymentPhase.MONITORING
        reason = "Monitoring disabled for test environment"
        
        await progress_tracker.skip_phase(phase, reason)
        
        phase_progress = progress_tracker.deployment_record.phases[phase]
        assert phase_progress.status == ProgressStatus.SKIPPED
        assert phase_progress.current_step == f"Skipped: {reason}"
        assert phase_progress.progress_percentage == 100.0
    
    @pytest.mark.asyncio
    async def test_update_deployment_status(self, progress_tracker):
        """Test updating deployment status."""
        new_status = DeploymentStatus.COMPLETED
        
        await progress_tracker.update_deployment_status(new_status)
        
        assert progress_tracker.deployment_record.status == new_status
        assert progress_tracker.deployment_record.end_time is not None
        assert progress_tracker.deployment_record.metrics.total_duration_seconds > 0
    
    @pytest.mark.asyncio
    async def test_add_metadata(self, progress_tracker):
        """Test adding metadata."""
        key = "test_key"
        value = "test_value"
        
        await progress_tracker.add_metadata(key, value)
        
        assert progress_tracker.deployment_record.metadata[key] == value
    
    @pytest.mark.asyncio
    async def test_add_health_check_result(self, progress_tracker):
        """Test adding health check result."""
        result = {
            "endpoint": "/health",
            "status_code": 200,
            "response_time_ms": 150,
            "success": True
        }
        
        await progress_tracker.add_health_check_result(result)
        
        assert result in progress_tracker.deployment_record.health_check_results
    
    @pytest.mark.asyncio
    async def test_add_validation_result(self, progress_tracker):
        """Test adding validation result."""
        result = {
            "validator": "code_quality",
            "success": True,
            "score": 95.5
        }
        
        await progress_tracker.add_validation_result(result)
        
        assert result in progress_tracker.deployment_record.validation_results
    
    def test_get_current_progress(self, progress_tracker):
        """Test getting current progress information."""
        progress = progress_tracker.get_current_progress()
        
        assert progress['deployment_id'] == progress_tracker.deployment_record.deployment_id
        assert progress['status'] == progress_tracker.deployment_record.status.value
        assert 'phases' in progress
        assert 'start_time' in progress
        assert 'errors' in progress
        assert 'warnings' in progress
    
    def test_calculate_overall_progress(self, progress_tracker):
        """Test overall progress calculation."""
        # Mark some phases as completed
        progress_tracker.deployment_record.phases[DeploymentPhase.VALIDATION].status = ProgressStatus.COMPLETED
        progress_tracker.deployment_record.phases[DeploymentPhase.BUILD].status = ProgressStatus.COMPLETED
        progress_tracker.deployment_record.phases[DeploymentPhase.DEPLOYMENT].status = ProgressStatus.IN_PROGRESS
        progress_tracker.deployment_record.phases[DeploymentPhase.DEPLOYMENT].progress_percentage = 50.0
        
        overall_progress = progress_tracker.deployment_record.calculate_overall_progress()
        
        # Should be approximately (2 completed + 0.5 in progress) / total phases * 100
        expected_progress = (2.5 / len(DeploymentPhase)) * 100
        assert abs(overall_progress - expected_progress) < 1.0
    
    @pytest.mark.asyncio
    async def test_progress_callbacks(self, progress_tracker):
        """Test that progress callbacks are called."""
        callback_called = False
        callback_data = None
        
        async def test_callback(data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = data
        
        progress_tracker.add_progress_callback(test_callback)
        
        await progress_tracker.start_phase(DeploymentPhase.VALIDATION, 1)
        
        # Give async callbacks time to execute
        await asyncio.sleep(0.1)
        
        assert callback_called
        assert callback_data is not None
        assert callback_data['deployment_id'] == progress_tracker.deployment_record.deployment_id
    
    @pytest.mark.asyncio
    async def test_phase_callbacks(self, progress_tracker):
        """Test that phase-specific callbacks are called."""
        callback_called = False
        callback_phase = None
        callback_data = None
        
        async def test_phase_callback(phase, data):
            nonlocal callback_called, callback_phase, callback_data
            callback_called = True
            callback_phase = phase
            callback_data = data
        
        progress_tracker.add_phase_callback(DeploymentPhase.VALIDATION, test_phase_callback)
        
        await progress_tracker.start_phase(DeploymentPhase.VALIDATION, 1)
        
        # Give async callbacks time to execute
        await asyncio.sleep(0.1)
        
        assert callback_called
        assert callback_phase == DeploymentPhase.VALIDATION
        assert callback_data is not None
    
    @pytest.mark.asyncio
    async def test_callback_error_handling(self, progress_tracker):
        """Test that callback errors don't break progress tracking."""
        def failing_callback(data):
            raise Exception("Callback error")
        
        progress_tracker.add_progress_callback(failing_callback)
        
        # This should not raise an exception
        await progress_tracker.start_phase(DeploymentPhase.VALIDATION, 1)
        
        # Progress should still be updated despite callback error
        phase_progress = progress_tracker.deployment_record.phases[DeploymentPhase.VALIDATION]
        assert phase_progress.status == ProgressStatus.IN_PROGRESS


if __name__ == "__main__":
    pytest.main([__file__])