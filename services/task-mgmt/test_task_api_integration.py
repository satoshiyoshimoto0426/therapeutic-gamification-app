"""
タスクAPIエラー

Task 6.3: タスクAPIエラー
- タスクCRUD?APIを
- ?16タスク
- タスクXP?APIを
- タスクAPIの

Requirements: 3.4, 5.1
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from main import app
from shared.interfaces.task_system import TaskType, TaskDifficulty, TaskPriority, TaskStatus, ADHDSupportLevel
from shared.interfaces.core_types import CrystalAttribute

client = TestClient(app)

class TestTaskCRUDOperations:
    """タスクCRUD?"""
    
    def test_create_task_success(self):
        """タスク"""
        uid = "test_user_001"
        task_data = {
            "task_type": "routine",
            "title": "?",
            "description": "30?",
            "difficulty": 2,
            "priority": "medium",
            "estimated_duration": 30,
            "adhd_support_level": "basic",
            "pomodoro_sessions_planned": 1,
            "break_reminders_enabled": True,
            "focus_music_enabled": False,
            "tags": ["?", "?"],
            "is_recurring": True,
            "recurrence_pattern": "daily"
        }
        
        response = client.post(f"/tasks/{uid}/create", json=task_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["uid"] == uid
        assert data["task_type"] == "routine"
        assert data["title"] == "?"
        assert data["description"] == "30?"
        assert data["difficulty"] == 2
        assert data["priority"] == "medium"
        assert data["status"] == "pending"
        assert data["estimated_duration"] == 30
        assert data["adhd_support_level"] == "basic"
        assert data["pomodoro_sessions_planned"] == 1
        assert data["break_reminders_enabled"] is True
        assert data["focus_music_enabled"] is False
        assert data["tags"] == ["?", "?"]
        assert data["is_recurring"] is True
        assert data["recurrence_pattern"] == "daily"
        assert data["base_xp"] > 0
        assert data["xp_earned"] == 0  # ?XPは0
        assert data["is_overdue"] is False
    
    def test_get_user_tasks(self):
        """ユーザー"""
        uid = "test_user_002"
        
        # ?
        task_types = ["routine", "one_shot", "skill_up", "social"]
        created_tasks = []
        
        for i, task_type in enumerate(task_types):
            task_data = {
                "task_type": task_type,
                "title": f"?{i+1}",
                "description": f"{task_type}タスク",
                "difficulty": (i % 3) + 1,
                "priority": "medium",
                "estimated_duration": 30
            }
            
            response = client.post(f"/tasks/{uid}/create", json=task_data)
            assert response.status_code == 200
            created_tasks.append(response.json())
        
        # タスク
        response = client.get(f"/tasks/{uid}")
        
        assert response.status_code == 200
        tasks = response.json()
        
        assert len(tasks) == 4
        
        # タスク
        response = client.get(f"/tasks/{uid}?task_type=routine")
        assert response.status_code == 200
        routine_tasks = response.json()
        assert len(routine_tasks) == 1
        assert routine_tasks[0]["task_type"] == "routine"
    
    def test_get_specific_task(self):
        """?"""
        uid = "test_user_003"
        
        # タスク
        task_data = {
            "task_type": "one_shot",
            "title": "?",
            "description": "プレビュー",
            "difficulty": 3,
            "priority": "high",
            "estimated_duration": 120
        }
        
        create_response = client.post(f"/tasks/{uid}/create", json=task_data)
        assert create_response.status_code == 200
        created_task = create_response.json()
        task_id = created_task["task_id"]
        
        # ?
        response = client.get(f"/tasks/{uid}/{task_id}")
        
        assert response.status_code == 200
        task = response.json()
        
        assert task["task_id"] == task_id
        assert task["title"] == "?"
        assert task["difficulty"] == 3
        assert task["priority"] == "high"
    
    def test_update_task(self):
        """タスク"""
        uid = "test_user_004"
        
        # タスク
        task_data = {
            "task_type": "skill_up",
            "title": "Python学",
            "description": "基本",
            "difficulty": 2,
            "priority": "medium",
            "estimated_duration": 60
        }
        
        create_response = client.post(f"/tasks/{uid}/create", json=task_data)
        assert create_response.status_code == 200
        created_task = create_response.json()
        task_id = created_task["task_id"]
        
        # タスク
        update_data = {
            "title": "Python?",
            "description": "?",
            "difficulty": 4,
            "priority": "high",
            "estimated_duration": 90,
            "tags": ["プレビュー", "ストーリー"]
        }
        
        response = client.put(f"/tasks/{uid}/{task_id}", json=update_data)
        
        assert response.status_code == 200
        updated_task = response.json()
        
        assert updated_task["title"] == "Python?"
        assert updated_task["description"] == "?"
        assert updated_task["difficulty"] == 4
        assert updated_task["priority"] == "high"
        assert updated_task["estimated_duration"] == 90
        assert updated_task["tags"] == ["プレビュー", "ストーリー"]
    
    def test_start_task(self):
        """タスク"""
        uid = "test_user_005"
        
        # タスク
        task_data = {
            "task_type": "routine",
            "title": "?",
            "description": "?",
            "difficulty": 2,
            "priority": "medium",
            "estimated_duration": 45
        }
        
        create_response = client.post(f"/tasks/{uid}/create", json=task_data)
        assert create_response.status_code == 200
        created_task = create_response.json()
        task_id = created_task["task_id"]
        
        # タスク
        start_data = {
            "pomodoro_session": True
        }
        
        response = client.post(f"/tasks/{uid}/{task_id}/start", json=start_data)
        
        assert response.status_code == 200
        started_task = response.json()
        
        assert started_task["status"] == "in_progress"
        assert started_task["started_at"] is not None
    
    def test_complete_task_with_xp_calculation(self):
        """タスクXP計算"""
        uid = "test_user_006"
        
        # タスク
        task_data = {
            "task_type": "social",
            "title": "?",
            "description": "?",
            "difficulty": 3,
            "priority": "high",
            "estimated_duration": 120,
            "adhd_support_level": "enhanced"
        }
        
        create_response = client.post(f"/tasks/{uid}/create", json=task_data)
        assert create_response.status_code == 200
        created_task = create_response.json()
        task_id = created_task["task_id"]
        
        # タスク
        start_response = client.post(f"/tasks/{uid}/{task_id}/start", json={})
        assert start_response.status_code == 200
        
        # タスク
        complete_data = {
            "mood_score": 4,
            "actual_duration": 110,
            "notes": "と",
            "pomodoro_sessions_completed": 2
        }
        
        response = client.post(f"/tasks/{uid}/{task_id}/complete", json=complete_data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert result["task"]["status"] == "completed"
        assert result["task"]["completed_at"] is not None
        assert result["task"]["mood_at_completion"] == 4
        assert result["task"]["actual_duration"] == 110
        assert result["task"]["notes"] == "と"
        assert result["task"]["pomodoro_sessions_completed"] == 2
        
        # XP計算
        assert result["xp_earned"] > 0
        assert "xp_calculation" in result
        xp_calc = result["xp_calculation"]
        assert xp_calc["base_xp"] > 0
        assert xp_calc["mood_coefficient"] > 0
        assert xp_calc["adhd_assist_multiplier"] >= 1.0
        assert xp_calc["final_xp"] > 0
        
        # Pomodoro?
        assert "pomodoro_integration" in result
        pomodoro_info = result["pomodoro_integration"]
        assert pomodoro_info["sessions_completed"] == 2
        assert pomodoro_info["adhd_assist_multiplier"] >= 1.0
    
    def test_delete_task(self):
        """タスク"""
        uid = "test_user_007"
        
        # タスク
        task_data = {
            "task_type": "one_shot",
            "title": "?",
            "description": "こ",
            "difficulty": 1,
            "priority": "low",
            "estimated_duration": 15
        }
        
        create_response = client.post(f"/tasks/{uid}/create", json=task_data)
        assert create_response.status_code == 200
        created_task = create_response.json()
        task_id = created_task["task_id"]
        
        # タスク
        response = client.delete(f"/tasks/{uid}/{task_id}")
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["success"] is True
        assert result["task_id"] == task_id
        
        # ?
        get_response = client.get(f"/tasks/{uid}/{task_id}")
        assert get_response.status_code == 404


class TestDailyTaskLimit:
    """?16タスク"""
    
    def test_daily_task_limit_enforcement(self):
        """?"""
        uid = "test_user_limit"
        
        # 16?
        for i in range(16):
            task_data = {
                "task_type": "routine",
                "title": f"タスク{i+1}",
                "description": f"?{i+1}",
                "difficulty": 1,
                "priority": "low",
                "estimated_duration": 15
            }
            
            response = client.post(f"/tasks/{uid}/create", json=task_data)
            assert response.status_code == 200
        
        # 17?
        task_data = {
            "task_type": "routine",
            "title": "?",
            "description": "こ",
            "difficulty": 1,
            "priority": "low",
            "estimated_duration": 15
        }
        
        response = client.post(f"/tasks/{uid}/create", json=task_data)
        
        assert response.status_code == 429
        assert "Daily task limit exceeded" in response.json()["detail"]
    
    def test_daily_summary_with_limit_info(self):
        """?"""
        uid = "test_user_summary"
        
        # 10?
        for i in range(10):
            task_data = {
                "task_type": "routine",
                "title": f"?{i+1}",
                "description": f"?{i+1}",
                "difficulty": 1,
                "priority": "medium",
                "estimated_duration": 20
            }
            
            response = client.post(f"/tasks/{uid}/create", json=task_data)
            assert response.status_code == 200
        
        # ?
        response = client.get(f"/tasks/{uid}/daily-summary")
        
        assert response.status_code == 200
        summary = response.json()
        
        assert summary["total_tasks"] == 10
        assert summary["daily_limit"] == 16
        assert summary["remaining_slots"] == 6
        assert summary["limit_reached"] is False
        
        # ?
        today = datetime.utcnow().date().isoformat()
        assert summary["date"] == today


class TestTaskStatisticsAndAnalytics:
    """タスク"""
    
    def test_task_statistics(self):
        """タスク"""
        uid = "test_user_stats"
        
        # ?
        task_configs = [
            {"type": "routine", "difficulty": 1, "complete": True, "mood": 4},
            {"type": "routine", "difficulty": 2, "complete": True, "mood": 3},
            {"type": "one_shot", "difficulty": 3, "complete": True, "mood": 5},
            {"type": "skill_up", "difficulty": 2, "complete": False, "mood": None},
            {"type": "social", "difficulty": 4, "complete": True, "mood": 4}
        ]
        
        for i, config in enumerate(task_configs):
            # タスク
            task_data = {
                "task_type": config["type"],
                "title": f"?{i+1}",
                "description": f"{config['type']}タスク",
                "difficulty": config["difficulty"],
                "priority": "medium",
                "estimated_duration": 30
            }
            
            create_response = client.post(f"/tasks/{uid}/create", json=task_data)
            assert create_response.status_code == 200
            task = create_response.json()
            task_id = task["task_id"]
            
            if config["complete"]:
                # タスク
                start_response = client.post(f"/tasks/{uid}/{task_id}/start", json={})
                assert start_response.status_code == 200
                
                # タスク
                complete_data = {
                    "mood_score": config["mood"],
                    "actual_duration": 25,
                    "notes": "?",
                    "pomodoro_sessions_completed": 1
                }
                
                complete_response = client.post(f"/tasks/{uid}/{task_id}/complete", json=complete_data)
                assert complete_response.status_code == 200
        
        # ?
        response = client.get(f"/tasks/{uid}/statistics?days=30")
        
        assert response.status_code == 200
        stats = response.json()
        
        assert stats["total_tasks"] == 5
        assert stats["completed_tasks"] == 4
        assert stats["in_progress_tasks"] == 0
        assert stats["pending_tasks"] == 1
        assert stats["completion_rate"] == 0.8  # 4/5
        assert stats["total_xp_earned"] > 0
        assert stats["average_xp_per_task"] > 0
        
        # タスク
        type_stats = stats["task_type_statistics"]
        assert type_stats["routine"]["total"] == 2
        assert type_stats["routine"]["completed"] == 2
        assert type_stats["one_shot"]["total"] == 1
        assert type_stats["one_shot"]["completed"] == 1
        assert type_stats["skill_up"]["total"] == 1
        assert type_stats["skill_up"]["completed"] == 0
        assert type_stats["social"]["total"] == 1
        assert type_stats["social"]["completed"] == 1


class TestXPPreviewAndRecommendations:
    """XPプレビュー"""
    
    def test_xp_preview(self):
        """XPプレビュー"""
        preview_data = {
            "task_type": "skill_up",
            "difficulty": 3,
            "mood_score": 4,
            "adhd_support_level": "enhanced"
        }
        
        response = client.post("/tasks/xp-preview", json=preview_data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["task_type"] == "skill_up"
        assert result["difficulty"] == 3
        assert result["mood_score"] == 4
        assert result["adhd_support_level"] == "enhanced"
        assert result["estimated_xp"] > 0
    
    def test_task_recommendations(self):
        """タスク"""
        recommendation_data = {
            "primary_goal": "プレビュー",
            "user_experience_level": 3,
            "task_complexity": "moderate",
            "user_confidence": 4
        }
        
        response = client.post("/tasks/recommendations", json=recommendation_data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert result["primary_goal"] == "プレビュー"
        assert result["recommended_task_type"] in ["routine", "one_shot", "skill_up", "social"]
        assert result["recommended_difficulty"] in [1, 2, 3, 4, 5]
        assert isinstance(result["recommended_crystals"], list)
        assert "reasoning" in result
        assert "task_type_reason" in result["reasoning"]
        assert "difficulty_reason" in result["reasoning"]


class TestPomodoroIntegration:
    """Pomodoro?"""
    
    def test_pomodoro_session_lifecycle(self):
        """Pomodoro?"""
        uid = "test_user_pomodoro"
        
        # タスク
        task_data = {
            "task_type": "skill_up",
            "title": "?",
            "description": "Pomodoro?",
            "difficulty": 3,
            "priority": "high",
            "estimated_duration": 50,
            "pomodoro_sessions_planned": 2
        }
        
        create_response = client.post(f"/tasks/{uid}/create", json=task_data)
        assert create_response.status_code == 200
        task = create_response.json()
        task_id = task["task_id"]
        
        # タスク
        start_response = client.post(f"/tasks/{uid}/{task_id}/start", json={})
        assert start_response.status_code == 200
        
        # Pomodoro?
        pomodoro_start_data = {
            "duration": 25,
            "focus_music_enabled": True
        }
        
        pomodoro_response = client.post(
            f"/tasks/{uid}/{task_id}/pomodoro/start", 
            json=pomodoro_start_data
        )
        
        assert pomodoro_response.status_code == 200
        session = pomodoro_response.json()
        
        assert session["uid"] == uid
        assert session["task_id"] == task_id
        assert session["planned_duration"] == 25
        assert session["focus_music_enabled"] is True
        assert session["status"] == "active"
        
        session_id = session["session_id"]
        
        # Pomodoro?
        pomodoro_complete_data = {
            "actual_duration": 23,
            "notes": "?"
        }
        
        complete_response = client.post(
            f"/tasks/{uid}/{task_id}/pomodoro/{session_id}/complete",
            json=pomodoro_complete_data
        )
        
        assert complete_response.status_code == 200
        result = complete_response.json()
        
        assert result["success"] is True
        assert result["session"]["status"] == "completed"
        assert result["session"]["actual_duration"] == 23
        assert result["session"]["notes"] == "?"
        
        # ADHD支援
        assert "adhd_support_metrics" in result
        metrics = result["adhd_support_metrics"]
        assert "usage_frequency_score" in metrics
        assert "break_compliance_rate" in metrics
        assert "adhd_assist_multiplier" in metrics
    
    def test_pomodoro_statistics(self):
        """Pomodoro?"""
        uid = "test_user_pomodoro_stats"
        
        response = client.get(f"/tasks/{uid}/pomodoro/statistics?days=7")
        
        assert response.status_code == 200
        stats = response.json()
        
        assert "period_days" in stats
        assert "total_sessions" in stats
        assert "completed_sessions" in stats
        assert "total_focus_time" in stats
        assert "average_session_duration" in stats
        assert "break_compliance_rate" in stats
        assert "usage_frequency_score" in stats
        assert "adhd_assist_multiplier" in stats
        assert "interruption_rate" in stats


class TestErrorHandling:
    """エラー"""
    
    def test_task_not_found(self):
        """?"""
        uid = "test_user_error"
        non_existent_task_id = "non_existent_task_123"
        
        response = client.get(f"/tasks/{uid}/{non_existent_task_id}")
        
        assert response.status_code == 404
        assert "Task not found" in response.json()["detail"]
    
    def test_invalid_task_data(self):
        """無"""
        uid = "test_user_invalid"
        
        # 無
        invalid_task_data = {
            "task_type": "routine",
            "title": "無",
            "description": "無",
            "difficulty": 10,  # 無1-5の
            "priority": "medium",
            "estimated_duration": 30
        }
        
        response = client.post(f"/tasks/{uid}/create", json=invalid_task_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_complete_non_in_progress_task(self):
        """?"""
        uid = "test_user_complete_error"
        
        # タスク
        task_data = {
            "task_type": "routine",
            "title": "?",
            "description": "?",
            "difficulty": 2,
            "priority": "medium",
            "estimated_duration": 30
        }
        
        create_response = client.post(f"/tasks/{uid}/create", json=task_data)
        assert create_response.status_code == 200
        task = create_response.json()
        task_id = task["task_id"]
        
        # ?
        complete_data = {
            "mood_score": 3,
            "actual_duration": 25,
            "notes": "?",
            "pomodoro_sessions_completed": 0
        }
        
        response = client.post(f"/tasks/{uid}/{task_id}/complete", json=complete_data)
        
        assert response.status_code == 400
        assert "Task is not in progress" in response.json()["detail"]


def test_health_check():
    """ヘルパー"""
    response = client.get("/health")
    
    assert response.status_code == 200
    health = response.json()
    
    assert health["status"] == "healthy"
    assert health["service"] == "task-management"
    assert health["version"] == "1.0.0"
    assert "timestamp" in health


if __name__ == "__main__":
    # 基本
    print("タスクAPI?...")
    
    # ?
    test_uid = "integration_test_user"
    
    # 1. タスク
    print("1. タスク")
    task_data = {
        "task_type": "routine",
        "title": "?",
        "description": "API?",
        "difficulty": 2,
        "priority": "medium",
        "estimated_duration": 30
    }
    
    response = client.post(f"/tasks/{test_uid}/create", json=task_data)
    if response.status_code == 200:
        print("? タスク")
        task = response.json()
        task_id = task["task_id"]
    else:
        print(f"? タスク: {response.status_code}")
        exit(1)
    
    # 2. タスク
    print("2. タスク")
    response = client.get(f"/tasks/{test_uid}")
    if response.status_code == 200:
        tasks = response.json()
        print(f"? タスク: {len(tasks)}?")
    else:
        print(f"? タスク: {response.status_code}")
    
    # 3. タスク
    print("3. タスク")
    response = client.post(f"/tasks/{test_uid}/{task_id}/start", json={})
    if response.status_code == 200:
        print("? タスク")
    else:
        print(f"? タスク: {response.status_code}")
    
    # 4. タスク
    print("4. タスク")
    complete_data = {
        "mood_score": 4,
        "actual_duration": 28,
        "notes": "?",
        "pomodoro_sessions_completed": 1
    }
    
    response = client.post(f"/tasks/{test_uid}/{task_id}/complete", json=complete_data)
    if response.status_code == 200:
        result = response.json()
        print(f"? タスク: XP? {result['xp_earned']}")
    else:
        print(f"? タスク: {response.status_code}")
    
    # 5. ?
    print("5. ?")
    response = client.get(f"/tasks/{test_uid}/daily-summary")
    if response.status_code == 200:
        summary = response.json()
        print(f"? ?: {summary['total_tasks']}タスク, ?{summary['remaining_slots']}ストーリー")
    else:
        print(f"? ?: {response.status_code}")
    
    # 6. ヘルパー
    print("6. ヘルパー")
    response = client.get("/health")
    if response.status_code == 200:
        print("? ヘルパー")
    else:
        print(f"? ヘルパー: {response.status_code}")
    
    print("\n?")