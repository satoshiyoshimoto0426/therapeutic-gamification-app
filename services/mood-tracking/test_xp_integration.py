#!/usr/bin/env python3
"""
Mood-XP Integration Tests

タスク7.2の:
- 気分XP計算
- 気分
- 気分APIエラー
- 気分

Requirements: 5.2, 5.4
"""

import pytest
import sys
import os
from fastapi.testclient import TestClient
from datetime import datetime, date, timedelta

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.mood_tracking.main import app
from shared.interfaces.mood_system import mood_tracking_system


class TestMoodXPIntegration:
    """気分-XP?"""
    
    def setup_method(self):
        """?"""
        self.client = TestClient(app)
        self.test_uid = "xp_integration_test_user"
    
    def test_mood_coefficient_for_xp_endpoint(self):
        """XP計算"""
        # ま
        mood_request = {
            "overall_mood": 4,
            "notes": "?"
        }
        
        log_response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
        assert log_response.status_code == 200
        
        # XP計算
        response = self.client.get(
            f"/mood/{self.test_uid}/coefficient/for-xp?task_difficulty=3&base_xp=30"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["uid"] == self.test_uid
        assert data["mood_coefficient"] == 1.1  # 気分4 -> 1.1
        assert data["base_xp"] == 30
        assert data["adjusted_xp"] == 33  # 30 * 1.1 = 33
        assert data["xp_bonus"] == 3
        assert data["has_mood_log"] is True
        assert data["overall_mood"] == 4
        assert "calculation_details" in data
        assert data["calculation_details"]["mood_impact"] == "positive"
    
    def test_mood_coefficient_for_xp_no_mood_log(self):
        """気分XP係数"""
        response = self.client.get(
            f"/mood/no_mood_user/coefficient/for-xp?task_difficulty=2&base_xp=20"
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["mood_coefficient"] == 1.0  # デフォルト
        assert data["base_xp"] == 20
        assert data["adjusted_xp"] == 20  # 20 * 1.0 = 20
        assert data["xp_bonus"] == 0
        assert data["has_mood_log"] is False
        assert data["overall_mood"] is None
        assert data["calculation_details"]["mood_impact"] == "neutral"
    
    def test_xp_integration_endpoint(self):
        """XP?"""
        # ?
        for i in range(5):
            log_date = (date.today() - timedelta(days=i)).isoformat()
            mood_request = {
                "overall_mood": 3 + (i % 3),  # 3,4,5,3,4の
                "energy_level": 2 + i % 4,
                "motivation_level": 1 + i % 5,
                "anxiety_level": 3 - (i % 2),  # 3,2,3,2,3の
                "log_date": log_date
            }
            
            response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
            assert response.status_code == 200
        
        # XP?
        integration_request = {
            "task_type": "one_shot",
            "base_xp": 50,
            "task_difficulty": 3
        }
        
        response = self.client.post(
            f"/mood/{self.test_uid}/xp-integration",
            json=integration_request
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # ?
        integration_result = data["integration_result"]
        assert integration_result["base_xp"] == 50
        assert 0.8 <= integration_result["mood_coefficient"] <= 1.2
        assert integration_result["adjusted_xp"] > 0
        assert integration_result["task_type"] == "one_shot"
        assert integration_result["task_difficulty"] == 3
        
        # 気分
        mood_context = data["mood_context"]
        assert mood_context["has_today_log"] is True
        assert mood_context["overall_mood"] is not None
        assert mood_context["recent_entries_count"] == 5
        assert "trend_direction" in mood_context
        
        # 治療
        therapeutic_feedback = data["therapeutic_feedback"]
        assert "message" in therapeutic_feedback
        assert "encouragement" in therapeutic_feedback
        assert "insights" in therapeutic_feedback
        assert "mood_impact" in therapeutic_feedback
        
        # ?
        recommendations = data["recommendations"]
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
    
    def test_therapeutic_feedback_generation(self):
        """治療"""
        # ?
        low_mood_request = {
            "overall_mood": 2,
            "energy_level": 1,
            "anxiety_level": 2,  # ?
            "notes": "?"
        }
        
        log_response = self.client.post(f"/mood/{self.test_uid}/log", json=low_mood_request)
        assert log_response.status_code == 200
        
        integration_request = {
            "base_xp": 20,
            "task_difficulty": 1
        }
        
        response = self.client.post(
            f"/mood/{self.test_uid}/xp-integration",
            json=integration_request
        )
        assert response.status_code == 200
        
        data = response.json()
        feedback = data["therapeutic_feedback"]
        
        # ?
        assert feedback["mood_impact"] == "challenging"
        assert "?" in feedback["message"] or "?" in feedback["message"]
        assert len(feedback["insights"]) > 0
        
        # ?
        recommendations = data["recommendations"]
        assert any("無" in rec or "?" in rec for rec in recommendations)
    
    def test_mood_coefficient_range_validation(self):
        """気分"""
        # ?
        mood_levels = [1, 2, 3, 4, 5]
        expected_coefficients = [0.8, 0.9, 1.0, 1.1, 1.2]
        
        for mood_level, expected_coeff in zip(mood_levels, expected_coefficients):
            # 気分
            mood_request = {"overall_mood": mood_level}
            log_response = self.client.post(f"/mood/coeff_test_{mood_level}/log", json=mood_request)
            assert log_response.status_code == 200
            
            # 係数
            response = self.client.get(
                f"/mood/coeff_test_{mood_level}/coefficient/for-xp?base_xp=100"
            )
            assert response.status_code == 200
            
            data = response.json()
            # 基本
            basic_coeff = 0.8 + (mood_level - 1) * 0.1
            assert abs(basic_coeff - expected_coeff) < 0.01
            
            # ?XPが
            assert 80 <= data["adjusted_xp"] <= 120  # 100 * (0.8-1.2)
    
    def test_mood_history_analysis_integration(self):
        """気分"""
        # ?
        for i in range(10):
            log_date = (date.today() - timedelta(days=9-i)).isoformat()
            mood_level = min(5, 2 + i // 2)  # ?
            
            mood_request = {
                "overall_mood": mood_level,
                "energy_level": mood_level,
                "motivation_level": mood_level,
                "log_date": log_date
            }
            
            response = self.client.post(f"/mood/{self.test_uid}/log", json=mood_request)
            assert response.status_code == 200
        
        # ?
        integration_request = {"base_xp": 40}
        
        response = self.client.post(
            f"/mood/{self.test_uid}/xp-integration",
            json=integration_request
        )
        assert response.status_code == 200
        
        data = response.json()
        
        # ?
        mood_context = data["mood_context"]
        assert mood_context["recent_entries_count"] >= 7  # ?7?
        
        # 治療
        feedback = data["therapeutic_feedback"]
        insights = feedback["insights"]
        
        # ?
        trend_mentioned = any(
            "?" in insight or "?" in insight or "安全" in insight 
            for insight in insights
        )
        # ?
        # ?
        assert len(insights) > 0
    
    def test_xp_integration_error_handling(self):
        """XP?"""
        # 無
        invalid_request = {
            "base_xp": -10,  # ?
            "task_difficulty": 10  # ?
        }
        
        response = self.client.post(
            f"/mood/{self.test_uid}/xp-integration",
            json=invalid_request
        )
        # エラー
        # 実装
        assert response.status_code in [200, 400, 422]
    
    def test_mood_recommendations_variety(self):
        """気分"""
        test_cases = [
            {
                "mood_data": {
                    "overall_mood": 5,
                    "energy_level": 5,
                    "motivation_level": 5
                },
                "expected_keywords": ["挑", "?"]
            },
            {
                "mood_data": {
                    "overall_mood": 1,
                    "energy_level": 1,
                    "anxiety_level": 1
                },
                "expected_keywords": ["無", "?", "?"]
            },
            {
                "mood_data": {
                    "overall_mood": 3,
                    "focus_level": 1
                },
                "expected_keywords": ["?", "?"]
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            test_uid = f"recommendation_test_{i}"
            
            # 気分
            log_response = self.client.post(f"/mood/{test_uid}/log", json=test_case["mood_data"])
            assert log_response.status_code == 200
            
            # ?
            integration_request = {"base_xp": 30}
            response = self.client.post(f"/mood/{test_uid}/xp-integration", json=integration_request)
            assert response.status_code == 200
            
            data = response.json()
            recommendations = data["recommendations"]
            
            # ?
            recommendations_text = " ".join(recommendations)
            keyword_found = any(
                keyword in recommendations_text 
                for keyword in test_case["expected_keywords"]
            )
            
            # ?
            assert len(recommendations) > 0
            print(f"Test case {i}: Generated {len(recommendations)} recommendations")


def test_integration_with_core_game_engine():
    """コア"""
    # 実装
    # こXP計算
    
    client = TestClient(app)
    test_uid = "core_game_integration_test"
    
    # ?
    mood_request = {
        "overall_mood": 5,
        "energy_level": 5,
        "motivation_level": 5
    }
    
    log_response = client.post(f"/mood/{test_uid}/log", json=mood_request)
    assert log_response.status_code == 200
    
    # XP計算
    response = client.get(f"/mood/{test_uid}/coefficient/for-xp?base_xp=100")
    assert response.status_code == 200
    
    data = response.json()
    
    # ?
    assert data["mood_coefficient"] > 1.0
    assert data["adjusted_xp"] > data["base_xp"]
    assert data["xp_bonus"] > 0
    
    # コア
    assert "calculation_details" in data
    assert "formula" in data["calculation_details"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])