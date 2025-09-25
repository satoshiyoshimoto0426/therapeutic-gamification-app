"""
Report generation system for deployment operations.

This module provides comprehensive report generation capabilities
with multiple output formats and customizable templates.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
try:
    from jinja2 import Environment, FileSystemLoader, Template
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    Environment = None
    FileSystemLoader = None
    Template = None

from .models import DeploymentRecord, DeploymentSummary, ReportConfig
from .history_manager import DeploymentHistoryManager

logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generates comprehensive deployment reports in various formats."""
    
    def __init__(self, history_manager: DeploymentHistoryManager):
        """
        Initialize report generator.
        
        Args:
            history_manager: History manager for data retrieval
        """
        self.history_manager = history_manager
        self.template_env = None
        self._setup_templates()
    
    def _setup_templates(self):
        """Setup Jinja2 template environment."""
        if not JINJA2_AVAILABLE:
            logger.warning("Jinja2 not available, template functionality disabled")
            return
            
        try:
            # Look for templates in the templates directory
            template_dir = Path(__file__).parent / "templates"
            if template_dir.exists():
                self.template_env = Environment(
                    loader=FileSystemLoader(str(template_dir)),
                    autoescape=True
                )
                logger.info(f"Template environment initialized with directory: {template_dir}")
            else:
                logger.warning(f"Template directory not found: {template_dir}")
        except Exception as e:
            logger.error(f"Failed to setup template environment: {str(e)}")
    
    def generate_deployment_report(
        self,
        deployment_id: str,
        config: Optional[ReportConfig] = None
    ) -> Optional[str]:
        """
        Generate comprehensive report for a single deployment.
        
        Args:
            deployment_id: Deployment ID to generate report for
            config: Report configuration
            
        Returns:
            Generated report content or None if failed
        """
        if not config:
            config = ReportConfig()
        
        try:
            # Get deployment record
            record = self.history_manager.get_deployment_record(deployment_id)
            if not record:
                logger.error(f"Deployment record not found: {deployment_id}")
                return None
            
            # Generate report based on format
            if config.format.lower() == "json":
                return self._generate_json_report(record, config)
            elif config.format.lower() == "html":
                return self._generate_html_report(record, config)
            elif config.format.lower() == "markdown":
                return self._generate_markdown_report(record, config)
            else:
                logger.error(f"Unsupported report format: {config.format}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate deployment report for {deployment_id}: {str(e)}")
            return None
    
    def generate_summary_report(
        self,
        environment: Optional[str] = None,
        days: int = 30,
        config: Optional[ReportConfig] = None
    ) -> Optional[str]:
        """
        Generate summary report for multiple deployments.
        
        Args:
            environment: Filter by environment
            days: Number of days to include
            config: Report configuration
            
        Returns:
            Generated report content or None if failed
        """
        if not config:
            config = ReportConfig()
        
        try:
            # Get deployment history and statistics
            history = self.history_manager.get_deployment_history(
                environment=environment,
                limit=1000
            )
            statistics = self.history_manager.get_deployment_statistics(
                environment=environment,
                days=days
            )
            
            # Generate report based on format
            if config.format.lower() == "json":
                return self._generate_json_summary_report(history, statistics, config)
            elif config.format.lower() == "html":
                return self._generate_html_summary_report(history, statistics, config)
            elif config.format.lower() == "markdown":
                return self._generate_markdown_summary_report(history, statistics, config)
            else:
                logger.error(f"Unsupported report format: {config.format}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to generate summary report: {str(e)}")
            return None
    
    def _generate_json_report(self, record: DeploymentRecord, config: ReportConfig) -> str:
        """Generate JSON format report."""
        report_data = {
            'deployment_id': record.deployment_id,
            'environment': record.environment,
            'status': record.status.value,
            'start_time': record.start_time.isoformat(),
            'end_time': record.end_time.isoformat() if record.end_time else None,
            'duration_seconds': record.get_duration_seconds(),
            'commit_sha': record.commit_sha,
            'image_tag': record.image_tag,
            'revision_name': record.revision_name,
            'success': record.is_successful(),
            'overall_progress': record.overall_progress_percentage,
            'errors': record.errors,
            'warnings': record.warnings
        }
        
        if config.include_metrics:
            report_data['metrics'] = {
                'total_duration_seconds': record.metrics.total_duration_seconds,
                'validation_duration_seconds': record.metrics.validation_duration_seconds,
                'build_duration_seconds': record.metrics.build_duration_seconds,
                'deployment_duration_seconds': record.metrics.deployment_duration_seconds,
                'health_check_duration_seconds': record.metrics.health_check_duration_seconds,
                'cpu_usage_percent': record.metrics.cpu_usage_percent,
                'memory_usage_mb': record.metrics.memory_usage_mb,
                'network_io_mb': record.metrics.network_io_mb,
                'success_rate': record.metrics.success_rate,
                'error_count': record.metrics.error_count,
                'warning_count': record.metrics.warning_count
            }
        
        if config.include_health_checks:
            report_data['health_checks'] = record.health_check_results
        
        if config.include_validation_results:
            report_data['validation_results'] = record.validation_results
        
        if config.include_notifications:
            report_data['notifications'] = record.notifications_sent
        
        # Include phase information
        report_data['phases'] = {}
        for phase, progress in record.phases.items():
            report_data['phases'][phase.value] = {
                'status': progress.status.value,
                'start_time': progress.start_time.isoformat() if progress.start_time else None,
                'end_time': progress.end_time.isoformat() if progress.end_time else None,
                'duration_seconds': progress.duration_seconds,
                'progress_percentage': progress.progress_percentage,
                'current_step': progress.current_step,
                'total_steps': progress.total_steps,
                'completed_steps': progress.completed_steps,
                'error_message': progress.error_message,
                'warnings': progress.warnings
            }
        
        # Include configuration if requested
        report_data['deployment_config'] = record.deployment_config
        report_data['environment_config'] = record.environment_config
        report_data['metadata'] = record.metadata
        
        # Add rollback information if applicable
        if record.rollback_revision:
            report_data['rollback'] = {
                'revision': record.rollback_revision,
                'reason': record.rollback_reason,
                'time': record.rollback_time.isoformat() if record.rollback_time else None
            }
        
        # Add report metadata
        report_data['report_metadata'] = {
            'generated_at': datetime.utcnow().isoformat(),
            'format': 'json',
            'config': {
                'include_metrics': config.include_metrics,
                'include_health_checks': config.include_health_checks,
                'include_validation_results': config.include_validation_results,
                'include_notifications': config.include_notifications
            }
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def _generate_html_report(self, record: DeploymentRecord, config: ReportConfig) -> str:
        """Generate HTML format report."""
        if not self.template_env:
            return self._generate_simple_html_report(record, config)
        
        try:
            template = self.template_env.get_template('deployment_report.html')
            return template.render(
                record=record,
                config=config,
                generated_at=datetime.utcnow(),
                duration_formatted=self._format_duration(record.get_duration_seconds())
            )
        except Exception as e:
            logger.warning(f"Failed to use template, falling back to simple HTML: {str(e)}")
            return self._generate_simple_html_report(record, config)
    
    def _generate_simple_html_report(self, record: DeploymentRecord, config: ReportConfig) -> str:
        """Generate simple HTML report without templates."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Deployment Report - {record.deployment_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
                .warning {{ color: orange; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .progress-bar {{ 
                    width: 100%; 
                    background-color: #f0f0f0; 
                    border-radius: 5px; 
                    overflow: hidden; 
                }}
                .progress-fill {{ 
                    height: 20px; 
                    background-color: #4CAF50; 
                    text-align: center; 
                    line-height: 20px; 
                    color: white; 
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Deployment Report</h1>
                <p><strong>Deployment ID:</strong> {record.deployment_id}</p>
                <p><strong>Environment:</strong> {record.environment}</p>
                <p><strong>Status:</strong> <span class="{'success' if record.is_successful() else 'error'}">{record.status.value}</span></p>
                <p><strong>Duration:</strong> {self._format_duration(record.get_duration_seconds())}</p>
            </div>
            
            <div class="section">
                <h2>Overview</h2>
                <table>
                    <tr><th>Commit SHA</th><td>{record.commit_sha}</td></tr>
                    <tr><th>Image Tag</th><td>{record.image_tag}</td></tr>
                    <tr><th>Revision Name</th><td>{record.revision_name}</td></tr>
                    <tr><th>Start Time</th><td>{record.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}</td></tr>
                    <tr><th>End Time</th><td>{record.end_time.strftime('%Y-%m-%d %H:%M:%S UTC') if record.end_time else 'N/A'}</td></tr>
                    <tr><th>Overall Progress</th><td>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: {record.overall_progress_percentage}%">
                                {record.overall_progress_percentage:.1f}%
                            </div>
                        </div>
                    </td></tr>
                </table>
            </div>
        """
        
        # Add phases section
        if record.phases:
            html += """
            <div class="section">
                <h2>Deployment Phases</h2>
                <table>
                    <tr>
                        <th>Phase</th>
                        <th>Status</th>
                        <th>Progress</th>
                        <th>Duration</th>
                        <th>Current Step</th>
                    </tr>
            """
            
            for phase, progress in record.phases.items():
                status_class = "success" if progress.status.value == "completed" else "error" if progress.status.value == "failed" else ""
                duration_str = self._format_duration(progress.duration_seconds) if progress.duration_seconds else "N/A"
                
                html += f"""
                    <tr>
                        <td>{phase.value}</td>
                        <td><span class="{status_class}">{progress.status.value}</span></td>
                        <td>{progress.progress_percentage:.1f}%</td>
                        <td>{duration_str}</td>
                        <td>{progress.current_step}</td>
                    </tr>
                """
            
            html += "</table></div>"
        
        # Add errors and warnings
        if record.errors or record.warnings:
            html += '<div class="section"><h2>Issues</h2>'
            
            if record.errors:
                html += '<h3 class="error">Errors</h3><ul>'
                for error in record.errors:
                    html += f'<li class="error">{error}</li>'
                html += '</ul>'
            
            if record.warnings:
                html += '<h3 class="warning">Warnings</h3><ul>'
                for warning in record.warnings:
                    html += f'<li class="warning">{warning}</li>'
                html += '</ul>'
            
            html += '</div>'
        
        # Add metrics if requested
        if config.include_metrics:
            html += f"""
            <div class="section">
                <h2>Performance Metrics</h2>
                <table>
                    <tr><th>Total Duration</th><td>{self._format_duration(record.metrics.total_duration_seconds)}</td></tr>
                    <tr><th>Validation Duration</th><td>{self._format_duration(record.metrics.validation_duration_seconds)}</td></tr>
                    <tr><th>Build Duration</th><td>{self._format_duration(record.metrics.build_duration_seconds)}</td></tr>
                    <tr><th>Deployment Duration</th><td>{self._format_duration(record.metrics.deployment_duration_seconds)}</td></tr>
                    <tr><th>Health Check Duration</th><td>{self._format_duration(record.metrics.health_check_duration_seconds)}</td></tr>
                    <tr><th>CPU Usage</th><td>{record.metrics.cpu_usage_percent:.1f}%</td></tr>
                    <tr><th>Memory Usage</th><td>{record.metrics.memory_usage_mb:.1f} MB</td></tr>
                    <tr><th>Network I/O</th><td>{record.metrics.network_io_mb:.1f} MB</td></tr>
                    <tr><th>Success Rate</th><td>{record.metrics.success_rate:.1f}%</td></tr>
                </table>
            </div>
            """
        
        html += f"""
            <div class="section">
                <p><em>Report generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</em></p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_report(self, record: DeploymentRecord, config: ReportConfig) -> str:
        """Generate Markdown format report."""
        md = f"""# Deployment Report

## Overview

- **Deployment ID:** {record.deployment_id}
- **Environment:** {record.environment}
- **Status:** {record.status.value} {'✅' if record.is_successful() else '❌'}
- **Duration:** {self._format_duration(record.get_duration_seconds())}
- **Commit SHA:** {record.commit_sha}
- **Image Tag:** {record.image_tag}
- **Revision Name:** {record.revision_name}
- **Start Time:** {record.start_time.strftime('%Y-%m-%d %H:%M:%S UTC')}
- **End Time:** {record.end_time.strftime('%Y-%m-%d %H:%M:%S UTC') if record.end_time else 'N/A'}
- **Overall Progress:** {record.overall_progress_percentage:.1f}%

"""
        
        # Add phases section
        if record.phases:
            md += "## Deployment Phases\n\n"
            md += "| Phase | Status | Progress | Duration | Current Step |\n"
            md += "|-------|--------|----------|----------|-------------|\n"
            
            for phase, progress in record.phases.items():
                status_emoji = "✅" if progress.status.value == "completed" else "❌" if progress.status.value == "failed" else "⏳"
                duration_str = self._format_duration(progress.duration_seconds) if progress.duration_seconds else "N/A"
                
                md += f"| {phase.value} | {progress.status.value} {status_emoji} | {progress.progress_percentage:.1f}% | {duration_str} | {progress.current_step} |\n"
            
            md += "\n"
        
        # Add errors and warnings
        if record.errors or record.warnings:
            md += "## Issues\n\n"
            
            if record.errors:
                md += "### ❌ Errors\n\n"
                for error in record.errors:
                    md += f"- {error}\n"
                md += "\n"
            
            if record.warnings:
                md += "### ⚠️ Warnings\n\n"
                for warning in record.warnings:
                    md += f"- {warning}\n"
                md += "\n"
        
        # Add metrics if requested
        if config.include_metrics:
            md += "## Performance Metrics\n\n"
            md += "| Metric | Value |\n"
            md += "|--------|-------|\n"
            md += f"| Total Duration | {self._format_duration(record.metrics.total_duration_seconds)} |\n"
            md += f"| Validation Duration | {self._format_duration(record.metrics.validation_duration_seconds)} |\n"
            md += f"| Build Duration | {self._format_duration(record.metrics.build_duration_seconds)} |\n"
            md += f"| Deployment Duration | {self._format_duration(record.metrics.deployment_duration_seconds)} |\n"
            md += f"| Health Check Duration | {self._format_duration(record.metrics.health_check_duration_seconds)} |\n"
            md += f"| CPU Usage | {record.metrics.cpu_usage_percent:.1f}% |\n"
            md += f"| Memory Usage | {record.metrics.memory_usage_mb:.1f} MB |\n"
            md += f"| Network I/O | {record.metrics.network_io_mb:.1f} MB |\n"
            md += f"| Success Rate | {record.metrics.success_rate:.1f}% |\n"
            md += "\n"
        
        # Add rollback information if applicable
        if record.rollback_revision:
            md += "## Rollback Information\n\n"
            md += f"- **Rollback Revision:** {record.rollback_revision}\n"
            md += f"- **Rollback Reason:** {record.rollback_reason}\n"
            md += f"- **Rollback Time:** {record.rollback_time.strftime('%Y-%m-%d %H:%M:%S UTC') if record.rollback_time else 'N/A'}\n\n"
        
        md += f"---\n*Report generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*\n"
        
        return md
    
    def _generate_json_summary_report(
        self,
        history: List[DeploymentSummary],
        statistics: Dict[str, Any],
        config: ReportConfig
    ) -> str:
        """Generate JSON format summary report."""
        report_data = {
            'summary': statistics,
            'deployments': [
                {
                    'deployment_id': summary.deployment_id,
                    'environment': summary.environment,
                    'status': summary.status.value,
                    'start_time': summary.start_time.isoformat(),
                    'end_time': summary.end_time.isoformat() if summary.end_time else None,
                    'duration_seconds': summary.duration_seconds,
                    'commit_sha': summary.commit_sha,
                    'image_tag': summary.image_tag,
                    'success': summary.success,
                    'error_count': summary.error_count,
                    'warning_count': summary.warning_count
                }
                for summary in history
            ],
            'report_metadata': {
                'generated_at': datetime.utcnow().isoformat(),
                'format': 'json',
                'total_deployments': len(history)
            }
        }
        
        return json.dumps(report_data, indent=2, ensure_ascii=False)
    
    def _generate_html_summary_report(
        self,
        history: List[DeploymentSummary],
        statistics: Dict[str, Any],
        config: ReportConfig
    ) -> str:
        """Generate HTML format summary report."""
        # Implementation similar to single deployment HTML report
        # but with summary statistics and deployment list
        return self._generate_simple_html_summary_report(history, statistics, config)
    
    def _generate_simple_html_summary_report(
        self,
        history: List[DeploymentSummary],
        statistics: Dict[str, Any],
        config: ReportConfig
    ) -> str:
        """Generate simple HTML summary report."""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Deployment Summary Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .stats {{ display: flex; justify-content: space-around; }}
                .stat-box {{ text-align: center; padding: 20px; background-color: #f9f9f9; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Deployment Summary Report</h1>
                <p><strong>Period:</strong> {statistics.get('period_days', 30)} days</p>
                <p><strong>Generated:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
            </div>
            
            <div class="section">
                <h2>Statistics</h2>
                <div class="stats">
                    <div class="stat-box">
                        <h3>{statistics.get('total_deployments', 0)}</h3>
                        <p>Total Deployments</p>
                    </div>
                    <div class="stat-box">
                        <h3 class="success">{statistics.get('successful_deployments', 0)}</h3>
                        <p>Successful</p>
                    </div>
                    <div class="stat-box">
                        <h3 class="error">{statistics.get('failed_deployments', 0)}</h3>
                        <p>Failed</p>
                    </div>
                    <div class="stat-box">
                        <h3>{statistics.get('success_rate', 0):.1f}%</h3>
                        <p>Success Rate</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Recent Deployments</h2>
                <table>
                    <tr>
                        <th>Deployment ID</th>
                        <th>Environment</th>
                        <th>Status</th>
                        <th>Start Time</th>
                        <th>Duration</th>
                        <th>Commit</th>
                    </tr>
        """
        
        for summary in history[:20]:  # Show only recent 20
            status_class = "success" if summary.success else "error"
            duration_str = self._format_duration(summary.duration_seconds) if summary.duration_seconds else "N/A"
            
            html += f"""
                    <tr>
                        <td>{summary.deployment_id[:8]}...</td>
                        <td>{summary.environment}</td>
                        <td><span class="{status_class}">{summary.status.value}</span></td>
                        <td>{summary.start_time.strftime('%Y-%m-%d %H:%M')}</td>
                        <td>{duration_str}</td>
                        <td>{summary.commit_sha[:8]}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_markdown_summary_report(
        self,
        history: List[DeploymentSummary],
        statistics: Dict[str, Any],
        config: ReportConfig
    ) -> str:
        """Generate Markdown format summary report."""
        md = f"""# Deployment Summary Report

## Statistics ({statistics.get('period_days', 30)} days)

- **Total Deployments:** {statistics.get('total_deployments', 0)}
- **Successful Deployments:** {statistics.get('successful_deployments', 0)} ✅
- **Failed Deployments:** {statistics.get('failed_deployments', 0)} ❌
- **Success Rate:** {statistics.get('success_rate', 0):.1f}%
- **Average Duration:** {self._format_duration(statistics.get('avg_duration_seconds', 0))}
- **Total Errors:** {statistics.get('total_errors', 0)}
- **Total Warnings:** {statistics.get('total_warnings', 0)}

## Recent Deployments

| Deployment ID | Environment | Status | Start Time | Duration | Commit |
|---------------|-------------|--------|------------|----------|--------|
"""
        
        for summary in history[:20]:  # Show only recent 20
            status_emoji = "✅" if summary.success else "❌"
            duration_str = self._format_duration(summary.duration_seconds) if summary.duration_seconds else "N/A"
            
            md += f"| {summary.deployment_id[:8]}... | {summary.environment} | {summary.status.value} {status_emoji} | {summary.start_time.strftime('%Y-%m-%d %H:%M')} | {duration_str} | {summary.commit_sha[:8]} |\n"
        
        md += f"\n---\n*Report generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*\n"
        
        return md
    
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
    
    def save_report(self, content: str, file_path: str) -> bool:
        """
        Save report content to file.
        
        Args:
            content: Report content to save
            file_path: Path to save the report
            
        Returns:
            True if saved successfully
        """
        try:
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Report saved to: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save report to {file_path}: {str(e)}")
            return False