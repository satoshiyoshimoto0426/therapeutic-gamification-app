"""
Task Management Service Tests

タスク

Requirements: 5.1, 5.5
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.task_mgmt.main import app
from shared.interfaces.task_system import TaskType, TaskDifficulty, TaskPriority, TaskStatus, ADHDSupportLevel
from shared.interfaces.core_types import CrystalAttribute


class TestTaskManagementService:
    """タスク"""
    
    def setup_method(self):
        """?"""
        self.client = TestClient(app)
        self.test_uid = "test_user_001"
    
    def test_health_check(self):
        """ヘルパー"""
        response = self.client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "task-mgmt"
    
    def test_create_routine_task(self):
        """?"""
        task_request = {
            "task_type": TaskType.ROUTINE.value,
            "title": "?",
            "description": "?30?",
            "difficulty": TaskDifficulty.EASY.value,
            "priority": TaskPriority.HIGH.value,
            "estimated_duration": 30,
            "adhd_support_level": ADHDSupportLevel.BASIC.value,
            "pomodoro_sessions_planned": 1,
            "break_reminders_enabled": True,
            "tags": ["?", "?"],
            "is_recurring": True,
            "recurrence_pattern": "daily"
        }
        
        response = self.client.post(f"/tasks/{self.test_uid}/create", json=task_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_type"] == TaskType.ROUTINE.value
        assert data["title"] == "?"
        assert data["difficulty"] == TaskDifficulty.EASY.value
        assert data["status"] == TaskStatus.PENDING.value
        assert data["base_xp"] > 0  # ?XPが
        assert data["primary_crystal_attribute"] == CrystalAttribute.SELF_DISCIPLINE.value  # 自動
        assert data["is_recurring"] is True
        
        return data["task_id"]
    
    def test_create_one_shot_task(self):
        """?"""
        task_request = {
            "task_type": TaskType.ONE_SHOT.value,
            "title": "プレビュー",
            "description": "?",
            "difficulty": TaskDifficulty.HARD.value,
            "priority": TaskPriority.URGENT.value,
            "estimated_duration": 120,
            "due_date": (datetime.utcnow() + timedelta(days=7)).isoformat(),
            "adhd_support_level": ADHDSupportLevel.MODERATE.value,
            "pomodoro_sessions_planned": 4,
            "primary_crystal_attribute": CrystalAttribute.COURAGE.value,
            "tags": ["?", "?"]
        }
        
        response = self.client.post(f"/tasks/{self.test_uid}/create", json=task_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_type"] == TaskType.ONE_SHOT.value
        assert data["title"] == "プレビュー"
        assert data["difficulty"] == TaskDifficulty.HARD.value
        assert data["priority"] == TaskPriority.URGENT.value
        assert data["due_date"] is not None
        assert data["primary_crystal_attribute"] == CrystalAttribute.COURAGE.value
        
        return data["task_id"]
    
    def test_create_skill_up_task(self):
        """ストーリー"""
        task_request = {
            "task_type": TaskType.SKILL_UP.value,
            "title": "Python学",
            "description": "Pythonの",
            "difficulty": TaskDifficulty.MEDIUM.value,
            "estimated_duration": 60,
            "adhd_support_level": ADHDSupportLevel.INTENSIVE.value,
            "pomodoro_sessions_planned": 2,
            "focus_music_enabled": True,
            "tags": ["学", "プレビュー"]
        }
        
        response = self.client.post(f"/tasks/{self.test_uid}/create", json=task_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_type"] == TaskType.SKILL_UP.value
        assert data["title"] == "Python学"
        assert data["adhd_support_level"] == ADHDSupportLevel.INTENSIVE.value
        assert data["focus_music_enabled"] is True
        assert data["primary_crystal_attribute"] == CrystalAttribute.WISDOM.value  # 自動
        
        return data["task_id"]
    
    def test_create_social_task(self):
        """?"""
        task_request = {
            "task_type": TaskType.SOCIAL.value,
            "title": "?",
            "description": "?",
            "difficulty": TaskDifficulty.EASY.value,
            "estimated_duration": 45,
            "primary_crystal_attribute": CrystalAttribute.COMMUNICATION.value,
            "secondary_crystal_attributes": [CrystalAttribute.EMPATHY.value],
            "tags": ["?", "?"]
        }
        
        response = self.client.post(f"/tasks/{self.test_uid}/create", json=task_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_type"] == TaskType.SOCIAL.value
        assert data["title"] == "?"
        assert data["primary_crystal_attribute"] == CrystalAttribute.COMMUNICATION.value
        assert CrystalAttribute.EMPATHY.value in data["secondary_crystal_attributes"]
        
        return data["task_id"]
    
    def test_daily_task_limit(self):
        """?"""
        # 16?
        for i in range(16):
            task_request = {
                "task_type": TaskType.ROUTINE.value,
                "title": f"?{i+1}",
                "description": f"?{i+1}",
                "difficulty": TaskDifficulty.EASY.value
            }
            
            response = self.client.post(f"/tasks/{self.test_uid}/create", json=task_request)
            assert response.status_code == 200
        
        # 17?
        task_request = {
            "task_type": TaskType.ROUTINE.value,
            "title": "?",
            "description": "17?",
            "difficulty": TaskDifficulty.EASY.value
        }
        
        response = self.client.post(f"/tasks/{self.test_uid}/create", json=task_request)
        assert response.status_code == 429  # Too Many Requests
        assert "Daily task limit exceeded" in response.json()["detail"]
    
    def test_get_user_tasks(self):
        """ユーザー"""
        # い
        task_ids = []
        for i in range(3):
            task_id = self.test_create_routine_task()
            task_ids.append(task_id)
        
        # タスク
        response = self.client.get(f"/tasks/{self.test_uid}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) >= 3
        
        # ?
        returned_task_ids = [task["task_id"] for task in data]
        for task_id in task_ids:
            assert task_id in returned_task_ids
    
    def test_get_task_by_id(self):
        """タスクID?"""
        # タスク
        task_id = self.test_create_skill_up_task()
        
        # タスク
        response = self.client.get(f"/tasks/{self.test_uid}/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_id"] == task_id
        assert data["task_type"] == TaskType.SKILL_UP.value
        assert data["title"] == "Python学"
    
    def test_update_task(self):
        """タスク"""
        # タスク
        task_id = self.test_create_one_shot_task()
        
        # タスク
        update_request = {
            "title": "?",
            "description": "?",
            "priority": TaskPriority.HIGH.value,
            "notes": "?"
        }
        
        response = self.client.put(f"/tasks/{self.test_uid}/{task_id}", json=update_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "?"
        assert data["description"] == "?"
        assert data["priority"] == TaskPriority.HIGH.value
        assert data["notes"] == "?"
    
    def test_start_task(self):
        """タスク"""
        # タスク
        task_id = self.test_create_routine_task()
        
        # タスク
        start_request = {
            "pomodoro_session": True
        }
        
        response = self.client.post(f"/tasks/{self.test_uid}/{task_id}/start", json=start_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == TaskStatus.IN_PROGRESS.value
        assert data["started_at"] is not None
    
    def test_complete_task_with_xp_calculation(self):
        """タスクXP計算"""
        # タスク
        task_id = self.test_create_skill_up_task()
        
        # タスク
        start_request = {"pomodoro_session": True}
        start_response = self.client.post(f"/tasks/{self.test_uid}/{task_id}/start", json=start_request)
        assert start_response.status_code == 200
        
        # タスク
        complete_request = {
            "mood_score": 4,
            "actual_duration": 55,
            "notes": "学",
            "pomodoro_sessions_completed": 2
        }
        
        response = self.client.post(f"/tasks/{self.test_uid}/{task_id}/complete", json=complete_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["task"]["status"] == TaskStatus.COMPLETED.value
        assert data["task"]["completed_at"] is not None
        assert data["task"]["mood_at_completion"] == 4
        assert data["task"]["actual_duration"] == 55
        assert data["task"]["notes"] == "学"
        
        # XP計算
        assert data["xp_earned"] > 0
        assert "xp_calculation" in data
        xp_calc = data["xp_calculation"]
        assert xp_calc["base_xp"] > 0
        assert 0.8 <= xp_calc["mood_coefficient"] <= 1.2
        assert 1.0 <= xp_calc["adhd_assist_multiplier"] <= 1.5
        assert xp_calc["final_xp"] > 0
        
        # ?
        assert "crystal_growth_events" in data
        assert len(data["crystal_growth_events"]) > 0
    
    def test_delete_task(self):
        """タスク"""
        # タスク
        task_id = self.test_create_routine_task()
        
        # タスク
        response = self.client.delete(f"/tasks/{self.test_uid}/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert data["task_id"] == task_id
        
        # ?
        get_response = self.client.get(f"/tasks/{self.test_uid}/{task_id}")
        assert get_response.status_code == 404
    
    def test_xp_preview(self):
        """XPプレビュー"""
        preview_request = {
            "task_type": TaskType.SKILL_UP.value,
            "difficulty": TaskDifficulty.HARD.value,
            "mood_score": 5,
            "adhd_support_level": ADHDSupportLevel.INTENSIVE.value
        }
        
        response = self.client.post("/tasks/xp-preview", json=preview_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["task_type"] == TaskType.SKILL_UP.value
        assert data["difficulty"] == TaskDifficulty.HARD.value
        assert data["mood_score"] == 5
        assert data["estimated_xp"] > 0
    
    def test_task_recommendations(self):
        """タスク"""
        recommendation_request = {
            "primary_goal": "プレビュー",
            "user_experience_level": 3,
            "task_complexity": "moderate",
            "user_confidence": 4
        }
        
        response = self.client.post("/tasks/recommendations", json=recommendation_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["primary_goal"] == "プレビュー"
        assert data["recommended_task_type"] == TaskType.SKILL_UP.value  # "ストーリー"?
        assert data["recommended_difficulty"] in [d.value for d in TaskDifficulty]
        assert len(data["recommended_crystals"]) > 0
        assert "reasoning" in data
    
    def test_task_statistics(self):
        """タスク"""
        # い
        task_ids = []
        for i in range(5):
            task_id = self.test_create_routine_task()
            task_ids.append(task_id)
        
        # い
        for task_id in task_ids[:3]:
            # ?
            start_response = self.client.post(f"/tasks/{self.test_uid}/{task_id}/start", json={})
            assert start_response.status_code == 200
            
            # ?
            complete_request = {
                "mood_score": 3,
                "actual_duration": 25,
                "notes": "?"
            }
            complete_response = self.client.post(f"/tasks/{self.test_uid}/{task_id}/complete", json=complete_request)
            assert complete_response.status_code == 200
        
        # ?
        response = self.client.get(f"/tasks/{self.test_uid}/statistics?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_tasks"] >= 5
        assert data["completed_tasks"] >= 3
        assert data["completion_rate"] > 0
        assert data["total_xp_earned"] > 0
        assert "task_type_statistics" in data
        assert "difficulty_statistics" in data
    
    def test_daily_summary(self):
        """?"""
        # ?
        task_ids = []
        for i in range(3):
            task_id = self.test_create_routine_task()
            task_ids.append(task_id)
        
        # 1つ
        task_id = task_ids[0]
        start_response = self.client.post(f"/tasks/{self.test_uid}/{task_id}/start", json={})
        assert start_response.status_code == 200
        
        complete_request = {
            "mood_score": 4,
            "actual_duration": 30,
            "notes": "?"
        }
        complete_response = self.client.post(f"/tasks/{self.test_uid}/{task_id}/complete", json=complete_request)
        assert complete_response.status_code == 200
        
        # ?
        response = self.client.get(f"/tasks/{self.test_uid}/daily-summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_tasks"] >= 3
        assert data["completed_tasks"] >= 1
        assert data["daily_xp_earned"] > 0
        assert data["remaining_task_slots"] <= 16
        assert "task_type_completion" in data
    
    def test_task_filtering(self):
        """タスク"""
        # ?
        routine_id = self.test_create_routine_task()
        skill_up_id = self.test_create_skill_up_task()
        
        # ?
        response = self.client.get(f"/tasks/{self.test_uid}?task_type={TaskType.ROUTINE.value}")
        assert response.status_code == 200
        
        data = response.json()
        for task in data:
            assert task["task_type"] == TaskType.ROUTINE.value
        
        # ストーリー
        response = self.client.get(f"/tasks/{self.test_uid}?task_type={TaskType.SKILL_UP.value}")
        assert response.status_code == 200
        
        data = response.json()
        for task in data:
            assert task["task_type"] == TaskType.SKILL_UP.value


if __name__ == "__main__":
    pytest.main([__file__, "-v"])