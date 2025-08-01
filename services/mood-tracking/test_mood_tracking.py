"""
Mood Tracking Service Tests

気分

Requirements: 5.4
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from datetime import datetime, date, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.mood_tracking.main import app
from shared.interfaces.mood_system import MoodLevel, MoodTrigger


class TestMoodTrackingService:
    """気分"""
    
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
        assert data["service"] == "mood-tracking"
    
    def test_log_basic_mood(self):
        """基本"""
        mood_request = {
            "overall_mood": 4,
            "notes": "?"
        }
        
        response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["uid"] == self.test_uid
        assert data["overall_mood"] == 4
        assert data["notes"] == "?"
        assert data["date"] == date.today().isoformat()
        
        # 気分4 -> 1.1?
        expected_coefficient = 0.8 + (4 - 1) * 0.1  # 1.1
        assert abs(data["mood_coefficient"] - expected_coefficient) < 0.01
        
        # ?
        assert data["weighted_mood_coefficient"] > 0.8
        assert data["weighted_mood_coefficient"] < 1.2
        
        return data["entry_id"]
    
    def test_log_detailed_mood(self):
        """?"""
        mood_request = {
            "overall_mood": 3,
            "energy_level": 4,
            "motivation_level": 5,
            "focus_level": 3,
            "anxiety_level": 2,  # ?
            "stress_level": 1,   # ?
            "social_mood": 4,
            "physical_condition": 3,
            "mood_triggers": ["sleep", "exercise", "work_study"],
            "notes": "?",
            "sleep_hours": 7.5,
            "exercise_minutes": 45
        }
        
        response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["overall_mood"] == 3
        assert data["energy_level"] == 4
        assert data["motivation_level"] == 5
        assert data["anxiety_level"] == 2
        assert data["stress_level"] == 1
        assert data["sleep_hours"] == 7.5
        assert data["exercise_minutes"] == 45
        assert len(data["mood_triggers"]) == 3
        assert "sleep" in data["mood_triggers"]
        
        # カスタム
        category_scores = data["category_scores"]
        assert category_scores["overall"] == 3
        assert category_scores["energy"] == 4
        assert category_scores["anxiety"] == 4  # 6-2=4?
        assert category_scores["stress"] == 5   # 6-1=5?
        
        return data["entry_id"]
    
    def test_log_mood_with_date(self):
        """?"""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        mood_request = {
            "overall_mood": 2,
            "notes": "?",
            "log_date": yesterday
        }
        
        response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["date"] == yesterday
        assert data["overall_mood"] == 2
        
        # 気分2 -> 0.9?
        expected_coefficient = 0.8 + (2 - 1) * 0.1  # 0.9
        assert abs(data["mood_coefficient"] - expected_coefficient) < 0.01
    
    def test_get_today_mood(self):
        """?"""
        # ま
        self.test_log_basic_mood()
        
        # ?
        response = self.client.get(f"/mood/{self.test_uid}/today")
        assert response.status_code == 200
        
        data = response.json()
        assert data is not None
        assert data["uid"] == self.test_uid
        assert data["date"] == date.today().isoformat()
        assert data["overall_mood"] == 4
    
    def test_get_mood_by_date(self):
        """?"""
        # ?
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        mood_request = {
            "overall_mood": 3,
            "log_date": yesterday
        }
        
        log_response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
        assert log_response.status_code == 200
        
        # ?
        response = self.client.get(f"/mood/{self.test_uid}/date/{yesterday}")
        assert response.status_code == 200
        
        data = response.json()
        assert data is not None
        assert data["date"] == yesterday
        assert data["overall_mood"] == 3
    
    def test_get_recent_moods(self):
        """?"""
        # ?
        for i in range(5):
            log_date = (date.today() - timedelta(days=i)).isoformat()
            mood_request = {
                "overall_mood": 3 + (i % 3),  # 3, 4, 5, 3, 4の
                "log_date": log_date
            }
            
            response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
            assert response.status_code == 200
        
        # ?7?
        response = self.client.get(f"/mood/{self.test_uid}/recent?days=7")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5  # 5?5?
        
        # ?
        dates = [entry["date"] for entry in data]
        assert dates == sorted(dates, reverse=True)
    
    def test_get_current_mood_coefficient(self):
        """?"""
        # ?
        mood_request = {"overall_mood": 5}
        log_response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
        assert log_response.status_code == 200
        
        # ?
        response = self.client.get(f"/mood/{self.test_uid}/coefficient/current")
        assert response.status_code == 200
        
        data = response.json()
        assert data["uid"] == self.test_uid
        assert data["has_today_log"] is True
        assert data["overall_mood"] == 5
        
        # 気分5 -> 1.2?
        expected_coefficient = 0.8 + (5 - 1) * 0.1  # 1.2
        assert abs(data["mood_coefficient"] - expected_coefficient) < 0.01
        
        assert data["coefficient_range"]["min"] == 0.8
        assert data["coefficient_range"]["max"] == 1.2
    
    def test_get_mood_coefficient_by_date(self):
        """?"""
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        
        # ?
        mood_request = {
            "overall_mood": 1,  # ?
            "log_date": yesterday
        }
        log_response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
        assert log_response.status_code == 200
        
        # ?
        response = self.client.get(f"/mood/{self.test_uid}/coefficient/date/{yesterday}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["date"] == yesterday
        assert data["has_mood_log"] is True
        assert data["overall_mood"] == 1
        
        # 気分1 -> 0.8?
        expected_coefficient = 0.8 + (1 - 1) * 0.1  # 0.8
        assert abs(data["mood_coefficient"] - expected_coefficient) < 0.01
    
    def test_get_mood_coefficient_no_log(self):
        """気分"""
        # ?
        future_date = (date.today() + timedelta(days=1)).isoformat()
        
        response = self.client.get(f"/mood/{self.test_uid}/coefficient/date/{future_date}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["has_mood_log"] is False
        assert data["overall_mood"] is None
        assert data["mood_coefficient"] == 1.0  # デフォルト
        assert data["is_default"] is True
    
    def test_mood_trend_analysis(self):
        """気分"""
        # 30?
        for i in range(30):
            log_date = (date.today() - timedelta(days=29-i)).isoformat()
            # ?1か5?
            mood_value = min(5, max(1, int(1 + (i / 29) * 4)))
            
            mood_request = {
                "overall_mood": mood_value,
                "energy_level": mood_value,
                "motivation_level": mood_value,
                "log_date": log_date
            }
            
            response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
            assert response.status_code == 200
        
        # ?
        response = self.client.get(f"/mood/{self.test_uid}/trend?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert data["period_days"] == 30
        assert data["avg_overall_mood"] > 2.5  # ?
        assert data["overall_trend"] > 0  # ?
        assert data["best_day"] is not None
        assert data["worst_day"] is not None
        assert 0.8 <= data["avg_mood_coefficient"] <= 1.2
    
    def test_mood_insights(self):
        """気分"""
        # ?
        for i in range(14):
            log_date = (date.today() - timedelta(days=i)).isoformat()
            mood_request = {
                "overall_mood": 3 + (i % 3),
                "mood_triggers": ["sleep", "exercise"] if i % 2 == 0 else ["work_study", "stress_event"],
                "log_date": log_date
            }
            
            response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
            assert response.status_code == 200
        
        # ?
        response = self.client.get(f"/mood/{self.test_uid}/insights")
        assert response.status_code == 200
        
        data = response.json()
        insights = data["insights"]
        
        assert "latest_mood" in insights
        assert "current_vs_average" in insights
        assert "trend_direction" in insights
        assert "most_common_triggers" in insights
        assert "mood_coefficient" in insights
        assert insights["data_points"] == 14
    
    def test_mood_statistics(self):
        """気分"""
        # ?
        mood_levels = [1, 2, 3, 4, 5, 3, 4, 2, 5, 1]
        
        for i, mood in enumerate(mood_levels):
            log_date = (date.today() - timedelta(days=i)).isoformat()
            mood_request = {
                "overall_mood": mood,
                "sleep_hours": 7.0 + (i % 3),
                "exercise_minutes": 30 + (i * 10),
                "mood_triggers": ["sleep"] if i % 2 == 0 else ["exercise"],
                "log_date": log_date
            }
            
            response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
            assert response.status_code == 200
        
        # ?
        response = self.client.get(f"/mood/{self.test_uid}/statistics?days=30")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_entries"] == 10
        assert data["logging_rate"] == 10 / 30
        
        # 気分
        mood_distribution = data["mood_distribution"]
        assert mood_distribution["very_low"] == 2  # 1が2?
        assert mood_distribution["low"] == 2       # 2が2?
        assert mood_distribution["neutral"] == 2   # 3が2?
        assert mood_distribution["high"] == 2      # 4が2?
        assert mood_distribution["very_high"] == 2 # 5が2?
        
        # ?
        assert "trigger_analysis" in data
        assert "sleep" in data["trigger_analysis"]
        assert "exercise" in data["trigger_analysis"]
        
        # 気分
        coeff_stats = data["mood_coefficient_stats"]
        assert 0.8 <= coeff_stats["minimum"] <= 1.2
        assert 0.8 <= coeff_stats["maximum"] <= 1.2
        assert 0.8 <= coeff_stats["average"] <= 1.2
    
    def test_reminder_settings(self):
        """リスト"""
        # リスト
        reminder_request = {"enabled": True}
        response = self.client.post(f"/mood/{self.test_uid}/reminder", json=reminder_request)
        assert response.status_code == 200
        
        data = response.json()
        assert data["reminder_enabled"] is True
        
        # リスト
        response = self.client.get(f"/mood/{self.test_uid}/reminder")
        assert response.status_code == 200
        
        data = response.json()
        assert data["reminder_enabled"] is True
        assert data["needs_reminder"] is True  # ?True
        
        # ?
        mood_request = {"overall_mood": 3}
        log_response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
        assert log_response.status_code == 200
        
        response = self.client.get(f"/mood/{self.test_uid}/reminder")
        assert response.status_code == 200
        
        data = response.json()
        assert data["needs_reminder"] is False  # ?False
    
    def test_export_mood_data_json(self):
        """気分JSONエラー"""
        # ?
        for i in range(5):
            log_date = (date.today() - timedelta(days=i)).isoformat()
            mood_request = {
                "overall_mood": 3 + (i % 3),
                "notes": f"Day {i} mood",
                "log_date": log_date
            }
            
            response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
            assert response.status_code == 200
        
        # デフォルト
        start_date = (date.today() - timedelta(days=4)).isoformat()
        end_date = date.today().isoformat()
        
        response = self.client.get(
            f"/mood/{self.test_uid}/export?start_date={start_date}&end_date={end_date}&format=json"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["uid"] == self.test_uid
        assert data["total_entries"] == 5
        assert len(data["data"]) == 5
        
        # デフォルト
        first_entry = data["data"][0]
        assert "date" in first_entry
        assert "overall_mood" in first_entry
        assert "mood_coefficient" in first_entry
    
    def test_invalid_mood_values(self):
        """無"""
        # ?
        invalid_requests = [
            {"overall_mood": 0},   # ?
            {"overall_mood": 6},   # ?
            {"overall_mood": 3, "energy_level": 0},
            {"overall_mood": 3, "sleep_hours": -1}
        ]
        
        for invalid_request in invalid_requests:
            response = self.client.post(f"/mood/{self.test_uid}/log", json=invalid_request)
            assert response.status_code == 422  # Validation error
    
    def test_invalid_date_format(self):
        """無"""
        # 無
        response = self.client.get(f"/mood/{self.test_uid}/date/invalid-date")
        assert response.status_code == 400
        assert "Invalid date format" in response.json()["detail"]
    
    def test_system_statistics(self):
        """システム"""
        # い
        users = ["user1", "user2", "user3"]
        for user in users:
            mood_request = {"overall_mood": 3}
            response = self.client.post(f"/mood/{user}/log", json=mood_request)
            assert response.status_code == 200
        
        # システム
        response = self.client.get("/mood/system/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_users"] >= 3
        assert data["total_mood_entries"] >= 3
        assert data["today_logged_users"] >= 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])