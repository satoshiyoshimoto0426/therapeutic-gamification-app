"""
Daily Trio Service ?

?
- 3タスク3?
- ADHD?
- AI自動
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from datetime import datetime
import json

# ?
from main import app, daily_trio_engine, UserState, TaskCategory, TaskPriority

client = TestClient(app)

class TestDailyTrioEngine:
    """Daily Trio エラー"""
    
    def test_user_state_analysis(self):
        """ユーザー"""
        user_state = UserState(
            user_id="test_user_001",
            current_state="ACTION",
            mood_trend=0.3,
            energy_level=4,
            available_time=25,
            therapeutic_goals=["Self-Discipline", "Communication"],
            completed_tasks_today=1,
            streak_days=7,
            adhd_assist_level=1.2
        )
        
        analysis = daily_trio_engine._analyze_user_state(user_state)
        
        assert analysis["energy_category"] == "high"
        assert analysis["time_availability"] == "moderate"
        assert analysis["therapeutic_priority"] == "momentum"
        assert analysis["motivation_level"] > 0.5
        
        print("? ユーザー")
    
    def test_task_scoring_algorithm(self):
        """タスク"""
        user_state = UserState(
            user_id="test_user_002",
            current_state="INTEREST",
            mood_trend=0.1,
            energy_level=2,
            available_time=15,
            therapeutic_goals=["Self-Discipline"],
            completed_tasks_today=0,
            streak_days=2,
            adhd_assist_level=1.1
        )
        
        state_analysis = daily_trio_engine._analyze_user_state(user_state)
        scored_tasks = daily_trio_engine._score_tasks(user_state, state_analysis)
        
        # ストーリー
        scores = [score for task, score in scored_tasks]
        assert scores == sorted(scores, reverse=True)
        
        # ?
        top_task = scored_tasks[0][0]
        assert top_task.difficulty <= 3
        
        print("? タスク")
    
    def test_optimal_trio_selection(self):
        """?3つ"""
        user_state = UserState(
            user_id="test_user_003",
            current_state="ACTION",
            mood_trend=0.2,
            energy_level=3,
            available_time=20,
            therapeutic_goals=["Self-Discipline", "Empathy"],
            completed_tasks_today=0,
            streak_days=5,
            adhd_assist_level=1.15
        )
        
        state_analysis = daily_trio_engine._analyze_user_state(user_state)
        scored_tasks = daily_trio_engine._score_tasks(user_state, state_analysis)
        selected_tasks = daily_trio_engine._select_optimal_trio(scored_tasks, user_state)
        
        # 3つ
        assert len(selected_tasks) <= 3
        
        # ?
        total_time = sum(task.estimated_duration for task in selected_tasks)
        assert total_time <= user_state.available_time
        
        # カスタム
        categories = [task.category for task in selected_tasks]
        assert len(set(categories)) >= min(len(selected_tasks), 2)
        
        print("? ?3つ")
    
    async def test_daily_trio_selection_integration(self):
        """Daily Trio?"""
        user_state = UserState(
            user_id="integration_test_user",
            current_state="CONTINUATION",
            mood_trend=0.4,
            energy_level=4,
            available_time=30,
            therapeutic_goals=["Self-Discipline", "Communication", "Resilience"],
            completed_tasks_today=1,
            streak_days=10,
            adhd_assist_level=1.25
        )
        
        response = await daily_trio_engine.select_daily_trio(user_state)
        
        # レベル
        assert response.user_id == user_state.user_id
        assert len(response.trio_tasks) <= 3
        assert response.estimated_total_time <= user_state.available_time
        assert response.expected_xp > 0
        assert len(response.selection_reasoning) > 0
        
        # 治療
        assert isinstance(response.therapeutic_balance, dict)
        
        print("? Daily Trio?")
        return response

class TestADHDOptimization:
    """ADHD?"""
    
    def test_cognitive_load_reduction(self):
        """?"""
        # ?
        low_energy_user = UserState(
            user_id="low_energy_user",
            current_state="APATHY",
            mood_trend=-0.2,
            energy_level=1,
            available_time=10,
            therapeutic_goals=["Self-Discipline"],
            completed_tasks_today=0,
            streak_days=0,
            adhd_assist_level=1.3
        )
        
        state_analysis = daily_trio_engine._analyze_user_state(low_energy_user)
        scored_tasks = daily_trio_engine._score_tasks(low_energy_user, state_analysis)
        selected_tasks = daily_trio_engine._select_optimal_trio(scored_tasks, low_energy_user)
        
        # ?
        for task in selected_tasks:
            assert task.difficulty <= 2  # ?
            assert task.estimated_duration <= 5  # ?
            assert len(task.micro_rewards) > 0  # ?
        
        print("? ?")
    
    def test_micro_reward_system(self):
        """?"""
        # ?
        for task in daily_trio_engine.task_pool:
            assert len(task.micro_rewards) >= 2
            assert all(len(reward) > 0 for reward in task.micro_rewards)
        
        print("? ?")
    
    def test_three_tap_completion_flow(self):
        """3タスク"""
        # 3タスク
        user_id = "three_tap_user"
        
        # 1. Daily Trio?1タスク
        response = client.get(f"/daily-trio/{user_id}")
        assert response.status_code == 200
        trio_data = response.json()
        
        # 2. タスク2タスク
        first_task_id = trio_data["trio_tasks"][0]["task_id"]
        
        # 3. タスク3タスク
        completion_response = client.post(f"/daily-trio/{user_id}/complete/{first_task_id}")
        assert completion_response.status_code == 200
        completion_data = completion_response.json()
        
        # ?
        assert completion_data["success"] is True
        assert completion_data["xp_earned"] > 0
        assert len(completion_data["micro_rewards"]) > 0
        
        print("? 3タスク")

class TestTherapeuticAlignment:
    """治療"""
    
    def test_therapeutic_goal_alignment(self):
        """治療"""
        user_state = UserState(
            user_id="therapeutic_user",
            current_state="ACTION",
            mood_trend=0.1,
            energy_level=3,
            available_time=20,
            therapeutic_goals=["Self-Discipline", "Communication"],
            completed_tasks_today=0,
            streak_days=3,
            adhd_assist_level=1.1
        )
        
        state_analysis = daily_trio_engine._analyze_user_state(user_state)
        scored_tasks = daily_trio_engine._score_tasks(user_state, state_analysis)
        selected_tasks = daily_trio_engine._select_optimal_trio(scored_tasks, user_state)
        
        # 治療
        therapeutic_focuses = [task.therapeutic_focus for task in selected_tasks]
        goal_alignment = any(focus in user_state.therapeutic_goals for focus in therapeutic_focuses)
        assert goal_alignment
        
        print("? 治療")
    
    def test_state_based_task_selection(self):
        """?"""
        # APATHY?
        apathy_user = UserState(
            user_id="apathy_user",
            current_state="APATHY",
            mood_trend=-0.1,
            energy_level=2,
            available_time=15,
            therapeutic_goals=["Self-Discipline"],
            completed_tasks_today=0,
            streak_days=0,
            adhd_assist_level=1.2
        )
        
        state_analysis = daily_trio_engine._analyze_user_state(apathy_user)
        assert state_analysis["therapeutic_priority"] == "engagement"
        
        # HABITUATION?
        habituation_user = UserState(
            user_id="habituation_user",
            current_state="HABITUATION",
            mood_trend=0.3,
            energy_level=4,
            available_time=25,
            therapeutic_goals=["Self-Discipline", "Resilience"],
            completed_tasks_today=2,
            streak_days=21,
            adhd_assist_level=1.0
        )
        
        state_analysis = daily_trio_engine._analyze_user_state(habituation_user)
        assert state_analysis["therapeutic_priority"] == "mastery"
        
        print("? ?")

class TestAPIEndpoints:
    """APIエラー"""
    
    def test_select_daily_trio_endpoint(self):
        """Daily Trio?"""
        user_state_data = {
            "user_id": "api_test_user",
            "current_state": "ACTION",
            "mood_trend": 0.2,
            "energy_level": 3,
            "available_time": 20,
            "therapeutic_goals": ["Self-Discipline", "Communication"],
            "completed_tasks_today": 1,
            "streak_days": 5,
            "adhd_assist_level": 1.1
        }
        
        response = client.post("/daily-trio/select", json=user_state_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "trio_tasks" in data
        assert "selection_reasoning" in data
        assert "estimated_total_time" in data
        assert "expected_xp" in data
        
        print("? Daily Trio?")
    
    def test_get_daily_trio_endpoint(self):
        """Daily Trio?"""
        response = client.get("/daily-trio/test_user")
        assert response.status_code == 200
        
        data = response.json()
        assert "trio_tasks" in data
        assert len(data["trio_tasks"]) <= 3
        
        print("? Daily Trio?")
    
    def test_complete_task_endpoint(self):
        """タスク"""
        response = client.post("/daily-trio/test_user/complete/therapeutic_001")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "xp_earned" in data
        assert "micro_rewards" in data
        
        print("? タスク")
    
    def test_progress_endpoint(self):
        """?"""
        response = client.get("/daily-trio/test_user/progress")
        assert response.status_code == 200
        
        data = response.json()
        assert "completion_rate" in data
        assert "total_xp_earned" in data
        assert "next_task_hint" in data
        
        print("? ?")

def run_all_tests():
    """?"""
    print("Daily Trio Service ?")
    print("=" * 50)
    
    # 基本
    engine_tests = TestDailyTrioEngine()
    engine_tests.test_user_state_analysis()
    engine_tests.test_task_scoring_algorithm()
    engine_tests.test_optimal_trio_selection()
    
    # ?
    async def run_async_tests():
        await engine_tests.test_daily_trio_selection_integration()
    
    asyncio.run(run_async_tests())
    
    # ADHD?
    adhd_tests = TestADHDOptimization()
    adhd_tests.test_cognitive_load_reduction()
    adhd_tests.test_micro_reward_system()
    adhd_tests.test_three_tap_completion_flow()
    
    # 治療
    therapeutic_tests = TestTherapeuticAlignment()
    therapeutic_tests.test_therapeutic_goal_alignment()
    therapeutic_tests.test_state_based_task_selection()
    
    # APIエラー
    api_tests = TestAPIEndpoints()
    api_tests.test_select_daily_trio_endpoint()
    api_tests.test_get_daily_trio_endpoint()
    api_tests.test_complete_task_endpoint()
    api_tests.test_progress_endpoint()
    
    print("\n" + "=" * 50)
    print("? Daily Trio Service ?")
    print("\n?:")
    print("- 3タスク3? ?")
    print("- ADHD?1?3タスク ?")
    print("- AI自動 ?")
    print("- 治療 ?")
    print("- ? ?")

if __name__ == "__main__":
    run_all_tests()