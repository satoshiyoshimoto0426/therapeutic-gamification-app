"""
Pomodoro?APIエラー

Requirements: 3.2, 5.3
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timedelta

# プレビュー
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi.testclient import TestClient
from main import app
from shared.interfaces.task_system import Task, TaskType, TaskDifficulty, TaskStatus


def test_pomodoro_api_endpoints():
    """Pomodoro API エラー"""
    print("=== Pomodoro API エラー ===")
    
    client = TestClient(app)
    uid = "test_user_api"
    
    try:
        # 1. タスク
        print("1. ?...")
        task_data = {
            "task_type": "routine",
            "title": "Pomodoro?",
            "description": "API?",
            "difficulty": 3,
            "priority": "medium",
            "estimated_duration": 25,
            "adhd_support_level": "basic",
            "pomodoro_sessions_planned": 2,
            "break_reminders_enabled": True,
            "focus_music_enabled": True
        }
        
        response = client.post(f"/tasks/{uid}/create", json=task_data)
        assert response.status_code == 200
        task = response.json()
        task_id = task["task_id"]
        print(f"   ? タスク: {task_id}")
        
        # 2. Pomodoro?
        print("2. Pomodoro?...")
        pomodoro_data = {
            "duration": 25,
            "focus_music_enabled": True
        }
        
        response = client.post(f"/tasks/{uid}/{task_id}/pomodoro/start", json=pomodoro_data)
        assert response.status_code == 200
        session = response.json()
        session_id = session["session_id"]
        assert session["status"] == "active"
        assert session["planned_duration"] == 25
        assert session["focus_music_enabled"] is True
        print(f"   ? Pomodoro?: {session_id}")
        
        # 3. Pomodoro?
        print("3. Pomodoro?...")
        complete_data = {
            "actual_duration": 23,
            "notes": "API?"
        }
        
        response = client.post(f"/tasks/{uid}/pomodoro/{session_id}/complete", json=complete_data)
        assert response.status_code == 200
        result = response.json()
        assert result["success"] is True
        assert result["session"]["status"] == "completed"
        assert result["session"]["actual_duration"] == 23
        assert "adhd_assist_multiplier" in result
        print(f"   ? Pomodoro?")
        print(f"   ? ADHD支援: {result['adhd_assist_multiplier']}")
        
        # 4. ?
        print("4. ?...")
        response = client.get(f"/tasks/{uid}/work-time-check")
        assert response.status_code == 200
        work_check = response.json()
        assert "continuous_minutes" in work_check
        assert "needs_break" in work_check
        print(f"   ? ?: {work_check['continuous_minutes']}?")
        
        # 5. ADHD支援
        print("5. ADHD支援...")
        response = client.get(f"/tasks/{uid}/adhd-assist-multiplier")
        assert response.status_code == 200
        adhd_info = response.json()
        assert "adhd_assist_multiplier" in adhd_info
        assert 1.0 <= adhd_info["adhd_assist_multiplier"] <= 1.3
        print(f"   ? ADHD支援: {adhd_info['adhd_assist_multiplier']}")
        
        # 6. Pomodoro?
        print("6. Pomodoro?...")
        response = client.get(f"/tasks/{uid}/pomodoro/statistics?days=30")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_sessions"] >= 1
        assert stats["completed_sessions"] >= 1
        assert "adhd_assist_multiplier" in stats
        print(f"   ? ?: {stats['total_sessions']}?")
        
        # 7. タスクPomodoro?
        print("7. タスクPomodoro?...")
        complete_task_data = {
            "mood_score": 4,
            "actual_duration": 23,
            "notes": "Pomodoro?",
            "pomodoro_sessions_completed": 1
        }
        
        response = client.post(f"/tasks/{uid}/{task_id}/complete", json=complete_task_data)
        assert response.status_code == 200
        task_result = response.json()
        assert task_result["success"] is True
        assert "pomodoro_integration" in task_result
        assert task_result["pomodoro_integration"]["sessions_completed"] == 1
        assert task_result["pomodoro_integration"]["adhd_assist_multiplier"] > 1.0
        print("   ? タスクPomodoro?")
        
        print("? Pomodoro API エラー")
        return True
        
    except Exception as e:
        print(f"? Pomodoro API エラー: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_break_management_api():
    """?APIの"""
    print("\n=== ?API? ===")
    
    client = TestClient(app)
    uid = "test_user_break_api"
    
    try:
        # タスク
        print("1. ?...")
        task_data = {
            "task_type": "one_shot",
            "title": "?",
            "difficulty": 2
        }
        
        response = client.post(f"/tasks/{uid}/create", json=task_data)
        task_id = response.json()["task_id"]
        
        # Pomodoro?
        print("2. Pomodoro?...")
        response = client.post(f"/tasks/{uid}/{task_id}/pomodoro/start", json={"duration": 25})
        session_id = response.json()["session_id"]
        
        # ?
        print("3. ?...")
        response = client.post(f"/tasks/{uid}/pomodoro/{session_id}/complete", json={})
        assert response.status_code == 200
        
        # ?
        print("4. ?...")
        response = client.post(f"/tasks/{uid}/pomodoro/{session_id}/break/start", json="short")
        assert response.status_code == 200
        break_session = response.json()
        assert break_session["status"] == "break"
        assert break_session["break_type"] == "short"
        assert break_session["break_duration"] == 5
        print("   ? ?")
        
        # ?
        print("5. ?...")
        response = client.post(f"/tasks/{uid}/pomodoro/{session_id}/break/complete")
        assert response.status_code == 200
        completed_break = response.json()
        assert completed_break["status"] == "completed"
        print("   ? ?")
        
        print("? ?API?")
        return True
        
    except Exception as e:
        print(f"? ?API?: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_continuous_work_monitoring_api():
    """?APIの3.2?"""
    print("\n=== ?API? ===")
    
    client = TestClient(app)
    uid = "test_user_continuous"
    
    try:
        # ?
        print("1. ?...")
        response = client.get(f"/tasks/{uid}/work-time-check")
        assert response.status_code == 200
        initial_check = response.json()
        assert initial_check["continuous_minutes"] == 0
        assert initial_check["needs_break"] is False
        print("   ? ?")
        
        # ?
        print("2. ?...")
        response = client.post(f"/tasks/{uid}/break-refusal")
        assert response.status_code == 200
        refusal_result = response.json()
        assert "error" in refusal_result
        print("   ? ?")
        
        print("? ?API?")
        return True
        
    except Exception as e:
        print(f"? ?API?: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """メイン"""
    print("? Pomodoro?API?")
    print("=" * 50)
    
    tests = [
        test_pomodoro_api_endpoints,
        test_break_management_api,
        test_continuous_work_monitoring_api
    ]
    
    results = []
    for test in tests:
        result = test()
        results.append(result)
    
    print("\n" + "=" * 50)
    print("? API?")
    print(f"成: {sum(results)}/{len(results)}")
    
    if all(results):
        print("? ?API?")
        print("\n実装APIエラー:")
        print("? POST /tasks/{uid}/{task_id}/pomodoro/start")
        print("? POST /tasks/{uid}/pomodoro/{session_id}/complete")
        print("? POST /tasks/{uid}/pomodoro/{session_id}/break/start")
        print("? POST /tasks/{uid}/pomodoro/{session_id}/break/complete")
        print("? POST /tasks/{uid}/pomodoro/{session_id}/cancel")
        print("? GET /tasks/{uid}/work-time-check")
        print("? POST /tasks/{uid}/break-refusal")
        print("? GET /tasks/{uid}/pomodoro/statistics")
        print("? GET /tasks/{uid}/adhd-assist-multiplier")
        return True
    else:
        print("? 一般API?")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)