"""
Progress tracking system for deployment operations.

This module provides real-time progress tracking and notification
for deployment phases and steps.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any

from .models import (
    DeploymentRecord, DeploymentPhase, ProgressStatus, 
    PhaseProgress, DeploymentStatus
)

logger = logging.getLogger(__name__)


class ProgressTracker:
    """Tracks deployment progress and sends real-time updates."""
    
    def __init__(self, deployment_record: DeploymentRecord):
        """
        Initialize progress tracker.
        
        Args:
            deployment_record: Deployment record to track
        """
        self.deployment_record = deployment_record
        self.progress_callbacks: List[Callable] = []
        self.phase_callbacks: Dict[DeploymentPhase, List[Callable]] = {}
        self._lock = asyncio.Lock()
        
        # Initialize all phases
        self._initialize_phases()
    
    def _initialize_phases(self):
        """Initialize all deployment phases with default progress."""
        for phase in DeploymentPhase:
            if phase not in self.deployment_record.phases:
                self.deployment_record.phases[phase] = PhaseProgress(
                    phase=phase,
                    status=ProgressStatus.NOT_STARTED
                )
    
    def add_progress_callback(self, callback: Callable):
        """
        Add callback for progress updates.
        
        Args:
            callback: Function to call on progress updates
        """
        self.progress_callbacks.append(callback)
        logger.debug(f"Added progress callback: {callback.__name__}")
    
    def add_phase_callback(self, phase: DeploymentPhase, callback: Callable):
        """
        Add callback for specific phase updates.
        
        Args:
            phase: Deployment phase to monitor
            callback: Function to call on phase updates
        """
        if phase not in self.phase_callbacks:
            self.phase_callbacks[phase] = []
        self.phase_callbacks[phase].append(callback)
        logger.debug(f"Added phase callback for {phase.value}: {callback.__name__}")
    
    async def start_phase(
        self,
        phase: DeploymentPhase,
        total_steps: int = 1,
        description: str = ""
    ):
        """
        Start a deployment phase.
        
        Args:
            phase: Phase to start
            total_steps: Total number of steps in phase
            description: Phase description
        """
        async with self._lock:
            logger.info(f"Starting phase: {phase.value}")
            
            self.deployment_record.current_phase = phase
            self.deployment_record.update_phase_progress(
                phase,
                status=ProgressStatus.IN_PROGRESS,
                start_time=datetime.utcnow(),
                total_steps=total_steps,
                completed_steps=0,
                progress_percentage=0.0,
                current_step=description
            )
            
            await self._notify_progress_update(phase)
    
    async def update_step(
        self,
        phase: DeploymentPhase,
        step_description: str,
        completed_steps: Optional[int] = None
    ):
        """
        Update current step in a phase.
        
        Args:
            phase: Phase to update
            step_description: Description of current step
            completed_steps: Number of completed steps
        """
        async with self._lock:
            phase_progress = self.deployment_record.phases.get(phase)
            if not phase_progress:
                logger.warning(f"Phase {phase.value} not found for step update")
                return
            
            phase_progress.current_step = step_description
            
            if completed_steps is not None:
                phase_progress.completed_steps = completed_steps
                if phase_progress.total_steps > 0:
                    phase_progress.progress_percentage = (
                        completed_steps / phase_progress.total_steps
                    ) * 100.0
            
            logger.debug(f"Updated step for {phase.value}: {step_description}")
            await self._notify_progress_update(phase)
    
    async def complete_phase(
        self,
        phase: DeploymentPhase,
        success: bool = True,
        error_message: Optional[str] = None,
        warnings: Optional[List[str]] = None
    ):
        """
        Complete a deployment phase.
        
        Args:
            phase: Phase to complete
            success: Whether phase completed successfully
            error_message: Error message if failed
            warnings: List of warnings
        """
        async with self._lock:
            logger.info(f"Completing phase: {phase.value} (success: {success})")
            
            end_time = datetime.utcnow()
            phase_progress = self.deployment_record.phases.get(phase)
            
            if phase_progress:
                duration = None
                if phase_progress.start_time:
                    duration = (end_time - phase_progress.start_time).total_seconds()
                
                self.deployment_record.update_phase_progress(
                    phase,
                    status=ProgressStatus.COMPLETED if success else ProgressStatus.FAILED,
                    end_time=end_time,
                    duration_seconds=duration,
                    progress_percentage=100.0 if success else phase_progress.progress_percentage,
                    completed_steps=phase_progress.total_steps if success else phase_progress.completed_steps,
                    error_message=error_message,
                    warnings=warnings or []
                )
                
                if error_message:
                    self.deployment_record.errors.append(f"{phase.value}: {error_message}")
                
                if warnings:
                    self.deployment_record.warnings.extend([f"{phase.value}: {w}" for w in warnings])
            
            # Update overall progress
            self.deployment_record.calculate_overall_progress()
            
            await self._notify_progress_update(phase)
    
    async def fail_phase(
        self,
        phase: DeploymentPhase,
        error_message: str,
        warnings: Optional[List[str]] = None
    ):
        """
        Mark a phase as failed.
        
        Args:
            phase: Phase that failed
            error_message: Error message
            warnings: List of warnings
        """
        await self.complete_phase(phase, success=False, error_message=error_message, warnings=warnings)
    
    async def skip_phase(self, phase: DeploymentPhase, reason: str = ""):
        """
        Skip a deployment phase.
        
        Args:
            phase: Phase to skip
            reason: Reason for skipping
        """
        async with self._lock:
            logger.info(f"Skipping phase: {phase.value} - {reason}")
            
            self.deployment_record.update_phase_progress(
                phase,
                status=ProgressStatus.SKIPPED,
                current_step=f"Skipped: {reason}",
                progress_percentage=100.0
            )
            
            await self._notify_progress_update(phase)
    
    async def update_deployment_status(self, status: DeploymentStatus):
        """
        Update overall deployment status.
        
        Args:
            status: New deployment status
        """
        async with self._lock:
            logger.info(f"Updating deployment status: {status.value}")
            
            old_status = self.deployment_record.status
            self.deployment_record.status = status
            
            if status in [DeploymentStatus.COMPLETED, DeploymentStatus.FAILED, DeploymentStatus.ROLLED_BACK]:
                self.deployment_record.end_time = datetime.utcnow()
                
                # Calculate final metrics
                duration = self.deployment_record.get_duration_seconds()
                if duration:
                    self.deployment_record.metrics.total_duration_seconds = duration
            
            # Notify about status change
            await self._notify_status_change(old_status, status)
    
    async def add_metadata(self, key: str, value: Any):
        """
        Add metadata to deployment record.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        async with self._lock:
            self.deployment_record.metadata[key] = value
            logger.debug(f"Added metadata: {key} = {value}")
    
    async def add_health_check_result(self, result: Dict[str, Any]):
        """
        Add health check result to deployment record.
        
        Args:
            result: Health check result
        """
        async with self._lock:
            self.deployment_record.health_check_results.append(result)
            logger.debug(f"Added health check result: {result.get('endpoint', 'unknown')}")
    
    async def add_validation_result(self, result: Dict[str, Any]):
        """
        Add validation result to deployment record.
        
        Args:
            result: Validation result
        """
        async with self._lock:
            self.deployment_record.validation_results.append(result)
            logger.debug(f"Added validation result: {result.get('validator', 'unknown')}")
    
    def get_current_progress(self) -> Dict[str, Any]:
        """
        Get current progress information.
        
        Returns:
            Dictionary with current progress data
        """
        return {
            'deployment_id': self.deployment_record.deployment_id,
            'status': self.deployment_record.status.value,
            'current_phase': self.deployment_record.current_phase.value if self.deployment_record.current_phase else None,
            'overall_progress': self.deployment_record.overall_progress_percentage,
            'phases': {
                phase.value: {
                    'status': progress.status.value,
                    'progress': progress.progress_percentage,
                    'current_step': progress.current_step,
                    'completed_steps': progress.completed_steps,
                    'total_steps': progress.total_steps,
                    'duration': progress.duration_seconds,
                    'error': progress.error_message
                }
                for phase, progress in self.deployment_record.phases.items()
            },
            'start_time': self.deployment_record.start_time.isoformat(),
            'duration': self.deployment_record.get_duration_seconds(),
            'errors': self.deployment_record.errors,
            'warnings': self.deployment_record.warnings
        }
    
    async def _notify_progress_update(self, phase: DeploymentPhase):
        """
        Notify all callbacks about progress update.
        
        Args:
            phase: Phase that was updated
        """
        progress_data = self.get_current_progress()
        
        # Notify general progress callbacks
        for callback in self.progress_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(progress_data)
                else:
                    callback(progress_data)
            except Exception as e:
                logger.error(f"Error in progress callback {callback.__name__}: {str(e)}")
        
        # Notify phase-specific callbacks
        phase_callbacks = self.phase_callbacks.get(phase, [])
        for callback in phase_callbacks:
            try:
                phase_data = progress_data['phases'][phase.value]
                if asyncio.iscoroutinefunction(callback):
                    await callback(phase, phase_data)
                else:
                    callback(phase, phase_data)
            except Exception as e:
                logger.error(f"Error in phase callback {callback.__name__}: {str(e)}")
    
    async def _notify_status_change(self, old_status: DeploymentStatus, new_status: DeploymentStatus):
        """
        Notify about deployment status change.
        
        Args:
            old_status: Previous status
            new_status: New status
        """
        status_data = {
            'deployment_id': self.deployment_record.deployment_id,
            'old_status': old_status.value,
            'new_status': new_status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'progress': self.get_current_progress()
        }
        
        # Notify all progress callbacks about status change
        for callback in self.progress_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(status_data)
                else:
                    callback(status_data)
            except Exception as e:
                logger.error(f"Error in status change callback {callback.__name__}: {str(e)}")