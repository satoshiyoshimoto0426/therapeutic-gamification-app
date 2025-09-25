"""
Main deployment reporter that integrates progress tracking, history management,
and report generation with notification system.

This module provides the main interface for deployment status reporting
functionality.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

try:
    from ..notification.notification_manager import NotificationManager
    from ..notification.base import NotificationSeverity
except ImportError:
    # For testing purposes, create mock classes
    class NotificationManager:
        async def send_notification(self, **kwargs):
            pass
        async def test_channels(self):
            return []
    
    class NotificationSeverity:
        INFO = "info"
        ERROR = "error"
from .models import (
    DeploymentRecord, DeploymentPhase, DeploymentStatus, 
    ReportConfig, DeploymentSummary
)
from .progress_tracker import ProgressTracker
from .history_manager import DeploymentHistoryManager
from .report_generator import ReportGenerator

logger = logging.getLogger(__name__)


class DeploymentReporter:
    """
    Main deployment reporter that coordinates all reporting functionality.
    
    This class integrates progress tracking, history management, report generation,
    and notifications to provide comprehensive deployment status reporting.
    """
    
    def __init__(
        self,
        notification_manager: NotificationManager,
        history_db_path: str = "deployment_history.db",
        reports_dir: str = "deployment_reports"
    ):
        """
        Initialize deployment reporter.
        
        Args:
            notification_manager: Notification manager for sending updates
            history_db_path: Path to deployment history database
            reports_dir: Directory for storing generated reports
        """
        self.notification_manager = notification_manager
        self.history_manager = DeploymentHistoryManager(history_db_path)
        self.report_generator = ReportGenerator(self.history_manager)
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Active deployment trackers
        self.active_deployments: Dict[str, ProgressTracker] = {}
        
        # Configuration
        self.auto_save_enabled = True
        self.auto_report_enabled = True
        self.notification_enabled = True
        
        logger.info("Deployment reporter initialized")
    
    def create_deployment_tracker(
        self,
        deployment_id: str,
        environment: str,
        commit_sha: str,
        image_tag: str,
        revision_name: str = "",
        deployment_config: Optional[Dict[str, Any]] = None,
        environment_config: Optional[Dict[str, Any]] = None
    ) -> ProgressTracker:
        """
        Create a new deployment tracker.
        
        Args:
            deployment_id: Unique deployment identifier
            environment: Target environment
            commit_sha: Git commit SHA
            image_tag: Docker image tag
            revision_name: Cloud Run revision name
            deployment_config: Deployment configuration
            environment_config: Environment configuration
            
        Returns:
            Progress tracker for the deployment
        """
        # Create deployment record
        record = DeploymentRecord(
            deployment_id=deployment_id,
            environment=environment,
            commit_sha=commit_sha,
            image_tag=image_tag,
            revision_name=revision_name,
            deployment_config=deployment_config or {},
            environment_config=environment_config or {}
        )
        
        # Create progress tracker
        tracker = ProgressTracker(record)
        
        # Add progress callback for notifications and auto-save
        tracker.add_progress_callback(self._on_progress_update)
        
        # Store active tracker
        self.active_deployments[deployment_id] = tracker
        
        logger.info(f"Created deployment tracker: {deployment_id}")
        
        # Send initial notification
        if self.notification_enabled:
            asyncio.create_task(self._send_deployment_started_notification(record))
        
        return tracker
    
    def get_deployment_tracker(self, deployment_id: str) -> Optional[ProgressTracker]:
        """
        Get active deployment tracker.
        
        Args:
            deployment_id: Deployment ID
            
        Returns:
            Progress tracker if found
        """
        return self.active_deployments.get(deployment_id)
    
    async def complete_deployment(
        self,
        deployment_id: str,
        success: bool,
        final_status: Optional[DeploymentStatus] = None
    ) -> bool:
        """
        Complete a deployment and generate final report.
        
        Args:
            deployment_id: Deployment ID to complete
            success: Whether deployment was successful
            final_status: Final deployment status
            
        Returns:
            True if completed successfully
        """
        tracker = self.active_deployments.get(deployment_id)
        if not tracker:
            logger.error(f"Deployment tracker not found: {deployment_id}")
            return False
        
        try:
            # Update final status
            if final_status:
                await tracker.update_deployment_status(final_status)
            elif success:
                await tracker.update_deployment_status(DeploymentStatus.COMPLETED)
            else:
                await tracker.update_deployment_status(DeploymentStatus.FAILED)
            
            # Save to history
            if self.auto_save_enabled:
                saved = self.history_manager.save_deployment_record(tracker.deployment_record)
                if saved:
                    logger.info(f"Saved deployment record to history: {deployment_id}")
                else:
                    logger.error(f"Failed to save deployment record: {deployment_id}")
            
            # Generate final report
            if self.auto_report_enabled:
                await self._generate_completion_report(tracker.deployment_record)
            
            # Send completion notification
            if self.notification_enabled:
                await self._send_deployment_completed_notification(tracker.deployment_record)
            
            # Remove from active deployments
            del self.active_deployments[deployment_id]
            
            logger.info(f"Completed deployment: {deployment_id} (success: {success})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to complete deployment {deployment_id}: {str(e)}")
            return False
    
    async def generate_deployment_report(
        self,
        deployment_id: str,
        format: str = "json",
        save_to_file: bool = True
    ) -> Optional[str]:
        """
        Generate report for a specific deployment.
        
        Args:
            deployment_id: Deployment ID
            format: Report format (json, html, markdown)
            save_to_file: Whether to save report to file
            
        Returns:
            Generated report content
        """
        try:
            config = ReportConfig(format=format)
            report_content = self.report_generator.generate_deployment_report(
                deployment_id, config
            )
            
            if report_content and save_to_file:
                file_name = f"deployment_report_{deployment_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
                file_path = self.reports_dir / file_name
                
                if self.report_generator.save_report(report_content, str(file_path)):
                    logger.info(f"Deployment report saved: {file_path}")
                else:
                    logger.error(f"Failed to save deployment report: {file_path}")
            
            return report_content
            
        except Exception as e:
            logger.error(f"Failed to generate deployment report for {deployment_id}: {str(e)}")
            return None
    
    async def generate_summary_report(
        self,
        environment: Optional[str] = None,
        days: int = 30,
        format: str = "json",
        save_to_file: bool = True
    ) -> Optional[str]:
        """
        Generate summary report for multiple deployments.
        
        Args:
            environment: Filter by environment
            days: Number of days to include
            format: Report format (json, html, markdown)
            save_to_file: Whether to save report to file
            
        Returns:
            Generated report content
        """
        try:
            config = ReportConfig(format=format)
            report_content = self.report_generator.generate_summary_report(
                environment, days, config
            )
            
            if report_content and save_to_file:
                env_suffix = f"_{environment}" if environment else ""
                file_name = f"summary_report{env_suffix}_{days}days_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
                file_path = self.reports_dir / file_name
                
                if self.report_generator.save_report(report_content, str(file_path)):
                    logger.info(f"Summary report saved: {file_path}")
                else:
                    logger.error(f"Failed to save summary report: {file_path}")
            
            return report_content
            
        except Exception as e:
            logger.error(f"Failed to generate summary report: {str(e)}")
            return None
    
    def get_deployment_history(
        self,
        environment: Optional[str] = None,
        status: Optional[DeploymentStatus] = None,
        days: int = 30,
        limit: int = 100
    ) -> List[DeploymentSummary]:
        """
        Get deployment history with filtering.
        
        Args:
            environment: Filter by environment
            status: Filter by status
            days: Number of days to include
            limit: Maximum number of records
            
        Returns:
            List of deployment summaries
        """
        start_date = datetime.utcnow() - timedelta(days=days) if days > 0 else None
        
        return self.history_manager.get_deployment_history(
            environment=environment,
            status=status,
            start_date=start_date,
            limit=limit
        )
    
    def get_deployment_statistics(
        self,
        environment: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get deployment statistics.
        
        Args:
            environment: Filter by environment
            days: Number of days to include
            
        Returns:
            Dictionary with deployment statistics
        """
        return self.history_manager.get_deployment_statistics(environment, days)
    
    def get_active_deployments(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about currently active deployments.
        
        Returns:
            Dictionary with active deployment information
        """
        active_info = {}
        for deployment_id, tracker in self.active_deployments.items():
            active_info[deployment_id] = tracker.get_current_progress()
        
        return active_info
    
    async def cleanup_old_records(self, days_to_keep: int = 90) -> int:
        """
        Clean up old deployment records.
        
        Args:
            days_to_keep: Number of days of records to keep
            
        Returns:
            Number of records deleted
        """
        deleted_count = self.history_manager.cleanup_old_records(days_to_keep)
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old deployment records")
            
            # Send notification about cleanup
            if self.notification_enabled:
                await self.notification_manager.send_notification(
                    title="Deployment History Cleanup",
                    content=f"Cleaned up {deleted_count} deployment records older than {days_to_keep} days",
                    severity=NotificationSeverity.INFO,
                    metadata={'cleanup_count': deleted_count, 'days_kept': days_to_keep}
                )
        
        return deleted_count
    
    async def _on_progress_update(self, progress_data: Dict[str, Any]):
        """
        Handle progress updates from deployment trackers.
        
        Args:
            progress_data: Progress update data
        """
        deployment_id = progress_data.get('deployment_id')
        if not deployment_id:
            return
        
        try:
            # Auto-save if enabled
            if self.auto_save_enabled:
                tracker = self.active_deployments.get(deployment_id)
                if tracker:
                    self.history_manager.save_deployment_record(tracker.deployment_record)
            
            # Send progress notification if enabled
            if self.notification_enabled:
                await self._send_progress_notification(progress_data)
                
        except Exception as e:
            logger.error(f"Error handling progress update for {deployment_id}: {str(e)}")
    
    async def _send_deployment_started_notification(self, record: DeploymentRecord):
        """Send notification when deployment starts."""
        try:
            await self.notification_manager.send_notification(
                title=f"Deployment Started - {record.environment}",
                content=f"Deployment {record.deployment_id[:8]} started for {record.environment} environment\n"
                       f"Commit: {record.commit_sha[:8]}\n"
                       f"Image: {record.image_tag}",
                severity=NotificationSeverity.INFO,
                deployment_id=record.deployment_id,
                environment=record.environment,
                metadata={
                    'event_type': 'deployment_started',
                    'commit_sha': record.commit_sha,
                    'image_tag': record.image_tag
                }
            )
        except Exception as e:
            logger.error(f"Failed to send deployment started notification: {str(e)}")
    
    async def _send_progress_notification(self, progress_data: Dict[str, Any]):
        """Send progress notification for significant updates."""
        try:
            deployment_id = progress_data['deployment_id']
            status = progress_data['status']
            current_phase = progress_data.get('current_phase')
            overall_progress = progress_data.get('overall_progress', 0)
            
            # Only send notifications for significant progress milestones
            if current_phase and overall_progress % 25 == 0:  # Every 25% progress
                await self.notification_manager.send_notification(
                    title=f"Deployment Progress - {deployment_id[:8]}",
                    content=f"Phase: {current_phase}\n"
                           f"Progress: {overall_progress:.1f}%\n"
                           f"Status: {status}",
                    severity=NotificationSeverity.INFO,
                    deployment_id=deployment_id,
                    metadata={
                        'event_type': 'deployment_progress',
                        'phase': current_phase,
                        'progress': overall_progress
                    }
                )
        except Exception as e:
            logger.error(f"Failed to send progress notification: {str(e)}")
    
    async def _send_deployment_completed_notification(self, record: DeploymentRecord):
        """Send notification when deployment completes."""
        try:
            success = record.is_successful()
            severity = NotificationSeverity.INFO if success else NotificationSeverity.ERROR
            
            duration_str = self._format_duration(record.get_duration_seconds())
            
            content = f"Deployment {record.deployment_id[:8]} {'completed successfully' if success else 'failed'}\n"
            content += f"Environment: {record.environment}\n"
            content += f"Duration: {duration_str}\n"
            content += f"Commit: {record.commit_sha[:8]}\n"
            
            if record.errors:
                content += f"Errors: {len(record.errors)}\n"
            if record.warnings:
                content += f"Warnings: {len(record.warnings)}\n"
            
            await self.notification_manager.send_notification(
                title=f"Deployment {'Completed' if success else 'Failed'} - {record.environment}",
                content=content,
                severity=severity,
                deployment_id=record.deployment_id,
                environment=record.environment,
                metadata={
                    'event_type': 'deployment_completed',
                    'success': success,
                    'duration_seconds': record.get_duration_seconds(),
                    'error_count': len(record.errors),
                    'warning_count': len(record.warnings)
                }
            )
        except Exception as e:
            logger.error(f"Failed to send deployment completed notification: {str(e)}")
    
    async def _generate_completion_report(self, record: DeploymentRecord):
        """Generate completion report for deployment."""
        try:
            # Generate reports in multiple formats
            formats = ['json', 'html', 'markdown']
            
            for format in formats:
                config = ReportConfig(format=format)
                report_content = self.report_generator.generate_deployment_report(
                    record.deployment_id, config
                )
                
                if report_content:
                    file_name = f"deployment_report_{record.deployment_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{format}"
                    file_path = self.reports_dir / file_name
                    
                    self.report_generator.save_report(report_content, str(file_path))
                    
                    # Add report path to deployment record
                    if 'reports' not in record.metadata:
                        record.metadata['reports'] = []
                    record.metadata['reports'].append(str(file_path))
            
            logger.info(f"Generated completion reports for deployment: {record.deployment_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate completion report for {record.deployment_id}: {str(e)}")
    
    def _format_duration(self, seconds: Optional[float]) -> str:
        """Format duration in human-readable format."""
        if seconds is None or seconds <= 0:
            return "N/A"
        
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            remaining_seconds = int(seconds % 60)
            return f"{minutes}m {remaining_seconds}s"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            return f"{hours}h {minutes}m"
    
    def configure_auto_save(self, enabled: bool):
        """Configure automatic saving of deployment records."""
        self.auto_save_enabled = enabled
        logger.info(f"Auto-save {'enabled' if enabled else 'disabled'}")
    
    def configure_auto_report(self, enabled: bool):
        """Configure automatic report generation."""
        self.auto_report_enabled = enabled
        logger.info(f"Auto-report {'enabled' if enabled else 'disabled'}")
    
    def configure_notifications(self, enabled: bool):
        """Configure deployment notifications."""
        self.notification_enabled = enabled
        logger.info(f"Deployment notifications {'enabled' if enabled else 'disabled'}")
    
    async def test_reporting_system(self) -> Dict[str, Any]:
        """
        Test the reporting system functionality.
        
        Returns:
            Test results
        """
        test_results = {
            'timestamp': datetime.utcnow().isoformat(),
            'tests': {}
        }
        
        try:
            # Test notification system
            notification_results = await self.notification_manager.test_channels()
            test_results['tests']['notifications'] = {
                'success': all(r.success for r in notification_results),
                'results': [{'channel': r.channel_name, 'success': r.success} for r in notification_results]
            }
            
            # Test history manager
            test_deployment = DeploymentRecord(
                deployment_id="test-deployment",
                environment="test",
                commit_sha="test-commit",
                image_tag="test-image"
            )
            
            history_save_success = self.history_manager.save_deployment_record(test_deployment)
            history_retrieve_success = self.history_manager.get_deployment_record("test-deployment") is not None
            
            test_results['tests']['history'] = {
                'save': history_save_success,
                'retrieve': history_retrieve_success,
                'success': history_save_success and history_retrieve_success
            }
            
            # Test report generation
            report_content = self.report_generator.generate_deployment_report("test-deployment")
            test_results['tests']['report_generation'] = {
                'success': report_content is not None,
                'content_length': len(report_content) if report_content else 0
            }
            
            # Overall success
            test_results['overall_success'] = all(
                test.get('success', False) for test in test_results['tests'].values()
            )
            
            logger.info(f"Reporting system test completed: {test_results['overall_success']}")
            
        except Exception as e:
            logger.error(f"Reporting system test failed: {str(e)}")
            test_results['error'] = str(e)
            test_results['overall_success'] = False
        
        return test_results