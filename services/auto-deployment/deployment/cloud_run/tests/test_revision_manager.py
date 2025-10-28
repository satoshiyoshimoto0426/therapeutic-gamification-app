"""
Tests for Cloud Run revision management functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from revision_manager import (
    RevisionManager,
    RevisionInfo,
    RevisionStatus,
    RevisionCleanupResult
)
from cloud_run_client import CloudRunClient


class TestRevisionManager:
    """Test cases for RevisionManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock(spec=CloudRunClient)
        self.mock_client.parent = "projects/test-project/locations/us-central1"
        self.revision_manager = RevisionManager(self.mock_client)
    
    @patch('services.auto_deployment.deployment.cloud_run.revision_manager.run_v2.RevisionsClient')
    @patch('services.auto_deployment.deployment.cloud_run.revision_manager.run_v2.ServicesClient')
    def test_init(self, mock_services_client, mock_revisions_client):
        """Test revision manager initialization."""
        mock_client = Mock(spec=CloudRunClient)
        manager = RevisionManager(mock_client)
        assert manager.client == mock_client
        mock_revisions_client.assert_called_once()
        mock_services_client.assert_called_once()
    
    @patch('services.auto_deployment.deployment.cloud_run.revision_manager.run_v2.RevisionsClient')
    def test_get_revision_info_success(self, mock_revisions_client):
        """Test successful revision info retrieval."""
        # Setup mocks
        mock_revisions_instance = Mock()
        mock_revisions_client.return_value = mock_revisions_instance
        
        mock_revision = Mock()
        mock_revision.name = "projects/test-project/locations/us-central1/services/test-service/revisions/test-rev"
        mock_revision.create_time = datetime.now()
        mock_revision.spec.template.spec.containers = [Mock()]
        mock_revision.spec.template.spec.containers[0].image = "gcr.io/test-project/test-image:latest"
        mock_revision.metadata.labels = {"version": "1.0"}
        
        mock_revisions_instance.get_revision.return_value = mock_revision
        
        # Mock service and traffic allocation
        mock_service = Mock()
        self.mock_client.get_service.return_value = mock_service
        self.mock_client._get_traffic_allocation.return_value = {"test-rev": 50}
        
        # Create revision manager
        manager = RevisionManager(self.mock_client)
        
        # Get revision info
        result = manager.get_revision_info("test-service", "test-rev")
        
        # Verify results
        assert result is not None
        assert result.name == "test-rev"
        assert result.service_name == "test-service"
        assert result.traffic_percentage == 50
        assert result.metadata == {"version": "1.0"}
        
        # Verify calls
        mock_revisions_instance.get_revision.assert_called_once()
        self.mock_client.get_service.assert_called_once_with("test-service")
    
    @patch('services.auto_deployment.deployment.cloud_run.revision_manager.run_v2.RevisionsClient')
    def test_get_revision_info_not_found(self, mock_revisions_client):
        """Test revision info retrieval for non-existent revision."""
        # Setup mocks
        mock_revisions_instance = Mock()
        mock_revisions_client.return_value = mock_revisions_instance
        mock_revisions_instance.get_revision.side_effect = Exception("Not found")
        
        # Create revision manager
        manager = RevisionManager(self.mock_client)
        
        # Get revision info
        result = manager.get_revision_info("test-service", "non-existent-rev")
        
        # Verify result
        assert result is None
    
    @patch('services.auto_deployment.deployment.cloud_run.revision_manager.run_v2.RevisionsClient')
    def test_list_revisions(self, mock_revisions_client):
        """Test listing revisions for a service."""
        # Setup mocks
        mock_revisions_instance = Mock()
        mock_revisions_client.return_value = mock_revisions_instance
        
        # Create mock revisions
        mock_rev1 = self._create_mock_revision("rev1", datetime.now())
        mock_rev2 = self._create_mock_revision("rev2", datetime.now() - timedelta(hours=1))
        
        mock_revisions_instance.list_revisions.return_value = [mock_rev1, mock_rev2]
        
        # Mock service and traffic allocation
        mock_service = Mock()
        self.mock_client.get_service.return_value = mock_service
        self.mock_client._get_traffic_allocation.return_value = {"rev1": 100, "rev2": 0}
        
        # Create revision manager
        manager = RevisionManager(self.mock_client)
        
        # List revisions
        result = manager.list_revisions("test-service")
        
        # Verify results
        assert len(result) == 2
        assert result[0].name == "rev1"  # Should be sorted by creation time (newest first)
        assert result[1].name == "rev2"
        assert result[0].traffic_percentage == 100
        assert result[1].traffic_percentage == 0
    
    def test_get_latest_revision(self):
        """Test getting the latest revision."""
        # Mock list_revisions to return sorted revisions
        mock_revisions = [
            RevisionInfo(
                name="rev2", 
                service_name="test-service", 
                image="image:v2", 
                created_time=datetime.now(),
                status=RevisionStatus.ACTIVE
            ),
            RevisionInfo(
                name="rev1", 
                service_name="test-service", 
                image="image:v1", 
                created_time=datetime.now() - timedelta(hours=1),
                status=RevisionStatus.ACTIVE
            )
        ]
        
        self.revision_manager.list_revisions = Mock(return_value=mock_revisions)
        
        # Get latest revision
        result = self.revision_manager.get_latest_revision("test-service")
        
        # Verify result
        assert result is not None
        assert result.name == "rev2"
    
    def test_get_latest_revision_no_revisions(self):
        """Test getting latest revision when no revisions exist."""
        self.revision_manager.list_revisions = Mock(return_value=[])
        
        result = self.revision_manager.get_latest_revision("test-service")
        
        assert result is None
    
    def test_get_serving_revisions(self):
        """Test getting revisions serving traffic."""
        # Mock list_revisions
        mock_revisions = [
            RevisionInfo(
                name="rev1", 
                service_name="test-service", 
                image="image:v1", 
                created_time=datetime.now(),
                status=RevisionStatus.SERVING,
                traffic_percentage=70
            ),
            RevisionInfo(
                name="rev2", 
                service_name="test-service", 
                image="image:v2", 
                created_time=datetime.now() - timedelta(hours=1),
                status=RevisionStatus.SERVING,
                traffic_percentage=30
            ),
            RevisionInfo(
                name="rev3", 
                service_name="test-service", 
                image="image:v3", 
                created_time=datetime.now() - timedelta(hours=2),
                status=RevisionStatus.INACTIVE,
                traffic_percentage=0
            )
        ]
        
        self.revision_manager.list_revisions = Mock(return_value=mock_revisions)
        
        # Get serving revisions
        result = self.revision_manager.get_serving_revisions("test-service")
        
        # Verify results
        assert len(result) == 2
        assert all(rev.traffic_percentage > 0 for rev in result)
        assert {rev.name for rev in result} == {"rev1", "rev2"}
    
    def test_get_stable_revision(self):
        """Test getting the stable revision (highest traffic)."""
        # Mock get_serving_revisions
        mock_serving_revisions = [
            RevisionInfo(
                name="rev1", 
                service_name="test-service", 
                image="image:v1", 
                created_time=datetime.now(),
                status=RevisionStatus.SERVING,
                traffic_percentage=30
            ),
            RevisionInfo(
                name="rev2", 
                service_name="test-service", 
                image="image:v2", 
                created_time=datetime.now() - timedelta(hours=1),
                status=RevisionStatus.SERVING,
                traffic_percentage=70
            )
        ]
        
        self.revision_manager.get_serving_revisions = Mock(return_value=mock_serving_revisions)
        
        # Get stable revision
        result = self.revision_manager.get_stable_revision("test-service")
        
        # Verify result
        assert result is not None
        assert result.name == "rev2"
        assert result.traffic_percentage == 70
    
    def test_get_stable_revision_no_serving(self):
        """Test getting stable revision when no revisions are serving."""
        self.revision_manager.get_serving_revisions = Mock(return_value=[])
        
        result = self.revision_manager.get_stable_revision("test-service")
        
        assert result is None
    
    def test_cleanup_old_revisions(self):
        """Test cleaning up old revisions."""
        # Mock list_revisions
        now = datetime.now()
        mock_revisions = [
            RevisionInfo(
                name="rev-new", 
                service_name="test-service", 
                image="image:latest", 
                created_time=now,
                status=RevisionStatus.SERVING,
                traffic_percentage=100
            ),
            RevisionInfo(
                name="rev-old1", 
                service_name="test-service", 
                image="image:v1", 
                created_time=now - timedelta(days=40),
                status=RevisionStatus.INACTIVE,
                traffic_percentage=0
            ),
            RevisionInfo(
                name="rev-old2", 
                service_name="test-service", 
                image="image:v2", 
                created_time=now - timedelta(days=50),
                status=RevisionStatus.INACTIVE,
                traffic_percentage=0
            )
        ]
        
        self.revision_manager.list_revisions = Mock(return_value=mock_revisions)
        self.revision_manager._delete_revision = Mock(return_value=True)
        
        # Cleanup old revisions
        result = self.revision_manager.cleanup_old_revisions(
            "test-service", keep_count=1, keep_days=30
        )
        
        # Verify results
        assert result.success is True
        assert len(result.cleaned_revisions) == 2
        assert "rev-old1" in result.cleaned_revisions
        assert "rev-old2" in result.cleaned_revisions
        
        # Verify delete was called for old revisions
        assert self.revision_manager._delete_revision.call_count == 2
    
    def test_cleanup_old_revisions_no_cleanup_needed(self):
        """Test cleanup when no revisions need to be cleaned."""
        # Mock list_revisions with only recent revisions
        now = datetime.now()
        mock_revisions = [
            RevisionInfo(
                name="rev-recent", 
                service_name="test-service", 
                image="image:latest", 
                created_time=now,
                status=RevisionStatus.SERVING,
                traffic_percentage=100
            )
        ]
        
        self.revision_manager.list_revisions = Mock(return_value=mock_revisions)
        
        # Cleanup old revisions
        result = self.revision_manager.cleanup_old_revisions("test-service")
        
        # Verify results
        assert result.success is True
        assert len(result.cleaned_revisions) == 0
    
    @patch('services.auto_deployment.deployment.cloud_run.revision_manager.run_v2.ServicesClient')
    def test_tag_revision(self, mock_services_client):
        """Test tagging a revision."""
        # Setup mocks
        mock_services_instance = Mock()
        mock_services_client.return_value = mock_services_instance
        
        mock_service = Mock()
        mock_service.spec.traffic = []
        self.mock_client.get_service.return_value = mock_service
        
        mock_operation = Mock()
        mock_operation.result.return_value = None
        mock_services_instance.update_service.return_value = mock_operation
        
        # Create revision manager
        manager = RevisionManager(self.mock_client)
        
        # Tag revision
        result = manager.tag_revision("test-service", "test-rev", "stable")
        
        # Verify results
        assert result is True
        
        # Verify service was updated
        mock_services_instance.update_service.assert_called_once()
    
    def test_compare_revisions(self):
        """Test comparing two revisions."""
        # Mock get_revision_info
        rev1_info = RevisionInfo(
            name="rev1",
            service_name="test-service",
            image="gcr.io/test-project/test-image:v1",
            created_time=datetime.now(),
            status=RevisionStatus.ACTIVE,
            resource_limits={"memory": "2Gi", "cpu": "2"},
            env_vars={"ENV": "production", "DEBUG": "false"},
            metadata={"version": "1.0"}
        )
        
        rev2_info = RevisionInfo(
            name="rev2",
            service_name="test-service",
            image="gcr.io/test-project/test-image:v2",
            created_time=datetime.now(),
            status=RevisionStatus.ACTIVE,
            resource_limits={"memory": "4Gi", "cpu": "2"},
            env_vars={"ENV": "production", "DEBUG": "true"},
            metadata={"version": "2.0"}
        )
        
        self.revision_manager.get_revision_info = Mock()
        self.revision_manager.get_revision_info.side_effect = [rev1_info, rev2_info]
        
        # Compare revisions
        result = self.revision_manager.compare_revisions("test-service", "rev1", "rev2")
        
        # Verify results
        assert result["image_changed"] is True
        assert "memory" in result["resource_changes"]
        assert result["resource_changes"]["memory"]["from"] == "2Gi"
        assert result["resource_changes"]["memory"]["to"] == "4Gi"
        assert "DEBUG" in result["env_var_changes"]
        assert result["env_var_changes"]["DEBUG"]["from"] == "false"
        assert result["env_var_changes"]["DEBUG"]["to"] == "true"
        assert "version" in result["metadata_changes"]
    
    def test_compare_revisions_not_found(self):
        """Test comparing revisions when one doesn't exist."""
        self.revision_manager.get_revision_info = Mock()
        self.revision_manager.get_revision_info.side_effect = [None, Mock()]
        
        result = self.revision_manager.compare_revisions("test-service", "rev1", "rev2")
        
        assert "error" in result
        assert "not found" in result["error"]
    
    def test_identify_revisions_for_cleanup(self):
        """Test identifying revisions for cleanup."""
        now = datetime.now()
        revisions = [
            RevisionInfo(
                name="rev-serving", 
                service_name="test-service", 
                image="image:latest", 
                created_time=now,
                status=RevisionStatus.SERVING,
                traffic_percentage=100
            ),
            RevisionInfo(
                name="rev-recent", 
                service_name="test-service", 
                image="image:v2", 
                created_time=now - timedelta(hours=1),
                status=RevisionStatus.INACTIVE,
                traffic_percentage=0
            ),
            RevisionInfo(
                name="rev-old", 
                service_name="test-service", 
                image="image:v1", 
                created_time=now - timedelta(days=40),
                status=RevisionStatus.INACTIVE,
                traffic_percentage=0
            )
        ]
        
        # Identify revisions for cleanup
        result = self.revision_manager._identify_revisions_for_cleanup(
            revisions, keep_count=1, keep_days=30
        )
        
        # Verify results
        assert len(result) == 1
        assert "rev-old" in result
        assert "rev-serving" not in result  # Should not delete serving revisions
        assert "rev-recent" not in result   # Should keep recent revisions
    
    def _create_mock_revision(self, name: str, created_time: datetime):
        """Helper method to create mock revision."""
        mock_revision = Mock()
        mock_revision.name = f"projects/test-project/locations/us-central1/services/test-service/revisions/{name}"
        mock_revision.create_time = created_time
        mock_revision.spec.template.spec.containers = [Mock()]
        mock_revision.spec.template.spec.containers[0].image = f"gcr.io/test-project/test-image:{name}"
        mock_revision.metadata.labels = {}
        return mock_revision


class TestRevisionInfo:
    """Test cases for RevisionInfo dataclass."""
    
    def test_revision_info_creation(self):
        """Test RevisionInfo creation."""
        created_time = datetime.now()
        revision_info = RevisionInfo(
            name="test-rev",
            service_name="test-service",
            image="gcr.io/test-project/test-image:latest",
            created_time=created_time,
            status=RevisionStatus.ACTIVE,
            traffic_percentage=50
        )
        
        assert revision_info.name == "test-rev"
        assert revision_info.service_name == "test-service"
        assert revision_info.image == "gcr.io/test-project/test-image:latest"
        assert revision_info.created_time == created_time
        assert revision_info.status == RevisionStatus.ACTIVE
        assert revision_info.traffic_percentage == 50
        assert revision_info.metadata == {}
        assert revision_info.resource_limits == {}
        assert revision_info.env_vars == {}


class TestRevisionCleanupResult:
    """Test cases for RevisionCleanupResult dataclass."""
    
    def test_revision_cleanup_result_success(self):
        """Test successful cleanup result."""
        result = RevisionCleanupResult(
            success=True,
            cleaned_revisions=["rev1", "rev2"]
        )
        
        assert result.success is True
        assert result.cleaned_revisions == ["rev1", "rev2"]
        assert result.error_message is None
    
    def test_revision_cleanup_result_failure(self):
        """Test failed cleanup result."""
        result = RevisionCleanupResult(
            success=False,
            cleaned_revisions=[],
            error_message="Cleanup failed"
        )
        
        assert result.success is False
        assert result.cleaned_revisions == []
        assert result.error_message == "Cleanup failed"