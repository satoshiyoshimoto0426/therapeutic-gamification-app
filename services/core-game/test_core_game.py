"""
コアAPIの
Core Game Engine API integration tests
Requirements: 8.1, 8.2
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime
import json

# ?APIを
from main import app

# ?
client = TestClient(app)


class TestCoreGameAPI:
    """コアAPIの"""
    
    def test_health_check(self):
        """ヘルパー"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "core-game-engine"
        assert data["version"] == "1.0.0"
        assert "timestamp" in data
        assert "active_users" in data
        
        print("? Health check endpoint working")
    
    def test_add_xp_basic(self):
        """基本XP?"""
        request_data = {
            "uid": "test_user_001",
            "xp_amount": 100,
            "source": "test_task",
            "task_id": "task_123"
        }
        
        response = client.post("/xp/add", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["uid"] == "test_user_001"
        assert data["xp_added"] == 100
        assert data["total_xp"] == 100
        assert data["old_level"] == 1
        assert data["new_level"] >= 1
        assert isinstance(data["level_up"], bool)
        assert isinstance(data["rewards"], list)
        assert "yu_growth" in data
        
        print(f"? XP added: {data['xp_added']} XP, Level {data['old_level']}?{data['new_level']}")
    
    def test_add_xp_with_level_up(self):
        """レベルXP?"""
        request_data = {
            "uid": "test_user_002",
            "xp_amount": 500,  # ?XPで
            "source": "major_achievement"
        }
        
        response = client.post("/xp/add", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["level_up"] is True
        assert data["new_level"] > data["old_level"]
        assert len(data["rewards"]) > 0
        
        print(f"? Level up occurred: Level {data['old_level']}?{data['new_level']}")
        print(f"  Rewards: {data['rewards']}")
    
    def test_add_xp_with_resonance(self):
        """共有XP?"""
        uid = "test_user_003"
        
        # ?XPを
        request_data = {
            "uid": uid,
            "xp_amount": 2000,
            "source": "level_boost"
        }
        
        response = client.post("/xp/add", json=request_data)
        assert response.status_code == 200
        
        # ?XPを
        request_data = {
            "uid": uid,
            "xp_amount": 100,
            "source": "resonance_trigger"
        }
        
        response = client.post("/xp/add", json=request_data)
        data = response.json()
        
        assert response.status_code == 200
        
        # 共有
        if data.get("resonance_event"):
            resonance = data["resonance_event"]
            assert "event_id" in resonance
            assert "type" in resonance
            assert "intensity" in resonance
            assert "bonus_xp" in resonance
            assert resonance["bonus_xp"] > 0
            assert "therapeutic_message" in resonance
            
            print(f"? Resonance event triggered: {resonance['type']} ({resonance['intensity']})")
            print(f"  Bonus XP: {resonance['bonus_xp']}")
            print(f"  Message: {resonance['therapeutic_message']}")
        else:
            print("? No resonance event (conditions not met or cooldown active)")
    
    def test_level_progress(self):
        """レベル"""
        uid = "test_user_004"
        
        # まXPを
        add_xp_data = {
            "uid": uid,
            "xp_amount": 300,
            "source": "progress_test"
        }
        client.post("/xp/add", json=add_xp_data)
        
        # レベル
        progress_data = {"uid": uid}
        response = client.post("/level/progress", json=progress_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "data" in data
        
        progress = data["data"]
        assert progress["uid"] == uid
        assert "player" in progress
        assert "yu" in progress
        assert "level_difference" in progress
        
        player = progress["player"]
        assert player["current_level"] >= 1
        assert player["total_xp"] >= 300
        assert player["xp_for_current_level"] <= player["total_xp"]
        assert player["xp_for_next_level"] > player["total_xp"]
        assert 0 <= player["progress_percentage"] <= 100
        
        print(f"? Level progress retrieved:")
        print(f"  Player: Level {player['current_level']} ({player['progress_percentage']:.1f}%)")
        print(f"  Yu: Level {progress['yu']['current_level']}")
        print(f"  Level difference: {progress['level_difference']}")
    
    def test_resonance_check(self):
        """共有"""
        uid = "test_user_005"
        
        # レベルXPを
        add_xp_data = {
            "uid": uid,
            "xp_amount": 1000,
            "source": "resonance_setup"
        }
        client.post("/xp/add", json=add_xp_data)
        
        # 共有
        check_data = {"uid": uid, "force_check": False}
        response = client.post("/resonance/check", json=check_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        resonance_data = data["data"]
        
        assert resonance_data["uid"] == uid
        assert "can_resonate" in resonance_data
        assert "player_level" in resonance_data
        assert "yu_level" in resonance_data
        assert "level_difference" in resonance_data
        assert "statistics" in resonance_data
        assert "simulation" in resonance_data
        
        print(f"? Resonance check completed:")
        print(f"  Can resonate: {resonance_data['can_resonate']}")
        print(f"  Level difference: {resonance_data['level_difference']}")
        print(f"  Total events: {resonance_data['statistics']['total_events']}")
    
    def test_system_status(self):
        """システム"""
        uid = "test_user_006"
        
        # システムXPを
        add_xp_data = {
            "uid": uid,
            "xp_amount": 200,
            "source": "status_test"
        }
        client.post("/xp/add", json=add_xp_data)
        
        # システム
        status_data = {"uid": uid}
        response = client.post("/system/status", json=status_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        status = data["data"]
        
        assert status["uid"] == uid
        assert status["player_level"] >= 1
        assert status["player_xp"] >= 200
        assert status["yu_level"] >= 1
        assert status["system_health"] == "healthy"
        assert isinstance(status["resonance_available"], bool)
        assert isinstance(status["total_resonance_events"], int)
        
        print(f"? System status retrieved:")
        print(f"  Player: Level {status['player_level']} ({status['player_xp']} XP)")
        print(f"  Yu: Level {status['yu_level']}")
        print(f"  Resonance available: {status['resonance_available']}")
    
    def test_xp_calculation_preview(self):
        """XP計算"""
        request_data = {
            "task_difficulty": 3,
            "mood_score": 4,
            "adhd_assist_usage": "moderate"  # 文字
        }
        
        response = client.post("/xp/calculate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        calc_data = data["data"]
        
        assert calc_data["base_xp"] == 15  # TaskDifficulty.MEDIUM のXP
        assert calc_data["mood_coefficient"] == 1.1  # 0.8 + (4-1) * 0.1
        assert calc_data["final_xp"] > 0
        assert calc_data["level_up"] is False  # プレビューFalse
        
        print(f"? XP calculation preview:")
        print(f"  Base XP: {calc_data['base_xp']}")
        print(f"  Mood coefficient: {calc_data['mood_coefficient']}")
        print(f"  Final XP: {calc_data['final_xp']}")
    
    def test_error_handling(self):
        """エラー"""
        # 無
        invalid_data = {
            "uid": "",  # ?UID
            "xp_amount": -100,  # ?XP
            "source": "error_test"
        }
        
        response = client.post("/xp/add", json=invalid_data)
        
        assert response.status_code == 422  # Validation Error
        data = response.json()
        
        # FastAPIの
        if "detail" in data:
            # FastAPIの
            assert "detail" in data
            print("? Error handling working correctly (FastAPI format)")
        else:
            # カスタム
            assert data["success"] is False
            assert "error_code" in data
            assert "message" in data
            print("? Error handling working correctly (Custom format)")
    
    def test_resonance_trigger_manual(self):
        """?"""
        uid = "test_user_007"
        
        # レベルXPを
        add_xp_data = {
            "uid": uid,
            "xp_amount": 3000,
            "source": "manual_resonance_setup"
        }
        client.post("/xp/add", json=add_xp_data)
        
        # ?
        trigger_data = {
            "uid": uid,
            "resonance_type": "level_sync"
        }
        
        response = client.post("/resonance/trigger", json=trigger_data)
        
        # 共有400エラー
        if response.status_code == 400:
            data = response.json()
            assert data["success"] is False
            assert data["error_code"] == "RESONANCE_CONDITIONS_NOT_MET"
            print("? Resonance conditions not met (expected)")
        else:
            # 共有
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            resonance_data = data["data"]
            
            assert "resonance_event" in resonance_data
            assert "xp_result" in resonance_data
            
            event = resonance_data["resonance_event"]
            assert event["type"] == "level_sync"
            assert event["bonus_xp"] > 0
            
            print(f"? Manual resonance triggered: {event['type']}")
            print(f"  Bonus XP: {event['bonus_xp']}")


class TestAPIIntegration:
    """API?"""
    
    def test_complete_user_journey(self):
        """?"""
        uid = "integration_test_user"
        
        print(f"=== Complete User Journey Test: {uid} ===")
        
        # 1. ?
        status_response = client.post("/system/status", json={"uid": uid})
        initial_status = status_response.json()["data"]
        
        print(f"1. Initial state: Player L{initial_status['player_level']}, Yu L{initial_status['yu_level']}")
        
        # 2. ?XPを
        xp_additions = [100, 200, 300, 500, 800]
        
        for i, xp in enumerate(xp_additions, 1):
            add_response = client.post("/xp/add", json={
                "uid": uid,
                "xp_amount": xp,
                "source": f"journey_step_{i}"
            })
            
            result = add_response.json()
            print(f"2.{i}. Added {xp} XP: Level {result['old_level']}?{result['new_level']}")
            
            if result.get("resonance_event"):
                resonance = result["resonance_event"]
                print(f"     Resonance: {resonance['type']} (+{resonance['bonus_xp']} XP)")
        
        # 3. ?
        final_status_response = client.post("/system/status", json={"uid": uid})
        final_status = final_status_response.json()["data"]
        
        print(f"3. Final state: Player L{final_status['player_level']}, Yu L{final_status['yu_level']}")
        print(f"   Total resonance events: {final_status['total_resonance_events']}")
        
        # 4. レベル
        progress_response = client.post("/level/progress", json={"uid": uid})
        progress = progress_response.json()["data"]
        
        print(f"4. Progress: {progress['player']['progress_percentage']:.1f}% to next level")
        print(f"   XP needed: {progress['player']['xp_needed_for_next']}")
        
        # 5. 共有
        resonance_response = client.post("/resonance/check", json={"uid": uid})
        resonance_check = resonance_response.json()["data"]
        
        print(f"5. Resonance available: {resonance_check['can_resonate']}")
        
        print("=== User Journey Test Completed ===")
        
        # アプリ
        assert final_status["player_level"] > initial_status["player_level"]
        # 共有XPがXPの
        assert final_status["player_xp"] >= sum(xp_additions)
        print(f"   Expected minimum XP: {sum(xp_additions)}, Actual XP: {final_status['player_xp']}")


def run_all_tests():
    """?"""
    print("=== Running Core Game API Tests ===")
    
    # 基本API?
    api_test = TestCoreGameAPI()
    api_test.test_health_check()
    api_test.test_add_xp_basic()
    api_test.test_add_xp_with_level_up()
    api_test.test_add_xp_with_resonance()
    api_test.test_level_progress()
    api_test.test_resonance_check()
    api_test.test_system_status()
    api_test.test_xp_calculation_preview()
    api_test.test_error_handling()
    api_test.test_resonance_trigger_manual()
    print("? Basic API tests passed\n")
    
    # ?
    integration_test = TestAPIIntegration()
    integration_test.test_complete_user_journey()
    print("? Integration tests passed\n")
    
    print("=== All Core Game API Tests Passed! ===")


if __name__ == "__main__":
    run_all_tests()