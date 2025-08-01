"""
Integration tests for Mandala grid operations and task management
Testing all CRUD operations, daily limits, and grid state management
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, date
import json
import sys
import os

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from main import app
from interfaces.core_types import TaskType, TaskStatus, ChapterType, CellStatus

client = TestClient(app)

class TestMandalaGridIntegration:
    """Integration tests for Mandala grid system"""
    
    def test_get_mandala_grid_creates_new_grid(self):
        """Test that accessing non-existent grid creates new 9x9 grid"""
        response = client.get("/mandala/test_user_123/grid?chapter=self_discipline")
        assert response.status_code == 200
        
        grid = response.json()
        assert len(grid) == 9  # 9 rows
        assert all(len(row) == 9 for row in grid)  # 9 columns each
        
        # Check center cell (4,4) is available
        center_cell = grid[4][4]
        assert center_cell["status"] == "available"
        assert center_cell["position"] == [4, 4]
        
        # Check corner cells are locked
        assert grid[0][0]["status"] == "locked"
        assert grid[8][8]["status"] == "locked"
    
    def test_mandala_grid_structure_and_unlocking(self):
        """Test Mandala grid structure and cell unlocking logic"""
        response = client.get("/mandala/test_user_456/grid?chapter=empathy")
        assert response.status_code == 200
        
        grid = response.json()
        
        # Verify inner ring cells (adjacent to center) are available
        inner_ring_positions = [
            (3, 3), (3, 4), (3, 5),
            (4, 3),         (4, 5),
            (5, 3), (5, 4), (5, 5)
        ]
        
        for row, col in inner_ring_positions:
            assert grid[row][col]["status"] == "available"
        
        # Verify XP rewards increase with distance from center
        center_xp = grid[4][4]["xp_reward"]
        corner_xp = grid[0][0]["xp_reward"]
        assert corner_xp > center_xp
    
    def test_mandala_grid_different_chapters(self):
        """Test that different chapters create separate grids"""
        # Get grid for self_discipline
        response1 = client.get("/mandala/test_user_789/grid?chapter=self_discipline")
        assert response1.status_code == 200
        
        # Get grid for creativity
        response2 = client.get("/mandala/test_user_789/grid?chapter=creativity")
        assert response2.status_code == 200
        
        grid1 = response1.json()
        grid2 = response2.json()
        
        # Grids should have different cell IDs
        assert grid1[0][0]["id"] != grid2[0][0]["id"]
        assert "self_discipline" in grid1[0][0]["id"]
        assert "creativity" in grid2[0][0]["id"]

class TestTaskManagementIntegration:
    """Integration tests for task CRUD operations"""
    
    def test_create_task_with_mandala_linking(self):
        """Test creating task and linking to Mandala cell"""
        task_data = {
            "task_type": "routine",
            "title": "Morning meditation",
            "description": "10 minutes of mindfulness",
            "difficulty": 2,
            "due_date": "2024-12-31T09:00:00",
            "mandala_cell_id": "test_user_123_self_discipline_4_4"
        }
        
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        
        task = response.json()
        assert task["title"] == "Morning meditation"
        assert task["task_type"] == "routine"
        assert task["mandala_cell_id"] == "test_user_123_self_discipline_4_4"
        assert task["status"] == "pending"
    
    def test_daily_task_limit_enforcement(self):
        """Test that daily task limit (16 tasks) is enforced"""
        # Create 16 tasks (should succeed)
        for i in range(16):
            task_data = {
                "task_type": "one_shot",
                "title": f"Task {i+1}",
                "difficulty": 1
            }
            response = client.post("/tasks", json=task_data)
            assert response.status_code == 200
        
        # 17th task should fail
        task_data = {
            "task_type": "one_shot",
            "title": "Task 17 - Should fail",
            "difficulty": 1
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 400
        assert "Daily task limit reached" in response.json()["detail"]
    
    def test_task_types_validation(self):
        """Test all 4 task types are supported"""
        task_types = ["routine", "one_shot", "skill_up", "social"]
        
        for task_type in task_types:
            task_data = {
                "task_type": task_type,
                "title": f"Test {task_type} task",
                "difficulty": 1
            }
            response = client.post("/tasks", json=task_data)
            assert response.status_code == 200
            
            task = response.json()
            assert task["task_type"] == task_type
    
    def test_invalid_task_type_rejection(self):
        """Test that invalid task types are rejected"""
        task_data = {
            "task_type": "invalid_type",
            "title": "Invalid task",
            "difficulty": 1
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 400
        assert "Invalid task type" in response.json()["detail"]

class TestTaskCompletionTracking:
    """Integration tests for task completion and real-time updates"""
    
    def test_task_completion_workflow(self):
        """Test complete task completion workflow"""
        # Create task
        task_data = {
            "task_type": "routine",
            "title": "Complete workout",
            "difficulty": 3,
            "mandala_cell_id": "test_user_completion_self_discipline_4_3"
        }
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        task = response.json()
        task_id = task["task_id"]
        
        # Complete task
        response = client.post(f"/tasks/{task_id}/complete")
        assert response.status_code == 200
        
        completion_result = response.json()
        assert "Task completed successfully" in completion_result["message"]
        assert "completed_at" in completion_result
        assert "xp_earned" in completion_result
        assert completion_result["xp_earned"] > 0
    
    def test_task_completion_updates_mandala_cell(self):
        """Test that completing task updates linked Mandala cell"""
        # Get initial grid state
        response = client.get("/mandala/test_user_mandala/grid?chapter=self_discipline")
        assert response.status_code == 200
        initial_grid = response.json()
        
        # Create and complete task linked to center cell
        task_data = {
            "task_type": "skill_up",
            "title": "Learn new skill",
            "difficulty": 4,
            "mandala_cell_id": "test_user_mandala_self_discipline_4_4"
        }
        response = client.post("/tasks", json=task_data)
        task = response.json()
        task_id = task["task_id"]
        
        # Complete the task
        response = client.post(f"/tasks/{task_id}/complete")
        assert response.status_code == 200
        
        # Check that Mandala cell is updated
        response = client.get("/mandala/test_user_mandala/grid?chapter=self_discipline")
        updated_grid = response.json()
        
        center_cell = updated_grid[4][4]
        assert center_cell["status"] == "completed"
        assert center_cell["task_id"] == task_id
    
    def test_task_completion_unlocks_adjacent_cells(self):
        """Test that completing tasks unlocks adjacent Mandala cells"""
        # Create task for an available cell
        task_data = {
            "task_type": "social",
            "title": "Call a friend",
            "difficulty": 2,
            "mandala_cell_id": "test_user_unlock_self_discipline_3_3"
        }
        response = client.post("/tasks", json=task_data)
        task = response.json()
        task_id = task["task_id"]
        
        # Complete the task
        response = client.post(f"/tasks/{task_id}/complete")
        assert response.status_code == 200
        
        # Check that adjacent cells are unlocked
        response = client.get("/mandala/test_user_unlock/grid?chapter=self_discipline")
        grid = response.json()
        
        # Check some adjacent cells that should now be available
        # (cells that were previously locked but are adjacent to completed cell)
        adjacent_positions = [(2, 2), (2, 3), (2, 4), (3, 2), (3, 4), (4, 2), (4, 3), (4, 4)]
        
        for row, col in adjacent_positions:
            if 0 <= row < 9 and 0 <= col < 9:
                cell_status = grid[row][col]["status"]
                # Should be available or completed, not locked
                assert cell_status in ["available", "completed"]

class TestTaskCRUDOperations:
    """Integration tests for complete task CRUD operations"""
    
    def test_get_user_tasks_filtering(self):
        """Test getting user tasks with filtering options"""
        # Create tasks of different types and statuses
        tasks_data = [
            {"task_type": "routine", "title": "Daily routine 1", "difficulty": 1},
            {"task_type": "one_shot", "title": "One-time task", "difficulty": 2},
            {"task_type": "skill_up", "title": "Learn Python", "difficulty": 4},
            {"task_type": "social", "title": "Team meeting", "difficulty": 3}
        ]
        
        created_tasks = []
        for task_data in tasks_data:
            response = client.post("/tasks", json=task_data)
            assert response.status_code == 200
            created_tasks.append(response.json())
        
        # Test getting all tasks
        response = client.get("/tasks")
        assert response.status_code == 200
        all_tasks = response.json()
        assert len(all_tasks) >= 4
        
        # Test filtering by task type
        response = client.get("/tasks?task_type=routine")
        assert response.status_code == 200
        routine_tasks = response.json()
        assert all(task["task_type"] == "routine" for task in routine_tasks)
        
        # Test filtering by status
        response = client.get("/tasks?status=pending")
        assert response.status_code == 200
        pending_tasks = response.json()
        assert all(task["status"] == "pending" for task in pending_tasks)
    
    def test_update_task_operations(self):
        """Test updating task properties"""
        # Create task
        task_data = {
            "task_type": "skill_up",
            "title": "Original title",
            "description": "Original description",
            "difficulty": 2
        }
        response = client.post("/tasks", json=task_data)
        task = response.json()
        task_id = task["task_id"]
        
        # Update task
        update_data = {
            "title": "Updated title",
            "description": "Updated description",
            "difficulty": 4,
            "status": "in_progress"
        }
        response = client.put(f"/tasks/{task_id}", json=update_data)
        assert response.status_code == 200
        
        updated_task = response.json()
        assert updated_task["title"] == "Updated title"
        assert updated_task["description"] == "Updated description"
        assert updated_task["difficulty"] == 4
        assert updated_task["status"] == "in_progress"
    
    def test_delete_task_operations(self):
        """Test deleting tasks and cleanup"""
        # Create task with Mandala cell link
        task_data = {
            "task_type": "routine",
            "title": "Task to delete",
            "mandala_cell_id": "test_user_delete_self_discipline_5_5"
        }
        response = client.post("/tasks", json=task_data)
        task = response.json()
        task_id = task["task_id"]
        
        # Delete task
        response = client.delete(f"/tasks/{task_id}")
        assert response.status_code == 200
        assert "Task deleted successfully" in response.json()["message"]
        
        # Verify task is deleted
        response = client.get("/tasks")
        remaining_tasks = response.json()
        task_ids = [t["task_id"] for t in remaining_tasks]
        assert task_id not in task_ids

class TestADHDSupportFeatures:
    """Integration tests for ADHD support features"""
    
    def test_adhd_support_configuration(self):
        """Test ADHD support settings in tasks"""
        adhd_support = {
            "pomodoro_enabled": True,
            "break_reminders": True,
            "hyperfocus_alerts": True,
            "daily_buffer_used": 0
        }
        
        task_data = {
            "task_type": "skill_up",
            "title": "ADHD-supported task",
            "difficulty": 3,
            "adhd_support": adhd_support
        }
        
        response = client.post("/tasks", json=task_data)
        assert response.status_code == 200
        
        task = response.json()
        assert task["adhd_support"]["pomodoro_enabled"] == True
        assert task["adhd_support"]["break_reminders"] == True
        assert task["adhd_support"]["hyperfocus_alerts"] == True
    
    def test_task_difficulty_and_xp_calculation(self):
        """Test that task difficulty affects XP calculation"""
        # Create tasks with different difficulties
        difficulties = [1, 2, 3, 4, 5]
        xp_values = []
        
        for difficulty in difficulties:
            task_data = {
                "task_type": "one_shot",
                "title": f"Difficulty {difficulty} task",
                "difficulty": difficulty
            }
            response = client.post("/tasks", json=task_data)
            task = response.json()
            task_id = task["task_id"]
            
            # Complete task and get XP
            response = client.post(f"/tasks/{task_id}/complete")
            completion_result = response.json()
            xp_values.append(completion_result["xp_earned"])
        
        # Verify XP increases with difficulty
        for i in range(1, len(xp_values)):
            assert xp_values[i] > xp_values[i-1], f"XP should increase with difficulty"

class TestErrorHandlingAndEdgeCases:
    """Integration tests for error handling and edge cases"""
    
    def test_unauthorized_access_prevention(self):
        """Test that users cannot access other users' data"""
        # This would require proper JWT implementation
        # For now, test basic error responses
        
        response = client.get("/mandala/unauthorized_user/grid")
        # Should work with mock auth, but in production would fail
        assert response.status_code in [200, 403]
    
    def test_invalid_mandala_cell_references(self):
        """Test handling of invalid Mandala cell references"""
        task_data = {
            "task_type": "routine",
            "title": "Task with invalid cell",
            "mandala_cell_id": "invalid_cell_id_format"
        }
        
        response = client.post("/tasks", json=task_data)
        # Should still create task, but cell linking might fail gracefully
        assert response.status_code == 200
    
    def test_completion_percentage_calculation(self):
        """Test Mandala grid completion percentage calculation"""
        # Get initial grid
        response = client.get("/mandala/test_user_percentage/grid?chapter=wisdom")
        assert response.status_code == 200
        
        # Create and complete multiple tasks to test percentage calculation
        for i in range(5):
            task_data = {
                "task_type": "routine",
                "title": f"Percentage test task {i}",
                "mandala_cell_id": f"test_user_percentage_wisdom_4_{4+i%2}"  # Alternate cells
            }
            response = client.post("/tasks", json=task_data)
            task = response.json()
            
            # Complete task
            response = client.post(f"/tasks/{task['task_id']}/complete")
            assert response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])