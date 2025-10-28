"""
Tests for report generator functionality.
"""

import json
import pytest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from models import (
    DeploymentRecord, DeploymentStatus, DeploymentPhase, ProgressStatus,
    DeploymentMetrics, PhaseProgress, ReportConfig
)
from report_generator import ReportGenerator
from history_manager import DeploymentHistoryManager


class TestReportGenerator:
    """Test cases for ReportGenerator class."""
    
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
    def history_manager(self, temp_db_path):
        """Create test history manager."""
        return DeploymentHistoryManager(temp_db_path)
    
    @pytest.fixture
    def report_generator(self, history_manager):
        """Create test report generator."""
        return ReportGenerator(history_manager)
    
    @pytest.fixture
    def sample_deployment_record(self):
        """Create comprehensive sample deployment record."""
        record = DeploymentRecord(
            deployment_id="test-deployment-123",
            environment="production",
            commit_sha="abc123def456",
            image_tag="myapp:v1.2.3",
            revision_name="myapp-v123",
            status=DeploymentStatus.COMPLETED,
            start_time=datetime.utcnow() - timedelta(minutes=10),
            end_time=datetime.utcnow()
        )
        
        # Add comprehensive metrics
        record.metrics = DeploymentMetrics(
            total_duration_seconds=600.0,
            validation_duration_seconds=120.0,
            build_duration_seconds=180.0,
            deployment_duration_seconds=240.0,
            health_check_duration_seconds=60.0,
            cpu_usage_percent=75.5,
            memory_usage_mb=1024.0,
            network_io_mb=256.0,
            success_rate=98.5,
            error_count=0,
            warning_count=2
        )
        
        # Add phase information
        validation_phase = PhaseProgress(
            phase=DeploymentPhase.VALIDATION,
            status=ProgressStatus.COMPLETED,
            start_time=record.start_time,
            end_time=record.start_time + timedelta(minutes=2),
            duration_seconds=120.0,
            progress_percentage=100.0,
            current_step="Validation completed",
            total_steps=3,
            completed_steps=3,
            warnings=["Minor validation warning"]
        )
        
        build_phase = PhaseProgress(
            phase=DeploymentPhase.BUILD,
            status=ProgressStatus.COMPLETED,
            start_time=record.start_time + timedelta(minutes=2),
            end_time=record.start_time + timedelta(minutes=5),
            duration_seconds=180.0,
            progress_percentage=100.0,
            current_step="Build completed",
            total_steps=5,
            completed_steps=5
        )
        
        deployment_phase = PhaseProgress(
            phase=DeploymentPhase.DEPLOYMENT,
            status=ProgressStatus.COMPLETED,
            start_time=record.start_time + timedelta(minutes=5),
            end_time=record.start_time + timedelta(minutes=9),
            duration_seconds=240.0,
            progress_percentage=100.0,
            current_step="Deployment completed",
            total_steps=4,
            completed_steps=4
        )
        
        record.phases = {
            DeploymentPhase.VALIDATION: validation_phase,
            DeploymentPhase.BUILD: build_phase,
            DeploymentPhase.DEPLOYMENT: deployment_phase
        }
        
        # Add other data
        record.warnings = ["Warning 1", "Warning 2"]
        record.health_check_results = [
            {
                "endpoint": "/health",
                "status_code": 200,
                "response_time_ms": 150,
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "endpoint": "/api/health",
                "status_code": 200,
                "response_time_ms": 200,
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
        
        record.validation_results = [
            {
                "validator": "code_quality",
                "success": True,
                "score": 95.5,
                "details": "All checks passed"
            },
            {
                "validator": "security_scan",
                "success": True,
                "score": 98.0,
                "details": "No vulnerabilities found"
            }
        ]
        
        record.deployment_config = {
            "memory": "2Gi",
            "cpu": "1",
            "min_instances": 1,
            "max_instances": 10
        }
        
        record.environment_config = {
            "region": "us-central1",
            "project_id": "test-project",
            "service_name": "test-service"
        }
        
        record.metadata = {
            "triggered_by": "user@example.com",
            "build_number": "123",
            "branch": "main"
        }
        
        record.notifications_sent = [
            {
                "channel": "slack",
                "timestamp": datetime.utcnow().isoformat(),
                "message": "Deployment started"
            }
        ]
        
        record.calculate_overall_progress()
        
        return record
    
    @pytest.fixture
    def failed_deployment_record(self):
        """Create sample failed deployment record."""
        record = DeploymentRecord(
            deployment_id="failed-deployment-456",
            environment="staging",
            commit_sha="def456ghi789",
            image_tag="myapp:v1.2.4",
            revision_name="myapp-v124",
            status=DeploymentStatus.FAILED,
            start_time=datetime.utcnow() - timedelta(minutes=5),
            end_time=datetime.utcnow()
        )
        
        record.errors = [
            "Deployment failed: Service unavailable",
            "Health check timeout"
        ]
        record.warnings = ["Resource limit warning"]
        
        # Add failed phase
        failed_phase = PhaseProgress(
            phase=DeploymentPhase.DEPLOYMENT,
            status=ProgressStatus.FAILED,
            start_time=record.start_time,
            end_time=record.end_time,
            duration_seconds=300.0,
            progress_percentage=60.0,
            current_step="Deployment failed",
            total_steps=5,
            completed_steps=3,
            error_message="Service deployment failed"
        )
        
        record.phases = {DeploymentPhase.DEPLOYMENT: failed_phase}
        
        return record
    
    def test_initialization(self, report_generator, history_manager):
        """Test report generator initialization."""
        assert report_generator.history_manager == history_manager
        # Template environment may or may not be initialized depending on template directory
    
    def test_generate_json_deployment_report(self, report_generator, history_manager, sample_deployment_record):
        """Test generating JSON deployment report."""
        # Save record to history
        history_manager.save_deployment_record(sample_deployment_record)
        
        # Generate report
        config = ReportConfig(format="json", include_metrics=True, include_health_checks=True)
        report_content = report_generator.generate_deployment_report(
            sample_deployment_record.deployment_id, config
        )
        
        assert report_content is not None
        
        # Parse JSON to verify structure
        report_data = json.loads(report_content)
        
        # Verify basic information
        assert report_data['deployment_id'] == sample_deployment_record.deployment_id
        assert report_data['environment'] == sample_deployment_record.environment
        assert report_data['status'] == sample_deployment_record.status.value
        assert report_data['commit_sha'] == sample_deployment_record.commit_sha
        assert report_data['image_tag'] == sample_deployment_record.image_tag
        assert report_data['success'] is True
        
        # Verify metrics are included
        assert 'metrics' in report_data
        assert report_data['metrics']['total_duration_seconds'] == 600.0
        assert report_data['metrics']['cpu_usage_percent'] == 75.5
        
        # Verify health checks are included
        assert 'health_checks' in report_data
        assert len(report_data['health_checks']) == 2
        
        # Verify phases information
        assert 'phases' in report_data
        assert 'validation' in report_data['phases']
        assert 'build' in report_data['phases']
        assert 'deployment' in report_data['phases']
        
        # Verify report metadata
        assert 'report_metadata' in report_data
        assert report_data['report_metadata']['format'] == 'json'
    
    def test_generate_html_deployment_report(self, report_generator, history_manager, sample_deployment_record):
        """Test generating HTML deployment report."""
        # Save record to history
        history_manager.save_deployment_record(sample_deployment_record)
        
        # Generate report
        config = ReportConfig(format="html", include_metrics=True)
        report_content = report_generator.generate_deployment_report(
            sample_deployment_record.deployment_id, config
        )
        
        assert report_content is not None
        assert "<!DOCTYPE html>" in report_content
        assert "<title>Deployment Report" in report_content
        assert sample_deployment_record.deployment_id in report_content
        assert sample_deployment_record.environment in report_content
        assert "Performance Metrics" in report_content
    
    def test_generate_markdown_deployment_report(self, report_generator, history_manager, sample_deployment_record):
        """Test generating Markdown deployment report."""
        # Save record to history
        history_manager.save_deployment_record(sample_deployment_record)
        
        # Generate report
        config = ReportConfig(format="markdown", include_metrics=True)
        report_content = report_generator.generate_deployment_report(
            sample_deployment_record.deployment_id, config
        )
        
        assert report_content is not None
        assert "# Deployment Report" in report_content
        assert f"**Deployment ID:** {sample_deployment_record.deployment_id}" in report_content
        assert f"**Environment:** {sample_deployment_record.environment}" in report_content
        assert "## Performance Metrics" in report_content
        assert "✅" in report_content  # Success indicator
    
    def test_generate_failed_deployment_report(self, report_generator, history_manager, failed_deployment_record):
        """Test generating report for failed deployment."""
        # Save record to history
        history_manager.save_deployment_record(failed_deployment_record)
        
        # Generate JSON report
        config = ReportConfig(format="json")
        report_content = report_generator.generate_deployment_report(
            failed_deployment_record.deployment_id, config
        )
        
        assert report_content is not None
        report_data = json.loads(report_content)
        
        assert report_data['success'] is False
        assert report_data['status'] == DeploymentStatus.FAILED.value
        assert len(report_data['errors']) == 2
        assert len(report_data['warnings']) == 1
        
        # Generate Markdown report
        config = ReportConfig(format="markdown")
        md_report = report_generator.generate_deployment_report(
            failed_deployment_record.deployment_id, config
        )
        
        assert "❌" in md_report  # Failure indicator
        assert "## Issues" in md_report
        assert "### ❌ Errors" in md_report
        assert "### ⚠️ Warnings" in md_report
    
    def test_generate_json_summary_report(self, report_generator, history_manager):
        """Test generating JSON summary report."""
        # Create multiple deployment records
        records = []
        for i in range(5):
            record = DeploymentRecord(
                deployment_id=f"deployment-{i}",
                environment="production" if i % 2 == 0 else "staging",
                commit_sha=f"commit-{i}",
                image_tag=f"app:v{i}",
                status=DeploymentStatus.COMPLETED if i % 3 != 0 else DeploymentStatus.FAILED,
                start_time=datetime.utcnow() - timedelta(hours=i),
                end_time=datetime.utcnow() - timedelta(hours=i-1) if i > 0 else datetime.utcnow()
            )
            records.append(record)
            history_manager.save_deployment_record(record)
        
        # Generate summary report
        config = ReportConfig(format="json")
        report_content = report_generator.generate_summary_report(
            environment="production", days=30, config=config
        )
        
        assert report_content is not None
        report_data = json.loads(report_content)
        
        assert 'summary' in report_data
        assert 'deployments' in report_data
        assert 'report_metadata' in report_data
        
        # Check summary statistics
        summary = report_data['summary']
        assert 'total_deployments' in summary
        assert 'successful_deployments' in summary
        assert 'success_rate' in summary
        
        # Check deployments list
        deployments = report_data['deployments']
        assert len(deployments) == 3  # Only production deployments (0, 2, 4)
    
    def test_generate_html_summary_report(self, report_generator, history_manager):
        """Test generating HTML summary report."""
        # Create test records
        for i in range(3):
            record = DeploymentRecord(
                deployment_id=f"deployment-{i}",
                environment="production",
                commit_sha=f"commit-{i}",
                image_tag=f"app:v{i}",
                status=DeploymentStatus.COMPLETED,
                start_time=datetime.utcnow() - timedelta(hours=i),
                end_time=datetime.utcnow() - timedelta(hours=i-1) if i > 0 else datetime.utcnow()
            )
            history_manager.save_deployment_record(record)
        
        # Generate HTML summary report
        config = ReportConfig(format="html")
        report_content = report_generator.generate_summary_report(
            environment="production", days=30, config=config
        )
        
        assert report_content is not None
        assert "<!DOCTYPE html>" in report_content
        assert "<title>Deployment Summary Report" in report_content
        assert "Statistics" in report_content
        assert "Recent Deployments" in report_content
    
    def test_generate_markdown_summary_report(self, report_generator, history_manager):
        """Test generating Markdown summary report."""
        # Create test records
        for i in range(3):
            record = DeploymentRecord(
                deployment_id=f"deployment-{i}",
                environment="production",
                commit_sha=f"commit-{i}",
                image_tag=f"app:v{i}",
                status=DeploymentStatus.COMPLETED,
                start_time=datetime.utcnow() - timedelta(hours=i),
                end_time=datetime.utcnow() - timedelta(hours=i-1) if i > 0 else datetime.utcnow()
            )
            history_manager.save_deployment_record(record)
        
        # Generate Markdown summary report
        config = ReportConfig(format="markdown")
        report_content = report_generator.generate_summary_report(
            environment="production", days=30, config=config
        )
        
        assert report_content is not None
        assert "# Deployment Summary Report" in report_content
        assert "## Statistics" in report_content
        assert "## Recent Deployments" in report_content
        assert "| Deployment ID |" in report_content  # Table header
    
    def test_generate_report_nonexistent_deployment(self, report_generator):
        """Test generating report for non-existent deployment."""
        config = ReportConfig(format="json")
        report_content = report_generator.generate_deployment_report(
            "non-existent-deployment", config
        )
        
        assert report_content is None
    
    def test_generate_report_unsupported_format(self, report_generator, history_manager, sample_deployment_record):
        """Test generating report with unsupported format."""
        # Save record to history
        history_manager.save_deployment_record(sample_deployment_record)
        
        # Try unsupported format
        config = ReportConfig(format="xml")
        report_content = report_generator.generate_deployment_report(
            sample_deployment_record.deployment_id, config
        )
        
        assert report_content is None
    
    def test_report_config_options(self, report_generator, history_manager, sample_deployment_record):
        """Test different report configuration options."""
        # Save record to history
        history_manager.save_deployment_record(sample_deployment_record)
        
        # Test with minimal config
        minimal_config = ReportConfig(
            format="json",
            include_metrics=False,
            include_health_checks=False,
            include_validation_results=False,
            include_notifications=False
        )
        
        report_content = report_generator.generate_deployment_report(
            sample_deployment_record.deployment_id, minimal_config
        )
        
        assert report_content is not None
        report_data = json.loads(report_content)
        
        # These should not be included
        assert 'metrics' not in report_data
        assert 'health_checks' not in report_data
        assert 'validation_results' not in report_data
        assert 'notifications' not in report_data
        
        # Basic info should still be included
        assert 'deployment_id' in report_data
        assert 'environment' in report_data
        assert 'phases' in report_data
    
    def test_save_report(self, report_generator):
        """Test saving report to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = os.path.join(temp_dir, "test_report.json")
            content = '{"test": "content"}'
            
            success = report_generator.save_report(content, file_path)
            
            assert success is True
            assert os.path.exists(file_path)
            
            # Verify content
            with open(file_path, 'r', encoding='utf-8') as f:
                saved_content = f.read()
            assert saved_content == content
    
    def test_save_report_create_directory(self, report_generator):
        """Test saving report with directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "nested", "dir", "test_report.json")
            content = '{"test": "content"}'
            
            success = report_generator.save_report(content, nested_path)
            
            assert success is True
            assert os.path.exists(nested_path)
    
    def test_format_duration(self, report_generator):
        """Test duration formatting."""
        # Test various durations
        assert report_generator._format_duration(None) == "N/A"
        assert report_generator._format_duration(0) == "N/A"
        assert report_generator._format_duration(-5) == "N/A"
        assert report_generator._format_duration(30.5) == "30.5s"
        assert report_generator._format_duration(90) == "1m 30s"
        assert report_generator._format_duration(3665) == "1h 1m"
        assert report_generator._format_duration(7200) == "2h 0m"
    
    def test_report_with_rollback_info(self, report_generator, history_manager):
        """Test report generation with rollback information."""
        record = DeploymentRecord(
            deployment_id="rollback-deployment",
            environment="production",
            commit_sha="abc123",
            image_tag="app:v1.0.0",
            status=DeploymentStatus.ROLLED_BACK
        )
        
        record.rollback_revision = "app-v099"
        record.rollback_reason = "Health check failures"
        record.rollback_time = datetime.utcnow()
        
        history_manager.save_deployment_record(record)
        
        # Generate JSON report
        config = ReportConfig(format="json")
        report_content = report_generator.generate_deployment_report(record.deployment_id, config)
        
        assert report_content is not None
        report_data = json.loads(report_content)
        
        assert 'rollback' in report_data
        assert report_data['rollback']['revision'] == record.rollback_revision
        assert report_data['rollback']['reason'] == record.rollback_reason
        
        # Generate Markdown report
        config = ReportConfig(format="markdown")
        md_report = report_generator.generate_deployment_report(record.deployment_id, config)
        
        assert "## Rollback Information" in md_report
        assert record.rollback_revision in md_report
        assert record.rollback_reason in md_report


if __name__ == "__main__":
    pytest.main([__file__])