"""
Tests for Cloud Run traffic management functionality.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from ..traffic_manager import (
    TrafficManager,
    TrafficStrategy,
    TrafficSplit,
    TrafficUpdateResult
)
from ..cloud_run_client import CloudRunClient


class TestTrafficManager:
    """Test cases for TrafficManager."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_client = Mock(spec=CloudRunClient)
        self.traffic_manager = TrafficManager(self.mock_client)
    
    @patch('services.auto_deployment.deployment.cloud_run.traffic_manager.run_v2.ServicesClient')
    def test_init(self, mock_services_client):
        """Test traffic manager initialization."""
        mock_client = Mock(spec=CloudRunClient)
        manager = TrafficManager(mock_client)
        assert manager.client == mock_client
        mock_services_client.assert_called_once()
    
    @patch('services.auto_deployment.deployment.cloud_run.traffic_manager.run_v2.ServicesClient')
    def test_update_traffic_success(self, mock_services_client):
        """Test successful traffic update."""
        # Setup mocks
        mock_services_instance = Mock()
        mock_services_client.return_value = mock_services_instance
        
        mock_service = Mock()
        mock_service.spec.traffic = []
        self.mock_client.get_service.return_value = mock_service
        
        mock_operation = Mock()
        mock_result = Mock()
        mock_operation.result.return_value = mock_result
        mock_services_instance.update_service.return_value = mock_operation
        
        self.mock_client._get_traffic_allocation.return_value = {"rev1": 70, "rev2": 30}
        
        # Create traffic manager
        manager = TrafficManager(self.mock_client)
        
        # Create traffic splits
        traffic_splits = [
            TrafficSplit(revision_name="rev1", percentage=70),
            TrafficSplit(revision_name="rev2", percentage=30)
        ]
        
        # Update traffic
        result = manager.update_traffic("test-service", traffic_splits)
        
        # Verify results
        assert result.success is True
        assert result.current_traffic == {"rev1": 70, "rev2": 30}
        assert result.error_message is None
        
        # Verify service was retrieved and updated
        self.mock_client.get_service.assert_called_once_with("test-service")
        mock_services_instance.update_service.assert_called_once()
    
    def test_update_traffic_invalid_splits(self):
        """Test traffic update with invalid splits."""
        # Create traffic splits that don't sum to 100
        traffic_splits = [
            TrafficSplit(revision_name="rev1", percentage=60),
            TrafficSplit(revision_name="rev2", percentage=30)
        ]
        
        # Update traffic
        result = self.traffic_manager.update_traffic("test-service", traffic_splits)
        
        # Verify failure
        assert result.success is False
        assert "percentages must sum to 100" in result.error_message
    
    def test_update_traffic_service_not_found(self):
        """Test traffic update when service doesn't exist."""
        self.mock_client.get_service.return_value = None
        
        traffic_splits = [
            TrafficSplit(revision_name="rev1", percentage=100)
        ]
        
        result = self.traffic_manager.update_traffic("non-existent-service", traffic_splits)
        
        assert result.success is False
        assert "Service non-existent-service not found" in result.error_message
    
    @patch('services.auto_deployment.deployment.cloud_run.traffic_manager.time.sleep')
    def test_execute_canary_deployment(self, mock_sleep):
        """Test canary deployment execution."""
        # Mock successful traffic updates
        self.traffic_manager.update_traffic = Mock()
        self.traffic_manager.update_traffic.side_effect = [
            TrafficUpdateResult(success=True, current_traffic={"new-rev": 10, "old-rev": 90}),
            TrafficUpdateResult(success=True, current_traffic={"new-rev": 100})
        ]
        
        # Execute canary deployment
        result = self.traffic_manager.execute_canary_deployment(
            "test-service", "new-rev", "old-rev", canary_percentage=10, monitoring_duration=60
        )
        
        # Verify results
        assert result.success is True
        assert result.current_traffic == {"new-rev": 100}
        
        # Verify traffic updates were called twice
        assert self.traffic_manager.update_traffic.call_count == 2
        
        # Verify monitoring duration was respected
        mock_sleep.assert_called_once_with(60)
    
    def test_execute_canary_deployment_failure(self):
        """Test canary deployment with initial failure."""
        # Mock failed initial traffic update
        self.traffic_manager.update_traffic = Mock()
        self.traffic_manager.update_traffic.return_value = TrafficUpdateResult(
            success=False, 
            current_traffic={}, 
            error_message="Traffic update failed"
        )
        
        # Execute canary deployment
        result = self.traffic_manager.execute_canary_deployment(
            "test-service", "new-rev", "old-rev"
        )
        
        # Verify failure
        assert result.success is False
        assert result.error_message == "Traffic update failed"
        
        # Verify only one traffic update was attempted
        assert self.traffic_manager.update_traffic.call_count == 1
    
    def test_execute_blue_green_deployment_switch_to_green(self):
        """Test blue-green deployment switching to green."""
        # Mock successful traffic update
        self.traffic_manager.update_traffic = Mock()
        self.traffic_manager.update_traffic.return_value = TrafficUpdateResult(
            success=True, 
            current_traffic={"green-rev": 100, "blue-rev": 0}
        )
        
        # Execute blue-green deployment
        result = self.traffic_manager.execute_blue_green_deployment(
            "test-service", "blue-rev", "green-rev", switch_to_green=True
        )
        
        # Verify results
        assert result.success is True
        assert result.current_traffic == {"green-rev": 100, "blue-rev": 0}
        
        # Verify traffic update was called with correct splits
        self.traffic_manager.update_traffic.assert_called_once()
        call_args = self.traffic_manager.update_traffic.call_args
        traffic_splits = call_args[0][1]
        
        # Find green and blue splits
        green_split = next(split for split in traffic_splits if split.revision_name == "green-rev")
        blue_split = next(split for split in traffic_splits if split.revision_name == "blue-rev")
        
        assert green_split.percentage == 100
        assert green_split.tag == "live"
        assert blue_split.percentage == 0
        assert blue_split.tag == "standby"
    
    def test_execute_blue_green_deployment_stay_on_blue(self):
        """Test blue-green deployment staying on blue."""
        # Mock successful traffic update
        self.traffic_manager.update_traffic = Mock()
        self.traffic_manager.update_traffic.return_value = TrafficUpdateResult(
            success=True, 
            current_traffic={"blue-rev": 100, "green-rev": 0}
        )
        
        # Execute blue-green deployment
        result = self.traffic_manager.execute_blue_green_deployment(
            "test-service", "blue-rev", "green-rev", switch_to_green=False
        )
        
        # Verify results
        assert result.success is True
        assert result.current_traffic == {"blue-rev": 100, "green-rev": 0}
        
        # Verify traffic update was called with correct splits
        call_args = self.traffic_manager.update_traffic.call_args
        traffic_splits = call_args[0][1]
        
        blue_split = next(split for split in traffic_splits if split.revision_name == "blue-rev")
        green_split = next(split for split in traffic_splits if split.revision_name == "green-rev")
        
        assert blue_split.percentage == 100
        assert blue_split.tag == "live"
        assert green_split.percentage == 0
        assert green_split.tag == "standby"
    
    def test_rollback_traffic(self):
        """Test traffic rollback."""
        # Mock successful traffic update
        self.traffic_manager.update_traffic = Mock()
        self.traffic_manager.update_traffic.return_value = TrafficUpdateResult(
            success=True, 
            current_traffic={"target-rev": 100}
        )
        
        # Execute rollback
        result = self.traffic_manager.rollback_traffic("test-service", "target-rev")
        
        # Verify results
        assert result.success is True
        assert result.current_traffic == {"target-rev": 100}
        
        # Verify traffic update was called with rollback split
        call_args = self.traffic_manager.update_traffic.call_args
        traffic_splits = call_args[0][1]
        
        assert len(traffic_splits) == 1
        assert traffic_splits[0].revision_name == "target-rev"
        assert traffic_splits[0].percentage == 100
        assert traffic_splits[0].tag == "stable"
    
    def test_get_current_traffic(self):
        """Test getting current traffic allocation."""
        mock_service = Mock()
        self.mock_client.get_service.return_value = mock_service
        self.mock_client._get_traffic_allocation.return_value = {"rev1": 60, "rev2": 40}
        
        result = self.traffic_manager.get_current_traffic("test-service")
        
        assert result == {"rev1": 60, "rev2": 40}
        self.mock_client.get_service.assert_called_once_with("test-service")
        self.mock_client._get_traffic_allocation.assert_called_once_with(mock_service)
    
    def test_get_current_traffic_service_not_found(self):
        """Test getting traffic for non-existent service."""
        self.mock_client.get_service.return_value = None
        
        result = self.traffic_manager.get_current_traffic("non-existent-service")
        
        assert result == {}
    
    def test_split_traffic_evenly(self):
        """Test splitting traffic evenly between revisions."""
        # Mock successful traffic update
        self.traffic_manager.update_traffic = Mock()
        self.traffic_manager.update_traffic.return_value = TrafficUpdateResult(
            success=True, 
            current_traffic={"rev1": 34, "rev2": 33, "rev3": 33}
        )
        
        # Split traffic evenly between 3 revisions
        result = self.traffic_manager.split_traffic_evenly(
            "test-service", ["rev1", "rev2", "rev3"]
        )
        
        # Verify results
        assert result.success is True
        
        # Verify traffic splits
        call_args = self.traffic_manager.update_traffic.call_args
        traffic_splits = call_args[0][1]
        
        assert len(traffic_splits) == 3
        
        # Check that percentages sum to 100 and are distributed fairly
        total_percentage = sum(split.percentage for split in traffic_splits)
        assert total_percentage == 100
        
        # With 3 revisions, should be 34, 33, 33
        percentages = sorted([split.percentage for split in traffic_splits], reverse=True)
        assert percentages == [34, 33, 33]
    
    def test_split_traffic_evenly_no_revisions(self):
        """Test splitting traffic with no revisions."""
        result = self.traffic_manager.split_traffic_evenly("test-service", [])
        
        assert result.success is False
        assert "No revisions provided" in result.error_message
    
    def test_validate_traffic_splits_valid(self):
        """Test validation of valid traffic splits."""
        traffic_splits = [
            TrafficSplit(revision_name="rev1", percentage=70),
            TrafficSplit(revision_name="rev2", percentage=30)
        ]
        
        result = self.traffic_manager._validate_traffic_splits(traffic_splits)
        assert result is True
    
    def test_validate_traffic_splits_invalid_sum(self):
        """Test validation of invalid traffic splits (wrong sum)."""
        traffic_splits = [
            TrafficSplit(revision_name="rev1", percentage=60),
            TrafficSplit(revision_name="rev2", percentage=30)
        ]
        
        result = self.traffic_manager._validate_traffic_splits(traffic_splits)
        assert result is False
    
    def test_validate_traffic_splits_empty(self):
        """Test validation of empty traffic splits."""
        result = self.traffic_manager._validate_traffic_splits([])
        assert result is False


class TestTrafficSplit:
    """Test cases for TrafficSplit dataclass."""
    
    def test_traffic_split_creation(self):
        """Test TrafficSplit creation."""
        split = TrafficSplit(revision_name="test-rev", percentage=50)
        
        assert split.revision_name == "test-rev"
        assert split.percentage == 50
        assert split.tag is None
    
    def test_traffic_split_with_tag(self):
        """Test TrafficSplit creation with tag."""
        split = TrafficSplit(revision_name="test-rev", percentage=100, tag="stable")
        
        assert split.revision_name == "test-rev"
        assert split.percentage == 100
        assert split.tag == "stable"


class TestTrafficUpdateResult:
    """Test cases for TrafficUpdateResult dataclass."""
    
    def test_traffic_update_result_success(self):
        """Test successful traffic update result."""
        result = TrafficUpdateResult(
            success=True,
            current_traffic={"rev1": 100}
        )
        
        assert result.success is True
        assert result.current_traffic == {"rev1": 100}
        assert result.error_message is None
    
    def test_traffic_update_result_failure(self):
        """Test failed traffic update result."""
        result = TrafficUpdateResult(
            success=False,
            current_traffic={},
            error_message="Update failed"
        )
        
        assert result.success is False
        assert result.current_traffic == {}
        assert result.error_message == "Update failed"