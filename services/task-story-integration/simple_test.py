#!/usr/bin/env python3
"""
Task-Story Integration Service Simple Test

タスク-ストーリー
"""

import requests
import json
from datetime import datetime, timedelta

def test_service_health():
    """?"""
    try:
        response = requests.get("http://localhost:8007/health", timeout=5)
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_story_choice_to_task():
    """ストーリー"""
    
    choice_data = {
        "uid": "test_user_123",
        "choice_id": "choice_001",
        "choice_text": "?",
        "habit_tag": "skill_development",
        "task_template": {
            "task_type": "SKILL_UP",
            "title": "プレビュー",
            "description": "?",
            "difficulty": "MEDIUM",
            "estimated_duration": 60,
            "primary_crystal_attribute": "CURIOSITY"
        },
        "mandala_impact": {
            "attribute": "CURIOSITY",
            "impact_strength": 1.5
        },
        "therapeutic_weight": 1.3
    }
    
    try:
        response = requests.post(
            "http://localhost:8007/integration/story-choice-to-task",
            json=choice_data,
            timeout=10
        )
        
        print(f"Story Choice to Task: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 基本
        assert result["success"] is True
        assert result["integration_type"] == "story_to_task"
        assert "task_creation" in result
        assert result["task_creation"]["success"] is True
        
        return True
        
    except Exception as e:
        print(f"Story choice to task test failed: {e}")
        return False

def test_task_completion_sync():
    """タスク"""
    
    completion_data = {
        "uid": "test_user_123",
        "task_id": "task_001",
        "completion_data": {
            "mood_score": 4,
            "actual_duration": 45,
            "notes": "?",
            "pomodoro_used": True
        },
        "story_progression_trigger": True,
        "mandala_update_trigger": True,
        "xp_calculation_data": {
            "difficulty": "MEDIUM",
            "task_type": "SKILL_UP"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8007/integration/task-completion-sync",
            json=completion_data,
            timeout=10
        )
        
        print(f"Task Completion Sync: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 基本
        assert result["success"] is True
        assert result["integration_type"] == "task_to_story"
        assert "sync_result" in result
        assert len(result["sync_result"]["sync_results"]) >= 4
        
        return True
        
    except Exception as e:
        print(f"Task completion sync test failed: {e}")
        return False

def test_mandala_reflection():
    """Mandala?"""
    
    reflection_request = {
        "uid": "test_user_123",
        "story_choices": [
            {
                "choice_id": "choice_003",
                "choice_text": "?",
                "habit_tag": "persistence",
                "mandala_impact": {
                    "attribute": "SELF_DISCIPLINE",
                    "impact_strength": 1.2
                },
                "therapeutic_weight": 1.1
            },
            {
                "choice_id": "choice_004",
                "choice_text": "創",
                "habit_tag": "creativity",
                "mandala_impact": {
                    "attribute": "CREATIVITY",
                    "impact_strength": 1.4
                },
                "therapeutic_weight": 1.3
            }
        ],
        "chapter_context": "self_discipline",
        "therapeutic_focus": ["habit_formation", "creative_thinking"]
    }
    
    try:
        response = requests.post(
            "http://localhost:8007/integration/mandala-reflection",
            json=reflection_request,
            timeout=10
        )
        
        print(f"Mandala Reflection: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 基本
        assert result["success"] is True
        assert result["integration_type"] == "story_to_mandala"
        assert "mandala_update" in result
        
        return True
        
    except Exception as e:
        print(f"Mandala reflection test failed: {e}")
        return False

def test_real_time_hooks():
    """リスト"""
    
    # ま
    choice_data = {
        "uid": "test_user_123",
        "choice_id": "choice_005",
        "choice_text": "勇",
        "habit_tag": "courage_action",
        "task_template": {
            "task_type": "ONE_SHOT",
            "title": "勇",
            "description": "?",
            "difficulty": "MEDIUM"
        }
    }
    
    try:
        # ?
        requests.post(
            "http://localhost:8007/integration/story-choice-to-task",
            json=choice_data,
            timeout=10
        )
        
        # リスト
        hook_data = {
            "uid": "test_user_123",
            "chapter_context": "courage"
        }
        
        response = requests.post(
            "http://localhost:8007/integration/process-real-time-hooks",
            json=hook_data,
            timeout=10
        )
        
        print(f"Real-time Hooks: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 基本
        assert result["success"] is True
        assert result["processed_choices"] >= 1
        assert "tomorrow_tasks" in result
        
        return True
        
    except Exception as e:
        print(f"Real-time hooks test failed: {e}")
        return False

def test_integration_status():
    """?"""
    
    try:
        response = requests.get(
            "http://localhost:8007/integration/status/test_user_123",
            timeout=10
        )
        
        print(f"Integration Status: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 基本
        assert result["uid"] == "test_user_123"
        assert "story_choice_hooks" in result
        assert "task_story_syncs" in result
        assert "mandala_reflections" in result
        
        return True
        
    except Exception as e:
        print(f"Integration status test failed: {e}")
        return False

def test_integration_analytics():
    """?"""
    
    try:
        response = requests.get(
            "http://localhost:8007/integration/analytics",
            timeout=10
        )
        
        print(f"Integration Analytics: {response.status_code}")
        result = response.json()
        print(f"Response: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        # 基本
        assert "total_story_choice_hooks" in result
        assert "sync_success_rate" in result
        assert "integration_health" in result
        
        return True
        
    except Exception as e:
        print(f"Integration analytics test failed: {e}")
        return False

def main():
    """メイン"""
    
    print("=== Task-Story Integration Service Simple Test ===\n")
    
    tests = [
        ("Service Health Check", test_service_health),
        ("Story Choice to Task", test_story_choice_to_task),
        ("Task Completion Sync", test_task_completion_sync),
        ("Mandala Reflection", test_mandala_reflection),
        ("Real-time Hooks", test_real_time_hooks),
        ("Integration Status", test_integration_status),
        ("Integration Analytics", test_integration_analytics)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
            print(f"? {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append((test_name, False))
            print(f"? {test_name}: FAILED - {e}")
    
    # ?
    print(f"\n=== Test Results Summary ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "? PASSED" if result else "? FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("? All tests passed!")
        return True
    else:
        print("?  Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)