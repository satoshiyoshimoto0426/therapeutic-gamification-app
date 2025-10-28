"""
Tests for deployment history manager functionality.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta
from pathlib import Path

from models import DeploymentRecord, DeploymentStatus, DeploymentMetrics, DeploymentSummary
from history_manager import DeploymentHistoryManager


class TestDeploymentHistoryManager:
    """Test cases for DeploymentHistoryManager class."""
    
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
    def sample_deployment_record(self):
        """Create sample deployment record."""
        record = DeploymentRecord(
            deployment_id="test-deployment-123",
            environment="production",
            commit_sha="abc123def456",
            image_tag="myapp:v1.2.3",
            revision_name="myapp-v123",
            status=DeploymentStatus.COMPLETED
        )
        
        # Add some metrics
        record.metrics = DeploymentMetrics(
            total_duration_seconds=300.5,
            validation_duration_seconds=45.2,
            build_duration_seconds=120.8,
            deployment_duration_seconds=89.3,
            health_check_duration_seconds=45.2,
            cpu_usage_percent=65.5,
            memory_usage_mb=512.0,
            network_io_mb=128.5,
            success_rate=98.5,
            error_count=0,
            warning_count=2
        )
        
        # Add some test data
        record.errors = []
        record.warnings = ["Warning 1", "Warning 2"]
        record.metadata = {"test_key": "test_value"}
        record.deployment_config = {"memory": "2Gi", "cpu": "1"}
        record.environment_config = {"region": "us-central1"}
        
        return record
    
    def test_database_initialization(self, history_manager):
        """Test database initialization."""
        # Database should be created and tables should exist
        with history_manager._get_connection() as conn:
            # Check if tables exist
            tables = conn.execute("""
                SELECT name FROM sqlite_master WHERE type='table'
            """).fetchall()
            
            table_names = [table['name'] for table in tables]
            assert 'deployments' in table_names
            assert 'deployment_phases' in table_names
            assert 'deployment_metrics' in table_names
            assert 'deployment_logs' in table_names
    
    def test_save_deployment_record(self, history_manager, sample_deployment_record):
        """Test saving deployment record."""
        success = history_manager.save_deployment_record(sample_deployment_record)
        assert success
        
        # Verify record was saved
        retrieved_record = history_manager.get_deployment_record(sample_deployment_record.deployment_id)
        assert retrieved_record is not None
        assert retrieved_record.deployment_id == sample_deployment_record.deployment_id
        assert retrieved_record.environment == sample_deployment_record.environment
        assert retrieved_record.commit_sha == sample_deployment_record.commit_sha
        assert retrieved_record.image_tag == sample_deployment_record.image_tag
        assert retrieved_record.status == sample_deployment_record.status
    
    def test_get_deployment_record_not_found(self, history_manager):
        """Test getting non-existent deployment record."""
        record = history_manager.get_deployment_record("non-existent-id")
        assert record is None
    
    def test_get_deployment_history(self, history_manager):
        """Test getting deployment history."""
        # Create multiple test records
        records = []
        for i in range(5):
            record = DeploymentRecord(
                deployment_id=f"test-deployment-{i}",
                environment="production" if i % 2 == 0 else "staging",
                commit_sha=f"commit-{i}",
                image_tag=f"image:v{i}",
                status=DeploymentStatus.COMPLETED if i % 3 != 0 else DeploymentStatus.FAILED
            )
            records.append(record)
            history_manager.save_deployment_record(record)
        
        # Test getting all history
        history = history_manager.get_deployment_history()
        assert len(history) == 5
        
        # Test filtering by environment
        prod_history = history_manager.get_deployment_history(environment="production")
        assert len(prod_history) == 3  # Records 0, 2, 4
        
        # Test filtering by status
        completed_history = history_manager.get_deployment_history(status=DeploymentStatus.COMPLETED)
        assert len(completed_history) == 4  # Records 1, 2, 4 (i % 3 != 0 means failed)
        
        # Test limit
        limited_history = history_manager.get_deployment_history(limit=3)
        assert len(limited_history) == 3
    
    def test_get_deployment_statistics(self, history_manager):
        """Test getting deployment statistics."""
        # Create test records with different statuses
        successful_record = DeploymentRecord(
            deployment_id="success-1",
            environment="production",
            commit_sha="commit1",
            image_tag="image:v1",
            status=DeploymentStatus.COMPLETED,
            start_time=datetime.utcnow() - timedelta(hours=1),
            end_time=datetime.utcnow()
        )
        successful_record.metrics.total_duration_seconds = 300.0
        
        failed_record = DeploymentRecord(
            deployment_id="failed-1",
            environment="production",
            commit_sha="commit2",
            image_tag="image:v2",
            status=DeploymentStatus.FAILED,
            start_time=datetime.utcnow() - timedelta(hours=2),
            end_time=datetime.utcnow() - timedelta(hours=1)
        )
        failed_record.metrics.total_duration_seconds = 150.0
        failed_record.errors = ["Error 1", "Error 2"]
        failed_record.warnings = ["Warning 1"]
        
        history_manager.save_deployment_record(successful_record)
        history_manager.save_deployment_record(failed_record)
        
        # Get statistics
        stats = history_manager.get_deployment_statistics(environment="production", days=1)
        
        assert stats['total_deployments'] == 2
        assert stats['successful_deployments'] == 1
        assert stats['failed_deployments'] == 1
        assert stats['success_rate'] == 50.0
        assert stats['avg_duration_seconds'] == 225.0  # (300 + 150) / 2
        assert stats['total_errors'] == 2
        assert stats['total_warnings'] == 1
    
    def test_cleanup_old_records(self, history_manager):
        """Test cleaning up old deployment records."""
        # Create old and new records
        old_record = DeploymentRecord(
            deployment_id="old-deployment",
            environment="production",
            commit_sha="old-commit",
            image_tag="old:image",
            start_time=datetime.utcnow() - timedelta(days=100)
        )
        
        new_record = DeploymentRecord(
            deployment_id="new-deployment",
            environment="production",
            commit_sha="new-commit",
            image_tag="new:image",
            start_time=datetime.utcnow() - timedelta(days=1)
        )
        
        history_manager.save_deployment_record(old_record)
        history_manager.save_deployment_record(new_record)
        
        # Cleanup records older than 30 days
        deleted_count = history_manager.cleanup_old_records(days_to_keep=30)
        
        assert deleted_count == 1
        
        # Verify old record is gone, new record remains
        assert history_manager.get_deployment_record("old-deployment") is None
        assert history_manager.get_deployment_record("new-deployment") is not None
    
    def test_deployment_summary_from_record(self, sample_deployment_record):
        """Test creating deployment summary from record."""
        summary = DeploymentSummary.from_record(sample_deployment_record)
        
        assert summary.deployment_id == sample_deployment_record.deployment_id
        assert summary.environment == sample_deployment_record.environment
        assert summary.status == sample_deployment_record.status
        assert summary.commit_sha == sample_deployment_record.commit_sha
        assert summary.image_tag == sample_deployment_record.image_tag
        assert summary.success == sample_deployment_record.is_successful()
        assert summary.error_count == len(sample_deployment_record.errors)
        assert summary.warning_count == len(sample_deployment_record.warnings)


if __name__ == "__main__":
    pytest.main([__file__])