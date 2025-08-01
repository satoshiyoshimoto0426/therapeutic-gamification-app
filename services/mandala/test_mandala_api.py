"""
Mandala API?

?API実装

Requirements: 4.1, 4.3
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.mandala.main import app
from shared.interfaces.mandala_system import MandalaSystemInterface, CellStatus


class TestMandalaAPI:
    """Mandala API?"""
    
    def setup_method(self):
        """?"""
        self.client = TestClient(app)
        self.test_uid = "test_user_001"
        self.mandala_interface = MandalaSystemInterface()
    
    def test_health_check(self):
        """ヘルパー"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "mandala"
    
    def test_get_mandala_grid_new_user(self):
        """?Mandala?"""
        response = self.client.get(f"/mandala/{self.test_uid}/grid")
        assert response.status_code == 200
        
        data = response.json()
        assert data["uid"] == self.test_uid
        assert data["total_cells"] == 81
        assert data["unlocked_count"] == 0
        assert len(data["grid"]) == 9
        assert len(data["grid"][0]) == 9
        
        # ?
        core_value_positions = [(4, 4), (3, 4), (5, 4), (4, 3), (4, 5), (3, 3), (5, 5), (3, 5), (5, 3)]
        for x, y in core_value_positions:
            cell = data["grid"][x][y]
            assert cell["status"] == "core_value"
            assert "quest_title" in cell
            assert "therapeutic_focus" in cell
    
    def test_unlock_cell_success(self):
        """?"""
        # ?
        unlock_request = {
            "x": 4,
            "y": 2,  # ?(4,3)に
            "quest_title": "?",
            "quest_description": "5?",
            "xp_reward": 25,
            "difficulty": 2,
            "therapeutic_focus": "Mindfulness"
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "?" in data["message"]
        assert data["unlocked_count"] == 1
        assert data["cell_info"] is not None
        assert data["cell_info"]["quest_title"] == "?"
    
    def test_unlock_cell_invalid_coordinates(self):
        """無"""
        unlock_request = {
            "x": 10,  # 無
            "y": 5,
            "quest_title": "無",
            "quest_description": "無",
            "xp_reward": 25,
            "difficulty": 2
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert response.status_code == 422  # Validation error
    
    def test_unlock_cell_no_adjacent_unlocked(self):
        """?"""
        unlock_request = {
            "x": 0,
            "y": 0,  # ?
            "quest_title": "?",
            "quest_description": "?",
            "xp_reward": 25,
            "difficulty": 2
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert response.status_code == 400
        
        data = response.json()
        assert "アプリ" in data["detail"]
    
    def test_unlock_core_value_cell(self):
        """?"""
        unlock_request = {
            "x": 4,
            "y": 4,  # ?
            "quest_title": "無",
            "quest_description": "?",
            "xp_reward": 25,
            "difficulty": 2
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert response.status_code == 400
        
        data = response.json()
        assert "?" in data["detail"]
    
    def test_complete_cell_success(self):
        """?"""
        # ま
        unlock_request = {
            "x": 4,
            "y": 2,
            "quest_title": "?",
            "quest_description": "10?",
            "xp_reward": 30,
            "difficulty": 2
        }
        
        unlock_response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert unlock_response.status_code == 200
        
        # ?
        complete_request = {
            "x": 4,
            "y": 2
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/complete", json=complete_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "?" in data["message"]
        assert data["xp_earned"] == 30
        assert data["completion_time"] is not None
    
    def test_complete_locked_cell(self):
        """ログ"""
        complete_request = {
            "x": 0,
            "y": 0  # ログ
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/complete", json=complete_request)
        assert response.status_code == 400
        
        data = response.json()
        assert "?" in data["detail"]
    
    def test_complete_core_value_cell(self):
        """?"""
        complete_request = {
            "x": 4,
            "y": 4  # ?
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/complete", json=complete_request)
        assert response.status_code == 400
        
        data = response.json()
        assert "?" in data["detail"]
    
    def test_get_daily_reminder(self):
        """?"""
        response = self.client.get(f"/mandala/{self.test_uid}/reminder")
        assert response.status_code == 200
        
        data = response.json()
        assert "reminder" in data
        assert "?" in data["reminder"]  # 価
    
    def test_get_mandala_status(self):
        """Mandalaストーリー"""
        response = self.client.get(f"/mandala/{self.test_uid}/status")
        assert response.status_code == 200
        
        data = response.json()
        assert data["uid"] == self.test_uid
        assert data["total_cells"] == 81
        assert "unlocked_count" in data
        assert "completed_count" in data
        assert "completion_rate" in data
        assert "core_values_count" in data
        assert "last_updated" in data
        assert "available_unlocks" in data
    
    def test_unlock_validation_missing_fields(self):
        """?"""
        unlock_request = {
            "x": 4,
            "y": 2
            # quest_title, quest_description, xp_reward, difficulty が
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert response.status_code == 422  # Validation error
    
    def test_unlock_validation_invalid_difficulty(self):
        """無"""
        unlock_request = {
            "x": 4,
            "y": 2,
            "quest_title": "?",
            "quest_description": "?",
            "xp_reward": 25,
            "difficulty": 10  # 無1-5の
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert response.status_code == 422  # Validation error
    
    def test_unlock_validation_invalid_xp_reward(self):
        """無XP?"""
        unlock_request = {
            "x": 4,
            "y": 2,
            "quest_title": "?",
            "quest_description": "?",
            "xp_reward": 2000,  # 無XP?1-1000の
            "difficulty": 3
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert response.status_code == 422  # Validation error
    
    def test_unlock_validation_invalid_therapeutic_focus(self):
        """無"""
        unlock_request = {
            "x": 4,
            "y": 2,
            "quest_title": "?",
            "quest_description": "?",
            "xp_reward": 25,
            "difficulty": 2,
            "therapeutic_focus": "InvalidFocus"  # 無
        }
        
        response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert response.status_code == 400
        
        data = response.json()
        assert "治療" in data["detail"]
    
    def test_progressive_unlock_pattern(self):
        """?"""
        # ?
        unlock_positions = [
            (4, 2),  # ?(4,3)に
            (4, 1),  # (4,2)に
            (3, 2),  # (4,2)に
            (5, 2)   # (4,2)に
        ]
        
        for i, (x, y) in enumerate(unlock_positions):
            unlock_request = {
                "x": x,
                "y": y,
                "quest_title": f"?{i+1}",
                "quest_description": f"?{i+1}",
                "xp_reward": 20 + i * 5,
                "difficulty": 1 + i % 3
            }
            
            response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
            assert response.status_code == 200
            
            data = response.json()
            assert data["success"] is True
            assert data["unlocked_count"] == i + 1
    
    def test_grid_state_persistence(self):
        """?"""
        # ?
        unlock_request = {
            "x": 4,
            "y": 2,
            "quest_title": "?",
            "quest_description": "?",
            "xp_reward": 35,
            "difficulty": 3
        }
        
        unlock_response = self.client.post(f"/mandala/{self.test_uid}/unlock", json=unlock_request)
        assert unlock_response.status_code == 200
        
        # ?
        grid_response = self.client.get(f"/mandala/{self.test_uid}/grid")
        assert grid_response.status_code == 200
        
        data = grid_response.json()
        assert data["unlocked_count"] == 1
        
        cell = data["grid"][4][2]
        assert cell["status"] == "unlocked"
        assert cell["quest_title"] == "?"
        assert cell["xp_reward"] == 35
        assert cell["difficulty"] == 3


def test_mandala_system_integration():
    """Mandalaシステム"""
    interface = MandalaSystemInterface()
    test_uid = "integration_test_user"
    
    # ?
    grid = interface.get_or_create_grid(test_uid)
    assert grid.uid == test_uid
    assert grid.total_cells == 81
    assert grid.unlocked_count == 0
    
    # ?
    core_value_positions = [(4, 4), (3, 4), (5, 4), (4, 3), (4, 5), (3, 3), (5, 5), (3, 5), (5, 3)]
    for x, y in core_value_positions:
        cell = grid.get_cell(x, y)
        assert cell is not None
        assert cell.status == CellStatus.CORE_VALUE
    
    # ?
    quest_data = {
        "quest_title": "?",
        "quest_description": "システム",
        "xp_reward": 40,
        "difficulty": 2,
        "therapeutic_focus": "Self-Discipline"
    }
    
    success = interface.unlock_cell_for_user(test_uid, 4, 2, quest_data)
    assert success is True
    
    # アプリ
    updated_grid = interface.get_or_create_grid(test_uid)
    assert updated_grid.unlocked_count == 1
    
    unlocked_cell = updated_grid.get_cell(4, 2)
    assert unlocked_cell is not None
    assert unlocked_cell.status == CellStatus.UNLOCKED
    assert unlocked_cell.quest_title == "?"
    
    # ?
    complete_success = interface.complete_cell_for_user(test_uid, 4, 2)
    assert complete_success is True
    
    # ?
    completed_grid = interface.get_or_create_grid(test_uid)
    completed_cell = completed_grid.get_cell(4, 2)
    assert completed_cell.status == CellStatus.COMPLETED
    assert completed_cell.completion_time is not None
    
    # API?
    api_response = interface.get_grid_api_response(test_uid)
    assert api_response["uid"] == test_uid
    assert api_response["unlocked_count"] == 1
    assert len(api_response["grid"]) == 9
    
    # ?
    reminder = interface.get_daily_reminder_for_user(test_uid)
    assert "?" in reminder
    assert len(reminder) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])